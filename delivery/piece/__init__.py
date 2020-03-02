# _*_ coding:utf-8 _*_
"""

Create: 2019-
Author: zizle
"""

import random
import requests
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap, QFont, QImage
from PyQt5.QtCore import Qt

from delivery import config


class StartScreen(QSplashScreen):
    def __init__(self):
        super(StartScreen, self).__init__()
        self.resize(300,260)
        self.__init_ui()

    def __init_ui(self):
        index = random.randint(1, 10)
        img = 'media/images/start%d.png' % index
        # 请求图片数据
        try:
            response = requests.get(url=config.SERVER + img)
            response_img = response.content
            if response.status_code != 200:
                raise ValueError('get screeen image error.')
        except Exception as e:
            self.setPixmap(QPixmap('images/start.png'))
        else:
            screen_image = QImage.fromData(response_img)
            self.setPixmap(QPixmap.fromImage(screen_image))
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.setFont(font)
        self.showMessage("欢迎使用交割通 V"+config.VERSION+"\n程序正在启动中...", Qt.AlignCenter, Qt.red)