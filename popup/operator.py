# _*_ coding:utf-8 _*_
# __Author__： zizle
import re
import json
import requests
from PIL import Image
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import QWidget, QDialog, QGridLayout, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QLabel,\
    QComboBox, QTabWidget, QTableWidget, QTableWidgetItem, QDateEdit, QHeaderView, QTreeWidget, QTreeWidgetItem, QMenu,\
    QAction, QAbstractItemView, QListView, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QDate
from PyQt5.QtGui import QCursor
import settings
from widgets.operator import TableCheckBox
from popup.tips import InformationPopup, WarningPopup

__all__ = [
    'EditUserInformationPopup',
    'EditClientInformationPopup',
    'ModuleSubsInformationPopup',
    'EditVarietyInformationPopup',
    'CreateNewModulePopup',
    'CreateNewVarietyPopup'
]


# 有效期编辑控件
class TableDatetimeEdit(QWidget):
    edit_activated = pyqtSignal(QWidget)

    def __init__(self, date_text, *args, **kwargs):
        super(TableDatetimeEdit, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        layout.setContentsMargins(5,0,0,0)
        self.label_show = QLabel(date_text, parent=self)
        initial_day = QDate.fromString(self.label_show.text(), 'yyyy-MM-dd')
        self.date_edit = QDateEdit(initial_day, parent=self, objectName='dateEdit')
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.hide()
        self.edit_button = QPushButton('修改', parent=self, objectName='editButton', clicked=self.edit_date_time)
        self.edit_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.label_show)
        layout.addWidget(self.date_edit)
        layout.addWidget(self.edit_button, alignment=Qt.AlignRight)
        self.setLayout(layout)
        self.setStyleSheet("""
        #editButton{
            border:none;
            color: rgb(100,200,240);
        }
        #editButton:hover{
            color: rgb(240,200,100);
        }
        """)

    # 按钮点击修改有效期
    def edit_date_time(self):
        if self.date_edit.isHidden():
            self.edit_button.setText('设置')
            self.label_show.hide()
            self.date_edit.show()
        else:
            self.edit_button.setText('修改')
            # 读取时间，写入label
            date_str = self.date_edit.date().toString('yyyy-MM-dd')
            self.label_show.setText(date_str)
            self.label_show.show()
            self.date_edit.hide()
            # 传出信号，设置有效期
            self.edit_activated.emit(self)


""" 管理用户基础信息相关(编辑用户弹窗子集) """


