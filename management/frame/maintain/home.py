# _*_ coding:utf-8 _*_
"""
all tabs of data-maintenance module, in the home page
Create: 2019-07-25
Author: zizle
"""
import sys
import json
import requests
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import *

import config
from popup.maintain import CreateNewBulletin, CreateNewCarousel, CreateNewReport, CreateNewNotice, CreateNewCommodity, CreateNewFinance


class BulletinInfo(QWidget):
    def __init__(self):
        super(BulletinInfo, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        create_btn = QPushButton("设置")
        refresh_btn = QPushButton('刷新')
        create_btn.clicked.connect(self.create_new_bulletin)
        self.show_bulletin_table = QTableWidget()
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.show_bulletin_table)
        self.setLayout(layout)

    def create_new_bulletin(self):
        # dialog widget for edit bulletin information
        def update_bulletin(signal):
            # create new bulletin or update a bulletin in server
            print('frame.maintain.home.py {} : '.format(str(sys._getframe().f_lineno)), "公告信号:", signal)
            headers = config.CLIENT_HEADERS
            cookies = config.app_dawn.value('cookies')
            machine_code = config.app_dawn.value('machine')
            if signal["set_option"] == "new_bulletin":
                data = dict()
                data["name"] = signal["name"]
                data["show_type"] = signal["show_type"]
                data['machine_code'] = machine_code
                if signal["show_type"] == "show_file":
                    file_raw_name = signal["file"].rsplit("/", 1)
                    file = open(signal["file"], "rb")
                    file_content = file.read()
                    file.close()
                    data["file"] = (file_raw_name[1], file_content)
                elif signal["show_type"] == "show_text":
                    data["content"] = signal["content"]
                encode_data = encode_multipart_formdata(data)
                data = encode_data[0]
                headers['Content-Type'] = encode_data[1]
                try:
                    response = requests.post(
                        url=config.SERVER_ADDR + "homepage/bulletin/",
                        headers=headers,
                        data=data,
                        cookies=cookies
                    )
                except Exception as error:
                    QMessageBox.information(self, '提示', "发生了个错误!\n{}".format(error), QMessageBox.Yes)
                    return
                response_data = json.loads(response.content.decode('utf-8'))
                if response.status_code != 201:
                    QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
                    return
                else:
                    QMessageBox.information(self, '成功', '创建成功, 赶紧刷新看看吧.', QMessageBox.Yes)
                    popup.close()  # close the dialog
        popup = CreateNewBulletin()
        popup.new_data_signal.connect(update_bulletin)
        if not popup.exec():
            del popup


class CarouselInfo(QWidget):
    def __init__(self):
        super(CarouselInfo, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        create_btn.clicked.connect(self.create_new_carousel)
        self.show_carousel_table = QTableWidget()
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.show_carousel_table)
        self.setLayout(layout)

    def create_new_carousel(self):
        # dialog for add new carousel
        def upload_carousel(signal):
            print('frame.maintain.py {} 轮播信号:'.format(str(sys._getframe().f_lineno)), signal)
            data = dict()
            data["name"] = signal["name"]
            data['machine_code'] = config.app_dawn.value('machine')
            # handler image data
            image_name_list = signal['image'].rsplit('/', 1)
            image = open(signal['image'], 'rb')
            image_content = image.read()
            image.close()
            data['image'] = (image_name_list[1], image_content)
            if signal['file']: # file show
                file_raw_name = signal["file"].rsplit("/", 1)
                file = open(signal["file"], "rb")
                file_content = file.read()
                file.close()
                data["file"] = (file_raw_name[1], file_content)
            data["content"] = signal["content"]
            data["redirect_url"] = signal['redirect']
            encode_data = encode_multipart_formdata(data)
            data = encode_data[0]
            headers = config.CLIENT_HEADERS
            headers['Content-Type'] = encode_data[1]
            try:
                response = requests.post(
                    url=config.SERVER_ADDR + "homepage/carousel/",
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
                QMessageBox.information(self, '成功', '创建成功, 赶紧刷新看看吧.', QMessageBox.Yes)
                popup.close()  # close the dialog
        popup = CreateNewCarousel()
        popup.new_data_signal.connect(upload_carousel)
        if not popup.exec():
            del popup


class CommodityInfo(QWidget):
    def __init__(self):
        super(CommodityInfo, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        add_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        add_btn.clicked.connect(self.add_new_commodity)
        self.show_commodity_table = QTableWidget()
        action_layout.addWidget(add_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.show_commodity_table)
        self.setLayout(layout)

    def add_new_commodity(self):
        def upload_commodity(signal):
            print('frame.maintain.home.py {} 新现货：'.format(sys._getframe().f_lineno), signal)
            data = dict()
            data['machine_code'] = config.app_dawn.value('machine')
            data['commodity_list'] = signal
            try:
                response = requests.post(
                    url=config.SERVER_ADDR + "homepage/commodity/",
                    headers=config.CLIENT_HEADERS,
                    data=json.dumps(data),
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
        popup = CreateNewCommodity()
        popup.new_data_signal.connect(upload_commodity)
        if not popup.exec():
            del popup


class FinanceInfo(QWidget):
    def __init__(self):
        super(FinanceInfo, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        add_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        add_btn.clicked.connect(self.add_new_finance)
        self.show_finance_table = QTableWidget()
        action_layout.addWidget(add_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.show_finance_table)
        self.setLayout(layout)

    def add_new_finance(self):
        def upload_finance(signal):
            print('frame.maintain.home.py {} 新财经：'.format(sys._getframe().f_lineno), signal)
            data = dict()
            data['machine_code'] = config.app_dawn.value('machine')
            data['finance_list'] = signal
            try:
                response = requests.post(
                    url=config.SERVER_ADDR + "homepage/finance/",
                    headers=config.CLIENT_HEADERS,
                    data=json.dumps(data),
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
        popup = CreateNewFinance()
        popup.new_data_signal.connect(upload_finance)
        if not popup.exec():
            del popup


class NoticeInfo(QWidget):
    def __init__(self):
        super(NoticeInfo, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        create_btn.clicked.connect(self.create_new_notice)
        self.show_notice_table = QTableWidget()
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.show_notice_table)
        self.setLayout(layout)

    def create_new_notice(self):
        def upload_notice(signal):
            print('frame.maintain.home.py {} 新通知:'.format(str(sys._getframe().f_lineno)), signal)
            data = dict()
            data['machine_code'] = config.app_dawn.value('machine')
            data['type_en'] = signal['type_en']
            data['type_zh'] = signal['type_zh']
            data['name'] = signal['name']
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
                    url=config.SERVER_ADDR + "homepage/notice/",
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
        popup = CreateNewNotice()
        popup.new_data_signal.connect(upload_notice)
        if not popup.exec():
            del popup


class ReportInfo(QWidget):
    def __init__(self):
        super(ReportInfo, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        create_btn.clicked.connect(self.create_new_report)
        self.show_report_table = QTableWidget()
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.show_report_table)
        self.setLayout(layout)

    def create_new_report(self):
        def upload_report(signal):
            print('frame.maintain.home.py {} 新报告:'.format(str(sys._getframe().f_lineno)), signal)
            data=dict()
            data['machine_code'] = config.app_dawn.value('machine')
            data['type_en'] = signal['type_en']
            data['type_zh'] = signal['type_zh']
            data['name'] = signal['name']
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
                    url=config.SERVER_ADDR + "homepage/report/",
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
        popup = CreateNewReport()
        popup.new_data_signal.connect(upload_report)
        if not popup.exec():
            del popup

