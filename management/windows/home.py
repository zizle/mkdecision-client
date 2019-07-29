# _*_ coding:utf-8 _*_
"""
homepage frame window will make in tab
Update: 2019-07-25
Author: zizle
"""
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

from piece.home import ShowBulletin, MenuTree, Carousel
from frame.base import NoDataWindow
from frame.home import Report


class HomePage(QScrollArea):
    def __init__(self, menu_parent, *args, **kwargs):
        super(HomePage, self).__init__(*args, **kwargs)
        self.menu_parent = menu_parent
        self.home = QWidget()
        self.draw_home()
        self.setWidgetResizable(True)
        self.setWidget(self.home)

    def draw_home(self):
        layout = QVBoxLayout()
        ble_crl_layout = QHBoxLayout() # bulletin and carousel layout
        lmn_frame_layout = QHBoxLayout()  # left list menu and middle frame window layout
        bull_table = ShowBulletin()  # bulletin table
        bull_table.setMaximumWidth(400)
        try:
            caro_show = Carousel()  # advertisement carousel widget
        except Exception as e:
            import traceback
            traceback.print_exc()
        # add bulletin widget and advertisement widget to layout
        ble_crl_layout.addWidget(bull_table)
        ble_crl_layout.addWidget(caro_show)
        self.menu_tree = MenuTree(menu_parent=self.menu_parent)  # left list menu
        self.menu_tree.clicked.connect(self.tree_menu_clicked)
        self.show_tab = QTabWidget()  # middle frame window container (use QTabWidget)
        self.show_tab.setTabBarAutoHide(True)
        # add left tree menu widget and frame window container to layout
        lmn_frame_layout.addWidget(self.menu_tree)
        lmn_frame_layout.addWidget(self.show_tab)
        # add child layout to main layout
        layout.addLayout(ble_crl_layout)
        layout.addLayout(lmn_frame_layout)
        self.home.setLayout(layout)  # add layout to home widget

    def tree_menu_clicked(self):
        menu = self.menu_tree.currentItem()
        print('frame.home.py {} 左菜单点击 :'.format(str(sys._getframe().f_lineno)), menu.id, menu.text(0))
        text = menu.text(0)
        if text == '常规报告':
            tab = Report()
        else:
            tab = NoDataWindow(name=text)
        self.show_tab.clear()
        self.show_tab.addTab(tab, text)


