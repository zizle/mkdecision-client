# _*_ coding:utf-8 _*_
"""
customer widgets in home
Update: 2019-07-29
Author: zizle
"""
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

class CarouselLabel(QLabel):
    def __init__(self, *args):
        super(CarouselLabel, self).__init__(*args)
        self.setScaledContents(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print('点击左键')
            print(self.width(), self.height())



