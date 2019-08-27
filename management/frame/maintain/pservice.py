# _*_ coding:utf-8 _*_
"""

Create: 2019-08-02
Author: zizle
"""
import json
import requests
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import *

import config

from popup.maintain.base import UploadFile
from popup.maintain.pservice import CreateMessage, CreateNewAdviser

"""咨询服务"""
class MessageCommMaintain(QWidget):
    def __init__(self):
        super(MessageCommMaintain, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        # widgets
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        self.table = QTableWidget()
        # signal
        create_btn.clicked.connect(self.create_new_msg_comm)
        # style
        self.table.verticalHeader().setVisible(False)
        # add to layout
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def create_new_msg_comm(self):
        def create_message(signal):
            try:
                response = requests.post(
                    url=config.SERVER_ADDR + 'pservice/consult/msg/',
                    data=json.dumps(signal[1]),
                    cookies=config.app_dawn.value('cookies')
                )
                response_data = json.loads(response.content.decode('utf-8'))
            except Exception as error:
                QMessageBox.information(popup, '错误', '创建失败.\n{}'.format(error), QMessageBox.Yes)
                return
            if response.status_code != 201:
                QMessageBox.information(popup, '错误', response_data['message'], QMessageBox.Yes)
                return
            QMessageBox.information(popup, '成功', '创建成功.赶紧刷新看看吧。', QMessageBox.Yes)
            popup.close()
        popup = CreateMessage()
        popup.new_data_signal.connect(create_message)
        if not popup.exec():
            del popup


class MarketAnalysisMaintain(QWidget):
    def __init__(self):
        super(MarketAnalysisMaintain, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        # widgets
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        self.table = QTableWidget()
        # signal
        create_btn.clicked.connect(self.create_new_mks)
        # style
        self.table.verticalHeader().setVisible(False)
        # add to layout
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def create_new_mks(self):
        popup = UploadFile(url=config.SERVER_ADDR + 'pservice/consult/mks/')
        if not popup.exec():
            del popup


class TopicalStudyMaintain(QWidget):
    def __init__(self):
        super(TopicalStudyMaintain, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        # widgets
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        self.table = QTableWidget()
        # signal
        create_btn.clicked.connect(self.create_new_tps)
        # style
        self.table.verticalHeader().setVisible(False)
        # add to layout
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def create_new_tps(self):
        popup = UploadFile(url=config.SERVER_ADDR + 'pservice/consult/tps/')
        if not popup.exec():
            del popup


class ResearchReportMaintain(QWidget):
    def __init__(self):
        super(ResearchReportMaintain, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        # widgets
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        self.table = QTableWidget()
        # signal
        create_btn.clicked.connect(self.create_new_rsr)
        # style
        self.table.verticalHeader().setVisible(False)
        # add to layout
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def create_new_rsr(self):
        popup = UploadFile(url=config.SERVER_ADDR + 'pservice/consult/rsr/')
        if not popup.exec():
            del popup


"""顾问服务"""
class AdviserMaintain(QWidget):
    def __init__(self):
        super(AdviserMaintain, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        # widgets
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        self.table = QTableWidget()
        # signal
        create_btn.clicked.connect(self.create_new_adviser)
        # style
        self.table.verticalHeader().setVisible(False)
        # add layout
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)
        # initial data

    def create_new_adviser(self):
        def upload_adviser(signal):
            data=dict()
            data['machine_code'] = config.app_dawn.value('machine')
            data['category'] = signal['category']
            data['title'] = signal['title']
            file_raw_name = signal["file_path"].rsplit("/", 1)
            file = open(signal["file_path"], "rb")
            file_content = file.read()
            file.close()
            data["file"] = (file_raw_name[1], file_content)
            encode_data = encode_multipart_formdata(data)
            data = encode_data[0]
            headers = config.CLIENT_HEADERS
            headers['Content-Type'] = encode_data[1]
            try:
                response = requests.post(
                    url=config.SERVER_ADDR + "pservice/adviser/",
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
                popup.close()  # close the dialog
        popup = CreateNewAdviser()
        popup.new_data_signal.connect(upload_adviser)
        if not popup.exec():
            del popup