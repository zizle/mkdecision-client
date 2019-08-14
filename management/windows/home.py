# _*_ coding:utf-8 _*_
"""
homepage frame window will make in tab
Update: 2019-07-25
Author: zizle
"""
import sys
from PyQt5.QtWidgets import *

import config
from widgets.base import MenuScrollContainer, TableShow
from piece.home import ShowBulletin, MenuTree, Carousel
from frame.base import NoDataWindow
from thread.request import RequestThread
from frame.home import Report, Notice, Commodity, Finance


class HomePage(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(HomePage, self).__init__(*args, **kwargs)
        self.home = QWidget()
        self.setWidgetResizable(True)  # resize to windows size
        self.setWidget(self.home)
        layout = QVBoxLayout()
        ble_crl_layout = QHBoxLayout() # bulletin and carousel layout
        lmn_frame_layout = QHBoxLayout()  # left list menu and middle frame window layout
        bull_table = ShowBulletin()  # bulletin table
        bull_table.setMaximumWidth(330)
        caro_show = Carousel()  # advertisement carousel widget
        # add bulletin widget and advertisement widget to layout
        ble_crl_layout.addWidget(bull_table)
        ble_crl_layout.addWidget(caro_show)
        self.left_menu = MenuScrollContainer(column=4)  # left list menu

        self.show_tab = QTabWidget()  # middle frame window container (use QTabWidget)
        self.show_tab.setTabBarAutoHide(True)
        # signal
        self.left_menu.menu_clicked.connect(self.tree_menu_clicked)
        # add left tree menu widget and frame window container to layout
        lmn_frame_layout.addWidget(self.left_menu)
        lmn_frame_layout.addWidget(self.show_tab)
        # add child layout to main layout
        layout.addLayout(ble_crl_layout)
        layout.addLayout(lmn_frame_layout)
        self.home.setLayout(layout)  # add layout to home widget
        # request menu
        self.left_menu.get_menu(url=config.SERVER_ADDR + 'homepage/module/')

    def tree_menu_clicked(self, menu):
        parent = menu.parent
        parent_en = menu.parent_en
        name_en = menu.name_en
        print('windows.home.py {} 左菜单点击 :'.format(str(sys._getframe().f_lineno)), menu.parent_en, menu.name_en)
        if parent_en == 'routine_report':
            tab = Report(category=name_en)
        else:
            tab = NoDataWindow(name=parent + '·' + menu.text())

        # if text == '常规报告':
        #     tab = Report()
        # elif text == '交易通知':
        #     tab = Notice()
        # elif text == '现货报表':
        #     tab = Commodity()
        # elif text == '财经日历':
        #     tab = Finance()
        # else:

        self.show_tab.clear()
        self.show_tab.addTab(tab, menu.text())








