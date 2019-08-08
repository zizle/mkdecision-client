# _*_ coding:utf-8 _*_
"""
request threading
Create: 2019-07-31
Author: zizle
"""

import json
import requests
from PyQt5.QtCore import QThread, pyqtSignal


class RequestThread(QThread):
    response_signal = pyqtSignal(dict)

    def __init__(self, url, method, headers=None, cookies=None, data=None):
        super(RequestThread, self).__init__()
        self.url = url
        self.method = method
        self.headers = headers
        self.data = data
        self.cookies = cookies

    def run(self):
        try:
            if self.method == "get":
                response = requests.get(
                    url=self.url,
                    headers=self.headers,
                    data=self.data,
                    cookies=self.cookies,
                )
                response_content = json.loads(response.content.decode('utf-8'))
                response_content["error"] = False
                self.response_signal.emit(response_content)
            else:
                self.response_signal.emit({"error": True, "message": "不支持的方法!", "data":[]})
        except Exception as error:
            self.response_signal.emit({"error": True, "message": "请求数据发生错误!\n{}".format(error), "data":[]})