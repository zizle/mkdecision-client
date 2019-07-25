# _*_ coding:utf-8 _*_
"""
all tabs in base windows
Update: 2019-07-25
Author: zizle
"""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class NoDataWindow(QWidget):
    def __init__(self,name, *args):
        super(NoDataWindow, self).__init__(*args)
        layout = QHBoxLayout()
        label = QLabel(name + "暂未开放!\n敬请期待,感谢支持~.")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("QLabel{color:red}")
        font = QFont()
        font.setPointSize(15)
        label.setFont(font)
        layout.addWidget(label)
        self.setLayout(layout)