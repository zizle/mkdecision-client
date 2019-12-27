# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QHBoxLayout, QLabel, QComboBox, \
    QTableWidget, QPushButton
from widgets.base import LoadedPage
from PyQt5.QtCore import Qt
import settings


""" 管理产品服务的菜单 """

# 产品服务管理主页
class InfoServicePageCollector(QWidget):
    def __init__(self, *args, **kwargs):
        super(InfoServicePageCollector, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0)
        # 左侧管理菜单
        self.left_tree = QTreeWidget(clicked=self.left_tree_clicked)
        self.left_tree.header().hide()
        layout.addWidget(self.left_tree, alignment=Qt.AlignLeft)
        # 右侧显示窗口
        self.right_frame = LoadedPage()
        layout.addWidget(self.right_frame)
        self.setLayout(layout)
        self._addLeftTreeContentes()

    # 添加管理菜单
    def _addLeftTreeContentes(self):
        contents = [
            {
                'name': u'咨询服务',
                'subs': [
                    {'id': 1, 'name': u'短信通'},
                    {'id': 2, 'name': u'市场分析'},
                    {'id': 3, 'name': u'专题研究'},
                    {'id': 4, 'name': u'调研报告'},
                    {'id': 5, 'name': u'市场路演'},
                ]
            },
            {
                'name': u'顾问服务',
                'subs': [
                    {'id': 6, 'name': u'人才培养'},
                    {'id': 7, 'name': u'部门组建'},
                    {'id': 8, 'name': u'制度考核'},
                ]
            },
            {
                'name': u'策略服务',
                'subs': [
                    {'id': 9, 'name': u'交易策略'},
                    {'id': 10, 'name': u'投资方案'},
                    {'id': 11, 'name': u'套保方案'},
                ]
            },
            {
                'name': u'培训服务',
                'subs': [
                    {'id': 12, 'name': u'品种介绍'},
                    {'id': 13, 'name': u'基本分析'},
                    {'id': 14, 'name': u'技术分析'},
                    {'id': 15, 'name': u'制度规则'},
                    {'id': 16, 'name': u'交易管理'},
                    {'id': 17, 'name': u'经验分享'},
                ]
            },
        ]
        # 填充树
        for group_item in contents:
            group = QTreeWidgetItem(self.left_tree)
            group.setText(0, group_item['name'])
            # 添加子节点
            for variety_item in group_item['subs']:
                child = QTreeWidgetItem()
                child.setText(0, variety_item['name'])
                child.sid = variety_item['id']
                group.addChild(child)
        self.left_tree.expandAll()  # 展开所有

    # 点击左侧菜单
    def left_tree_clicked(self):
        item = self.left_tree.currentItem()
        if item.childCount():  # has children open the root
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
            return
        service_id = item.sid
        text = item.text(0)
        print(service_id)
        if service_id == 0:
            page = QWidget()
        else:
            page = QLabel('【' + text + '】还不能进行数据管理...',
                          styleSheet='color:rgb(50,180,100); font-size:15px;font-weight:bold', alignment=Qt.AlignCenter)

        self.right_frame.clear()
        self.right_frame.addWidget(page)










