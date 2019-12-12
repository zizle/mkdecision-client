# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
from PyQt5.QtWidgets import QWidget, QListWidget, QHBoxLayout, QVBoxLayout, QTabWidget, QLabel, QComboBox, \
    QHeaderView, QPushButton
from PyQt5.QtCore import Qt
from popup.operator import EditUserInformationPopup, EditClientInformationPopup, CreateNewModulePopup,\
    EditModuleInformationPopup, CreateNewVarietyPopup, EditVarietyInformationPopup
import settings
from widgets.base import ManageTable

""" 用户管理相关 """


# 显示用户表格
class UsersTable(ManageTable):
    KEY_LABELS = [
        ('id', '序号'),
        ('username', '用户名/昵称'),
        ('phone', '手机'),
        ('email', '邮箱'),
        ('role', '角色'),
        ('last_login', '最近登录'),
        ('note', '备注'),
        ('is_active', '有效'),
    ]
    CHECK_COLUMNS = [7]

    # 初始化表格
    def resetTableMode(self, row_count):
        super(UsersTable, self).resetTableMode(row_count)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(self.columnCount() - 1, QHeaderView.ResizeToContents)

    # 选择状态发生改变
    def check_box_changed(self, check_box):
        row, column = self.get_widget_index(check_box)
        user_id = self.item(row, 0).id
        print('改变id=%d的用户的为%s' % (user_id, '有效' if check_box.check_box.isChecked() else '无效'))
        # 修改用户有效的请求
        try:
            r = requests.patch(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/baseInfo/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({'is_active': check_box.check_box.isChecked()})
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            self.network_result.emit(response['message'])

    # 修改用户信息
    def edit_button_clicked(self, edit_button):
        row, column = self.get_widget_index(edit_button)
        user_id = self.item(row, 0).id
        # 弹窗设置当前用户信息
        edit_popup = EditUserInformationPopup(user_id=user_id, parent=self)
        if not edit_popup.exec_():
            edit_popup.deleteLater()
            del edit_popup


# 用户管理页面
class UserManagePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(UserManagePage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 用户的类型选择与网络请求结果
        combo_message_layout = QHBoxLayout()
        self.role_combo = QComboBox()
        self.role_combo.activated.connect(self.getCurrentUsers)
        combo_message_layout.addWidget(self.role_combo)
        self.network_message = QLabel()
        combo_message_layout.addWidget(self.network_message)
        combo_message_layout.addStretch()
        layout.addLayout(combo_message_layout)
        # 用户表显示
        self.users_table = UsersTable()
        self.users_table.network_result.connect(self.network_message.setText)
        layout.addWidget(self.users_table)
        self.setLayout(layout)
        self._addRoleComboItems()

    # 填充选择下拉框
    def _addRoleComboItems(self):
        for combo_item in [
            ('全部', 'all'),
            ('运营管理员', 'is_operator'),  # 与后端对应
            ('信息管理员', 'is_collector'),  # 与后端对应
            ('研究员', 'is_researcher'),  # 与后端对应
            ('普通用户', 'normal'),
        ]:
            self.role_combo.addItem(combo_item[0], combo_item[1])

    # 获取相关用户
    def getCurrentUsers(self):
        current_data = self.role_combo.currentData()
        params = {}
        if current_data == 'all':
            pass
        elif current_data == 'normal':
            params['is_operator'] = False
            params['is_collector'] = False
            params['is_researcher'] = False
        else:
            params[current_data] = True
        # 请求数据
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value("AUTHORIZATION")},
                data=json.dumps(params)
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message.setText(str(e))
        else:
            self.users_table.setRowContents(response['data'])
            self.network_message.setText(response['message'])


""" 客户端管理相关 """


# 客户端管理表格
class ClientsTable(ManageTable):
    KEY_LABELS = [
        ('id', '序号'),
        ('name', '名称'),
        ('machine_code', '机器码'),
        ('is_active', '有效'),
        ('category', '类型'),
    ]
    CHECK_COLUMNS = [3]

    def resetTableMode(self, row_count):
        super(ClientsTable, self).resetTableMode(row_count)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(self.columnCount() - 1, QHeaderView.ResizeToContents)

    # 修改有效与否
    def check_box_changed(self, check_box):
        current_row, current_column = self.get_widget_index(check_box)
        client_id = self.item(current_row, 0).id
        # 修改客户端有效的请求
        try:
            r = requests.patch(
                url=settings.SERVER_ADDR + 'client/' + str(client_id) + '/?mc=' + settings.app_dawn.value(
                    'machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({'is_active': check_box.check_box.isChecked()})
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            self.network_result.emit(response['message'])

    # 点击编辑信息
    def edit_button_clicked(self, edit_button):
        row, column = self.get_widget_index(edit_button)
        client_id = self.item(row, 0).id
        print(client_id)
        # 弹窗设置当前客户端信息
        try:
            edit_popup = EditClientInformationPopup(client_id=client_id, parent=self)
            edit_popup.getCurrentClient()
            if not edit_popup.exec_():
                edit_popup.deleteLater()
                del edit_popup
        except Exception as e:
            print(e)


# 客户端管理页面
class ClientManagePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(ClientManagePage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 客户端的类型选择与网络请求结果
        combo_message_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.activated.connect(self.getCurrentClients)
        combo_message_layout.addWidget(self.category_combo)
        self.network_message = QLabel()
        combo_message_layout.addWidget(self.network_message)
        combo_message_layout.addStretch()
        layout.addLayout(combo_message_layout)
        # 客户端列表显示
        self.clients_table = ClientsTable()
        self.clients_table.network_result.connect(self.network_message.setText)
        layout.addWidget(self.clients_table)
        self.setLayout(layout)
        self._addCategoryItems()

    # 填充选择下拉框
    def _addCategoryItems(self):
        for combo_item in [
            ('全部', 'all'),
            ('管理端', 'is_manager'),  # 与后端对应
            ('普通端', 'normal'),
        ]:
            self.category_combo.addItem(combo_item[0], combo_item[1])

    # 获取相关客户端
    def getCurrentClients(self):
        current_data = self.category_combo.currentData()
        params = {}
        if current_data == 'all':
            pass
        elif current_data == 'normal':
            params['is_manager'] = False
        else:
            params[current_data] = True
        # 请求数据
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'client/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value("AUTHORIZATION")},
                data=json.dumps(params)
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message.setText(str(e))
        else:
            self.clients_table.setRowContents(response['data'])
            self.network_message.setText(response['message'])


""" 系统模块管理相关 """


# 模块显示管理表格
class ModulesTable(ManageTable):
    KEY_LABELS = [
        ('id', '序号'),
        ('name', '名称'),
        ('is_active', '有效')
    ]
    CHECK_COLUMNS = [2]

    def resetTableMode(self, row_count):
        super(ModulesTable, self).resetTableMode(row_count)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

    # 编辑模块的有效
    def check_box_changed(self, check_box):
        current_row, current_col = self.get_widget_index(check_box)
        module_id = self.item(current_row, 0).id
        try:
            r = requests.patch(
                url=settings.SERVER_ADDR + 'module/' + str(module_id) + '/?mc=' + settings.app_dawn.value(
                    'machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({'is_active': check_box.check_box.isChecked()})
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            self.network_result.emit(response['message'])

    def edit_button_clicked(self, edit_button):
        current_row, current_col = self.get_widget_index(edit_button)
        module_id = self.item(current_row, 0).id
        # 弹窗编辑信息
        edit_popup = EditModuleInformationPopup(module_id=module_id, parent=self)
        edit_popup.getCurrentModule()
        if not edit_popup.exec_():
            edit_popup.deleteLater()
            del edit_popup


# 模块管理页面
class ModuleManagePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(ModuleManagePage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 信息显示与新增按钮布局
        message_button_layout = QHBoxLayout()
        self.network_message = QLabel()
        message_button_layout.addWidget(self.network_message)
        message_button_layout.addStretch()
        self.add_button = QPushButton('新增', clicked=self.create_new_module)
        message_button_layout.addWidget(self.add_button, alignment=Qt.AlignRight)
        # 模块编辑显示表格
        self.module_table = ModulesTable(parent=self)
        self.module_table.network_result.connect(self.network_message.setText)
        layout.addLayout(message_button_layout)
        layout.addWidget(self.module_table)
        self.setLayout(layout)

    # 获取系统模块信息
    def getCurrentModules(self):
        # 请求数据
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'module/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message.setText(str(e))
        else:
            self.module_table.setRowContents(response['data'])
            self.network_message.setText(response['message'])

    # 新增系统模块
    def create_new_module(self):
        popup = CreateNewModulePopup(parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup


""" 品种管理相关 """


# 品种显示管理表格
class VarietiesTable(ManageTable):
    KEY_LABELS = [
        ('id', '序号'),
        ('name', '名称'),
        ('name_en', '英文代码'),
        ('group', '所属组'),
    ]

    def resetTableMode(self, row_count):
        super(VarietiesTable, self).resetTableMode(row_count)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(len(self.KEY_LABELS), QHeaderView.ResizeToContents)

    def edit_button_clicked(self, edit_button):
        current_row, current_col = self.get_widget_index(edit_button)
        variety_id = self.item(current_row, 0).id
        print('修改品种', variety_id)
        # 弹窗编辑信息
        edit_popup = EditVarietyInformationPopup(variety_id=variety_id, parent=self)
        edit_popup.getCurrentVariety()
        if not edit_popup.exec_():
            edit_popup.deleteLater()
            del edit_popup


# 品种管理页面
class VarietyManagePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(VarietyManagePage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 上方品种大类选择和信息提示
        combo_message_layout = QHBoxLayout()
        self.select_combo = QComboBox(activated=self.getCurrentVarieties)
        combo_message_layout.addWidget(self.select_combo)
        self.network_message_label = QLabel()
        combo_message_layout.addWidget(self.network_message_label)
        combo_message_layout.addStretch()
        # 新增品种按钮
        self.add_button = QPushButton('新增', clicked=self.create_new_variety)
        combo_message_layout.addWidget(self.add_button)
        layout.addLayout(combo_message_layout)
        # 下方显示管理表格
        self.variety_table = VarietiesTable(parent=self)
        layout.addWidget(self.variety_table)
        self.setLayout(layout)

    # 获取分组
    def getVarietyGroup(self):
        # 请求数据
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'group-varieties/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            # 增加全部选项
            self.select_combo.addItem('全部', 0)
            for group_item in response['data']:
                self.select_combo.addItem(group_item['name'], group_item['id'])
            self.network_message_label.setText(response['message'])

    # 获取品种
    def getCurrentVarieties(self):
        current_gid = self.select_combo.currentData()
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'group-varieties/' + str(current_gid) + '/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.variety_table.setRowContents(response['data'])
            self.network_message_label.setText(response['message'])

    # 新增品种
    def create_new_variety(self):
        popup = CreateNewVarietyPopup(parent=self)
        popup.getGroupWithVarieties()
        if not popup.exec_():
            popup.deleteLater()
            del popup


""" 运营管理主页 """


# 运营管理主页
class OperatorMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(OperatorMaintain, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        # 左侧管理项目列表
        self.operate_list = QListWidget()
        self.operate_list.clicked.connect(self.operate_list_clicked)
        layout.addWidget(self.operate_list, alignment=Qt.AlignLeft)
        # 右侧tab显示
        self.frame_tab = QTabWidget()
        self.frame_tab.setDocumentMode(True)
        self.frame_tab.tabBar().hide()
        layout.addWidget(self.frame_tab)
        self.setLayout(layout)

    # 加入运营管理菜单
    def addListItem(self):
        self.operate_list.addItems([u'用户管理', u'客户端管理', u'模块管理', u'品种管理'])

    # 点击左侧管理菜单
    def operate_list_clicked(self):
        text = self.operate_list.currentItem().text()
        try:
            if text == u'用户管理':
                tab = UserManagePage(parent=self)
                tab.getCurrentUsers()
            elif text == u'客户端管理':
                tab = ClientManagePage(parent=self)
                tab.getCurrentClients()
            elif text == u'模块管理':
                tab = ModuleManagePage(parent=self)
                tab.getCurrentModules()
            elif text == u'品种管理':
                tab = VarietyManagePage(parent=self)
                tab.getVarietyGroup()
                tab.getCurrentVarieties()
            else:
                tab = QLabel(parent=self,
                             styleSheet='font-size:16px;font-weight:bold;color:rgb(230,50,50)',
                             alignment=Qt.AlignCenter)
                tab.setText("「" + text + "」正在加紧开放中...")
        except Exception as e:
            import traceback
            traceback.print_exc()
        self.frame_tab.clear()
        self.frame_tab.addTab(tab, text)
