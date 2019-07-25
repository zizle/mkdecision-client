# _*_ coding:utf-8 _*_
"""
dialog in clients and users info tab
Update: 2019-07-25
Author: zizle
"""
import re
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator

import config

class CreateNewClient(QDialog):
    new_data_signal = pyqtSignal(dict)
    def __init__(self, *args):
        super(CreateNewClient, self).__init__(*args)
        self.setMinimumWidth(360)
        self.setWindowTitle('新建')
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignRight)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('为这个客户端起一个名字')
        self.machine = QLineEdit()
        self.machine.setPlaceholderText('输入机器码(小写字母与数字组合)')
        self.bulletin_days = QLineEdit()
        self.bulletin_days.setPlaceholderText("支持输入整数(默认为1)")
        self.bulletin_days.setValidator(QIntValidator())
        self.admin_check = QCheckBox()
        self.active_check = QCheckBox()
        self.active_check.setChecked(True)
        submit_btn = QPushButton("提交")
        submit_btn.clicked.connect(self.new_client_signal)
        layout.addRow('*客户端名称：', self.name_edit)
        layout.addRow('*机器码：', self.machine)
        layout.addRow('公告展示(天)：', self.bulletin_days)
        layout.addRow('管理端：', self.admin_check)
        layout.addRow('有效：', self.active_check)
        layout.addRow('', submit_btn)
        self.setLayout(layout)

    def new_client_signal(self):
        # 收集客户端信息
        bulletin_day = self.bulletin_days.text().strip(' ')
        data = dict()
        data['name'] = self.name_edit.text().strip(' ')
        data['machine_code'] = self.machine.text().strip(' ')
        data['bulletin_days'] = bulletin_day if bulletin_day else 1
        data['is_admin'] = self.admin_check.isChecked()
        data['is_active'] = self.active_check.isChecked()
        data['operation_code'] = config.app_dawn.value('machine')
        if not config.app_dawn.value('cookies'):
            QMessageBox.information(self, '提示', "请先登录再进行操作~", QMessageBox.Yes)
            return
        if not data['name']:
            QMessageBox.information(self, '提示', "请为这个客户端取个名字~", QMessageBox.Yes)
            return
        if not re.match(r'^[0-9a-z]+$', data['machine_code']):
            QMessageBox.information(self, '提示', "机器码格式有误~", QMessageBox.Yes)
            return
        # emit signal
        self.new_data_signal.emit(data)