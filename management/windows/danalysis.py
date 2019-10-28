# _*_ coding:utf-8 _*_
# __Author__： zizle
"""
data analysis 数据分析
"""
import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTabWidget, QTabBar
from widgets.base import MenuScrollContainer

import config
from widgets.danalysis import VarietyDetailMenuWidget


class DAnalysis(QWidget):
    def __init__(self, *args, **kwargs):
        super(DAnalysis, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        # widgets
        self.left_selected_tab = QTabWidget()
        self.tab_show = QTabWidget()
        layout.addWidget(self.left_selected_tab)
        layout.addWidget(self.tab_show)
        self.variety_menu = MenuScrollContainer(column=3)
        self.left_selected_tab.addTab(self.variety_menu, '品种')
        # signal
        self.variety_menu.menu_clicked.connect(self.variety_selected)
        self.setLayout(layout)
        # 获取品种菜单
        # style
        self.left_selected_tab.setTabsClosable(True)
        self.left_selected_tab.tabBar().setTabButton(0, QTabBar.RightSide, None)
        self.variety_menu.get_menu(url=config.SERVER_ADDR + 'danalysis/variety_menu/')

    def variety_selected(self, menu):
        print('windows.danalysis.py {} 选择菜单：'.format(sys._getframe().f_lineno), menu.parent, menu.name_en)
        parent = menu.parent
        parent_en = menu.parent_en
        name = menu.text()
        name_en = menu.name_en
        self.left_selected_tab.removeTab(1)
        self.left_selected_tab.addTab(VarietyDetailMenuWidget(), '行业数据')
        self.left_selected_tab.setCurrentIndex(1)


