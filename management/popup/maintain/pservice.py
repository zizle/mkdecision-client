# _*_ coding:utf-8 _*_
"""

Create: 2019-08-02
Author: zizle
"""
import json
import requests
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt

import config

class CreateNewMenu(QDialog):
    new_data_signal = pyqtSignal(dict)
    def __init__(self, *args):
        super(CreateNewMenu, self).__init__(*args)
        layout = QGridLayout()
        # labels
        name_label = QLabel('名称：')
        parent_label = QLabel('父级：')
        # edit
        self.name_edit = QLineEdit()
        # combo
        self.parent_combo = QComboBox()
        self.parent_combo.addItem('')
        # submit
        submit_btn = QPushButton('提交')
        # signal
        submit_btn.clicked.connect(self.submit_menu)
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(self.name_edit, 0, 1)
        layout.addWidget(parent_label, 1, 0)
        layout.addWidget(self.parent_combo, 1, 1)
        layout.addWidget(submit_btn, 2, 1)
        self.setLayout(layout)
        # get parent module name
        self.get_parent_module()
        # show message
        self.message = QLabel('正在创建...', self)
        self.message.setStyleSheet('background-color:rgb(200,200,200)')
        self.message.setAlignment(Qt.AlignCenter)
        self.message.move(50, 5)
        self.message.hide()

    def get_parent_module(self):
        try:
            response = requests.get(
                url=config.SERVER_ADDR + 'pservice/module/',  # query param parent=None
                headers=config.CLIENT_HEADERS,
                data=json.dumps({'machine_code':config.app_dawn.value('machine')}),
                cookies=config.app_dawn.value('cookies')
            )
        except Exception as error:
            QMessageBox(self, "错误", str(error))
            return
        response_data = json.loads(response.content.decode('utf-8'))
        for item in response_data['data']:
            self.parent_combo.addItem(item['name'])


    def submit_menu(self):
        data = dict()
        name = self.name_edit.text().strip(' ')
        if not name:
            QMessageBox.information(self, "错误", "请填写名称.", QMessageBox.Yes)
            return
        data['name'] = name
        data['parent'] = self.parent_combo.currentText()
        self.message.show()
        self.new_data_signal.emit(data)


