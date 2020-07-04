import random
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5 import QtCore
from command_parser import *
from openpyxl import Workbook
import os
import subprocess

# UI파일 연결 - UI파일은 Python 코드 파일과 같은 디렉토리에 위치
form_class = uic.loadUiType("mainwindow_tab.ui")[0]

command_model = QStandardItemModel()
process_model = QStandardItemModel()
result_model = QStandardItemModel()


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
        command_model.clear()

    def import_command(self):
        print("import command")
        file_name = QFileDialog.getOpenFileName(self, 'Open file', './')
        if file_name[0]:
            read_command_from_json(file_name[0])

    def import_device(self):
        print("import device")
        file_name = QFileDialog.getOpenFileName(self, 'Open file', './')
        if file_name[0]:
            with open(file_name[0]) as json_file:
                json_data = json.load(json_file)
                self.lineEdit_device_name.setText(json_data["name"])
                self.lineEdit_device_uuid.setText(json_data["uuid"])
                self.lineEdit_device_addr.setText(json_data["eui64"])
                self.lineEdit_device_ep.setText(json_data["ep"])

    def export_device(self):
        print("export device")
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
            print("device info not exist")
            QMessageBox.about(self, "fail making json", "장치 정보가 입력되지 않았습니다.")

    def export_command(self):
        print("\nexport command")
        count = command_model.rowCount()
        if count != 0:
            list = []
            for index in range(command_model.rowCount()):
                item = command_model.item(index).text()
                list.append(item)
            make_command(list, self.cbo_module.currentIndex(), self.cbo_port.currentIndex())
        else:
            print("command not exist")
            QMessageBox.about(self, "fail making json", "커맨드가 입력되지 않았습니다.")

    def add_command(self, command_string, count):
        for i in range(count):
            command_model.appendRow(QStandardItem(command_string))

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
            self.lineEdit_color_routine.show()
        elif index == 1:
            self.lineEdit_color_routine.hide()
        elif index == 2:
            self.lineEdit_color_routine.hide()
        else:
            self.lineEdit_color_routine.hide()

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
            self.lineEdit_level_routine.show()
        elif index == 1:
            self.lineEdit_level_routine.hide()
        elif index == 2:
            self.lineEdit_level_routine.hide()
        else:
            self.lineEdit_level_routine.hide()

    def click_insert(self):
        print("btn_insert Clicked")
        module_type = self.cbo_module.currentIndex()
        if module_type == 0:  # Zigbee HA
            command_type = self.tab_single.currentIndex()
            if command_type == 0:  # connect
                item = "connect"
                self.add_command(item, 1)
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
                        item = "on/off, toggle, 빠질 예정 "
                        # self.add_command(item)
                    else:
                        print("insert nothing")
                elif onoff_input_type == 1:  # regular random
                    # temp = random.randint(0x00, 0x01)
                    # item = "on/off, " + hex(temp)
                    item = "on/off, regular random"
                    self.add_command(item, onoff_count)
                elif onoff_input_type == 2:  # irregular random
                    # temp = random.randint(0x00, 0x01)
                    # item = "on/off, " + hex(temp)
                    item = "on/off, irregular random"
                    self.add_command(item, onoff_count)
                else:  # random
                    # temp = random.randint(0x00, 0x01)
                    # item = "on/off, " + hex(temp)
                    item = "on/off, random"
                    self.add_command(item, onoff_count)
            elif command_type == 2:  # color
                color_input_type = self.cbo_input_color.currentIndex()
                color_count = self.spinBox_color.value()
                if color_input_type == 0:  # self input
                    temp = self.lineEdit_color.text()
                    if "0x" in temp:
                        item = "color, " + int(temp)
                        self.add_command(item, color_count)
                    elif temp.isdigit and temp != "":
                        # temp = int(temp)
                        item = "color, " + temp
                        self.add_command(item, color_count)
                elif color_input_type == 1:  # regular random
                    # temp = random.randint(200, 370)
                    # item = "color, " + hex(temp)
                    item = "color, regular random"
                    self.add_command(item, color_count)
                elif color_input_type == 2:  # irregular random
                    # temp = random.randint(0x0000, 0xfeff) + 0xff00
                    # item = "color, " + hex(temp)
                    item = "color, irregular random"
                    self.add_command(item, color_count)
                else:  # random
                    # temp = random.randint(200, 370) if random.randint(0, 1) == 0 else random.randint(0x0000,
                    #                                                                                  0xfeff) + 0xff00
                    # item = "color, " + hex(temp)
                    item = "color, random"
                    self.add_command(item, color_count)
            elif command_type == 3:  # level
                level_input_type = self.cbo_input_color.currentIndex()
                level_count = self.spinBox_level.value()
                if level_input_type == 0:  # self input
                    temp = self.lineEdit_level.text()
                    if "0x" in temp:
                        item = "level, " + int(temp)
                        self.add_command(item, level_count)
                    elif temp.isdigit and temp != "":
                        # temp = int(temp)
                        item = "level, " + temp
                        self.add_command(item, level_count)
                elif level_input_type == 1:  # regular random
                    # temp = random.randint(0x00, 0xfe)
                    # item = "level, " + hex(temp)
                    item = "level, regular random"
                    self.add_command(item, level_count)
                elif level_input_type == 2:  # irregular random
                    # temp = random.randint(0x00, 0xfe) + 0xff
                    # item = "level, " + hex(temp)
                    item = "level, irregular random"
                    self.add_command(item, level_count)
                else:
                    # temp = random.randint(0x00, 0xfe) if random.randint(0, 1) == 0 else random.randint(0x00,
                    #                                                                                    0xfe) + 0xff
                    # item = "level, " + hex(temp)
                    item = "level, random"
                    self.add_command(item, level_count)
            else:  # disconnect
                item = "disconnect"
                self.add_command(item, 1)
        # elif type == 1: #Zigbee 3.0
        # elif type == 2: #BLE
        # else: #UART

    def click_insert_routine(self):
        print("btn_insert_routine Clicked")
        module_type = self.cbo_module.currentIndex()
        if module_type == 0:  # Zigbee HA
            order = self.cbo_routine.currentIndex()
            item_connect = "connect"
            item_disconnect = "disconnect"
            item_onoff = ""
            item_color = ""
            item_level = ""

            onoff_input_type = self.cbo_input_onoff_routine.currentIndex()
            onoff_routine_count = self.spinBox_onoff_routine.value()
            if onoff_routine_count != 0:
                if onoff_input_type == 0:  # self input
                    if self.rdo_on_routine.isChecked():
                        item_onoff = "on/off, on"
                    elif self.rdo_off_routine.isChecked():
                        item_onoff = "on/off, off"
                    # elif self.rdo_toggle_routine.isChecked():
                    # item_onoff = "on/off, toggle, 빠질 예정 "
                    else:
                        print("insert nothing")
                elif onoff_input_type == 1:  # regular random
                    # temp = random.randint(0x00, 0x01)
                    # item_onoff = "on/off, " + hex(temp)
                    item_onoff = "on/off, regular random"
                elif onoff_input_type == 2:  # irregular random
                    # temp = random.randint(0x00, 0x01)
                    # item_onoff = "on/off, " + hex(temp)
                    item_onoff = "on/off, irregular random"
                else:  # random
                    # temp = random.randint(0x00, 0x01)
                    # item_onoff = "on/off, " + hex(temp)
                    item_onoff = "on/off, random"
            else:
                print("no onoff")

            color_input_type = self.cbo_input_color_routine.currentIndex()
            color_routine_count = self.spinBox_color_routine.value()
            if color_routine_count != 0:
                if color_input_type == 0:  # self input
                    temp = self.lineEdit_color_routine.text()
                    if "0x" in temp:
                        item_color = "color, " + int(temp)
                    elif temp.isdigit and temp != "":
                        # temp = int(temp)
                        item_color = "color, " + temp
                elif color_input_type == 1:  # regular random
                    # temp = random.randint(200, 370)
                    # item_color = "color, " + hex(temp)
                    item_color = "color, regular random"
                elif color_input_type == 2:  # irregular random
                    # temp = random.randint(0x0000, 0xfeff) + 0xff00
                    # item_color = "color, " + hex(temp)
                    item_color = "color, irregular random"
                else:
                    # temp = random.randint(200, 370) if random.randint(0, 1) == 0 else random.randint(0x0000,
                    #                                                                                  0xfeff) + 0xff00
                    # item_color = "color, " + hex(temp)
                    item_color = "color, random"
            else:
                print("no color")

            level_input_type = self.cbo_input_color_routine.currentIndex()
            level_routine_count = self.spinBox_level_routine.value()
            if level_routine_count != 0:
                if level_input_type == 0:  # self input
                    temp = self.lineEdit_level_routine.text()
                    if "0x" in temp:
                        item_level = "level, " + int(temp)
                    elif temp.isdigit and temp != "":
                        # temp = int(temp)
                        item_level = "level, " + temp
                elif level_input_type == 1:  # regular random
                    # temp = random.randint(0x00, 0xfe)
                    # item_level = "level, " + hex(temp)
                    item_level = "level, regular random"
                elif level_input_type == 2:  # irregular random
                    # temp = random.randint(0x00, 0xfe) + 0xff
                    # item_level = "level, " + hex(temp)
                    item_level = "level, irregular random"
                else:
                    # temp = random.randint(0x00, 0xfe) if random.randint(0, 1) == 0 else random.randint(0x00,
                    #                                                                                    0xfe) + 0xff
                    # item_level = "level, " + hex(temp)
                    item_level = "level, random"
            else:
                print("no level")

            print(item_color, item_level)
            for i in range(self.spinBox_routine.value()):
                self.add_command(item_connect, 1)
                if order == 0:  # connect-onoff-color-level-disconnect
                    if item_onoff != "":
                        self.add_command(item_onoff, onoff_routine_count)
                    if item_color != "":
                        self.add_command(item_color, color_routine_count)
                    if item_level != "":
                        self.add_command(item_level, level_routine_count)
                elif order == 1:  # connect-onoff-level-color-disconnect
                    if item_onoff != "":
                        self.add_command(item_onoff, onoff_routine_count)
                    if item_level != "":
                        self.add_command(item_level, level_routine_count)
                    if item_color != "":
                        self.add_command(item_color, color_routine_count)
                elif order == 2:  # connect-color-onoff-level-disconnect
                    if item_color != "":
                        self.add_command(item_color, color_routine_count)
                    if item_onoff != "":
                        self.add_command(item_onoff, onoff_routine_count)
                    if item_level != "":
                        self.add_command(item_level, level_routine_count)
                elif order == 3:  # connect-level-onoff-color-disconnect
                    if item_level != "":
                        self.add_command(item_level, level_routine_count)
                    if item_onoff != "":
                        self.add_command(item_onoff, onoff_routine_count)
                    if item_color != "":
                        self.add_command(item_color, color_routine_count)
                elif order == 4:  # connect-color-level-onoff-disconnect
                    if item_color != "":
                        self.add_command(item_color, color_routine_count)
                    if item_level != "":
                        self.add_command(item_level, level_routine_count)
                    if item_onoff != "":
                        self.add_command(item_onoff, onoff_routine_count)
                else:  # connect-level-color-onoff-disconnect
                    if item_level != "":
                        self.add_command(item_level, level_routine_count)
                    if item_color != "":
                        self.add_command(item_color, color_routine_count)
                    if item_onoff != "":
                        self.add_command(item_onoff, onoff_routine_count)
                self.add_command(item_disconnect, 1)

        # elif module_type == 1: #Zigbee 3.0
        # elif module_type == 2: #BLE
        # else: #UART

    def click_more(self):
        print("btn_more Clicked")
        ResultWindow(self)

    def click_save(self):
        print("btn_save clicked")
        save_result()

    def click_start(self):
        print("btn_start Clicked")
        count = command_model.rowCount()
        if count != 0:
            for index in range(command_model.rowCount()):
                item = command_model.item(index).text()
                result = random.randint(0, 2)
                if result == 0:
                    i = QStandardItem(item + ",ok")
                    i.setBackground(QColor('#7fc97f'))
                    process_model.appendRow(i)
                else:
                    i = QStandardItem(item + ",error")
                    i.setBackground(QColor('#f0027f'))
                    process_model.appendRow(i)
        self.listView_process.setModel(process_model)


