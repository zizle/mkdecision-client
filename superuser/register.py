# _*_ coding:utf-8 _*_
# date: 2019-11-16

import sys
import json
import requests
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLabel, QLineEdit, QPushButton

SERVER = 'http://127.0.0.1:8000/'


# 注册超级管理员
class SuperUserRegister(QWidget):
    def __init__(self, *args, **kwargs):
        super(SuperUserRegister, self).__init__(*args, **kwargs)
        self.setWindowTitle('注册超级管理员')
        layout = QGridLayout()
        self.phone = QLineEdit()
        layout.addWidget(QLabel('<div>手&nbsp;&nbsp;机：</div>'), 0,0)
        layout.addWidget(self.phone, 0, 1)
        layout.addWidget(QLabel(objectName='phoneError'), 1, 0, 1, 2)
        layout.addWidget(QLabel('<div>邮&nbsp;&nbsp;箱：</div>'), 2, 0)
        self.email = QLineEdit()
        layout.addWidget(self.email, 2, 1)
        layout.addWidget(QLabel(objectName='emailError'), 3, 0, 1, 2)
        layout.addWidget(QLabel('<div>密&nbsp;&nbsp;码：</div>'), 4, 0)
        self.password = QLineEdit()
        layout.addWidget(self.password, 4, 1)
        layout.addWidget(QLabel(objectName='psError'), 5, 0, 1, 2)
        layout.addWidget(QLabel('确认密码：'), 6, 0)
        self.re_password = QLineEdit()
        layout.addWidget(self.re_password, 6, 1)
        layout.addWidget(QLabel(objectName='repsError'), 7, 0, 1, 2)
        layout.addWidget(QLabel(parent=self, objectName='registerError'))
        layout.addWidget(QPushButton('确认注册', objectName='commitBtn', clicked=self.register_superuser), 8, 1)
        self.setLayout(layout)
        self.setFixedSize(250, 250)

    # 注册
    def register_superuser(self):
        phone = self.phone.text()
        password = self.password.text()
        email = self.email.text()
        re_password = self.re_password.text()
        el = self.findChild(QLabel, 'registerError')
        try:
            r = requests.post(
                url=SERVER + 'user/createsuper/',
                data=json.dumps({
                    'username': '超级管理员',
                    'email': email,
                    'phone': phone,
                    'password': password,
                    'is_superuser': True,
                    'note': '超级管理员'
                })
            )
            response = json.loads(r.content.decode('utf-8'))
        except Exception as e:
            el.setText(str(e))
            return
        el.setText(response['message'])


app = QApplication(sys.argv)
super_register = SuperUserRegister()
super_register.show()
sys.exit(app.exec_())
