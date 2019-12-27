# _*_ coding:utf-8 _*_
# __Author__： zizle
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel


# 产品服务主页
class InfoServicePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(InfoServicePage, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        layout.addWidget(QLabel('产品服务正在开发中...'))
        self.setLayout(layout)