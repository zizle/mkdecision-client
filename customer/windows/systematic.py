# _*_ coding:utf-8 _*_
# company: RuiDa Futures
# author: zizle
import hashlib
import requests
import json
import config
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel,\
    QPushButton, QLineEdit,QMessageBox, QVBoxLayout, QTreeView, QTreeWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from utilss.machine import machine
from config import SERVER_ADDR, CLIENT_HEADERS
from widgets.dialog import SelectParentModuleDialog


class SystemSetupWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(SystemSetupWindow, self).__init__(*args, **kwargs)
        self.__init_ui()

    def __init_ui(self):
        layout = QHBoxLayout()
        v_layout = QVBoxLayout()
        label = QLabel("本系统暂无需进行任何设置！")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("QLabel{color:red}")
        font = QFont()
        font.setPointSize(15)
        label.setFont(font)
        machine_code_button = QPushButton("查看机器码：")
        machine_code_button.clicked.connect(self.show_machine_code)
        self.machine_code_edit = QLineEdit()
        layout.addWidget(machine_code_button)
        layout.addWidget(self.machine_code_edit)
        layout.addStretch()
        v_layout.addLayout(layout)
        v_layout.addStretch()
        self.setLayout(v_layout)

    def show_machine_code(self):
        """展示机器码"""
        md = hashlib.md5()
        main_board = machine.main_board()
        disk = machine.disk()
        md.update(main_board.encode("utf-8"))
        md.update(disk.encode("utf-8"))
        self.machine_code_edit.setText(md.hexdigest())


