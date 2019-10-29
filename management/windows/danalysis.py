# _*_ coding:utf-8 _*_
# __Author__： zizle
"""
data analysis 数据分析
"""
import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTabWidget, QTabBar
from widgets.base import MenuScrollContainer

import config
from piece.danalysis import VarietyHome, VarietyDetail


class DAnalysis(QTabWidget):
    def __init__(self, *args, **kwargs):
        super(DAnalysis, self).__init__(*args, **kwargs)
        # 索引为0的tab，即首页
        self.tab_0 = VarietyHome()
        # 索引1为点击品种后产生
        self.addTab(self.tab_0, '品种')
        # signal
        self.tab_0.variety_menu.menu_clicked.connect(self.variety_selected)
        self.tabCloseRequested.connect(self.click_tab_closed)
        # style
        self.setTabsClosable(True)
        self.tabBar().setTabButton(0, QTabBar.RightSide, None)
        self.setStyleSheet("""
           QTabBar::pane{
               border: 0.5px solid rgb(180,180,180);
           }
           QTabBar::tab{
               min-height: 25px
           }
           QTabBar::tab:selected {
           
           }
           QTabBar::tab:!selected {
               background-color:rgb(180,180,180)
           }
           QTabBar::tab:hover {
               color: rgb(20,100,230);
               background: rgb(220,220,220)
           }
           """
        )

    # 选择品种后的相信tab
    def variety_selected(self, menu):
        print('windows.danalysis.py {} 选择品种菜单：'.format(sys._getframe().f_lineno), menu.parent, menu.name_en)
        parent = menu.parent
        parent_en = menu.parent_en
        name = menu.text()
        name_en = menu.name_en
        self.removeTab(1)
        tab_1 = VarietyDetail(variety=name_en, width=self.tab_0.variety_menu.width())
        self.addTab(tab_1, '行业数据')
        self.setCurrentIndex(1)

    def click_tab_closed(self, index):
        self.removeTab(index)

