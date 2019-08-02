# _*_ coding:utf-8 _*_
"""
product service windows made in main tab
Create: 2019-08-01
Author: zizle
"""
import sys
from PyQt5.QtWidgets import *

from piece.pservice import MenuListWidget


class PService(QWidget):
    def __init__(self, *args, **kwargs):
        super(PService, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        menu_list = MenuListWidget(column=3)
        menu_list.menu_clicked.connect(self.left_menu_clicked)
        # right tab
        self.show_tab = QTabWidget()
        # add layout
        layout.addWidget(menu_list)
        layout.addWidget(self.show_tab)
        self.setLayout(layout)

    def left_menu_clicked(self, menu):
        print('windows.pservice.py {} 选择菜单：'.format(sys._getframe().f_lineno), menu.parent_name, menu.text())






