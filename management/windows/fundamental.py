# _*_ coding:utf-8 _*_
# author: zizle
# Date: 20190509
"""基本分析"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class FundamentalWindow(QWidget):
    def __init__(self):
        super(FundamentalWindow, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        layout = QHBoxLayout()
        label = QLabel("`基本分析`暂未开放\n敬请期待！")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("QLabel{color:red}")
        font = QFont()
        font.setPointSize(15)
        label.setFont(font)
        layout.addWidget(label)
        self.setLayout(layout)


