# _*_ coding:utf-8 _*_
# __Author__： zizle
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget


class VarietyDetailMenuWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(VarietyDetailMenuWidget, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        tab_show = QTabWidget()
        tab_show.addTab(QWidget(), '行业数据')
        tab_show.addTab(QWidget(), '我的收藏')
        layout.addWidget(tab_show)
        self.setLayout(layout)
