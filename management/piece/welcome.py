# _*_ coding:utf-8 _*_
# __Author__： zizle

import json
import requests
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

import config
from utils.machine import get_machine_code


# 欢迎页
class WelcomePage(QSplashScreen):
    def __init__(self, *args, **kwargs):
        super(WelcomePage, self).__init__(*args, *kwargs)
        self.setPixmap(QPixmap('media/start.png'))
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.setFont(font)
        self.showMessage("欢迎使用分析决策系统\n程序正在启动中...", Qt.AlignCenter, Qt.red)

    # 启动使客户端存在
    @staticmethod
    def make_client_existed():
        machine_code = get_machine_code()  # 获取机器码
        # 查询机器是否存在
        try:
            r = requests.post(
                url=config.SERVER_ADDR + 'basic/client/',
                data=json.dumps({
                    'machine_code': machine_code,
                    'is_manager': config.ADMINISTRATOR
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            return
        else:
            # 写入配置
            print('utils.client.make_client_existed写入配置')
            config.app_dawn.setValue('machine', response['data']['machine_code'])

