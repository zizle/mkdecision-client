# _*_ coding:utf-8 _*_
"""
管理端数据维护窗口
Create: 2019-07-22
Update: 2019-07-22
Author: zizle
"""
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

from threads import RequestThread
import config

class MaintenanceWindow(QWidget):
    def __init__(self):
        super(MaintenanceWindow, self).__init__()
        hor_layout = QHBoxLayout()
        left_tree = QTreeWidget()
        left_tree.setColumnCount(1)
        hor_layout.addWidget(left_tree, alignment=Qt.AlignLeft)
        layout = QVBoxLayout()
        layout.addLayout(hor_layout)
        self.setLayout(layout)
        # 线程请求菜单
        self.set_tree_menu()

    def get_tree_menu(self):
        """ get menus """
        headers = config.CLIENT_HEADERS
        self.tree_thread = RequestThread(
            url='',
            method='get',
            headers=headers,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.tree_thread.finished.connect(self.tree_thread.deleteLater)
        self.tree_thread.response_signal.connect(self.set_tree_menu)


    def set_tree_menu(self, content):
        """ set the left tree navigate"""
        print(content)



