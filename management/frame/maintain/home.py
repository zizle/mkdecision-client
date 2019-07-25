# _*_ coding:utf-8 _*_
"""
all tabs of data-maintenance module, in the home page
Update: 2019-07-25
Author: zizle
"""
from PyQt5.QtWidgets import *

from popup.maintain import CreateNewBulletin

class BulletinInfo(QWidget):
    def __init__(self):
        super(BulletinInfo, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        create_btn = QPushButton("设置")
        refresh_btn = QPushButton('刷新')
        create_btn.clicked.connect(self.create_new_bulletin)
        self.show_bulletin_table = QTableWidget()
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.show_bulletin_table)
        self.setLayout(layout)

    def create_new_bulletin(self):
        # dialog widget for edit bulletin information
        popup = CreateNewBulletin()
        if not popup.exec():
            del popup