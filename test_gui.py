import sys

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5 import QtCore
from DongleHandler import *
import random
from command_parser import *
from openpyxl import Workbook
import os
import subprocess
import time
import logging
import serial
from result_parser import *

GUIlogger = logging.getLogger("GUI")
GUIlogger.setLevel(logging.DEBUG)

def serial_ports():   
    """ Lists serial port names   
       
        :raises EnvironmentError:   
            On unsupported or unknown platforms   
        :returns:   
            A list of the serial ports available on the system   
    """   
    if sys.platform.startswith('win'):   
        ports = ['COM%s' % (i + 1) for i in range(256)]   
    else:   
        raise EnvironmentError('Unsupported platform')   
       
    result = []   
    for port in ports:   
        try:   
            s = serial.Serial(port)   
            s.close()   
            result.append(port)   
        except (OSError, serial.SerialException):   
            pass   
    return result   

# UI파일 연결 - UI파일은 Python 코드 파일과 같은 디렉토리에 위치
form_class = uic.loadUiType("mainwindow.ui")[0]

attribute_model = QStandardItemModel()
command_model = QStandardItemModel()
process_model = QStandardItemModel()
result_model = QStandardItemModel()
command_data = []
log_data = []
is_changed = False
log_file_name = ""
attribute_data = [
    {"type": "on/off", "objects": ["ON_OFF_ONOFF_ATTR"]},
    {"type": "color", "objects": ["COLOR_CTRL_CURR_HUE_ATTR", "COLOR_CTRL_CURR_SAT_ATTR",
                                  "COLOR_CTRL_REMAINING_TIME_ATTR", "COLOR_CTRL_CURR_X_ATTR",
                                  "COLOR_CTRL_CURR_Y_ATTR", "COLOR_CTRL_COLOR_TEMP_MIRED_ATTR",
                                  "COLOR_CTRL_COLOR_MODE_ATTR", "COLOR_CTRL_ENHANCED_COLOR_MODE_ATTR",
                                  "COLOR_CTRL_COLOR_CAPABILITY_ATTR", "COLOR_CTRL_COLOR_TEMP_MIN_MIRED_ATTR",
                                  "COLOR_CTRL_COLOR_TEMP_MAX_MIRED_ATTR"]},
    {"type": "level", "objects": ["LVL_CTRL_CURR_LVL_ATTR", "LVL_CTRL_REMAIN_TIME_ATTR",
                                  "LVL_CTRL_ONOFF_TRANS_TIME_ATTR", "LVL_CTRL_ON_LEVEL_ATTR"]}]


class Worker(QThread):
    threadEvent = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.device_addr = ""
        self.device_name = ""
        self.device_ep = 0
        self.module_type = 0
        self.isRun = False
        self.device_uuid = ""
        self.main = parent

    def run(self):
        while self.isRun:
            print(command_data)
            log_list = []
            if self.module_type == 0:  # Zigbee_HA
                zblogger = ZigbeeLogger()
                zblogger.log_init()

                if "iteration" in command_data:  # routine 의 경우
                    iteration = command_data["iteration"]
                elif "tasks" in command_data:  # routine 형식이 아닐 경우
                    single_command_list = command_data["tasks"]
                    task_list = parse_zigbee_task_list(single_command_list)
                    name = self.device_name
                    uuid = self.device_uuid
                    addr = int(self.device_addr, 16)
                    ep = self.device_ep
                    device = Device(name, uuid, addr, ep)
                    task_routine = TaskRoutine(device, 0, task_list, 1)
                    task_routine.start_routine()
                log_data = OrderedDict()
                log_data["log_list"] = log_list

            # 로그 다 찍고 표시 다 했을 경우 아래 처럼 쓰레드 종료
            self.isRun = False
            self.threadEvent.emit()

