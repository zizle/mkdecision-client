# _*_ coding:utf-8 _*_
"""
homepage frame window will make in tab
Update: 2019-07-25
Author: zizle
"""
import sys
from PyQt5.QtWidgets import *

import config
from piece.base import MenuBar
from piece.home import ShowReport

class Report(QWidget):
    def __init__(self, *args, **kwargs):
        super(Report, self).__init__(*args, *kwargs)
        layout = QVBoxLayout(spacing=5)
        menu_bar = MenuBar()
        menu_bar.setContentsMargins(0,0,0,0)
        menu_bar.addMenuButtons(["全部", "日报", "周报", "月报", "年报", "专题", "投资报告", "其他"])
        menu_bar.addStretch()
        menu_bar.menu_btn_clicked.connect(self.menu_clicked)
        # report table
        self.show_table = ShowReport()
        layout.addWidget(menu_bar)
        layout.addWidget(self.show_table)
        self.setStyleSheet("""
        MenuBar {
            background-color:rgb(255,255,255);
        }
        """)
        self.setLayout(layout)
        # get report
        self.show_table.get_report(url=config.SERVER_ADDR + 'homepage/report/')  # query param type=None

    def menu_clicked(self, menu):
        print(menu.text())
        self.show_table.get_report(url=config.SERVER_ADDR + 'homepage/report/?category=')