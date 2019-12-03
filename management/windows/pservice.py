# _*_ coding:utf-8 _*_
"""
product service windows made in main tab
Create: 2019-08-01
Author: zizle
"""
import sys
from PyQt5.QtWidgets import *

import config
from widgets.base import MenuScrollContainer
from frame.pservice import MessageComm, MarketAnalysis, TopicalStudy, ResearchReport, AdviserShow


class PService(QWidget):
    def __init__(self, *args, **kwargs):
        super(PService, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        # widgets
        left_menu = MenuScrollContainer(column=3)
        self.tab_show = QTabWidget()
        # signal
        left_menu.menu_clicked.connect(self.left_menu_clicked)
        # style
        layout.setContentsMargins(0,0,0,0)
        self.tab_show.setTabBarAutoHide(True)
        # add to layout
        layout.addWidget(left_menu)
        layout.addWidget(self.tab_show)
        self.setLayout(layout)
        # initial data
        # 左侧2级菜单
        left_menu.get_menu(url=config.SERVER_ADDR + 'pservice/module/')

    def left_menu_clicked(self, menu):
        print('windows.pservice.py {} 选择菜单：'.format(sys._getframe().f_lineno), menu.parent, menu.name_en)
        parent = menu.parent
        parent_en = menu.parent_en
        name = menu.text()
        name_en = menu.name_en
        if parent_en == 'consultation':  # 咨询服务
            if name_en == 'message_comm':
                tab = MessageComm()
            elif name_en == 'market_analysis':
                tab = MarketAnalysis()
            elif name_en == 'topical_study':
                tab = TopicalStudy()
            elif name_en == 'research':
                tab = ResearchReport()
            else:
                tab = NoDataWindow(name=parent + '·' + name)
        elif parent_en == 'adviser':   # 顾问服务
            tab = AdviserShow(category=name_en)  # 显示pdf文件内容
        else:
            tab = NoDataWindow(name=parent + '·' + name)
        self.tab_show.clear()
        self.tab_show.addTab(tab, parent + '·' + name)