def parse_zigbee_task_list(list):
    task_list = []
    for parsed_task in list:
        task_kind = parsed_task['task_kind']
        cluster = parsed_task['cluster']
        duration = parsed_task['duration']
        if task_kind == COMMAND_TASK:
            command = parsed_task['command']
            payloads = parsed_task['payloads']
            if payloads == 'random':
                random_task = Cmd.generate_random_random_cmd(cluster, duration)
                task_list.append(random_task)
            else:
                cmd_task = Cmd(cluster, command, payloads, duration)
                task_list.append(cmd_task)
            
        elif task_kind == READ_ATTRIBUTE_TASK:
            attr_id = parsed_task['attr_id']
            read_attr_task = ReadAttr(cluster, attr_id, duration)
            task_list.append(read_attr_task)
        elif task_kind == WRITE_ATTRIBUTE_TASK:
            attr_id = parsed_task['attr_id']
            write_attr_task = WriteAttr(cluster, attr_id, duration)
            task_list.append(write_attr_task)
    return task_list

def parse_zigbee_routine(device, list):
    iteration   = list['iteration']
    file_list = list['task_list']
    task_list = []
    duration = 0.51
    for file_name in file_list:    
        if 'onoff_random' in file_name:
            random_task = Cmd.generate_random_random_cmd(ON_OFF_CLUSTER, duration)
            task_list.append(random_task)
        elif 'level_random' in file_name:
            random_task = Cmd.generate_random_random_cmd(LVL_CTRL_CLUSTER, duration)
            task_list.append(random_task)
        elif 'color_random' in file_name:
            random_task = Cmd.generate_random_random_cmd(COLOR_CTRL_CLUSTER, duration)
            task_list.append(random_task)
        else: 
            task = parse_json_command(file_name)
            task_list.append(task)
    return TaskRoutine(device, 0, task_list, iteration)

