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

from windows.maintain_wickets import HomePage, SystemPage
from threads import RequestThread
import config


class MaintenanceWindow(QWidget):
    def __init__(self):
        super(MaintenanceWindow, self).__init__()
        hor_layout = QHBoxLayout()
        self.left_tree = QTreeWidget()
        self.left_tree.clicked.connect(self.left_tree_clicked)
        self.module_windows = QStackedWidget()
        hor_layout.addWidget(self.left_tree, alignment=Qt.AlignLeft)
        hor_layout.addWidget(self.module_windows)
        layout = QVBoxLayout()
        layout.addLayout(hor_layout)

        self.setLayout(layout)
        # 线程请求菜单
        self.get_list_menu()

    def get_list_menu(self):
        """ get menus """
        headers = config.CLIENT_HEADERS
        self.left_tree_thread = RequestThread(
            url=config.SERVER_ADDR + 'basic/maintenance/',
            method='get',
            headers=headers,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.left_tree_thread.finished.connect(self.left_tree_thread.deleteLater)
        self.left_tree_thread.response_signal.connect(self.set_list_menu)
        self.left_tree_thread.start()

    def left_tree_clicked(self):
        """ click action """
        item = self.left_tree.currentItem()
        frame_id = list()
        for index in range(self.module_windows.count()):
            frame = self.module_windows.widget(index)
            if frame.id == item.id:
                self.module_windows.setCurrentWidget(frame)
            frame_id.append(frame.id)
        if item.id not in frame_id:
            QMessageBox.information(self, '敬请期待', '本模块功能暂未开放。', QMessageBox.Yes)
        print('点击事件完毕')

    def set_list_menu(self, content):
        """ set the left list navigate"""
        if content['error']:
            pass
        for module in content['data']:
            menu = QTreeWidgetItem(self.left_tree)
            menu.setText(0, module['name'])
            menu.id = module['id']
            # 同时创建窗口(根节点窗口)
            if module['name'] == "首页":
                home_page = HomePage()
                home_page.id = module['id']
                home_page.name = module['name']
                self.module_windows.addWidget(home_page)
            elif module['name'] == '系统信息':
                system_page = SystemPage()
                system_page.id = module['id']
                system_page.name = module['name']
                self.module_windows.addWidget(system_page)
            # 子节点窗口