class ResultWindow(QMainWindow):
    def __init__(self, parent):
        super(ResultWindow, self).__init__(parent)
        result_ui = 'resultwindow.ui'
        uic.loadUi(result_ui, self)
        self.tableView.setSelectionMode(QAbstractItemView.NoSelection)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.btn_save.clicked.connect(self.click_save)
        self.btn_print.clicked.connect(self.click_print)

        table_model = QStandardItemModel()
        self.tableView.setModel(table_model)
        self.tableView.setColumnWidth(6, 240)
        self.tableView.setRowHeight(table_model.rowCount() - 1, 20)
        table_model.setHorizontalHeaderLabels(['시간', 'CLuster', 'Command', 'payload', 'return value', 'result'])

        # 실험 결과 가져와서 추가
        table_model.appendRow([QStandardItem("1"), QStandardItem('ON_OFF_CLUSTER'), QStandardItem('ON_OFF_ON_CMD'),
                               QStandardItem('None'), QStandardItem('True'), QStandardItem('ok')])
        self.show()

    def click_save(self):
        save_result()

    def click_print(self):
        if sys.platform == "win32":
            os.startfile('test.xlsx', "print")
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, 'test.xlsx'])


def save_result():
    write_wb = Workbook()
    write_ws = write_wb.active
    write_ws['A1'] = '시간'
    write_ws['B1'] = 'CLuster'
    write_ws['C1'] = 'Command'
    write_ws['D1'] = 'payload'
    write_ws['E1'] = 'return value'
    write_ws['F1'] = 'result'

    # 실험 결과 가져와서 추가
    write_ws.append([1, 'ON_OFF_CLUSTER', 'ON_OFF_ON_CMD', 'None', 'True', 'ok'])

    write_wb.save('test.xlsx')


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)
    # MainWindow의 인스턴스 생성
    myWindow = MainWindow()
    # 프로그램 화면을 보여주는 코드
    myWindow.show()
    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
