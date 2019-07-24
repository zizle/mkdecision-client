# _*_ coding:utf-8 _*_
"""
all of tab in data-maintenance
Update: 2019-07-24
Author: zizle
"""
import re
import json
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QCursor, QIntValidator, QFont

import config
from threads import RequestThread
from widgets.maintain_widgets import TableCheckBox
from popups.maintain import CreateNewClient, CreateNewBulletin


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
        try:
            popup = CreateNewBulletin()
        except Exception as e:
            print(e)
        if not popup.exec():
            del popup




class ClientInfo(QWidget):
    # 客户端信息
    def __init__(self):
        super(ClientInfo, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout(margin=0)
        create_btn = QPushButton('+新增')
        refresh_btn = QPushButton('刷新')
        create_btn.clicked.connect(self.create_new_client)
        refresh_btn.clicked.connect(self.get_all_clients)
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        # show clients info table
        self.show_clients_table = QTableWidget()
        # all widgets and layout into layout
        layout.addLayout(action_layout)
        layout.addWidget(self.show_clients_table)
        self.setLayout(layout)
        # get clients info from server
        self.get_all_clients()

    def create_new_client(self):
        # dialog widget for edit client information
        def upload_new_client(signal):
            # create new client in server
            try:
                response = requests.post(
                    url=config.SERVER_ADDR + 'user/clients/',
                    headers=config.CLIENT_HEADERS,
                    data=json.dumps(signal),
                    cookies=config.app_dawn.value('cookies')
                )
            except Exception as error:
                QMessageBox.information(self, '提示', "发生了个错误!\n{}".format(error), QMessageBox.Yes)
                return
            response_data = json.loads(response.content.decode('utf-8'))
            if response.status_code != 201:
                QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
                return
            else:
                QMessageBox.information(self, '成功', '创建成功, 赶紧刷新看看吧.', QMessageBox.Yes)
                popup.close()  # close the dialog
        popup = CreateNewClient()
        popup.new_data_signal.connect(upload_new_client)
        if not popup.exec():
            del popup

    def fill_show_clients_table(self, content):
        if content['error']:
            return
        keys = [('serial_num', '序号'), ('update_time', '最近更新'), ("name", "名称"), ("machine_code", "机器码"),('bulletin_days', '公告(天)'), ('is_admin', "管理端"), ('is_active', "启用")]
        data = content['data']
        row = len(data)
        self.show_clients_table.setRowCount(row)
        self.show_clients_table.setColumnCount(len(keys))  # 列数
        labels = []
        set_keys = []
        for key_label in keys:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        self.show_clients_table.setHorizontalHeaderLabels(labels)
        self.show_clients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 列自适应
        self.show_clients_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 第一列根据文字宽自适应
        # self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 行自适应
        self.show_clients_table.verticalHeader().setVisible(False)
        for r in range(row):
            for c in range(self.show_clients_table.columnCount()):
                if c == 0:
                    item = QTableWidgetItem(str(r + 1))  # 序号
                else:
                    label_key = set_keys[c]
                    if label_key == 'is_admin' or label_key == 'is_active':  # 是否启用选择框展示
                        checkbox = TableCheckBox(row=r, col=c, option_label=label_key)
                        checkbox.setChecked(int(data[r][label_key]))
                        checkbox.check_change_signal.connect(self.update_client_info)
                        self.show_clients_table.setCellWidget(r, c, checkbox)
                    item = QTableWidgetItem(str(data[r][label_key]))
                item.setTextAlignment(132)
                self.show_clients_table.setItem(r, c, item)

    def get_all_clients(self):
        self.clients_thread = RequestThread(
            url=config.SERVER_ADDR + 'user/clients/',
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"machine_code": config.app_dawn.value('machine')}),
            cookies=config.app_dawn.value('cookies'),
        )
        self.clients_thread.finished.connect(self.clients_thread.deleteLater)
        self.clients_thread.response_signal.connect(self.fill_show_clients_table)
        self.clients_thread.start()

    def update_client_info(self, signal):
        """ checkbox in table has changed """
        # 获取机器码
        print(signal)
        table_item = self.show_clients_table.item(signal['row'], 3)
        machine_code = table_item.text()
        # 请求修改客户端信息
        print(machine_code)


class UserInfo(QWidget):
    # 用户信息
    def __init__(self, *args):
        super(UserInfo, self).__init__(*args)
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.get_all_users)
        self.show_users_table = QTableWidget()
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.show_users_table)
        self.setLayout(layout)
        # get all users information
        self.get_all_users()

    def fill_show_users_table(self, content):
        if content['error']:
            return
        keys = [('serial_num', '序号'), ('update_time', '最近更新'), ('username', '账号'), ('phone', '手机'), ("nick_name", "昵称"), ('is_admin', "管理员"), ('is_active', "启用")]
        data = content['data']
        row = len(data)
        self.show_users_table.setRowCount(row)
        self.show_users_table.setColumnCount(len(keys))  # 列数
        labels = []
        set_keys = []
        for key_label in keys:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        self.show_users_table.setHorizontalHeaderLabels(labels)
        self.show_users_table.verticalHeader().setVisible(False)
        self.show_users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 列自适应
        self.show_users_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 第一列根据文字宽自适应
        for r in range(row):
            for c in range(self.show_users_table.columnCount()):
                if c == 0:
                    item = QTableWidgetItem(str(r + 1))  # 序号
                else:
                    label_key = set_keys[c]
                    if label_key == 'is_admin' or label_key == 'is_active':  # 是否启用选择框展示
                        checkbox = TableCheckBox(row=r, col=c, option_label=label_key)
                        checkbox.setChecked(int(data[r][label_key]))
                        checkbox.check_change_signal.connect(self.update_user_info)
                        self.show_users_table.setCellWidget(r, c, checkbox)
                    item = QTableWidgetItem(str(data[r][label_key]))
                item.setTextAlignment(132)
                self.show_users_table.setItem(r, c, item)

    def get_all_users(self):
        self.users_thread = RequestThread(
            url=config.SERVER_ADDR + 'user/users/',
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"machine_code": config.app_dawn.value('machine')}),
            cookies=config.app_dawn.value('cookies')
        )
        self.users_thread.finished.connect(self.users_thread.deleteLater)
        self.users_thread.response_signal.connect(self.fill_show_users_table)
        self.users_thread.start()

    def update_user_info(self, signal):
        """ checkbox in table has changed """
        # 获取机器码
        print(signal)
        machine_code = config.app_dawn.value('machine')
        # 请求修改客户端信息
        print(machine_code)


class NoDataWindow(QWidget):
    def __init__(self,name, *args):
        super(NoDataWindow, self).__init__(*args)
        layout = QHBoxLayout()
        label = QLabel(name + "暂不可操作!")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("QLabel{color:red}")
        font = QFont()
        font.setPointSize(15)
        label.setFont(font)
        layout.addWidget(label)
        self.setLayout(layout)

