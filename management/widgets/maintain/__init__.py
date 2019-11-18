# _*_ coding:utf-8 _*_
"""

Create: 2019-
Author: zizle
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QStyleOption, QStyle
from PyQt5.QtCore import QPropertyAnimation, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QPainter


# 功能模块控件
class ModuleBlock(QWidget):
    enter_clicked = pyqtSignal(QPushButton)

    def __init__(self, module_name, *args, **kwargs):
        super(ModuleBlock, self).__init__(*args, **kwargs)
        self.module_name = module_name
        layout = QVBoxLayout()
        self.enter_button = QPushButton('进入', parent=self)
        self.enter_button.clicked.connect(self.enter_button_clicked)
        self.setLayout(layout)
        # 本身样式设置
        self.setObjectName('moduleBlock')
        self.resize(200, 200)
        self.setStyleSheet("""
        #moduleBlock{
            background-color:rgb(200, 200, 200)
        }
        """)
        # 保存点击之间的原始位置
        self.original_x = 0
        self.original_y = 0
        # 保存原始大小
        self.original_width = 0
        self.original_height = 0

    # 记录原始位置
    def set_original_rect(self, x, y, w, h):
        self.original_x = x
        self.original_y = y
        self.original_width = w
        self.original_height = h

    # 重写，可以设置背景颜色
    def paintEvent(self, envent):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    # 设置显示控件
    def set_module_widget(self, widget):
        self.layout().addWidget(widget)
        self.layout().addWidget(self.enter_button)

    # 点击了进入按钮
    def enter_button_clicked(self):
        self.enter_clicked.emit(self.enter_button)