# Main화면을 띄우는데 사용되는 Class 선언
class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # menu bar
        self.action_import_device.triggered.connect(self.import_device)
        self.action_import_command.triggered.connect(self.import_command)
        self.action_export_device.triggered.connect(self.export_device)
        self.action_export_command.triggered.connect(self.export_command)

        # main window
        self.btn_more.clicked.connect(self.click_more)
        self.btn_start.clicked.connect(self.click_start)
        self.btn_save.clicked.connect(self.click_save)
        self.btn_clear_command.clicked.connect(self.click_clear_command)

        self.cbo_module.currentIndexChanged.connect(self.module_changed)
        self.cbo_port.currentIndexChanged.connect(self.set_serial_port)
        self.cbo_port.clear()
        self.cbo_port.addItems( serial_ports())
        # for port in serial_ports():
        #     self.cbo_port.addItems()
        self.tabWidget.currentChanged.connect(self.changed_command_tab)
        # self.worker = Worker()
        # self.worker.threadEvent.connect(self.show_result)

        self.btn_up.clicked.connect(self.click_item_up)
        self.btn_down.clicked.connect(self.click_item_down)
        self.btn_up.hide()
        self.btn_down.hide()
        self.listView_command.setDragDropMode(QAbstractItemView.InternalMove)
        self.listView_command.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.listView_command.setSpacing(5)
        self.listView_command.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView_process.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView_process.setSelectionMode(QAbstractItemView.NoSelection)
        self.listView_process.setSpacing(5)
        self.listView_result.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView_result.setSelectionMode(QAbstractItemView.NoSelection)
        self.listView_result.setSpacing(5)

        self.listView_command.setModel(command_model)
        self.listView_process.setModel(process_model)
        self.listView_result.setModel(result_model)

        # read attribute tab
        self.treeView.setModel(attribute_model)
        self.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.treeView.setHeaderHidden(True)
        if self.cbo_module.currentIndex() == 0:
            for j, _type in enumerate(attribute_data):
                item = QStandardItem(_type["type"])
                for obj in _type["objects"]:
                    child = QStandardItem(obj)
                    item.appendRow(child)
                attribute_model.setItem(j, 0, item)
        self.btn_insert_attribute.clicked.connect(self.click_read_attribute)

        # single command tab
        self.cbo_input_onoff.currentIndexChanged.connect(self.select_onoff_input_style)
        self.cbo_input_color.currentIndexChanged.connect(self.select_color_input_style)
        self.cbo_input_level.currentIndexChanged.connect(self.select_level_input_style)
        self.btn_insert.clicked.connect(self.click_insert)

        # routine tab
        self.cbo_input_onoff_routine.currentIndexChanged.connect(self.select_onoff_routine_input_style)
        self.cbo_input_color_routine.currentIndexChanged.connect(self.select_color_routine_input_style)
        self.cbo_input_level_routine.currentIndexChanged.connect(self.select_level_routine_input_style)
        self.btn_insert_routine.clicked.connect(self.click_insert_routine)

    def click_item_up(self):
        item = self.listView_command.selectedIndexes()
        if item:  # item != []
            row = item[0].row()
            column = item[0].column()
            print(item, "up", row, column)
            # command_model.beginMoveColumns(self, item[0].first(),item[0].last(), command_model.itemFromIndex(self, row-1),column)

    def click_item_down(self):
        item = self.listView_command.selectedIndexes()
        if item:  # item != []
            row = item[0].row()
            print(item, "down", row)

    def click_clear_command(self):
        print("clear command")
        # if self.worker.isRun:
        #     command_model.clear()
        # else:
        command_model.clear()
        process_model.clear()
        result_model.clear()

    def import_command(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file', './')
        if file_name[0]:
            input_command = read_command_from_json(file_name[0], self.cbo_module.currentIndex())
            if input_command:
                command_model.clear()
                for command in input_command:
                    self.add_command(command)
            else:
                QMessageBox.about(self, "명령 정보 가져오기 실패", "명령 파일이 아닙니다.")

    def import_device(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file', './')
        if file_name[0]:
            with open(file_name[0]) as json_file:
                json_data = json.load(json_file)
                if "uuid" in json_data:
                    self.lineEdit_device_name.setText(json_data["name"])
                    self.lineEdit_device_uuid.setText(json_data["uuid"])
                    self.lineEdit_device_addr.setText(json_data["eui64"])
                    self.lineEdit_device_ep.setText(json_data["ep"])
                else:
                    QMessageBox.about(self, "장치 정보 불러오기 실패", "장치 파일이 아닙니다.")

    def export_device(self):
        name = self.lineEdit_device_name.text()
        uuid = self.lineEdit_device_uuid.text()
        addr = self.lineEdit_device_addr.text()
        ep = self.lineEdit_device_ep.text()
        if name != "" and uuid != "" and addr != "" and ep != "":
            device_data = OrderedDict()
            device_data["name"] = name
            device_data["uuid"] = uuid
            device_data["eui64"] = addr
            device_data["ep"] = ep
            with open('device.json', 'w', encoding='utf-8') as make_file:
                json.dump(device_data, make_file, ensure_ascii=False, indent="\t")
        else:
            QMessageBox.about(self, "장치정보 파일 생성 실패", "장치 정보가 입력되지 않았습니다.")

    def export_command(self):
        count = command_model.rowCount()
        if count != 0:
            list = []
            for index in range(command_model.rowCount()):
                item = command_model.item(index).text()
                list.append(item)
            first_item = list[0].split(", ")
            if first_item[0] == "routine":
                make_command(list, self.cbo_module.currentIndex(), int(first_item[1]), True)
            else:
                make_command(list, self.cbo_module.currentIndex(), make_file=True)
        else:
            QMessageBox.about(self, "명령 파일 생성 실패", "명령이 입력되지 않았습니다.")

    def add_command(self, command_string, count=1):
        for i in range(count):
            command_model.appendRow(QStandardItem(command_string))

    def changed_command_tab(self):
        tab_now = self.tabWidget.currentIndex()
        # if tab_now != 0: #single, routine
        #     if tab_before != tab_now:
        #         command_model.clear()
        #         process_model.clear()
        #         result_model.clear()
        #     else:
        #         tab_before = tab_now

    def set_serial_port(self):
        global is_changed
        # if self.worker.isRun and not is_changed:
            # QMessageBox.about(self, "시리얼 포트 설정 실패", "실험이 진행중이라 포트가 변경되지 않습니다.")
            # with open('resource\\dongle_status.json', "r") as dongle_file:
            #     dongle_config = json.load(dongle_file)
            #     port = dongle_config['port']
            #     is_changed = True
            #     self.cbo_port.setCurrentIndex(int(port.split("COM")[1])-1)
            #     dongle_file.close()
        # elif not self.worker.isRun:
            # is_changed = False
        with open('resource\\dongle_status.json', "r") as dongle_file:
            dongle_config = json.load(dongle_file)
            status = dongle_config['status']
            dongle_file.close()
        with open('resource\\dongle_status.json', "w") as dongle_file:
            dongle_config['port'] = self.cbo_port.currentText()
            json.dump(dongle_config, dongle_file)
            dongle_file.close()
    

    def module_changed(self):
        if self.cbo_module.currentIndex() == 0:
            attribute_model.clear()
            for j, _type in enumerate(attribute_data):
                item = QStandardItem(_type["type"])
                for obj in _type["objects"]:
                    child = QStandardItem(obj)
                    item.appendRow(child)
                attribute_model.setItem(j, 0, item)

    def select_onoff_input_style(self):
        index = self.cbo_input_onoff.currentIndex()
        if index == 0:
            self.rdo_on.show()
            self.rdo_off.show()
            self.rdo_toggle.show()
        elif index == 1:
            self.rdo_on.hide()
            self.rdo_off.hide()
            self.rdo_toggle.hide()
        elif index == 2:
            self.rdo_on.hide()
            self.rdo_off.hide()
            self.rdo_toggle.hide()
        else:
            self.rdo_on.hide()
            self.rdo_off.hide()
            self.rdo_toggle.hide()

    def select_onoff_routine_input_style(self):
        index = self.cbo_input_onoff_routine.currentIndex()
        if index == 0:
            self.rdo_on_routine.show()
            self.rdo_off_routine.show()
            self.rdo_toggle_routine.show()
        elif index == 1:
            self.rdo_on_routine.hide()
            self.rdo_off_routine.hide()
            self.rdo_toggle_routine.hide()
        elif index == 2:
            self.rdo_on_routine.hide()
            self.rdo_off_routine.hide()
            self.rdo_toggle_routine.hide()
        else:
            self.rdo_on_routine.hide()
            self.rdo_off_routine.hide()
            self.rdo_toggle_routine.hide()

    def select_color_input_style(self):
        index = self.cbo_input_color.currentIndex()
        if index == 0:
            self.lineEdit_color.show()
        elif index == 1:
            self.lineEdit_color.hide()
        elif index == 2:
            self.lineEdit_color.hide()
        else:
            self.lineEdit_color.hide()

    def select_color_routine_input_style(self):
        index = self.cbo_input_color_routine.currentIndex()
        if index == 0:
            self.cbo_routine_color_value.show()
        elif index == 1:
            self.cbo_routine_color_value.hide()
        elif index == 2:
            self.cbo_routine_color_value.hide()
        else:
            self.cbo_routine_color_value.hide()

    def select_level_input_style(self):
        index = self.cbo_input_level.currentIndex()
        if index == 0:
            self.lineEdit_level.show()
        elif index == 1:
            self.lineEdit_level.hide()
        elif index == 2:
            self.lineEdit_level.hide()
        else:
            self.lineEdit_level.hide()

    def select_level_routine_input_style(self):
        index = self.cbo_input_level_routine.currentIndex()
        if index == 0:
            self.cbo_routine_level_value.show()
        elif index == 1:
            self.cbo_routine_level_value.hide()
        elif index == 2:
            self.cbo_routine_level_value.hide()
        else:
            self.cbo_routine_level_value.hide()

    def click_read_attribute(self):
        module_type = self.cbo_module.currentIndex()
        if module_type == 0:  # Zigbee HA
            selected = attribute_model.itemData(self.treeView.selectedIndexes()[0])[0]
            if selected not in ["on/off", "color", "level"]:
                self.add_command("read attribute, " + selected)

    def click_insert(self):
        print("btn_insert Clicked")
        module_type = self.cbo_module.currentIndex()
        if module_type == 0:  # Zigbee HA
            command_type = self.tab_single.currentIndex()
            if command_type == 0:  # connect
                item = "connect"
                self.add_command(item)
            elif command_type == 1:  # on/off
                onoff_input_type = self.cbo_input_onoff.currentIndex()
                onoff_count = self.spinBox_onoff.value()
                if onoff_input_type == 0:  # self input
                    if self.rdo_on.isChecked():
                        item = "on/off, on"
                        self.add_command(item, onoff_count)
                    elif self.rdo_off.isChecked():
                        item = "on/off, off"
                        self.add_command(item, onoff_count)
                    elif self.rdo_toggle.isChecked():
                        item = "on/off, toggle"
                        self.add_command(item, onoff_count)
                    else:
                        print("insert nothing")
                elif onoff_input_type == 1:  # regular random
                    for i in range(onoff_count):
                        item = "on/off, regular random"
                        self.add_command(item)
                elif onoff_input_type == 2:  # irregular random
                    for i in range(onoff_count):
                        item = "on/off, irregular random" 
                        self.add_command(item)
                else:  # random
                    for i in range(onoff_count):
                        item = "on/off, random"
                        self.add_command(item)
            elif command_type == 2:  # color
                color_input_type = self.cbo_input_color.currentIndex()
                color_count = self.spinBox_color.value()
                if color_input_type == 0:  # self input
                    temp = self.lineEdit_color.text()
                    if "0x" in temp:
                        item = "color, " + str(int(temp, 0))
                        self.add_command(item, color_count)
                    elif temp.isdigit and temp != "":
                        item = "color, " + temp
                        self.add_command(item, color_count)
                elif color_input_type == 1:  # regular random
                    for i in range(color_count):
                        item = "color, regular random" 
                        self.add_command(item)
                elif color_input_type == 2:  # irregular random
                    for i in range(color_count):
                        item = "color, irregular random"
                        self.add_command(item)
                else:  # random
                    for i in range(color_count):
                        item = "color, random"
                        self.add_command(item)
            elif command_type == 3:  # level
                level_input_type = self.cbo_input_level.currentIndex()
                level_count = self.spinBox_level.value()
                if level_input_type == 0:  # self input
                    temp = self.lineEdit_level.text()
                    if "0x" in temp:
                        item = "level, " + str(int(temp, 0))
                        self.add_command(item, level_count)
                    elif temp.isdigit and temp != "":
                        item = "level, " + temp
                        self.add_command(item, level_count)
                elif level_input_type == 1:  # regular random
                    for i in range(level_count):
                        item = "level, regular random"
                        self.add_command(item)
                elif level_input_type == 2:  # irregular random
                    for i in range(level_count):
                        item = "level, irregular random"
                        self.add_command(item)
                else:
                    for i in range(level_count):
                        item = "level, random"
                        self.add_command(item)
            else:  # disconnect
                item = "disconnect"
                self.add_command(item)
        # elif type == 1: #Zigbee 3.0
        # elif type == 2: #BLE
        # else: #UART

    def click_insert_routine(self):
        GUIlogger.debug("click_insert_routine:btn_insert_routine Clicked")
        # print("btn_insert_routine Clicked")
        command_model.clear()
        process_model.clear()
        result_model.clear()

        module_type = self.cbo_module.currentIndex()
        if module_type == 0:  # Zigbee HA
            order = self.cbo_routine.currentIndex()
            item_connect = "connect"
            item_disconnect = "disconnect"
            item_onoff = ""
            item_color = ""
            item_level = ""
            onoff_items = []
            color_items = []
            level_items = []

            onoff_input_type = self.cbo_input_onoff_routine.currentIndex()
            onoff_routine_count = self.spinBox_onoff_routine.value()
            if onoff_routine_count != 0:
                if onoff_input_type == 0:  # self input
                    if self.rdo_on_routine.isChecked():
                        item_onoff = "on/off, on"
                    elif self.rdo_off_routine.isChecked():
                        item_onoff = "on/off, off"
                    elif self.rdo_toggle_routine.isChecked():
                        item_onoff = "on/off, toggle"
                    else:
                        print("insert nothing")
                elif onoff_input_type == 1:  # regular random
                    for i in range(onoff_routine_count):
                        item_onoff = "on/off, regular random" 
                        onoff_items.append(item_onoff)
                elif onoff_input_type == 2:  # irregular random
                    for i in range(onoff_routine_count):
                        item_onoff = "on/off, irregular random" 
                        onoff_items.append(item_onoff)
                else:  # random
                    for i in range(onoff_routine_count):
                        item_onoff = "on/off, random"
                        onoff_items.append(item_onoff)

            color_input_type = self.cbo_input_color_routine.currentIndex()
            color_routine_count = self.spinBox_color_routine.value()
            if color_routine_count != 0:
                if color_input_type == 0:  # self input
                    temp = self.cbo_routine_color_value.currentText()
                    item_color = "color, " + temp
                elif color_input_type == 1:  # regular random
                    for i in range(color_routine_count):
                        item_color = "color, regular random"
                        color_items.append(item_color)
                elif color_input_type == 2:  # irregular random
                    for i in range(color_routine_count):
                        item_color = "color, irregular random"
                        color_items.append(item_color)
                else:
                    for i in range(color_routine_count):
                        item_color = "color, random"
                        color_items.append(item_color)

            level_input_type = self.cbo_input_color_routine.currentIndex()
            level_routine_count = self.spinBox_level_routine.value()
            if level_routine_count != 0:
                if level_input_type == 0:  # self input
                    temp = self.cbo_routine_level_value.currentText()
                    item_level = "level, " + temp
                elif level_input_type == 1:  # regular random
                    for i in range(level_routine_count):
                        item_level = "level, regular random"
                        level_items.append(item_level)
                elif level_input_type == 2:  # irregular random
                    for i in range(level_routine_count):
                        item_level = "level, irregular random"
                        level_items.append(item_level)
                else:
                    for i in range(level_routine_count):
                        item_level = "level, random"
                        level_items.append(item_level)

            self.add_command("routine, " + str(self.spinBox_routine.value()))
            self.add_command(item_connect)
            if order == 0:  # connect-onoff-color-level-disconnect
                if item_onoff != "":
                    if onoff_items:
                        for item in onoff_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_onoff, onoff_routine_count)
                if item_color != "":
                    if color_items:
                        for item in color_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_color, color_routine_count)
                if item_level != "":
                    if level_items:
                        for item in level_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_level, level_routine_count)
            elif order == 1:  # connect-onoff-level-color-disconnect
                if item_onoff != "":
                    if onoff_items:
                        for item in onoff_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_onoff, onoff_routine_count)
                if item_level != "":
                    if level_items:
                        for item in level_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_level, level_routine_count)
                if item_color != "":
                    if color_items:
                        for item in color_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_color, color_routine_count)
            elif order == 2:  # connect-color-onoff-level-disconnect
                if item_color != "":
                    if color_items:
                        for item in color_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_color, color_routine_count)
                if item_onoff != "":
                    if onoff_items:
                        for item in onoff_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_onoff, onoff_routine_count)
                if item_level != "":
                    if level_items:
                        for item in level_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_level, level_routine_count)
            elif order == 3:  # connect-level-onoff-color-disconnect
                if item_level != "":
                    if level_items:
                        for item in level_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_level, level_routine_count)
                if item_onoff != "":
                    if onoff_items:
                        for item in onoff_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_onoff, onoff_routine_count)
                if item_color != "":
                    if color_items:
                        for item in color_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_color, color_routine_count)
            elif order == 4:  # connect-color-level-onoff-disconnect
                if item_color != "":
                    if color_items:
                        for item in color_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_color, color_routine_count)
                if item_level != "":
                    if level_items:
                        for item in level_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_level, level_routine_count)
                if item_onoff != "":
                    if onoff_items:
                        for item in onoff_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_onoff, onoff_routine_count)
            else:  # connect-level-color-onoff-disconnect
                if item_level != "":
                    if level_items:
                        for item in level_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_level, level_routine_count)
                if item_color != "":
                    if color_items:
                        for item in color_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_color, color_routine_count)
                if item_onoff != "":
                    if onoff_items:
                        for item in onoff_items:
                            self.add_command(item)
                    else:
                        self.add_command(item_onoff, onoff_routine_count)
            self.add_command(item_disconnect)

        # elif module_type == 1: #Zigbee 3.0
        # elif module_type == 2: #BLE
        # else: #UART

    def click_more(self):
        GUIlogger.debug("click_more:more clicked")
        # print("more clicked")
        # if self.worker.isRun:
        #     QMessageBox.about(self, "더보기 실패", "실험이 진행중이라, 결과 저장이 불가능합니다.")
        # elif not log_data:
        #     QMessageBox.about(self, "더보기 실패", "실험 결과가 존재하지 않습니다.")
        # else:
        ResultWindow(self)

    def click_save(self):
        # if self.worker.isRun:
        #     QMessageBox.about(self, "결과 저장 실패", "실험이 진행중이라, 결과 저장이 불가능합니다.")
        if not log_data:
            QMessageBox.about(self, "결과 저장 실패", "실험 결과가 존재하지 않습니다.")
        else:
            save_result()

    def click_start(self):
        GUIlogger.debug("click_start:started")
        # 명령 보내기
        name = self.lineEdit_device_name.text()
        uuid = self.lineEdit_device_uuid.text()
        addr = self.lineEdit_device_addr.text()
        ep = self.lineEdit_device_ep.text()
        module_type = self.cbo_module.currentIndex()
        count = command_model.rowCount()
        if name != "" and uuid != "" and addr != "" and ep != "" and count != 0:
            # if self.worker.isRun:
            #     QMessageBox.about(self, "실험 시작 실패", "이미 진행중인 실험이 있습니다.")
            # else:
                global command_data
                process_model.clear()
                result_model.clear()
                list = []
                for index in range(command_model.rowCount()):
                    item = command_model.item(index).text()
                    list.append(item)
                first_item = list[0].split(", ")
                global log_file_name, log_data
                if first_item[0] == "routine":
                    json_type_command = make_command(list, module_type, int(first_item[1]))
                    command_data = json_type_command
                    device = Device(name, uuid, int(addr, 16), int(ep))
                    task_routine = parse_zigbee_routine(device, command_data)
                    log_file_name = task_routine.start_routine()
                    if log_file_name != "":
                        process_model.clear()
                        result_model.clear()
                        log_data = analyze_result(log_file_name)
                        for item in log_data:
                                item_string = str(item)
                                i = QStandardItem(item_string)
                                if item[-1] == "OK":
                                    i.setBackground(QColor('#7fc97f'))
                                    process_model.appendRow(i)
                                else:
                                    i.setBackground(QColor('#f0027f'))
                                    process_model.appendRow(i)        
                        self.show_result()
                else:
                    json_type_command = make_command(list, module_type)
                    command_data = json_type_command
                   
                    task_list =  parse_zigbee_task_list(command_data["tasks"])
                    device = Device(name, uuid, int(addr, 16), int(ep))
                    task_routine = TaskRoutine(device, 0, task_list, 1)
                    log_file_name = task_routine.start_routine()
                    if log_file_name != "":
                        process_model.clear()
                        result_model.clear()
                        log_data = analyze_result(log_file_name)
                        for item in log_data:
                                item_string = str(item)
                                i = QStandardItem(item_string)
                                if item[-1] == "OK":
                                    i.setBackground(QColor('#7fc97f'))
                                    process_model.appendRow(i)
                                else:
                                    i.setBackground(QColor('#f0027f'))
                                    process_model.appendRow(i)        
                        self.show_result()
                # self.worker.device_addr =addr
                # self.worker.device_uuid = uuid
                # self.worker.device_name = name
                # self.worker.ep = int(ep) 
                # self.worker.module_type = module_type
                # self.worker.isRun = True
                # self.worker.start()
        elif count == 0:
            QMessageBox.about(self, "실험 시작 실패", "커맨드가 입력되지 않았습니다.")
        else:
            QMessageBox.about(self, "실험 시작 실패", "장치 정보가 입력되지 않았습니다.")

    def show_result(self):
        for index in range(process_model.rowCount()):
            item = process_model.item(index).text()
            result = item.split(", ")
            i = QStandardItem(item)
            if "OK" in result[-1]:
                i.setBackground(QColor('#7fc97f'))
                result_model.appendRow(i)
            else:
                i.setBackground(QColor('#f0027f'))
                result_model.appendRow(i)


