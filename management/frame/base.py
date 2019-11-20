# _*_ coding:utf-8 _*_
"""
Update: 2019-11-20
Author: zizle
"""
import re
import json
import requests
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QCursor

import config
from utils.machine import get_machine_code


# 不存在的模块
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
        self.machine_label = QLabel(parent=self, objectName='showLabel')
        self.name_edit = QLineEdit(parent=self)
        self.name_error = QLabel(parent=self, objectName='nameError')
        self.submit_btn = QPushButton('提交\n注册此客户端',parent=self, objectName='commitBtn', clicked=self.register_client)
        self.register_error = QLabel(parent=self, objectName='registerError')
        # 样式
        self.name_error.setAlignment(Qt.AlignCenter)
        self.register_error.setAlignment(Qt.AlignCenter)
        self.machine_label.setAlignment(Qt.AlignCenter)
        self.submit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.name_edit.setPlaceholderText('请填写本客户端名称(可写个人或单位名称)')
        # 错误的label限制大小
        self.name_error.setFixedHeight(25)
        self.register_error.setFixedHeight(25)
        # signal
        layout.addWidget(self.machine_label)
        layout.addWidget(self.name_edit)
        layout.addWidget(self.name_error)
        layout.addWidget(self.submit_btn)
        layout.addWidget(self.register_error)
        self.setLayout(layout)
        self.setStyleSheet("""
        #showLabel{
            max-height:100px;
            font-size:20px;
            font-weight:bold;
        }
        #nameError,#registerError{
            color:rgb(250, 10, 10)
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

    # 获取机器码
    def get_machine_code(self):
        machine_code = get_machine_code()
        self.machine_label.setText(machine_code)
        if not machine_code:
            self.machine_label.setText('获取机器码失败')
            self.submit_btn.setEnabled(False)

    def register_client(self):
        # 注册客户端
        name = re.sub(r'\s+', '', self.name_edit.text())
        if not name:
            self.name_error.setText('请填写名称')
            return
        try:
            r = requests.post(
                url=config.SERVER_ADDR + 'basic/client/',
                headers=config.CLIENT_HEADERS,
                data=json.dumps({
                    'name': name,
                    'machine_code': self.machine_label.text(),
                    'is_manager': config.ADMINISTRATOR
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            print(e)
            self.register_error.setText(str(e))
            return
        else:
            config.app_dawn.setValue("machine", self.machine_label.text())  # 在配置里保存
            self.register_error.setText('注册成功,请重启使用.')