# 用户基础信息
class UserBaseInfo(QWidget):
    def __init__(self, user_id, *args, **kwargs):
        super(UserBaseInfo, self).__init__(*args, **kwargs)
        self.user_id = user_id
        base_info_layout = QGridLayout()
        # 用户名
        base_info_layout.addWidget(QLabel('用户名/昵称:'), 0, 0)
        self.username_edit = QLineEdit()
        base_info_layout.addWidget(self.username_edit, 0, 1)
        base_info_layout.addWidget(QLabel(parent=self, objectName='usernameError'), 1, 0, 1, 2)
        # 手机
        base_info_layout.addWidget(QLabel('手机:'), 2, 0)
        self.phone_edit = QLineEdit()
        base_info_layout.addWidget(self.phone_edit, 2, 1)
        base_info_layout.addWidget(QLabel(parent=self, objectName='phoneError'), 3, 0, 1, 2)
        # 邮箱
        base_info_layout.addWidget(QLabel('邮箱:'), 4, 0)
        self.email_edit = QLineEdit()
        base_info_layout.addWidget(self.email_edit, 4, 1)
        base_info_layout.addWidget(QLabel(parent=self, objectName='emailError'), 5, 0, 1, 2)
        # 备注
        base_info_layout.addWidget(QLabel('备注：'), 6, 0)
        self.note_edit = QLineEdit()
        base_info_layout.addWidget(self.note_edit, 6, 1)
        base_info_layout.addWidget(QLabel(parent=self, objectName='noteError'), 7, 0, 1, 2)
        # 提交
        self.commit_button = QPushButton('确定', clicked=self.edit_user_info)
        base_info_layout.addWidget(self.commit_button, 8, 0, 1, 2)
        self.setLayout(base_info_layout)

    # 获取当前用户信息
    def getCurrentUser(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/' + str(self.user_id) + '/baseInfo/?mc=' + settings.app_dawn.value(
                    'machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            el = self.findChild(QLabel, 'noteError')
            el.setText(str(e))
        else:
            user_data = response['data']
            self.username_edit.setText(user_data['username'])
            self.phone_edit.setText(user_data['phone'])
            self.email_edit.setText(user_data['email'])
            self.note_edit.setText(user_data['note'])

    # 写入用户基础信息
    def edit_user_info(self):
        username = re.sub(r'\s+', '', self.username_edit.text())
        phone = re.match(r'^[1]([3-9])[0-9]{9}$', self.phone_edit.text())
        if not phone:
            self.findChild(QLabel, 'phoneError').setText('请输入正确的手机号！')
            return
        email = self.email_edit.text()
        if email:
            email = re.match(r'^\w+\@+[0-9a-zA-Z]+\.(com|com.cn|edu|hk|cn|net)$', email)
            if not email:
                self.findChild(QLabel, 'emailError').setText('请输入正确的邮箱！')
                return
            else:
                email = email.group()
        note = re.sub(r'\s+', '', self.note_edit.text())
        # 发起修改请求
        try:
            r = requests.patch(
                url=settings.SERVER_ADDR + 'user/' + str(self.user_id) + '/baseInfo/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'username': username,
                    'phone': phone.group(),
                    'email': email,
                    'note': note
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.findChild(QLabel, 'noteError').setText(str(e))
        else:
            self.findChild(QLabel, 'noteError').setText(response['message'])


""" 用户-客户端权限编辑相关(编辑用户弹窗子集) """


# 显示客户端的表格
class UserToClientTable(QTableWidget):
    network_message = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '名称'),
        ('machine_code', '机器码'),
        ('accessed', '可登录'),
        ('expire_date', '有效期'),
        ('category', '类型'),
    ]

    def __init__(self, user_id, *args, **kwargs):
        super(UserToClientTable, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.verticalHeader().hide()

    # 显示信息
    def showClientContents(self, client_list):
        self.clear()
        self.setRowCount(len(client_list))
        self.setColumnCount(len(self.KEY_LABELS))
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(self.columnCount() - 2, QHeaderView.ResizeToContents)
        for row, client_item in enumerate(client_list):
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = client_item['id']
                else:
                    table_item = QTableWidgetItem(str(client_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
                # 设置可登录的复选框
                if header[0] == 'accessed':
                    check_box = TableCheckBox(checked=client_item['accessed'])
                    check_box.check_activated.connect(self.item_check_changed)
                    self.setCellWidget(row, col, check_box)
                # 设置有效期编辑控件
                if header[0] == 'expire_date' and client_item['accessed']:
                    date_edit = TableDatetimeEdit(date_text=client_item['expire_date'])
                    date_edit.edit_activated.connect(self.set_expire_date)
                    self.setCellWidget(row, col, date_edit)
                    self.item(row, col).setText('')

    # 可登陆按钮发生改变
    def item_check_changed(self, check_widget):
        current_row, current_col = self._get_widget_index(check_widget)
        current_cid = self.item(current_row, 0).id
        checked = check_widget.check_box.isChecked()
        # 发起修改可登录状态
        params = {
            'accessed': checked,
            'client_id': current_cid,
            'expire_date': '3000-01-01',  # 默认有效期为3000-01-01
        }
        response = self._running_accessed_expire_date_request(params)
        if response:
            if checked:  # 可登录改变有效期控件显示
                expire_date = response['data']['expire_date']
                date_edit = TableDatetimeEdit(date_text=expire_date)
                date_edit.edit_activated.connect(self.set_expire_date)
                self.setCellWidget(current_row, current_col + 1, date_edit)
                self.horizontalHeader().setSectionResizeMode(current_col + 1, QHeaderView.ResizeToContents)
            else:
                self.removeCellWidget(current_row, current_col + 1)
            self.network_message.emit(response['message'])

    # 设置有效期(状态为可登录才有得设置)
    def set_expire_date(self, edit_widget):
        current_row, current_col = self._get_widget_index(edit_widget)
        expire_date = edit_widget.date_edit.date().toString('yyyy-MM-dd')
        current_cid = self.item(current_row, 0).id
        # 发起修改有效期
        params = {
            'expire_date': expire_date,
            'client_id': current_cid,
            'accessed': True  # 默认为可登录才能设置
        }
        response = self._running_accessed_expire_date_request(params)
        if response:
            # 将返回的有效期写入label
            edit_widget.label_show.setText(response['data']['expire_date'])
            self.network_message.emit(response['message'])

    # 获取控件所在行和列
    def _get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()

    # 发起可登录与有效期的设置请求
    def _running_accessed_expire_date_request(self, params):
        try:
            r = requests.patch(
                url=settings.SERVER_ADDR + 'user/' + str(self.user_id) + '/clients/?mc=' + settings.app_dawn.value(
                    'machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps(params)
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message.emit(str(e))
            return {}
        else:
            return response


# 客户端权限管理
class UserToClientEdit(QWidget):
    def __init__(self, user_id, *args, **kwargs):
        super(UserToClientEdit, self).__init__(*args, **kwargs)
        self.user_id = user_id
        layout = QVBoxLayout(margin=0)
        # 上方选择客户端类型与网络结果
        message_combo_layout = QHBoxLayout()
        self.network_message_label = QLabel('显示网络请求信息')
        message_combo_layout.addWidget(self.network_message_label, alignment=Qt.AlignLeft)
        self.category_combo = QComboBox()
        self.category_combo.activated.connect(self.getClients)
        message_combo_layout.addWidget(self.category_combo, alignment=Qt.AlignRight)
        layout.addLayout(message_combo_layout)
        # 下方客户端显示表格
        self.client_user_table = UserToClientTable(user_id=self.user_id)
        self.client_user_table.network_message.connect(self.network_message_label.setText)
        layout.addWidget(self.client_user_table)
        self.setLayout(layout)
        self._addCategoryCombo()

    # 填充类型选择
    def _addCategoryCombo(self):
        for combo_item in [('全部', 'all'), ('管理端', 'is_manager'), ('普通端', 'normal')]:
            self.category_combo.addItem(combo_item[0], combo_item[1])

    # 根据当前选择情况获取客户端信息
    def getClients(self):
        self.network_message_label.setText('')
        current_data = self.category_combo.currentData()
        params = {}
        if current_data == 'normal':
            params['is_manager'] = False
        elif current_data == 'is_manager':
            params['is_manager'] = True
        else:
            pass
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/' + str(self.user_id) + '/clients/?mc=' + settings.app_dawn.value(
                    'machine'),
                data=json.dumps(params)
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.network_message_label.setText(response['message'])
            # 显示客户端信息
            self.client_user_table.showClientContents(response['data'])


""" 用户-模块权限编辑相关(编辑用户弹窗子集) """


# 显示模块的表格
class UserToModuleTable(QTableWidget):
    network_message = pyqtSignal(str)
    KEY_LABELS = [
        ('id', '序号'),
        ('name', '名称'),
        ('accessed', '可进入'),
        ('expire_date', '有效期'),
    ]

    def __init__(self, user_id, *args, **kwargs):
        super(UserToModuleTable, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.verticalHeader().hide()

    # 显示模块信息
    def showModuleContents(self, module_list):
        self.clear()
        self.setRowCount(len(module_list))
        self.setColumnCount(len(self.KEY_LABELS))
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, module_item in enumerate(module_list):
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = module_item['id']
                else:
                    table_item = QTableWidgetItem(str(module_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
                # 设置可登录的复选框
                if header[0] == 'accessed':
                    check_box = TableCheckBox(checked=module_item['accessed'])
                    check_box.check_activated.connect(self.item_check_changed)
                    self.setCellWidget(row, col, check_box)
                # 设置有效期编辑控件
                if header[0] == 'expire_date' and module_item['accessed']:
                    date_edit = TableDatetimeEdit(date_text=module_item['expire_date'])
                    date_edit.edit_activated.connect(self.set_expire_date)
                    self.setCellWidget(row, col, date_edit)
                    self.item(row, col).setText('')

    # 可进入按钮发生改变
    def item_check_changed(self, check_box):
        current_row, current_col = self._get_widget_index(check_box)
        current_mid = self.item(current_row, 0).id
        checked = check_box.check_box.isChecked()
        # 发起修改可进入状态
        params = {
            'accessed': checked,
            'module_id': current_mid,
            'expire_date': '3000-01-01',  # 默认有效期为3000-01-01
        }
        response = self._running_accessed_expire_date_request(params)
        if response:
            if checked:  # 可登录改变有效期控件显示
                expire_date = response['data']['expire_date']
                date_edit = TableDatetimeEdit(date_text=expire_date)
                date_edit.edit_activated.connect(self.set_expire_date)
                self.setCellWidget(current_row, current_col + 1, date_edit)
            else:
                self.removeCellWidget(current_row, current_col + 1)
            self.network_message.emit(response['message'])

    # 设置有效期
    def set_expire_date(self, edit_widget):
        current_row, current_col = self._get_widget_index(edit_widget)
        expire_date = edit_widget.date_edit.date().toString('yyyy-MM-dd')
        current_mid = self.item(current_row, 0).id
        # 发起修改有效期
        params = {
            'expire_date': expire_date,
            'module_id': current_mid,
            'accessed': True  # 默认为可登录才能设置
        }
        response = self._running_accessed_expire_date_request(params)
        if response:
            # 将返回的有效期写入label
            edit_widget.label_show.setText(response['data']['expire_date'])
            self.network_message.emit(response['message'])

    # 获取控件所在行和列
    def _get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()

    # 发起可登录与有效期的设置请求
    def _running_accessed_expire_date_request(self, params):
        try:
            r = requests.patch(
                url=settings.SERVER_ADDR + 'user/' + str(self.user_id) + '/modules/?mc=' + settings.app_dawn.value(
                    'machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps(params)
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message.emit(str(e))
            return {}
        else:
            return response


# 模块权限管理
class UserToModuleEdit(QWidget):
    network_message = pyqtSignal(str)

    def __init__(self, user_id, *args, **kwargs):
        super(UserToModuleEdit, self).__init__(*args, **kwargs)
        self.user_id = user_id
        layout = QVBoxLayout(margin=0)
        # 模块权限管理表格
        self.module_user_table = UserToModuleTable(user_id=self.user_id)
        self.module_user_table.network_message.connect(self.network_message.emit)
        layout.addWidget(self.module_user_table)
        self.setLayout(layout)

    # 获取模块
    def getModules(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/' + str(self.user_id) + '/modules/?mc=' + settings.app_dawn.value(
                    'machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message.emit(str(e))
        else:
            self.network_message.emit(response['message'])
            self.module_user_table.showModuleContents(response['data'])


""" 用户-品种权限编辑相关(编辑用户弹窗子集) """


# 显示品种的表格
class UserToVarietyTable(QTableWidget):
    network_message = pyqtSignal(str)
    KEY_LABELS = [
        ('id', '序号'),
        ('name', '名称'),
        ('name_en', '英文代码'),
        ('accessed', '可操作'),
        ('expire_date', '有效期'),
        ('group', '所属组'),
    ]

    def __init__(self, user_id, *args, **kwargs):
        super(UserToVarietyTable, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.verticalHeader().hide()

    # 显示品种信息
    def showVarietyContents(self, variety_list):
        self.clear()
        self.setRowCount(len(variety_list))
        self.setColumnCount(len(self.KEY_LABELS))
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, variety_item in enumerate(variety_list):
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = variety_item['id']
                else:
                    table_item = QTableWidgetItem(str(variety_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
                # 设置可登录的复选框
                if header[0] == 'accessed':
                    check_box = TableCheckBox(checked=variety_item['accessed'])
                    check_box.check_activated.connect(self.item_check_changed)
                    self.setCellWidget(row, col, check_box)
                # 设置有效期编辑控件
                if header[0] == 'expire_date' and variety_item['accessed']:
                    date_edit = TableDatetimeEdit(date_text=variety_item['expire_date'])
                    date_edit.edit_activated.connect(self.set_expire_date)
                    self.setCellWidget(row, col, date_edit)
                    self.item(row, col).setText('')

    # 可操作选框发生改变
    def item_check_changed(self, check_box):
        current_row, current_col = self._get_widget_index(check_box)
        current_vid = self.item(current_row, 0).id
        checked = check_box.check_box.isChecked()
        # 发起修改可进入状态
        params = {
            'accessed': checked,
            'variety_id': current_vid,
            'expire_date': '3000-01-01',  # 默认有效期为3000-01-01
        }
        response = self._running_accessed_expire_date_request(params)
        if response:
            if checked:  # 可登录改变有效期控件显示
                expire_date = response['data']['expire_date']
                date_edit = TableDatetimeEdit(date_text=expire_date)
                date_edit.edit_activated.connect(self.set_expire_date)
                self.setCellWidget(current_row, current_col + 1, date_edit)
            else:
                self.removeCellWidget(current_row, current_col + 1)
            self.network_message.emit(response['message'])

    # 设置有效期
    def set_expire_date(self, edit_widget):
        current_row, current_col = self._get_widget_index(edit_widget)
        expire_date = edit_widget.date_edit.date().toString('yyyy-MM-dd')
        current_vid = self.item(current_row, 0).id
        # 发起修改有效期
        params = {
            'expire_date': expire_date,
            'variety_id': current_vid,
            'accessed': True  # 默认为可登录才能设置
        }
        response = self._running_accessed_expire_date_request(params)
        if response:
            # 将返回的有效期写入label
            edit_widget.label_show.setText(response['data']['expire_date'])
            self.network_message.emit(response['message'])

    # 获取控件所在行和列
    def _get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()

    # 发起可登录与有效期的设置请求
    def _running_accessed_expire_date_request(self, params):
        try:
            r = requests.patch(
                url=settings.SERVER_ADDR + 'user/' + str(self.user_id) + '/varieties/?mc=' + settings.app_dawn.value(
                    'machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps(params)
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message.emit(str(e))
            return {}
        else:
            return response


# 品种权限管理
class UserToVarietyEdit(QWidget):
    network_message = pyqtSignal(str)

    def __init__(self, user_id, *args, **kwargs):
        super(UserToVarietyEdit, self).__init__(*args, **kwargs)
        self.user_id = user_id
        layout = QVBoxLayout(margin=0)
        # 上方选择品种组与网络结果
        message_combo_layout = QHBoxLayout()
        self.network_message_label = QLabel('显示网络请求信息')
        message_combo_layout.addWidget(self.network_message_label, alignment=Qt.AlignLeft)
        self.variety_group_combo = QComboBox(activated=self.getCurrentVarieties)
        message_combo_layout.addWidget(self.variety_group_combo, alignment=Qt.AlignRight)
        layout.addLayout(message_combo_layout)
        # 下方品种显示表格
        self.variety_user_table = UserToVarietyTable(user_id=self.user_id)
        self.variety_user_table.network_message.connect(self.network_message_label.setText)
        layout.addWidget(self.variety_user_table)
        self.setLayout(layout)

    # 获取品种分组并加上【全部】
    def getVarietyGroups(self):
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
            self.variety_group_combo.addItem('全部', 0)
            for group_item in response['data']:
                self.variety_group_combo.addItem(group_item['name'], group_item['id'])
            self.network_message_label.setText(response['message'])

    # 获取当前品种
    def getCurrentVarieties(self):
        current_gid = self.variety_group_combo.currentData()
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/' + str(self.user_id) + '/varieties/?mc=' + settings.app_dawn.value('machine'),
                data=json.dumps({'group_id': current_gid})
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.variety_user_table.showVarietyContents(response['data'])
            self.network_message_label.setText(response['message'])


""" 运营管理-【编辑】用户信息 """


# 编辑用户信息
class EditUserInformationPopup(QDialog):
    def __init__(self, user_id, *args, **kwargs):
        super(EditUserInformationPopup, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.setWindowTitle('编辑用户')
        # 布局
        layout = QVBoxLayout(margin=0)
        # 编辑的功能选择与信息显示的布局
        select_message_layout = QHBoxLayout()
        self.edit_select = QComboBox(parent=self)
        self.edit_select.activated.connect(self.selected_edit_state)
        select_message_layout.addWidget(self.edit_select)
        self.network_message_label = QLabel('显示信息使用')
        select_message_layout.addWidget(self.network_message_label)
        select_message_layout.addStretch()
        layout.addLayout(select_message_layout)
        # 显示的stackedWidget
        self.tab_show = QTabWidget(parent=self)
        self.tab_show.tabBar().hide()
        self.tab_show.setDocumentMode(True)
        layout.addWidget(self.tab_show)
        self.setLayout(layout)
        self.setFixedSize(750, 360)
        self._addComboItems()

    # 获取选择选项
    def _addComboItems(self):
        for item_data in [('基础信息', 'base_info'), ('客户端权限', 'client'), ('模块权限', 'module'), ('品种权限', 'variety')]:
            self.edit_select.addItem(item_data[0], item_data[1])

    # 选择编辑的类型
    def selected_edit_state(self):
        self.network_message_label.setText('')  # 清除信息显示，否则模块权限显示的消息会一直显示
        current_text = self.edit_select.currentData()
        self.tab_show.clear()
        if current_text == 'base_info':  # 基础信息管理
            tab = UserBaseInfo(user_id=self.user_id)
            tab.getCurrentUser()
        elif current_text == 'client':  # 客户端权限管理
            tab = UserToClientEdit(user_id=self.user_id)
            tab.getClients()
        elif current_text == 'module':  # 系统模块权限管理
            tab = UserToModuleEdit(user_id=self.user_id)
            tab.network_message.connect(self.network_message_label.setText)
            tab.getModules()
        elif current_text == 'variety':  # 品种权限管理
            tab = UserToVarietyEdit(user_id=self.user_id)
            tab.getVarietyGroups()
            tab.getCurrentVarieties()
        else:
            tab = QLabel('暂无相关维护')
        self.tab_show.addTab(tab, '')


""" 运营管理-【编辑】客户端信息 """


class EditClientInformationPopup(QDialog):
    def __init__(self, client_id, *args, **kwargs):
        super(EditClientInformationPopup, self).__init__(*args, **kwargs)
        self.setWindowTitle('编辑客户端')
        self.client_id = client_id
        layout = QGridLayout()
        layout.addWidget(QLabel('名称:'), 0, 0)
        # 名称
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit, 0, 1)
        layout.addWidget(QLabel(parent=self, objectName='nameError'), 1, 0, 1, 2)
        # 机器码
        layout.addWidget(QLabel('机器码:'), 2, 0)
        self.machine_code_edit = QLineEdit()
        layout.addWidget(self.machine_code_edit, 2, 1)
        layout.addWidget(QLabel(parent=self, objectName='machineError'), 3, 0, 1, 2)
        # 确定按钮
        self.commit_button = QPushButton('确定提交', clicked=self.edit_client_info)
        layout.addWidget(self.commit_button, 4, 0, 1, 2)
        self.setLayout(layout)
        self.setFixedSize(330,180)

    # 获取当前用户信息
    def getCurrentClient(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'client/' + str(self.client_id) + '/?mc=' + settings.app_dawn.value(
                    'machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            el = self.findChild(QLabel, 'machineError')
            el.setText(str(e))
        else:
            client_data = response['data']
            self.name_edit.setText(client_data['name'])
            self.machine_code_edit.setText(client_data['machine_code'])

    # 提交客户端信息
    def edit_client_info(self):
        name = re.sub(r'\s+', '', self.name_edit.text())
        machine_code = re.match(r'[a-f0-9]+', self.machine_code_edit.text())
        if not machine_code:
            el = self.findChild(QLabel, 'machineError')
            el.setText('请输入正确的机器码.')
            return
        machine_code = machine_code.group()
        # 发起请求
        try:
            r = requests.patch(
                url=settings.SERVER_ADDR + 'client/' + str(self.client_id) + '/?mc=' + settings.app_dawn.value(
                    'machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'name': name,
                    'machine_code': machine_code
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.findChild(QLabel, 'machineError').setText(str(e))
        else:
            self.findChild(QLabel, 'machineError').setText(response['message'])


""" 运营管理-【查看】子模块信息 """


# 子模块信息
class ModuleSubsInformationPopup(QDialog):
    def __init__(self, parent_id, parent_name, module_subs, *args, **kwargs):
        super(ModuleSubsInformationPopup, self).__init__(*args, **kwargs)
        self.setWindowTitle(parent_name + '-子模块')
        self.parent_id = parent_id
        self.module_subs = module_subs
        layout = QVBoxLayout()
        self.module_table = QTableWidget()
        self.module_table.verticalHeader().hide()
        self.module_table.setFocusPolicy(Qt.NoFocus)
        self.module_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.module_table.cellClicked.connect(self.cell_clicked)
        layout.addWidget(self.module_table)
        self.setLayout(layout)

        # layout = QGridLayout()
        # layout.addWidget(QLabel('名称:'), 0, 0)
        # self.name_edit = QLineEdit()
        # layout.addWidget(self.name_edit, 0, 1)
        # layout.addWidget(QLabel(parent=self, objectName='nameError'), 1, 0, 1, 2)
        # self.commit_button = QPushButton('确认提交', clicked=self.edit_module_info)
        # layout.addWidget(self.commit_button, 2, 1)
        # self.setLayout(layout)
        self.setFixedSize(500, 400)
        self.show_module_subs()

    # 显示子模块
    def show_module_subs(self):
        self.module_table.clear()
        self.module_table.setRowCount(len(self.module_subs))
        self.module_table.setColumnCount(4)
        self.module_table.setHorizontalHeaderLabels(['序号', '名称', '有效', '排序'])
        self.module_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.module_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, sub_module_item in enumerate(self.module_subs):
            item1 = QTableWidgetItem(str(row + 1))
            item1.setTextAlignment(Qt.AlignCenter)
            item1.module_id = sub_module_item['id']
            self.module_table.setItem(row, 0, item1)
            item2 = QTableWidgetItem(str(sub_module_item['name']))
            item2.setTextAlignment(Qt.AlignCenter)
            self.module_table.setItem(row, 1, item2)
            item3 = TableCheckBox(checked=sub_module_item['is_active'])
            item3.check_activated.connect(self.check_box_changed)
            self.module_table.setCellWidget(row, 2, item3)
            item4 = QTableWidgetItem("上移")
            item4.setTextAlignment(Qt.AlignCenter)
            self.module_table.setItem(row, 3, item4)

    # 有效信息发生变化
    def check_box_changed(self, check_box):
        current_row, current_col = self.get_widget_index(check_box)
        module_id = self.module_table.item(current_row, 0).module_id
        for sub_module in self.module_subs:
            if sub_module['id'] == module_id:
                sub_module['is_active'] = 1 if check_box.check_box.isChecked() else 0
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
            pass

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.module_table.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()

    # 点击排序
    def cell_clicked(self, row, col):
        if col == 3:
            if row == 0:
                return
            current_item_id = self.module_table.item(row, 0).module_id
            up_item_id = self.module_table.item(row -1, 0).module_id
            # 发起请求
            try:  # 发起请求
                r = requests.patch(
                    url=settings.SERVER_ADDR + 'module/?mc=' + settings.app_dawn.value('machine'),
                    headers={"AUTHORIZATION": settings.app_dawn.value('AUTHORIZATION')},
                    data=json.dumps({"current_id": current_item_id, "replace_id": up_item_id})
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 200:
                    raise ValueError(response['message'])
            except Exception as e:
                pass
            else:
                new_module_data = response['data']
                # 加入两行
                self.module_table.insertRow(row)
                self.module_table.insertRow(row)
                # 原两行删除
                self.module_table.removeRow(row + 2)
                self.module_table.removeRow(row - 1)
                # 新数据填入行 row-1, row
                for index, module_item in enumerate(new_module_data):
                    index = row - 1 if not index else row
                    item1 = QTableWidgetItem(str(index + 1))
                    item1.setTextAlignment(Qt.AlignCenter)
                    item1.module_id = module_item['id']
                    self.module_table.setItem(index, 0, item1)
                    item2 = QTableWidgetItem(str(module_item['name']))
                    item2.setTextAlignment(Qt.AlignCenter)
                    self.module_table.setItem(index, 1, item2)
                    item3 = TableCheckBox(checked=module_item['is_active'])
                    item3.check_activated.connect(self.check_box_changed)
                    self.module_table.setCellWidget(index, 2, item3)
                    item4 = QTableWidgetItem("上移")
                    item4.setTextAlignment(Qt.AlignCenter)
                    self.module_table.setItem(index, 3, item4)


""" 运营管理-【新增模块】"""


# 新增模块
class CreateNewModulePopup(QDialog):
    def __init__(self, module_combo, *args, **kwargs):
        super(CreateNewModulePopup, self).__init__(*args, **kwargs)
        self.setWindowTitle('新增模块')
        self.setMaximumSize(300,150)
        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QGridLayout()
        layout.addWidget(QLabel('名称:'), 0, 0)
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit, 0, 1)
        layout.addWidget(QLabel(''), 1, 0)  # 占位
        # 附属
        layout.addWidget(QLabel('附属:'), 2, 0)
        self.attach_combo = QComboBox()
        # 添加选项
        self.attach_combo.addItem('无', None)
        for module_item in module_combo:
            self.attach_combo.addItem(module_item['name'], module_item['id'])
        layout.addWidget(self.attach_combo, 2, 1)
        layout.addWidget(QLabel(parent=self, objectName='nameError'), 3, 0, 1, 2)
        self.commit_button = QPushButton('确认提交', clicked=self.commit_new_module)
        layout.addWidget(self.commit_button, 4, 1)
        self.setLayout(layout)

    # 提交新增模块
    def commit_new_module(self):
        name = re.sub(r'\s+', '', self.name_edit.text())
        if not name:
            self.findChild(QLabel, 'nameError').setText('请输入模块名称!')
            return
        parent = self.attach_combo.currentData()
        print(parent)
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'module/',
                headers={'Content-Type': 'application/json;charset=utf8'},
                data=json.dumps({
                    'module_name': name,
                    'parent_id': parent,
                    'utoken': settings.app_dawn.value('AUTHORIZATION')
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.findChild(QLabel, 'nameError').setText(str(e))
        else:
            self.network_message.setText(response['message'])


""" 运营管理-【新增品种】 """


# 弹窗新增分组-新增品种弹窗的子弹窗
class CreateNewVarietyGroup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateNewVarietyGroup, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        layout.addWidget(QLabel('组名称:'), 0, 0)
        self.group_edit = QLineEdit()
        layout.addWidget(self.group_edit, 0, 1)
        layout.addWidget(QLabel(parent=self, objectName='groupNameError'), 1, 0, 1, 2)
        self.commit_button = QPushButton('确定提交', clicked=self.commit_new_group)
        layout.addWidget(self.commit_button, 2, 1)
        self.setLayout(layout)
        self.setWindowTitle('新建组')

    # 提交新品种组
    def commit_new_group(self):
        name = re.sub(r'\s+', '', self.group_edit.text())
        if not name:
            self.findChild(QLabel, 'groupNameError').setText('请输入正确的组名称!')
            return
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'group-varieties/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({'name': name})
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            self.findChild(QLabel, 'groupNameError').setText(str(e))
        else:
            self.findChild(QLabel, 'groupNameError').setText(response['message'])


# 品种的分组树
class VarietyGroupTree(QTreeWidget):
    # 仅触发右击事件，左键事件依然保持原来的
    def contextMenuEvent(self, event, *args, **kwargs):
        point = event.pos()
        current_item = self.itemAt(point)
        # 没有父级的item
        if not current_item.parent():
            popup_menu = QMenu(self)
            popup_menu.clear()
            popup_menu.addAction(QAction('删除', self, triggered=self.delete_variety_group))
            popup_menu.exec_(QCursor.pos())
        event.accept()

    # 删除品种组
    def delete_variety_group(self, checked):
        def confirm_delete():
            current_item = self.currentItem()
            machine_code = settings.app_dawn.value('machine')
            try:
                r = requests.delete(
                    url=settings.SERVER_ADDR + 'group-varieties/' + str(current_item.gid) + '/?mc=' + machine_code,
                    headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')}
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 200:
                    raise ValueError(response['message'])
            except Exception as e:
                popup = InformationPopup(message=str(e), parent=warning)
                if not popup.exec_():
                    popup.deleteLater()
                    del popup
            else:
                popup = InformationPopup(message='删除成功!', parent=warning)
                if not popup.exec_():
                    popup.deleteLater()
                    del popup
                self.takeTopLevelItem(self.currentIndex().row())
            warning.close()
        warning = WarningPopup(message='确定删除此组及其下品种？\n此组下所有品种相关的所有数据将被清除且不可恢复!', parent=self)
        warning.confirm_button.connect(confirm_delete)
        if not warning.exec_():
            warning.deleteLater()
            del warning


# 弹窗新增品种主页
class CreateNewVarietyPopup(QDialog):
    def __init__(self, groups, *args, **kwargs):
        super(CreateNewVarietyPopup, self).__init__(*args, **kwargs)
        self.setFixedSize(300, 200)
        self.setWindowTitle("新增品种")
        layout = QGridLayout()
        layout.setParent(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        # 填写名称
        layout.addWidget(QLabel('名称:',self), 0, 0)
        self.name_edit = QLineEdit(self)
        layout.addWidget(self.name_edit, 0, 1)
        # 填写英文代码
        layout.addWidget(QLabel('代码:',self), 1, 0)
        self.name_en_edit = QLineEdit(self)
        layout.addWidget(self.name_en_edit, 1, 1)
        # 选择分组
        layout.addWidget(QLabel('分组:', self), 2,0)
        self.group_combobox = QComboBox(self)
        for group_item in groups:
            self.group_combobox.addItem(group_item[1], group_item[0])
        layout.addWidget(self.group_combobox, 2, 1)
        # 交易所
        layout.addWidget(QLabel('交易所:', self), 3, 0)
        self.exchange_combobox = QComboBox(self)
        for exchange_item in [
            (1, "郑州商品交易所"), (2, '上海期货交易所'),
            (3, '大连商品交易所'), (4, '中国金融期货交易所'),
            (5, '上海国际能源交易中心')
        ]:
            self.exchange_combobox.addItem(exchange_item[1], exchange_item[0])
        layout.addWidget(self.exchange_combobox, 3,1)

        self.commit_button = QPushButton("提交", self)
        self.commit_button.clicked.connect(self.commit_new_variety)
        layout.addWidget(self.commit_button, 4, 0, 1, 2)
        self.setLayout(layout)



        # layout = QHBoxLayout()
        # # 左侧上下布局
        # llayout = QVBoxLayout()
        # # 左侧分组树
        # self.group_tree = VarietyGroupTree(clicked=self.group_tree_clicked, objectName='groupTree')
        #
        # self.group_tree.header().hide()
        # self.group_tree.setFixedWidth(200)
        # llayout.addWidget(self.group_tree)
        # llayout.addWidget(QPushButton('新建组别', clicked=self.create_new_group), alignment=Qt.AlignLeft)
        # # 右侧显示新建页
        # rlayout = QVBoxLayout()
        # new_variety_layout = QGridLayout()
        # # 所属分组
        # new_variety_layout.addWidget(QLabel('所属分组:'), 0, 0)
        # self.attach_group = QLabel()
        # self.attach_group.gid = None  # 绑定所属组，便于提交时分辨
        # new_variety_layout.addWidget(self.attach_group, 0, 1)
        # new_variety_layout.addWidget(QLabel(parent=self, objectName='groupNameError'), 1, 0, 1, 2)
        # # 品种名称
        # new_variety_layout.addWidget(QLabel('品种名称:'), 2, 0)
        # self.variety_edit = QLineEdit()
        # new_variety_layout.addWidget(self.variety_edit, 2, 1)
        # new_variety_layout.addWidget(QLabel(parent=self, objectName='varietyEditError'), 3, 0, 1, 2)
        # # 品种英文代码
        # new_variety_layout.addWidget(QLabel('英文代码:'), 4, 0)
        # self.variety_en_edit = QLineEdit()
        # new_variety_layout.addWidget(self.variety_en_edit, 4, 1)
        # new_variety_layout.addWidget(QLabel(parent=self, objectName='varietyEnEditError'), 5, 0, 1, 2)
        # # 品种所属的交易所
        # new_variety_layout.addWidget(QLabel("交易所:"), 6, 0)
        # self.exchange_combo = QComboBox(objectName='exchangeCombo')
        # # 增加选项
        # for exchange_item in [
        #     (1, "郑州商品交易所"), (2, '上海期货交易所'),
        #     (3, '大连商品交易所'), (4, '中国金融期货交易所'),
        #     (5, '上海国际能源交易中心')
        # ]:
        #     self.exchange_combo.addItem(exchange_item[1], exchange_item[0])
        # new_variety_layout.addWidget(self.exchange_combo, 6, 1)
        # # 占位
        # new_variety_layout.addWidget(QLabel(' '), 7, 0)
        # # 提交按钮
        # self.commit_button = QPushButton('确认提交', clicked=self.commit_new_variety)
        # new_variety_layout.addWidget(self.commit_button, 8, 1)
        # rlayout.addLayout(new_variety_layout)
        # # 说明
        # rlayout.addWidget(QLabel(
        #     text='\n1.左侧选择要在哪个组下创建品种。\n\n2.键入新增品种信息-提交。\n\n3.如需新建大组,请点击左侧【新建组别】',
        #     styleSheet='color:rgb(100,160,120);font-size:15px'
        # ))
        # rlayout.addStretch()
        #
        # layout.addLayout(llayout)
        # layout.addLayout(rlayout)
        # self.setLayout(layout)
        # self.setWindowTitle('新增品种')
        # self.setFixedSize(600, 405)
        # self.setStyleSheet("""
        # #groupTree::item{
        #     height:20px;
        # }
        # #exchangeCombo{
        #     border: 1px solid rgb(240, 240, 240);
        #     color: rgb(7,99,109);
        # }
        # #exchangeCombo QAbstractItemView::item{
        #     height:20px;
        # }
        # #exchangeCombo::drop-down{
        #     border: 0px;
        # }
        # #exchangeCombo::down-arrow{
        #     image:url("media/more.png");
        #     width: 15px;
        #     height:15px;
        # }
        # """)
        # self.exchange_combo.setView(QListView())

    # 获取分组和每个分组下的品种
    def getGroupWithVarieties(self):
        self.group_tree.clear()
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'group-varieties/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
        except Exception:
            return
        # 填充品种树
        for group_item in response['data']:
            group = QTreeWidgetItem(self.group_tree)
            group.setText(0, group_item['name'])
            group.gid = group_item['id']
            # 添加子节点
            for variety_item in group_item['varieties']:
                child = QTreeWidgetItem()
                child.setText(0, variety_item['name'])
                child.vid = variety_item['id']
                group.addChild(child)
        self.group_tree.expandAll()  # 展开所有

    # 分组树点击
    def group_tree_clicked(self, event):
        item = self.group_tree.currentItem()
        if item.childCount():  # has children open the root
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        text = item.text(0)
        if item.parent():
            # 提示只能在大类下创建品种
            el = self.findChild(QLabel, 'groupNameError')
            el.setText('只能在分组下新增品种,如需新建,请点击左下角【新建组别】')
            self.commit_button.setEnabled(False)
        else:
            # 该品种所属分组
            self.attach_group.setText(text)
            self.attach_group.gid = item.gid
            # 清除提示消息
            el = self.findChild(QLabel, 'groupNameError')
            el.setText('')
            self.commit_button.setEnabled(True)

    # 新增品种
    def commit_new_variety(self):
        new_name = self.name_edit.text().strip()
        new_name_en = self.name_en_edit.text().strip()
        group_id = self.group_combobox.currentData()
        exchange = self.exchange_combobox.currentData()
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'variety/',
                headers={'Content-Type': 'application/json;charset=utf8'},
                data=json.dumps({
                    'variety_name': new_name,
                    "variety_name_en": new_name_en,
                    "parent_num": group_id,
                    "exchange_num": exchange,
                    "utoken": settings.app_dawn.value('AUTHORIZATION')
                })
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, "错误", "新增品种错误!")
        else:
            QMessageBox.information(self, "成功", response['message'])
            self.close()

    #
    # if not self.attach_group.gid:
    #         self.findChild(QLabel, 'groupNameError').setText('请选择新品种所属的分组!')
    #         return
    #     name = re.sub(r'\s+', '', self.variety_edit.text())
    #     if not name:
    #         self.findChild(QLabel, 'varietyEditError').setText('请输入正确的品种名称!')
    #         return
    #
    #     name_en = re.match(r'[a-zA-Z0-9]+', self.variety_en_edit.text())
    #     if not name_en:
    #         self.findChild(QLabel, 'varietyEnEditError').setText('请输入正确的品种英文代码!')
    #         return
    #     name_en = name_en.group()
    #     # 所属交易所
    #     exchange_lib_id = self.exchange_combo.currentData()
    #     # 提交
    #     try:
    #         r = requests.post(
    #             url=settings.SERVER_ADDR + 'group-varieties/'+str(self.attach_group.gid)+'/?mc=' + settings.app_dawn.value('machine'),
    #             headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
    #             data=json.dumps({
    #                 'name': name,
    #                 'name_en': name_en,
    #                 'exchange_lib': exchange_lib_id
    #             })
    #         )
    #         response = json.loads(r.content.decode('utf-8'))
    #         if r.status_code != 201:
    #             raise ValueError(response['message'])
    #     except Exception as e:
    #         self.findChild(QLabel, 'varietyEnEditError').setText(str(e))
    #     else:
    #         self.findChild(QLabel, 'varietyEnEditError').setText(response['message'])
    #         self.getGroupWithVarieties()




    # 新建分组
    def create_new_group(self):
        popup = CreateNewVarietyGroup(parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup
            # 刷新分组
            self.getGroupWithVarieties()


"""广告设置相关"""


class FilePathLineEdit(QLineEdit):
    def __init__(self,*args):
        super(FilePathLineEdit, self).__init__(*args)
        self.setReadOnly(True)

    def mousePressEvent(self, event):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择文件', '', "PDF files(*.pdf)")
        self.setText(file_path)


class ImagePathLineEdit(QLineEdit):
    def __init__(self,*args):
        super(ImagePathLineEdit, self).__init__(*args)
        self.setReadOnly(True)

    def mousePressEvent(self, event):
        image_path, _ = QFileDialog.getOpenFileName(self, '选择图片', '', "image PNG(*.png)")
        if image_path:
            # 对文件的大小进行限制
            img = Image.open(image_path)
            if 520 <= img.size[0] <= 660 and 260 <= img.size[1] <= 330:
                self.setText(image_path)
            else:
                QMessageBox.information(self, "提示", '图片像素大小范围:520~660;高:260~330')


# 新增广告
class CreateAdvertisementPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateAdvertisementPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFixedSize(350, 200)
        self.setWindowTitle("新建广告")
        layout = QGridLayout()
        layout.setParent(self)
        layout.addWidget(QLabel("标题:", self), 0, 0)
        self.title_edit = QLineEdit(self)
        layout.addWidget(self.title_edit, 0, 1)
        layout.addWidget(QLabel("图片:", self), 1, 0)
        self.image_path_edit = ImagePathLineEdit(self)
        layout.addWidget(self.image_path_edit, 1, 1)
        layout.addWidget(QLabel('文件:', self), 2, 0)
        self.file_path_edit = FilePathLineEdit(self)
        layout.addWidget(self.file_path_edit, 2, 1)
        self.commit_button = QPushButton("提交", self)
        self.commit_button.clicked.connect(self.commit_new_advertisement)
        layout.addWidget(self.commit_button, 3, 0, 1, 2)
        self.setLayout(layout)

    def commit_new_advertisement(self):
        self.commit_button.setEnabled(False)
        # 获取上传的类型
        title = re.sub(r'\s+', '', self.title_edit.text())
        if not title:
            QMessageBox.information(self, "错误", "标题不能为空!")
            return
        if not all([self.file_path_edit.text(), self.image_path_edit.text()]):
            QMessageBox.information(self, "错误", "请设置广告图片和内容文件")
            return
        data = dict()
        data['ad_title'] = title  # 标题
        data['utoken'] = settings.app_dawn.value('AUTHORIZATION')
        image = open(self.image_path_edit.text(), 'rb')
        image_content = image.read()
        image.close()
        data['ad_image'] = ("ad_image.png", image_content)
        file = open(self.file_path_edit.text(), "rb")  # 获取文件
        file_content = file.read()
        file.close()
        # 文件内容字段
        data["ad_file"] = ("ad_file.pdf", file_content)
        encode_data = encode_multipart_formdata(data)
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'ad/',
                headers={
                    'Content-Type': encode_data[1]
                },
                data=encode_data[0]
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, "失败", '上传新广告信息失败!')
        else:
            QMessageBox.information(self, "成功", '上传新广告信息成功!')
        finally:
            self.commit_button.setEnabled(True)
            self.close()

        #
        #
        # layout = QVBoxLayout()
        # category_select_layout = QHBoxLayout()
        # category_select_layout.addWidget(QLabel('显示类型:'), alignment=Qt.AlignLeft)
        # self.category_combo = QComboBox(currentIndexChanged=self.category_combo_selected)
        # category_select_layout.addWidget(self.category_combo)
        # # 错误提示
        # self.error_message_label = QLabel()
        # category_select_layout.addWidget(self.error_message_label)
        # category_select_layout.addStretch()
        # layout.addLayout(category_select_layout)
        # # 广告名称
        # title_layout = QHBoxLayout()
        # title_layout.addWidget(QLabel('广告名称:'))
        # self.advertisement_name_edit = QLineEdit()
        # title_layout.addWidget(self.advertisement_name_edit)
        # layout.addLayout(title_layout)
        # # 广告图片
        # image_layout = QHBoxLayout()
        # image_layout.addWidget(QLabel('广告图片:'))
        # self.advertisement_image_edit = QLineEdit()
        # self.advertisement_image_edit.setEnabled(False)
        # image_layout.addWidget(self.advertisement_image_edit)
        # image_layout.addWidget(QPushButton('浏览', clicked=self.browser_image))
        # layout.addLayout(image_layout)
        # # 文件选择
        # self.file_widget = QWidget(parent=self)
        # file_widget_layout = QHBoxLayout(margin=0)
        # self.file_path_edit = QLineEdit()
        # self.file_path_edit.setEnabled(False)
        # file_widget_layout.addWidget(QLabel('广告文件:'), alignment=Qt.AlignLeft)
        # file_widget_layout.addWidget(self.file_path_edit)
        # file_widget_layout.addWidget(QPushButton('浏览', clicked=self.browser_file))
        # self.file_widget.setLayout(file_widget_layout)
        # layout.addWidget(self.file_widget)
        # # 文字输入
        # self.text_widget = QWidget(parent=self)
        # text_widget_layout = QHBoxLayout(margin=0)
        # self.text_edit = QTextEdit()
        # text_widget_layout.addWidget(QLabel('广告内容:'), alignment=Qt.AlignLeft)
        # text_widget_layout.addWidget(self.text_edit)
        # self.text_widget.setLayout(text_widget_layout)
        # layout.addWidget(self.text_widget)
        # # 提交按钮
        # self.commit_button = QPushButton('确认提交', clicked=self.commit_advertisement)
        # layout.addWidget(self.commit_button)
        # layout.addStretch()
        # self.setWindowTitle('新增广告')
        # self.setLayout(layout)
        # self._addCategoryCombo()


""" 运营管理-【编辑】品种信息 """


class EditVarietyInformationPopup(QDialog):
    def __init__(self, variety_id, *args, **kwargs):
        super(EditVarietyInformationPopup, self).__init__(*args, **kwargs)
        self.setWindowTitle('编辑品种')
        self.variety_id = variety_id
        layout = QGridLayout()
        # 名称
        layout.addWidget(QLabel('名称:'), 0, 0)
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit, 0, 1)
        layout.addWidget(QLabel(parent=self, objectName='nameError'), 1, 0, 1, 2)
        # 英文代码
        layout.addWidget(QLabel('英文代码:'), 2, 0)
        self.name_en_edit = QLineEdit()
        layout.addWidget(self.name_en_edit, 2, 1)
        layout.addWidget(QLabel(parent=self, objectName='nameEnError'), 3, 0, 1, 2)
        # 所属分组
        layout.addWidget(QLabel('所属组:'), 4, 0)
        self.attach_group = QComboBox(objectName='exchangeCombo')
        layout.addWidget(self.attach_group, 4, 1)
        layout.addWidget(QLabel(parent=self, objectName='attachGroupError'), 5, 0, 1, 2)
        # 交易所
        layout.addWidget(QLabel('交易所:'), 6, 0)
        self.attach_exchange = QComboBox(objectName='exchangeCombo')
        # 增加选项
        for exchange_item in [
            (1, "郑州商品交易所"), (2, '上海期货交易所'),
            (3, '大连商品交易所'), (4, '中国金融期货交易所'),
            (5, '上海国际能源交易中心')
        ]:
            self.attach_exchange.addItem(exchange_item[1], exchange_item[0])
        layout.addWidget(self.attach_exchange, 6, 1)
        layout.addWidget(QLabel(parent=self, objectName='attachExchangeError'), 7, 0, 1, 2)  # 占位
        # 提交
        self.commit_button = QPushButton('确认提交', clicked=self.edit_variety_info)
        layout.addWidget(self.commit_button, 8, 0, 1, 2)
        self.setLayout(layout)
        self.setStyleSheet("""
            #exchangeCombo{
                border: 1px solid rgb(240, 240, 240);
                color: rgb(7,99,109);
            }
            #exchangeCombo QAbstractItemView::item{
                height:20px;
            }
            #exchangeCombo::drop-down{
                border: 0px;
            }
            #exchangeCombo::down-arrow{
                image:url("media/more.png");
                width: 15px;
                height:15px;
            }
            """)
        self.setMinimumWidth(350)
        self.attach_exchange.setView(QListView())
        self.attach_group.setView(QListView())

    # 获取当前品种信息
    def getCurrentVariety(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'variety/' + str(self.variety_id) + '/?mc=' + settings.app_dawn.value(
                    'machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.findChild(QLabel, 'attachGroupError').setText(str(e))
        else:
            variety_data = response['data']
            # print(variety_data)
            self.name_edit.setText(variety_data['name'])
            self.name_en_edit.setText(variety_data['name_en'])
            # 设置所属组选项
            for group_item in variety_data['all_groups']:
                self.attach_group.addItem(group_item['name'], group_item['id'])
                if variety_data['group'] == group_item['name']:
                    self.attach_group.setCurrentText(group_item['name'])
            # 设置所属交易所选项
            exchange_lib = {
                1: "郑州商品交易所",
                2: "上海期货交易所",
                3: "大连商品交易所",
                4: "中国金融期货交易所",
                5: "上海国际能源交易中心"
            }
            current_exchange = exchange_lib[variety_data['exchange']]
            self.attach_exchange.setCurrentText(current_exchange)

    # 修改品种信息
    def edit_variety_info(self):
        name = re.sub(r'\s+', '', self.name_edit.text())
        if not name:
            self.findChild(QLabel, 'nameError').setText('请输入品种名称!')
            return
        name_en = re.match(r'[a-zA-Z0-9]+', self.name_en_edit.text())
        if not name_en:
            self.findChild(QLabel, 'nameEnError').setText('请输入正确品种英文代码!')
            return
        name_en = name_en.group()
        attach_group_id = self.attach_group.currentData()
        exchange_id = self.attach_exchange.currentData()
        try:
            r = requests.put(
                url=settings.SERVER_ADDR + 'variety/' + str(self.variety_id) + '/?mc=' + settings.app_dawn.value(
                    'machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'name': name,
                    'name_en': name_en,
                    'group_id': int(attach_group_id),
                    'exchange': int(exchange_id)
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.findChild(QLabel, 'attachExchangeError').setText(str(e))
        else:
            self.findChild(QLabel, 'attachExchangeError').setText(response['message'])