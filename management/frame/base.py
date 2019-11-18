# _*_ coding:utf-8 _*_
"""
Update: 2019-07-25
Author: zizle
"""
import re
import json
import hashlib
import requests
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QLineEdit, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QCursor

import config
from utils.machine import machine
from popup.base import TipShow


class NoDataWindow(QWidget):
    def __init__(self, name, *args):
        super(NoDataWindow, self).__init__(*args)
        layout = QHBoxLayout()
        label = QLabel("「" + name + "」暂未开放!\n敬请期待,感谢支持~.")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("QLabel{color:red}")
        font = QFont()
        font.setPointSize(15)
        label.setFont(font)
        layout.addWidget(label)
        self.setLayout(layout)


# 初始化注册客户端
class RegisterClient(QWidget):
    def __init__(self, *args, **kwargs):
        super(RegisterClient, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=10)
        self.machine_label = QLabel(objectName='showLabel')
        self.name_edit = QLineEdit()
        self.submit_btn = QPushButton('提交\n注册此客户端', objectName='commitBtn')
        # style
        self.machine_label.setAlignment(Qt.AlignCenter)
        self.submit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.name_edit.setPlaceholderText('请填写本客户端名称(可写个人或单位名称)')
        # signal
        self.submit_btn.clicked.connect(self.register_client)
        layout.addWidget(self.machine_label)
        layout.addWidget(self.name_edit)
        layout.addWidget(self.submit_btn)
        self.setLayout(layout)
        self.setStyleSheet("""
        #showLabel{
            max-height:100px;
            font-size:20px;
            font-weight:bold;
        }
        QLineEdit{
            mim-height:35px;
            max-height:35px;
        }
        #commitBtn{
            border:none;
            border-radius:15px;
            background-color:rgb(110,140,220);
            min-height:130px;
            font-size:20px;
            color:rgb(255,255,255)
        }
        """)
        # 获取机器码
        self.get_machine_code()

    def get_machine_code(self):
        try:
            md = hashlib.md5()
            main_board = machine.main_board()
            disk = machine.disk()
            md.update(main_board.encode('utf-8'))
            md.update(disk.encode('utf-8'))
            machine_code = md.hexdigest()
            # 在配置里保存
            config.app_dawn.setValue("machine", machine_code)
            self.machine_label.setText(machine_code)
        except Exception as error:
            self.machine_label.setText('获取机器码失败:\n{}'.format(error))
            self.submit_btn.setEnabled(False)

    def register_client(self):
        # 注册客户端
        name = re.sub(r'\s+', '', self.name_edit.text())
        try:
            if not name:
                raise ValueError('请填写名称.')
            response = requests.post(
                url=config.SERVER_ADDR + 'basic/client/',
                headers=config.CLIENT_HEADERS,
                data=json.dumps({
                    'name': name,
                    'machine_code': config.app_dawn.value('machine'),
                    'is_manager': config.ADMINISTRATOR
                })
            )
            response_data = json.loads(response.content.decode('utf-8'))
        except Exception as error:
            popup = TipShow(parent=self)
            popup.information('错误', '客户端注册失败.\n{}'.format(error))
            popup.confirm_btn.clicked.connect(popup.close)
            popup.deleteLater()
            popup.exec()
            del popup
            return
        if response.status_code != 201:
            popup = TipShow(parent=self)
            popup.information('失败', response_data['message'])
            popup.confirm_btn.clicked.connect(popup.close)
            popup.deleteLater()
            popup.exec()
            del popup
            return
        else:
            popup = TipShow(parent=self)
            popup.information('成功', '恭喜!本客户端注册成功.\n请重启使用!')
            popup.confirm_btn.clicked.connect(popup.close)
            popup.deleteLater()
            popup.exec()
            del popup



