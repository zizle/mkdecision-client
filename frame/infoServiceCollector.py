# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
from PyQt5.QtWidgets import QWidget, QTreeWidget, QTreeWidgetItem, QHBoxLayout
from widgets.base import LoadedPage
from PyQt5.QtCore import Qt
import settings


# 产品服务管理主页
class InfoServicePageCollector(QWidget):
    def __init__(self, *args, **kwargs):
        super(InfoServicePageCollector, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0)
        # 左侧管理菜单
        self.left_tree = QTreeWidget()
        self.left_tree.header().hide()
        layout.addWidget(self.left_tree, alignment=Qt.AlignLeft)
        # 右侧显示窗口
        self.right_frame = LoadedPage()
        layout.addWidget(self.right_frame)
        self.setLayout(layout)

    # 请求管理菜单并添加
    def getServiceContents(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'info/group/?mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            services = response['data']
            services.insert(0, {'id': 0, 'name': '服务管理', 'subs': [{'id': 0, 'name': '服务内容'}]})
            # 填充品种树
            for group_item in services:
                group = QTreeWidgetItem(self.left_tree)
                group.setText(0, group_item['name'])
                group.gid = group_item['id']
                # 添加子节点
                for variety_item in group_item['subs']:
                    child = QTreeWidgetItem()
                    child.setText(0, variety_item['name'])
                    child.sid = variety_item['id']
                    group.addChild(child)
            self.left_tree.expandAll()  # 展开所有








