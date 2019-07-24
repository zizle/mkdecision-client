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

from windows.maintain_tab import NoDataWindow, BulletinInfo, ClientInfo, UserInfo
from threads import RequestThread
import config


class MaintenanceWindow(QWidget):
    def __init__(self):
        super(MaintenanceWindow, self).__init__()
        hor_layout = QHBoxLayout()
        self.left_tree = QTreeWidget()
        self.left_tree.setExpandsOnDoubleClick(False)
        self.left_tree.clicked.connect(self.left_tree_clicked)
        # a tab show windows
        self.right_tab = QTabWidget()
        self.right_tab.setTabsClosable(True)
        self.right_tab.tabCloseRequested.connect(self.close_tab)

        self.frame_windows = QStackedWidget()

        hor_layout.addWidget(self.left_tree, alignment=Qt.AlignLeft)
        hor_layout.addWidget(self.right_tab)
        layout = QVBoxLayout()
        layout.addLayout(hor_layout)

        self.setLayout(layout)
        # 线程请求菜单
        self.get_list_menu()

    def close_tab(self, index):
        if self.right_tab.count() > 1:
            self.right_tab.removeTab(index)
        else:
            # self.close()  # 当只有1个tab时，关闭主窗口
            return


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
        parent = item.parent()
        if parent is None:  # has not parent open the root
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        else:  # has parent to show frame window in tab
            text = item.text(0)
            if text == '客户端':
                tab = ClientInfo()
            elif text == '用户':
                tab = UserInfo()
            elif text == '公告栏':
                tab = BulletinInfo()
            else:
                tab = NoDataWindow(name=text)
            self.right_tab.addTab(tab, text)
            self.right_tab.setCurrentWidget(tab)
        print("点击事项完毕")

    def set_list_menu(self, content):
        """ set the left list navigate"""
        if content['error']:
            return
        for module in content['data']:
            menu = QTreeWidgetItem(self.left_tree)
            menu.setText(0, module['name'])
            menu.id = module['id']
            sub_menus = module['subs']
            # # 同时创建窗口(根节点窗口)
            # if module['name'] == "首页":
            #     home_page = HomePage(frame_names=sub_menus)
            #     home_page.id = module['id']
            #     home_page.name = module['name']
            #     self.frame_windows.addWidget(home_page)
            # elif module['name'] == '系统信息':
            #     system_page = SystemPage(frame_names=sub_menus)
            #     system_page.id = module['id']
            #     system_page.name = module['name']
            #     self.frame_windows.addWidget(system_page)
            # else:
            #     pass
            # 添加子节点
            for sub_module in sub_menus:
                child = QTreeWidgetItem()
                child.id = sub_module['id']
                child.setText(0, sub_module['name'])
                menu.addChild(child)




