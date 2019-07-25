# _*_ coding:utf-8 _*_
"""
homepage frame window will make in tab
Update: 2019-07-25
Author: zizle
"""
from PyQt5.QtWidgets import *
from piece.home import ShowBulletin


class HomePage(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(HomePage, self).__init__(*args, **kwargs)
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
        caro_show = QLabel("Advertising Rotation")  # advertisement carousel widget
        # add bulletin widget and advertisement widget to layout
        ble_crl_layout.addWidget(bull_table)
        ble_crl_layout.addWidget(caro_show)
        left_tree = QTreeWidget()  # left list menu
        show_tab = QTabWidget()  # middle frame window container (use QTabWidget)
        # add left tree menu widget and frame window container to layout
        lmn_frame_layout.addWidget(left_tree)
        lmn_frame_layout.addWidget(show_tab)
        # add child layout to main layout
        layout.addLayout(ble_crl_layout)
        layout.addLayout(lmn_frame_layout)
        self.home.setLayout(layout)  # add layout to home widget
