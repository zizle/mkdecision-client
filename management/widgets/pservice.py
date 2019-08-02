# _*_ coding:utf-8 _*_
"""
widgets for product service module
Create: 2019-08-01
Author: zizle
"""

from PyQt5.QtWidgets import QLabel, QWidget, QPushButton
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QCursor

class LeaderLabel(QLabel):
    clicked = pyqtSignal(QLabel)
    def __init__(self, *args):
        super(LeaderLabel, self).__init__(*args)
        self.setStyleSheet('padding:8px 0; border:none')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self)


class MenuWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(MenuWidget, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)

    # def enterEvent(self, QEvent):
    #     # self.setStyleSheet("background-color: rgb(200,200,200);border-bottom: 1px solid rgb(0,0,0)")
    #     super(MenuWidget, self).enterEvent(QEvent)
    #
    # def leaveEvent(self, QEvent):
    #     # self.setStyleSheet('background-color: rgb(255,255,255);border-bottom: 1px solid rgb(0,0,0)')
    #     super(MenuWidget, self).leaveEvent(QEvent)


class MenuButton(QPushButton):
    mouse_clicked = pyqtSignal(QPushButton)

    def __init__(self, *args, **kwargs):
        super(MenuButton, self).__init__(*args)
        self.clicked.connect(self.btn_clicked)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def btn_clicked(self):
        self.mouse_clicked.emit(self)