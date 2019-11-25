# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView,\
    QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal
import config
from utils.maintain import change_user_information


# 【进入】按钮
class EnterAuthorityButton(QPushButton):
    button_clicked = pyqtSignal(QPushButton)

    def __init__(self, uid, *args, **kwargs):
        super(EnterAuthorityButton, self).__init__(*args, **kwargs)
        self.setText('进入→')
        self.uid = uid
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(lambda: self.button_clicked.emit(self))


# 【有效】选择按钮
class CheckBox(QWidget):
    check_changed = pyqtSignal(QCheckBox)

    def __init__(self, cid, checked, *args, **kwargs):
        super(CheckBox, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        check_button = QCheckBox(parent=self)
        check_button.cid = cid
        check_button.setChecked(checked)
        check_button.setMinimumHeight(13)
        layout.addWidget(check_button, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        check_button.stateChanged.connect(lambda: self.check_changed.emit(check_button))


# 显示用户的表格
class UserTable(QTableWidget):
    enter_detail = pyqtSignal(int)
    active_changed = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        super(UserTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()

    # 添加显示用户
    def addUsers(self, json_list):
        self.clear()
        # 设置表头
        self.setRowCount(len(json_list))
        self.setColumnCount(9)
        self.setHorizontalHeaderLabels(['序号', '用户名/昵称', '手机号', '邮箱', '角色', '最近登录', '有效', '备注名', ' '])
        # 列宽模式
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(self.columnCount() - 1, QHeaderView.ResizeToContents)
        # 设置内容
        for row, user in enumerate(json_list):
            item_0 = QTableWidgetItem(str(row + 1))
            item_1 = QTableWidgetItem(str(user['username']))
            item_2 = QTableWidgetItem(str(user['phone']))
            item_3 = QTableWidgetItem(str(user['email']))
            # 判断用户角色
            if user['is_maintainer']:
                role = '数据搜集员'
            elif user['is_researcher']:
                role = '研究员'

            elif user['is_superuser']:
                role = '超级管理员'
            else:
                role = '普通用户'
            item_4 = QTableWidgetItem(role)
            last_login = str(user['last_login']) if user['last_login'] else ''
            item_5 = QTableWidgetItem(last_login)
            note = str(user['note']) if user['note'] else ''
            item_6 = QTableWidgetItem(note)
            item_0.setTextAlignment(Qt.AlignCenter)
            item_1.setTextAlignment(Qt.AlignCenter)
            item_2.setTextAlignment(Qt.AlignCenter)
            item_3.setTextAlignment(Qt.AlignCenter)
            item_4.setTextAlignment(Qt.AlignCenter)
            item_5.setTextAlignment(Qt.AlignCenter)
            item_6.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 0, item_0)
            self.setItem(row, 1, item_1)
            self.setItem(row, 2, item_2)
            self.setItem(row, 3, item_3)
            self.setItem(row, 4, item_4)
            self.setItem(row, 5, item_5)
            self.setItem(row, 7, item_6)
            if not user['is_superuser']:
                # 【有效】
                active_check = CheckBox(cid=user['id'], checked=user['is_active'])
                active_check.check_changed.connect(self.change_user_active)
                # 【进入】
                button = EnterAuthorityButton(uid=user['id'])
                button.button_clicked.connect(self.enter_authority)
                self.setCellWidget(row, 6, active_check)
                self.setCellWidget(row, 8, button)

    # 点击进入权限管理
    def enter_authority(self, button):
        self.enter_detail.emit(button.uid)

    # 该变用户的有效
    def change_user_active(self, check_box):
        # 发起设置请求
        change_user_information(
            uid=check_box.cid,
            data_dict={
                'is_active': check_box.isChecked()
            }
        )


# 设置【用户-客户端权限】的表格
class UserClientTable(QTableWidget):
    def __init__(self, uid, *args, **kwargs):
        super(UserClientTable, self).__init__(*args, **kwargs)
        self.uid = uid
        self.verticalHeader().hide()

    # 获取所有客户端
    def get_all_clients(self):
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'basic/clients/?mc=' + config.app_dawn.value('machine'),
                data=json.dumps({'uid': self.uid})
            )
            response = json.loads(r.content.decode('utf-8'))
        except Exception:
            return
        print(response)
        # 展示信息
        self.clear()
        client_list = response['data']
        self.setRowCount(len(client_list))
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(['序号', '可登录', '客户端名称', '客户端类型'])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, client_item in enumerate(client_list):
            item_0 = QTableWidgetItem(str(row + 1))
            item_0.setTextAlignment(Qt.AlignCenter)
            if client_item['accessed'] == 0 or client_item['accessed'] == 1:
                # 创建选择框
                accessed_box = CheckBox(cid=client_item['id'], checked=client_item['accessed'])
                self.setCellWidget(row, 1, accessed_box)
            else:
                item_1 = QTableWidgetItem(str(client_item['accessed']))
                item_1.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 1, item_1)
            client_name = str(client_item['name']) if client_item['name'] else ''
            item_2 = QTableWidgetItem(client_name)
            if client_item['is_manager']:
                client_type = '管理端'
            else:
                client_type = '普通端'
            item_3 = QTableWidgetItem(str(client_type))
            item_2.setTextAlignment(Qt.AlignCenter)
            item_3.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 0, item_0)
            self.setItem(row, 2, item_2)
            self.setItem(row, 3, item_3)








