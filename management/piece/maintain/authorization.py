# _*_ coding:utf-8 _*_
# Author: zizle QQ:462894999
import json
import requests
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QComboBox, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
import config


# 用户-品种权限管理
class UserVarietyAuth(QWidget):
    network_result = pyqtSignal(str)

    def __init__(self, uid, *args, **kwargs):
        super(UserVarietyAuth, self).__init__(*args, **kwargs)
        self.user_id = uid
        layout = QVBoxLayout()
        self.variety_group_combo = QComboBox(parent=self)
        # 管理表格
        self.auth_table = QTableWidget(parent=self)
        self.auth_table.verticalHeader().hide()
        # 品种组改变请求数据
        self.variety_group_combo.currentIndexChanged.connect(self.current_variety_changed)
        # 加入布局
        layout.addWidget(self.variety_group_combo, alignment=Qt.AlignLeft)
        layout.addWidget(self.auth_table)
        self.setLayout(layout)

    # 获取品种的分组，填入选择框
    def getVarietyGroup(self):
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'basic/variety-groups/?mc=' + config.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            for group_item in response['data']:
                self.variety_group_combo.addItem(group_item['name'], group_item['id'])

    # 品种组改变，请求当前组下的品种
    def current_variety_changed(self):
        current_gid = self.variety_group_combo.currentData()
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'basic/variety-groups/' + str(current_gid) + '/?mc=' + config.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            # 填充表格展示
            self._showVarieties(response['data'])

    # 填充展示表格数据
    def _showVarieties(self, variety_list):
        self.auth_table.clear()
        self.auth_table.setRowCount(len(variety_list))
        self.auth_table.setColumnCount(5)
        self.auth_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.auth_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.auth_table.setHorizontalHeaderLabels(['序号', '名称', '英文代码', '权限', '所属组'])
        for row, variety_item in enumerate(variety_list):
            item_0 = QTableWidgetItem(str(row + 1))
            item_0.setTextAlignment(Qt.AlignCenter)
            item_1 = QTableWidgetItem(variety_item['name'])
            item_1.setTextAlignment(Qt.AlignCenter)
            item_2 = QTableWidgetItem(variety_item['name_en'])
            item_2.setTextAlignment(Qt.AlignCenter)
            item_3 = QTableWidgetItem(str('未知'))
            item_4 = QTableWidgetItem(variety_item['group'])
            item_4.setTextAlignment(Qt.AlignCenter)
            self.auth_table.setItem(row, 0, item_0)
            self.auth_table.setItem(row, 1, item_1)
            self.auth_table.setItem(row, 2, item_2)
            self.auth_table.setItem(row, 3, item_3)
            self.auth_table.setItem(row, 4, item_4)
