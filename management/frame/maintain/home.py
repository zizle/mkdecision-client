# _*_ coding:utf-8 _*_
"""
all tabs of data-maintenance module, in the home page
Update: 2019-07-25
Author: zizle
"""
import sys
import json
import requests
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import *

import config
from popup.maintain import CreateNewBulletin, CreateNewCarousel


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

