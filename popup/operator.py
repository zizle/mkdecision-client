# _*_ coding:utf-8 _*_
# __Author__： zizle
import re
import json
import requests
from PyQt5.QtWidgets import QWidget, QDialog, QGridLayout, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, \
    QTabWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
import settings


""" 管理用户具体信息相关 """
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
        # 获取用户信息
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
            print(response)
        except Exception as e:
            print(e)
            self.findChild(QLabel, 'noteError').setText(str(e))
        else:
            self.findChild(QLabel, 'noteError').setText(response['message'])


""" 用户客户端权限编辑相关 """


class UserToClientTable(QTableWidget):
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
        print(client_list)
        self.setRowCount(len(client_list))
        self.setColumnCount(len(self.KEY_LABELS))
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS])
        for row, client_item in enumerate(client_list):
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = client_item['id']
                else:
                    table_item = QTableWidgetItem(str(client_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)


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


# 编辑用户信息
class EditUserInformationPopup(QDialog):
    def __init__(self, user_id, *args, **kwargs):
        super(EditUserInformationPopup, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.setWindowTitle('编辑用户')
        # 布局
        layout = QVBoxLayout(margin=0)
        # 编辑的功能选择
        self.edit_select = QComboBox(parent=self)
        self.edit_select.activated.connect(self.selected_edit_state)
        layout.addWidget(self.edit_select, alignment=Qt.AlignLeft)
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
        for item_data in [('基础信息', 'base_info'), ('客户端权限', 'client'), ('模块权限', 'module'), ('品种权限', 'vareity')]:
            self.edit_select.addItem(item_data[0], item_data[1])

    # 获取模块信息，编辑有当前用户权限
    def _getCurrentModule(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/' + str(self.user_id) + '/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            el = self.base_info.findChild(QLabel, 'noteError')
            el.setText(str(e))

    # 获取品种信息，标记有当前用户权限
    def _getCurrentVariety(self):
        print('品种权限')

    # 选择编辑的类型
    def selected_edit_state(self):
        current_text = self.edit_select.currentData()
        self.tab_show.clear()
        if current_text == 'base_info':
            tab = UserBaseInfo(user_id=self.user_id)
            tab.getCurrentUser()
        elif current_text == 'client':
            tab = UserToClientEdit(user_id=self.user_id)
            tab.getClients()
            # tab.getClients()
        # elif current_text == 'module_auth':
        #     self._getCurrentModule()
        #     tab = self.module_auth
        # elif current_text == 'variety_auth':
        #     self._getCurrentVariety()
        #     tab = self.variety_auth
        else:
            tab = QLabel('暂无相关维护')
        self.tab_show.addTab(tab, '')