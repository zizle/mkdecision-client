# _*_ coding:utf-8 _*_
"""
clients and users info in project
Update: 2019-07-25
Author: zizle
"""
import sys
import json
import requests
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, \
    QListView, QHeaderView, QLabel, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

import config
from thread.request import RequestThread
from piece.maintain import TableCheckBox
from popup.maintain import CreateNewClient
from popup.maintain.base import NewVarietyPopup
from widgets.maintain.base import ClientManagerTable, VarietyManagerTable


# 客户端管理
class ClientMaintain(QWidget):
    network_result = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(ClientMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        self.show_table = ClientManagerTable(parent=self)
        self.show_table.network_result.connect(self.emit_network_message)
        layout.addWidget(self.show_table)
        self.setLayout(layout)

    # 踢皮球，丢出控件发出来的信号
    def emit_network_message(self, message):
        self.network_result.emit(message)

    # 获取所有客户端
    def getClients(self):
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'basic/clients-maintain/?mc=' + config.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            # 填充表格内容
            self.show_table.addClients(response['data'])
            self.network_result.emit('')


# 品种管理
class VarietyMaintain(QWidget):
    network_result = pyqtSignal(str)   # 网络请求信号

    def __init__(self, *args, **kwargs):
        super(VarietyMaintain, self).__init__(*args, **kwargs)
        # 新增品种按钮,给上级窗口添加
        self.create_button = QPushButton('新增品种', clicked=self.create_variety)
        layout = QHBoxLayout(margin=0)
        # 左侧选择列表
        self.option_list = QListWidget()
        self.option_list.clicked.connect(self.option_list_clicked)
        # 右侧显示表格
        self.show_table = VarietyManagerTable()  # 品种管理表格
        self.show_table.verticalHeader().hide()  # 隐藏竖直表头
        self.show_table.network_result.connect(self.network_message_show_message)  # 表格发生的网络请求结果提示
        layout.addWidget(self.option_list, alignment=Qt.AlignLeft)
        layout.addWidget(self.show_table)

        # layout = QVBoxLayout(margin=0)
        # opl = QHBoxLayout()  # option layout 三级联动显示数据表
        # # 大类选择下拉菜单
        # self.combox_0 = QComboBox(parent=self, objectName='combo')
        # opl.addWidget(self.combox_0, alignment=Qt.AlignLeft)
        # # 网络请求结果显示
        # self.network_message = QLabel(parent=self, objectName='networkMessage')
        # opl.addWidget(self.network_message, alignment=Qt.AlignLeft)
        # opl.addStretch()  # 伸缩
        # self.show_table = VarietyManagerTable()  # 品种管理表格
        # self.show_table.verticalHeader().hide()  # 隐藏竖直表头
        # # 信号关联
        # self.show_table.network_result.connect(self.network_message_show_message)
        # self.combox_0.currentIndexChanged.connect(self.combox_0_changed)
        # layout.addLayout(opl)
        # layout.addWidget(self.show_table)
        self.setLayout(layout)
        # self.setStyleSheet("""
        # #combo QAbstractItemView::item{
        #     height: 22px;
        # }
        # #networkMessage{
        #     color: rgb(230,50,50);
        # }
        # """)
        # self.combox_0.setView(QListView())  # comboBox的高度设置生效
    
    # 获取品种组别
    def getVarietyGroups(self):
        # 此方法在表格单元格控件中也使用
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'basic/variety-groups/?mc=' + config.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
            return
        # 填入左侧list操作菜单
        for group_item in response['data']:
            item = QListWidgetItem(group_item['name'])
            item.gid = group_item['id']
            self.option_list.addItem(item)
            # self.combox_0.addItem(group_item['name'], group_item['id'])  # 在后续传入所需的数据，就是itemData

    # 请求当前组别下的品种
    def option_list_clicked(self):
        item = self.option_list.currentItem()
        self.show_table.clear()
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'basic/variety-groups/' + str(item.gid) + '/?mc=' + config.app_dawn.value(
                    'machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
            return
        self.show_table.addVarieties(response['data'])

    # def combox_0_changed(self):
    #     gid = self.combox_0.currentData()
    #     self.show_table.clear()
    #     try:
    #         r = requests.get(
    #             url=config.SERVER_ADDR + 'basic/variety-groups/' + str(gid) + '/?mc=' + config.app_dawn.value(
    #                 'machine'),
    #         )
    #         response = json.loads(r.content.decode('utf-8'))
    #         if r.status_code != 200:
    #             raise ValueError(response['message'])
    #     except Exception as e:
    #         self.network_message.setText(str(e))
    #         return
    #     self.show_table.addVarieties(response['data'])
    #     self.network_message.setText('')

    # 新增品种
    def create_variety(self):
        try:
            popup = NewVarietyPopup(parent=self)
            popup.deleteLater()
            if not popup.exec_():
                del popup
        except Exception as e:
            import traceback
            traceback.print_exc()

    # 踢皮球，将网络请求结果信号提出
    def network_message_show_message(self, message):
        self.network_result.emit(message)
        # self.network_message.setText(message)










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
                        checkbox.clicked_changed.connect(self.update_client_info)
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
        table_item = self.show_clients_table.item(signal['row'], 3)
        machine_code = table_item.text()
        print('frame.maintain.base.py {} 修改客户端：'.format(sys._getframe().f_lineno), machine_code)


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
                        checkbox.clicked_changed.connect(self.update_user_info)
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
