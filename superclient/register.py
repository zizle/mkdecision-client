# _*_ coding:utf-8 _*_
# __Author__： zizle
import sys
import json
import hashlib
import requests
from wmi import WMI
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLabel, QLineEdit, QPushButton

# SERVER = 'http://127.0.0.1:8000/'
SERVER = "http://210.13.218.130:9004/"
# SERVER = "http://192.168.0.103:8000/"


# 获取本机机器码
class MachineInfo(object):
    """获取电脑硬件信息"""
    def __init__(self):
        self.c = WMI()

    def main_board(self):
        """主板uuid+serialNumber"""
        board = self.c.Win32_BaseBoard()[0] if len(self.c.Win32_BaseBoard()) else None
        if board:
            uuid = board.qualifiers['UUID'][1:-1]  # 主板UUID
            serial_number = board.SerialNumber             # 主板序列号
            return uuid + serial_number
        else:
            return None

    def disk(self):
        """硬盘序列号"""
        disk = self.c.Win32_DiskDrive()[0] if len(self.c.Win32_DiskDrive()) else None
        if disk:
            return disk.SerialNumber.strip()

    def network_adapter(self):
        """网卡信息"""
        print(len(self.c.Win32_NetworkAdapter()))
        for n in self.c.Win32_NetworkAdapter():
            print(n.MACAddress)

    def cpu_info(self):
        """CPU信息"""
        for cpu in self.c.Win32_Processor():
            print(cpu)


# 获取机器码
def get_machine_code():
    machine = MachineInfo()
    try:
        md = hashlib.md5()
        main_board = machine.main_board()
        disk = machine.disk()
        md.update(main_board.encode('utf-8'))
        md.update(disk.encode('utf-8'))
        machine_code = md.hexdigest()
    except Exception:
        machine_code = ''
    return machine_code


# 超级管理员注册
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
        layout.addWidget(QPushButton('确认注册', objectName='commitBtn', clicked=self.register_superuser), 8, 1)
        self.setLayout(layout)
        self.setFixedSize(250, 250)

    # 注册
    def register_superuser(self):
        phone = self.phone.text()
        password = self.password.text()
        email = self.email.text()
        re_password = self.re_password.text()
        el = self.findChild(QLabel, 'repsError')
        if password != re_password:
            el.setText('两次输入密码不一致')
            return
        try:
            r = requests.post(
                url=SERVER + 'user/superuser/?mc=' + get_machine_code(),
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
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            el.setText(str(e))
        else:
            el.setText(response['message'])


app = QApplication(sys.argv)
super_register = SuperUserRegister()
super_register.show()
sys.exit(app.exec_())
