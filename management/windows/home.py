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
from piece.home import HomeBulletin, Carousel
from frame.base import NoDataWindow
from frame.home import Report, Notice, Commodity, Finance


class HomePage(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(HomePage, self).__init__(*args, **kwargs)
        self.home = QWidget()
        self.setWidgetResizable(True)  # resize to windows size
        self.setWidget(self.home)
        layout = QGridLayout()
        # widgets
        show_bulletin = HomeBulletin()  # bulletin table
        show_bulletin.setFixedWidth(330)
        show_bulletin.setFixedHeight(350)
        caro_show = Carousel()  # advertisement carousel widget
        caro_show.setFixedHeight(350)
        self.left_menu = MenuScrollContainer(column=4)  # left list menu
        self.show_tab = QTabWidget()  # middle frame window container (use QTabWidget)
        self.show_tab.setTabBarAutoHide(True)
        # signal
        self.left_menu.menu_clicked.connect(self.tree_menu_clicked)
        # style
        layout.setContentsMargins(0,0,0,0)
        # add to layout
        layout.addWidget(show_bulletin, 0, 0)
        layout.addWidget(caro_show, 0, 1)
        layout.addWidget(self.left_menu, 1, 0)
        layout.addWidget(self.show_tab, 1, 1)
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
        elif parent_en == 'transact_notice':
            tab = Notice(category=name_en)
        else:
            tab = NoDataWindow(name=parent + '·' + menu.text())
        # elif text == '现货报表':
        #     tab = Commodity()
        # elif text == '财经日历':
        #     tab = Finance()
        # else:

        self.show_tab.clear()
        self.show_tab.addTab(tab, menu.text())








