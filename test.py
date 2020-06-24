import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtGui import QStandardItem

#UI파일 연결 - UI파일은 Python 코드 파일과 같은 디렉토리에 위치
form_class = uic.loadUiType("mainwindow.ui")[0]

command_list = []
command_model = QStandardItemModel()

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        #single command tab
        self.cbo_command.currentIndexChanged.connect(self.select_command)
        self.onoff_grp.hide()
        self.color_grp.hide()
        self.cbo_input_color.currentIndexChanged.connect(self.select_input_style)
        self.level_grp.hide()
        self.cbo_input_level.currentIndexChanged.connect(self.select_input_style)
        self.btn_insert.clicked.connect(self.click_insert)

        #main window
        self.btn_more.clicked.connect(self.click_more)
        # self.cbo_module.currentIndexChanged.connect(self.)

    def select_input_style(self):
        index_color = self.cbo_input_color.currentIndex()
        if index_color == 0:
            self.lineEdit_color.show()
        else:
            self.lineEdit_color.hide()
        index_level = self.cbo_input_level.currentIndex()
        if index_level == 0:
            self.lineEdit_level.show()
        else:
            self.lineEdit_level.hide()

    def click_insert(self):
        print("btn_insert Clicked")
        index = self.cbo_command.currentIndex()
        if index == 0: # connect
            item = "connect"
            command_model.appendRow(QStandardItem(item))
            self.listView_command.setModel(command_model)
            print(item)
        elif index == 1: # on/off
            if self.rdo_on.isChecked():
                print("on Chekced")
                item = "on, " + str(self.spinBox_onoff.value())
                command_model.appendRow(QStandardItem(item))
                self.listView_command.setModel(command_model)
                print(item)
            elif self.rdo_off.isChecked():
                item = "off, " + str(self.spinBox_onoff.value())
                command_model.appendRow(QStandardItem(item))
                self.listView_command.setModel(command_model)
                print(item)
            elif self.rdo_toggle.isChecked():
                item = "toggle, " + str(self.spinBox_onoff.value())
                command_model.appendRow(QStandardItem(item))
                self.listView_command.setModel(command_model)
                print(item)
            else:
                print("insert nothing")
        elif index == 2: # color
            print(self.cbo_command.currentText())
            item = "color, " + str(self.spinBox_color.value())
            command_model.appendRow(QStandardItem(item))
            self.listView_command.setModel(command_model)
            print(item)
        elif index == 3: # level
            print(self.cbo_command.currentText())
            print(self.spinBox_level.value())
        else: # disconnect
            item = "disconnect"
            command_model.appendRow(QStandardItem(item))
            self.listView_command.setModel(command_model)
            print(item)

    def click_more(self):
        print("btn_1 Clicked")

    def select_command(self):
        index = self.cbo_command.currentIndex()
        if index == 0 :
            self.onoff_grp.hide()
            self.color_grp.hide()
            self.level_grp.hide()
        elif index == 1:
            self.onoff_grp.show()
            self.color_grp.hide()
            self.level_grp.hide()
        elif index == 2:
            self.onoff_grp.hide()
            self.color_grp.show()
            self.level_grp.hide()
        elif index == 3:
            self.onoff_grp.hide()
            self.color_grp.hide()
            self.level_grp.show()
        else:
            self.onoff_grp.hide()
            self.color_grp.hide()
            self.level_grp.hide()


if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
