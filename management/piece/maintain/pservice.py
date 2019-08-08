# _*_ coding:utf-8 _*_
"""
Create: 2019-08-08
Author: zizle
"""
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import pyqtSignal

class ArticleEditTools(QWidget):
    tool_clicked = pyqtSignal(str)
    def __init__(self, *args, **kwargs):
        super(ArticleEditTools, self).__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        add_img = QPushButton('img')
        add_img.clicked.connect(self.add_img_clicked)
        layout.addWidget(add_img)
        layout.addStretch()
        self.setLayout(layout)

    def add_img_clicked(self):
        self.tool_clicked.emit('image')