# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
from PyQt5.QtWidgets import QWidget, QListWidget, QHBoxLayout, QVBoxLayout, QTabWidget, QLabel, QComboBox, \
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
import settings

""" 用户管理相关 """


# 【有效】勾选按钮
class CheckBox(QWidget):
    check_activated = pyqtSignal(QWidget)

    def __init__(self, checked=False, *args, **kwargs):
        super(CheckBox, self).__init__(*args, **kwargs)
        self.check_box = QCheckBox(checked=checked)
        self.check_box.setMinimumHeight(14)
        layout = QVBoxLayout()
        layout.addWidget(self.check_box, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        self.check_box.stateChanged.connect(lambda: self.check_activated.emit(self))


# 显示用户表格
class UsersTable(QTableWidget):
    network_result = pyqtSignal(str)

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

    def __init__(self, *args, **kwargs):
        super(UsersTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()

    # 设置表格数据
    def setRowContents(self, user_list):
        self._resetTableMode(len(user_list))
        for row, user_item in enumerate(user_list):
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = user_item[header[0]]
                else:
                    table_item = QTableWidgetItem(str(user_item[header[0]]))
                if col in self.CHECK_COLUMNS:
                    check_box = CheckBox(checked=user_item[header[0]])
                    check_box.check_activated.connect(self.item_check_changed)
                    self.setCellWidget(row, col, check_box)
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)

    # 初始化表格
    def _resetTableMode(self, row_count):
        self.clear()
        self.setRowCount(row_count)
        self.setColumnCount(len(self.KEY_LABELS) + 1)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + [''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(self.columnCount() - 1, QHeaderView.ResizeToContents)

    # 选择状态发生改变
    def item_check_changed(self, check_widget):
        row, column = self._get_widget_index(check_widget)
        user_id = self.item(row, 0).id
        print('改变id=%d的用户的为%s' % (user_id, '有效' if check_widget.check_box.isChecked() else '无效'))
        # 修改用户有效的请求
        try:
            r = requests.patch(
                url=settings.SERVER + 'user/' + str(user_id) + '/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({'is_active': check_widget.check_box.isChecked()})
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            self.network_result.emit(response['message'])

    # 获取控件所在行和列
    def _get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 用户管理页面
class UserManagePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(UserManagePage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 用户的类型选择与网络请求结果
        combo_message_layout = QHBoxLayout()
        self.role_combo = QComboBox()
        self.role_combo.activated.connect(self.getCurrentUsers)
        combo_message_layout.addWidget(self.role_combo, alignment=Qt.AlignLeft)
        self.network_message = QLabel()
        combo_message_layout.addWidget(self.network_message)
        layout.addLayout(combo_message_layout)
        # 用户表显示
        self.users_table = UsersTable()
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
                url=settings.SERVER + 'user/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value("AUTHORIZATION")},
                data=json.dumps(params)
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.show_network_message(str(e))
        else:
            self.users_table.setRowContents(response['data'])

    # 显示网络请求结果
    def show_network_message(self, message):
        self.network_message.setText(message)


# 运营管理主页
class OperationMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(OperationMaintain, self).__init__(*args, **kwargs)
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
