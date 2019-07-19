# _*_ coding:utf-8 _*_
"""
packages for all apps
Create: 2019-07-09
Update: 2019-07-09
Author: zizle
"""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class BarrenWindow(QWidget):
    def __init__(self, name, *args, **kwargs):
        super(BarrenWindow, self).__init__(*args, **kwargs)
        self.name = name
        self.__init_ui()

    def __init_ui(self):
        layout = QHBoxLayout()
        label = QLabel("`{}`暂未开放\n敬请期待！".format(self.name))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("QLabel{color:red}")
        font = QFont()
        font.setPointSize(15)
        label.setFont(font)
        layout.addWidget(label)
        self.setLayout(layout)