class ResultWindow(QMainWindow):
    def __init__(self, parent):
        super(ResultWindow, self).__init__(parent)
        result_ui = 'resultwindow.ui'
        uic.loadUi(result_ui, self)
        self.tableView.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.btn_save.clicked.connect(self.click_save)
        self.btn_print.clicked.connect(self.click_print)

        
        if log_data != []:
            table_model = QStandardItemModel()
            self.tableView.setModel(table_model)
            self.tableView.setColumnWidth(8, 320)
            self.tableView.setRowHeight(len(log_data) - 1, 20)
            table_model.setHorizontalHeaderLabels(['Timestamp', 'Task kind', 'Cluster', 'Command', 'Payload','Duration',
                                               'Return value', 'Result'])
            for item in log_data:
                print(item)
                timestamp = item[0]
                task_kind = item[1]
                cluster = item[2]
                command = item[3]
                if task_kind == COMMAND_TASK:
                    payloads = item[4]
                    duration = item[5]
                    result = item[6]
                    table_model.appendRow([QStandardItem(timestamp), QStandardItem(task_kind), QStandardItem(cluster),
                                       QStandardItem(command), QStandardItem(payloads), QStandardItem(duration),
                                       QStandardItem(""), QStandardItem(result)])
                elif task_kind == READ_ATTRIBUTE_TASK:
                    duration = item[4]
                    return_val = item[5]
                    result = item[6]
                    table_model.appendRow([QStandardItem(timestamp), QStandardItem(task_kind), QStandardItem(cluster),
                                       QStandardItem(command), QStandardItem(""), QStandardItem(duration),
                                       QStandardItem(return_val), QStandardItem(result)])
                
        self.show()

    def click_save(self):
        save_result()

    def click_print(self):
        save_result()
        if sys.platform == "win32":
            os.startfile('test.xlsx', "print")
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, 'test.xlsx'])


def save_result():
    write_wb = Workbook()
    write_ws = write_wb.active
    write_ws['A1'] = 'Timestamp'
    write_ws['B1'] = 'Task kind'
    write_ws['C1'] = 'Cluster'
    write_ws['D1'] = 'Command'
    write_ws['E1'] = 'Payload'
    write_ws['F1'] = 'Duration'
    write_ws['G1'] = 'Return value'
    write_ws['H1'] = 'Result'
    if log_data != []:
        for item in log_data:
            timestamp = item[0]
            task_kind = item[1]
            cluster = item[2]
            command = item[3]
            if task_kind == COMMAND_TASK:
                payloads = item[4]
                duration = item[5]
                result = item[6]
                write_ws.append([timestamp, task_kind, cluster, command, payloads, duration, "", result])
            elif task_kind == READ_ATTRIBUTE_TASK:
                duration = item[4]
                return_val = item[5]
                result = item[6]
                write_ws.append([timestamp, task_kind, cluster, command, "", duration, return_val, result])
        write_wb.save('test.xlsx')
    GUIlogger.debug("save_result: result saved.")


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)
    # MainWindow의 인스턴스 생성
    myWindow = MainWindow()
    # 프로그램 화면을 보여주는 코드
    myWindow.show()
    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
