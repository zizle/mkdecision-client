# _*_ coding:utf-8 _*_
"""
all customer-widget in home page
Update: 2019-07-25
Author: zizle
"""
import json
import requests
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtCore import QTimer

import config
from threads import RequestThread

class ShowBulletin(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(ShowBulletin, self).__init__(*args)
        self.get_bulletin()

    def get_bulletin(self):
        print('请求数据...')
        headers = {"User-Agent": "DAssistant-Client/" + config.VERSION}
        self.ble_thread = RequestThread(
            url=config.SERVER_ADDR + "homepage/bulletin/",
            method='get',
            headers=headers,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.ble_thread.response_signal.connect(self.ble_thread_back)
        self.ble_thread.finished.connect(self.ble_thread.deleteLater)
        self.ble_thread.start()

    def ble_thread_back(self, content):
        print('请求完毕', content)


