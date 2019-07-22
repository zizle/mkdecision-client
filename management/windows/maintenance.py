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
        self.left_list = QListWidget()
        self.left_list.clicked.connect(self.left_list_clicked)
        hor_layout.addWidget(self.left_list, alignment=Qt.AlignLeft)
        layout = QVBoxLayout()
        layout.addLayout(hor_layout)
        self.setLayout(layout)
        # 线程请求菜单
        self.get_tree_menu()

    def get_tree_menu(self):
        """ get menus """
        headers = config.CLIENT_HEADERS
        self.left_list_thread = RequestThread(
            url=config.SERVER_ADDR + 'basic/maintenance/',
            method='get',
            headers=headers,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.left_list_thread.finished.connect(self.left_list_thread.deleteLater)
        self.left_list_thread.response_signal.connect(self.set_list_menu)
        self.left_list_thread.start()

    def left_list_clicked(self, tree_item):
        """ click action """
        item = self.left_list.currentItem()
        print(item, item.id)

    def set_list_menu(self, content):
        """ set the left tree navigate"""
        print(content)
        if content['error']:
            pass
        for module in content['data']:
            menu = QListWidgetItem(self.left_list)
            menu.setText(module['name'])
            menu.id = module['id']
            print(module['subs'])




