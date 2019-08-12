# _*_ coding:utf-8 _*_
"""
product service windows made in main tab
Create: 2019-08-01
Author: zizle
"""
import sys
from PyQt5.QtWidgets import *

from piece.pservice import MenuListWidget
from frame.base import NoDataWindow
from frame.pservice import MsgCommunication, MarketAnalysis, PersonTrain, TopicalStudy, ResearchReport


class PService(QWidget):
    def __init__(self, *args, **kwargs):
        super(PService, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        menu_list = MenuListWidget(column=3)
        menu_list.menu_clicked.connect(self.left_menu_clicked)
        # right tab
        self.show_tab = QTabWidget()
        self.show_tab.setTabBarAutoHide(True)
        # add layout
        layout.addWidget(menu_list)
        layout.addWidget(self.show_tab)
        self.setLayout(layout)

    def left_menu_clicked(self, menu):
        print('windows.pservice.py {} 选择菜单：'.format(sys._getframe().f_lineno), menu.parent_name, menu.text())
        main_text = menu.parent_name
        text = menu.text()
        if main_text == '咨询服务':
            if text == '短信通':
                tab = MsgCommunication()
            elif text == '市场分析':
                tab = MarketAnalysis()
            elif text == '专题研究':
                tab = TopicalStudy()
            elif text == '调研报告':
                tab = ResearchReport()
            else:
                tab = NoDataWindow(name=main_text + "·" +text)
        elif main_text == '顾问服务':
            if text == '人才培养':
                tab = PersonTrain()
            else:
                tab = NoDataWindow(name=main_text + "·" + text)
        else:
            tab = NoDataWindow(name=main_text + "·" +text)

        self.show_tab.clear()
        self.show_tab.addTab(tab, main_text + "·" +text)






