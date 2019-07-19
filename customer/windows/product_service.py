# _*_ coding:utf-8 _*_
# company: RuiDa Futures
# author: zizle
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class ProductServiceWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(ProductServiceWindow, self).__init__(*args, **kwargs)
        self.__init_ui()

    def __init_ui(self):
        layout = QHBoxLayout()
        label = QLabel("`产品服务`暂未开放\n敬请期待！")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("QLabel{color:red}")
        font = QFont()
        font.setPointSize(15)
        label.setFont(font)
        layout.addWidget(label)
        self.setLayout(layout)