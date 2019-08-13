# _*_ coding:utf-8 _*_
"""
homepage frame window will make in tab
Update: 2019-07-25
Author: zizle
"""
import sys
from PyQt5.QtWidgets import *

import config
from piece.home import ShowBulletin, MenuTree, Carousel
from frame.base import NoDataWindow
from frame.home import Report, Notice, Commodity, Finance


class HomePage(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(HomePage, self).__init__(*args, **kwargs)
        self.home = QWidget()
        self.draw_home()
        self.setWidgetResizable(True)  # resize to windows size
        self.setWidget(self.home)

    def draw_home(self):
        layout = QVBoxLayout()
        ble_crl_layout = QHBoxLayout() # bulletin and carousel layout
        lmn_frame_layout = QHBoxLayout()  # left list menu and middle frame window layout
        bull_table = ShowBulletin()  # bulletin table
        bull_table.setMaximumWidth(400)
        caro_show = Carousel()  # advertisement carousel widget
        # add bulletin widget and advertisement widget to layout
        ble_crl_layout.addWidget(bull_table)
        ble_crl_layout.addWidget(caro_show)
        self.menu_tree = MenuTree()  # left list menu
        self.show_tab = QTabWidget()  # middle frame window container (use QTabWidget)
        self.show_tab.setTabBarAutoHide(True)
        # signal
        self.menu_tree.clicked.connect(self.tree_menu_clicked)
        # add left tree menu widget and frame window container to layout
        lmn_frame_layout.addWidget(self.menu_tree)
        lmn_frame_layout.addWidget(self.show_tab)
        # add child layout to main layout
        layout.addLayout(ble_crl_layout)
        layout.addLayout(lmn_frame_layout)
        self.home.setLayout(layout)  # add layout to home widget

    def tree_menu_clicked(self):
        menu = self.menu_tree.currentItem()
        print('windows.home.py {} 左菜单点击 :'.format(str(sys._getframe().f_lineno)), menu.id, menu.text(0))
        text = menu.text(0)
        if text == '常规报告':
            tab = Report()
        elif text == '交易通知':
            tab = Notice()
        elif text == '现货报表':
            tab = Commodity()
        elif text == '财经日历':
            tab = Finance()
        else:
            tab = NoDataWindow(name=text)
        self.show_tab.clear()
        self.show_tab.addTab(tab, text)


