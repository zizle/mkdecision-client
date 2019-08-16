# _*_ coding:utf-8 _*_
"""
homepage frame window will make in tab
Update: 2019-07-25
Author: zizle
"""
import sys
from PyQt5.QtWidgets import *

import config
from widgets.base import MenuScrollContainer
from widgets.home import BulletinTable, CarouselLabel
from frame.base import NoDataWindow
from frame.home import Report, Notice, Commodity, Finance


class HomePage(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(HomePage, self).__init__(*args, **kwargs)
        home = QWidget()
        layout = QGridLayout()
        # widgets
        show_bulletin = BulletinTable()  # bulletin table
        caro_show = CarouselLabel()  # advertisement carousel widget
        left_menu = MenuScrollContainer(column=4)  # left list menu
        self.show_tab = QTabWidget()  # middle frame window container (use QTabWidget)
        self.report_show = Report()
        self.notice_show = None
        self.commodity_show = None
        self.finance_show = None
        # signal
        left_menu.menu_clicked.connect(self.tree_menu_clicked)
        # style
        self.setWidgetResizable(True)  # resize to windows size
        layout.setContentsMargins(0,0,0,0)
        show_bulletin.setFixedWidth(330)
        show_bulletin.setFixedHeight(350)
        caro_show.setFixedHeight(350)
        self.show_tab.setTabBarAutoHide(True)
        # add to layout
        self.setWidget(home)
        layout.addWidget(show_bulletin, 0, 0)
        layout.addWidget(caro_show, 0, 1)
        layout.addWidget(left_menu, 1, 0)
        layout.addWidget(self.show_tab, 1, 1)
        self.show_tab.addTab(self.report_show, '常规报告·全部')
        home.setLayout(layout)  # add layout to home widget
        # initial data
        show_bulletin.get_bulletin(url=config.SERVER_ADDR + "homepage/bulletin/") # bulletin
        caro_show.get_carousel(url=config.SERVER_ADDR + 'homepage/carousel/') # carousel
        left_menu.get_menu(url=config.SERVER_ADDR + 'homepage/module/')  # left menu list
        self.report_show.get_reports(category='all')  # initial report data

    def tree_menu_clicked(self, menu):
        parent = menu.parent
        parent_en = menu.parent_en
        name_en = menu.name_en
        print('windows.home.py {} 左菜单点击 :'.format(str(sys._getframe().f_lineno)), menu.parent_en, menu.name_en)
        if parent_en == 'routine_report':
            # tab = Report(category=name_en)
            self.report_show.get_reports(category=name_en)
            tab = self.report_show
        elif parent_en == 'transact_notice':
            if not self.notice_show:
                self.notice_show = Notice()
            self.notice_show.get_notices(category=name_en)
            tab = self.notice_show
        elif parent_en == 'spot_statement':
            try:
                if not self.commodity_show:
                    self.commodity_show = Commodity()
                self.commodity_show.set_current_date(date_name=name_en)
                self.commodity_show.get_commodity()
                tab = self.commodity_show
            except Exception as e:
                print(e)
        elif parent_en == 'economic_calendar':
            if not self.finance_show:
                self.finance_show = Finance()
            self.finance_show.set_current_date(date_name=name_en)
            self.finance_show.get_finance()
            tab = self.finance_show
        else:
            tab = NoDataWindow(name=parent + '·' + menu.text())
        self.show_tab.clear()
        self.show_tab.addTab(tab, menu.text())








