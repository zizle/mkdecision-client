# _*_ coding:utf-8 _*_
"""
all customer-widgets in each module
Update: 2019-07-25
Author: zizle
"""

from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

class StartScreen(QSplashScreen):
    def __init__(self):
        super(StartScreen, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        self.setPixmap(QPixmap('media/start.png'))
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.setFont(font)
        self.showMessage("欢迎使用分析决策系统\n程序正在启动中...", Qt.AlignCenter, Qt.red)