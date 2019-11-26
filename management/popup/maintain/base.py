# _*_ coding:utf-8 _*_
"""
dialog in clients and users info tab
Update: 2019-07-25
Author: zizle
"""
import re
import json
import requests
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator

import config
from utils import get_desktop_path


# 新增系统主模块
class NewModulePopup(QDialog):

    def __init__(self, *args, **kwargs):
        super(NewModulePopup, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        layout.addWidget(QLabel('名称:', parent=self), 0, 0)
        self.name_edit = QLineEdit(parent=self)
        layout.addWidget(self.name_edit, 0, 1)
        self.name_error_label = QLabel(parent=self, objectName='nameError')
        layout.addWidget(self.name_error_label, 1, 0, 1, 2)
        self.commit_button = QPushButton('确定提交', parent=self, clicked=self.commit_new_module)
        layout.addWidget(self.commit_button, 2, 1)
        self.network_result = QLabel()
        layout.addWidget(self.network_result, 3, 0, 1, 2)
        self.setLayout(layout)
        self.setWindowTitle('增加模块')

    # 提交新增
    def commit_new_module(self):
        name = self.name_edit.text()
        name = re.sub(r'\s+', '', name)
        if not name:
            self.name_error_label.setText('请填入模块名称')
            return
        # 提交
        try:
            r = requests.post(
                url=config.SERVER_ADDR + 'basic/modules-maintain/?mc=' + config.app_dawn.value('machine'),
                headers={
                    'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION'),
                },
                data=json.dumps({
                  'name': name
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.setText(str(e))
        else:
            self.close()

















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


class UploadFile(QDialog):
    def __init__(self, url):
        super(UploadFile, self).__init__()
        self.url = url
        layout = QGridLayout()
        # widgets
        title_label = QLabel('标题')
        file_label = QLabel('文件')
        self.title_edit = QLineEdit()
        self.file_edit = QLineEdit()
        select_btn = QPushButton('选择')
        submit_btn = QPushButton('提交')
        # signal
        select_btn.clicked.connect(self.select_file)
        submit_btn.clicked.connect(self.submit_file)
        # style
        self.setMinimumWidth(300)
        select_btn.setMaximumWidth(30)
        self.title_edit.setPlaceholderText('默认文件名')
        self.file_edit.setEnabled(False)
        # add layout
        layout.addWidget(title_label, 0, 0)
        layout.addWidget(self.title_edit, 0, 1, 1, 2)
        layout.addWidget(file_label, 1, 0)
        layout.addWidget(self.file_edit, 1,1)
        layout.addWidget(select_btn, 1,2)
        layout.addWidget(submit_btn, 2, 1, 1,2)
        self.setLayout(layout)

    def select_file(self):
        # select file
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        file_name_list = file_path.rsplit('/', 1)
        if not self.title_edit.text().strip(' '):
            self.title_edit.setText((file_name_list[1].rsplit('.', 1))[0])
        self.file_edit.setText(file_path)

    def submit_file(self):
        # submit file to server
        title = self.title_edit.text().strip(' ')
        if not title:
            self.title_edit.setPlaceholderText('您还未填写标题.')
            return
        data = dict()
        file_path = self.file_edit.text().strip(' ')
        file_raw_name = file_path.rsplit("/", 1)
        file = open(file_path, "rb")
        file_content = file.read()
        file.close()
        data['title'] = title
        data["file"] = (file_raw_name[1], file_content)
        data['machine_code'] = config.app_dawn.value('machine')
        encode_data = encode_multipart_formdata(data)
        data = encode_data[0]
        headers = config.CLIENT_HEADERS
        headers['Content-Type'] = encode_data[1]
        try:
            response = requests.post(
                url=self.url,
                headers=headers,
                data=data,
                cookies=config.app_dawn.value('cookies')
            )
        except Exception as error:
            QMessageBox.information(self, '提示', "发生了个错误!\n{}".format(error), QMessageBox.Yes)
            return
        response_data = json.loads(response.content.decode('utf-8'))
        if response.status_code != 201:
            QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
            return
        else:
            QMessageBox.information(self, '成功', '添加成功, 赶紧刷新看看吧.', QMessageBox.Yes)
            self.close()  # close the dialog
