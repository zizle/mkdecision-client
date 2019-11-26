# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QLabel, QTableWidgetItem, QPushButton, QHeaderView,\
    QCheckBox, QDateTimeEdit
from PyQt5.QtCore import Qt, pyqtSignal, QDateTime
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

    def __init__(self, cid, checked, row_index, *args, **kwargs):
        super(CheckBox, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        check_button = QCheckBox(parent=self)
        check_button.cid = cid
        check_button.row_index = row_index
        check_button.setChecked(checked)
        check_button.setMinimumHeight(13)
        layout.addWidget(check_button, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        check_button.stateChanged.connect(lambda: self.check_changed.emit(check_button))


# 【有效期】设置控件
class ExpireDateBox(QWidget):
    expire_date_setting = pyqtSignal(list)

    def __init__(self, client_id, expire_date=None, *args, **kwargs):
        super(ExpireDateBox, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0, spacing=2)
        self.client_id = client_id
        # 显示长期有效
        self.label_show = QLabel('长期', parent=self)
        self.label_show.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_show)
        # 设置日期(默认隐藏)
        if expire_date:  # 有效期编辑(有有效期的时候)
            self.label_show.setText(expire_date)
            date = QDateTime.fromString(expire_date, 'yyyy-MM-dd HH:mm:ss')  # 设置日期
            self.date_time = QDateTimeEdit(date, parent=self)
        else:  # 没有有效期的时候，有效期编辑
            self.date_time = QDateTimeEdit(QDateTime.currentDateTime(), parent=self)
        self.date_time.setCalendarPopup(True)  # 日历编辑
        self.date_time.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.date_time.setAlignment(Qt.AlignCenter)
        self.date_time.hide()
        # 设置按钮
        self.date_button = QPushButton('设置', parent=self, objectName='dateButton', clicked=self.setting_expire_date)
        self.date_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.date_time)
        layout.addWidget(self.date_button)
        self.setStyleSheet("""
        #dateButton{
            min-width:30px;
            max-width:30px;
        }
        #dateButton:hover{
            color: rgb(180,130,220)
        }
        """)
        self.setLayout(layout)

    # 设置可登录有效日期
    def setting_expire_date(self):
        if self.date_time.isHidden():
            self.label_show.hide()
            self.date_time.show()
            self.date_button.setText(u'确定')
        else:
            self.label_show.show()
            self.date_time.hide()
            self.date_button.setText(u'设置')
            # 获取当前有效期字符串
            expire_date = self.date_time.dateTime().toString('yyyy-MM-dd HH:mm:ss')
            # 【确定】发起请求设置有效期
            self.expire_date_setting.emit([self.client_id, expire_date])
            # 改变当前label的显示
            self.label_show.setText(expire_date)


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
                active_check = CheckBox(cid=user['id'], checked=user['is_active'], row_index=row)
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


# 设置用户-客户端权限的表格
class UserClientTable(QTableWidget):
    network_result = pyqtSignal(str)

    def __init__(self, uid, *args, **kwargs):
        super(UserClientTable, self).__init__(*args, **kwargs)
        self.uid = uid
        self.verticalHeader().hide()

    # 展示所有客户端和当前用户可登录状态(可登录含有效期)
    def addClients(self, client_list):
        self.clear()
        self.setRowCount(len(client_list))
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(['序号', '可登录', '有效期', '客户端名称', '客户端类型'])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, client_item in enumerate(client_list):
            item_0 = QTableWidgetItem(str(row + 1))
            item_1 = QTableWidgetItem()
            item_2 = QTableWidgetItem()
            item_0.setTextAlignment(Qt.AlignCenter)
            item_1.setTextAlignment(Qt.AlignCenter)
            item_2.setTextAlignment(Qt.AlignCenter)

            if client_item['accessed'] == 0 or client_item['accessed'] == 1:  # 勾选可登录的情况
                # 创建选择框
                accessed_box = CheckBox(cid=client_item['id'], checked=client_item['accessed'], row_index=row)
                accessed_box.check_changed.connect(self.change_user_access_client)
                self.setCellWidget(row, 1, accessed_box)  # 可登录选择框
                # 创建【有效期】时间编辑框item2
                if client_item['accessed'] == 0:  # 是勾选框，但是为不可登录状态
                    item_2 = QTableWidgetItem('不可登录')
                    item_2.setTextAlignment(Qt.AlignCenter)
                    self.setItem(row, 2, item_2)
                else:  # 是勾选框，为可登录状态
                    expire_date_box = ExpireDateBox(client_id=client_item['id'], expire_date=client_item['expire_date'])
                    expire_date_box.expire_date_setting.connect(self.setting_expire_date)
                    self.setCellWidget(row, 2, expire_date_box)
            else:  # 都可登录的情况
                item_1.setText(str(client_item['accessed']))
                item_2.setText('长期')

            client_name = str(client_item['name']) if client_item['name'] else ''
            item_3 = QTableWidgetItem(client_name)
            if client_item['is_manager']:
                client_type = '管理端'
            else:
                client_type = '普通端'
            item_4 = QTableWidgetItem(str(client_type))
            item_3.setTextAlignment(Qt.AlignCenter)
            item_4.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 0, item_0)
            self.setItem(row, 1, item_1)
            self.setItem(row, 2, item_2)
            self.setItem(row, 3, item_3)
            self.setItem(row, 4, item_4)

    # 设置用户可登录客户端的有效期
    def setting_expire_date(self, data_list):
        # 发起请求
        try:
            r = requests.put(
                url=config.SERVER_ADDR + 'limit/user-client/?mc=' + config.app_dawn.value('machine'),
                headers={"AUTHORIZATION": config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'uid': self.uid,
                    'cid': data_list[0],
                    'expire_date': data_list[1]
                })

            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            self.network_result.emit(response['message'])

    # 改变用户可登录客户端的状态
    def change_user_access_client(self, check_button):
        try:
            # 发起请求
            r = requests.post(
                url=config.SERVER_ADDR + 'limit/user-client/?mc=' + config.app_dawn.value('machine'),
                headers={"AUTHORIZATION": config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'uid': self.uid,
                    'cid': check_button.cid,
                    'accessed': check_button.isChecked()
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            if check_button.isChecked():  # 改变有效期的设置
                expire_date_box = ExpireDateBox(client_id=check_button.cid, expire_date=None)
                expire_date_box.expire_date_setting.connect(self.setting_expire_date)  # 连接设置有效期信号
                self.item(check_button.row_index, 2).setText('')  # 改变原先的‘不可登录’
                self.removeCellWidget(check_button.row_index, 2)  # 移除单元格上的控件
                self.setCellWidget(check_button.row_index, 2, expire_date_box)  # 设置控件
            else:
                self.removeCellWidget(check_button.row_index, 2)  # 移除单元格上的控件
                self.item(check_button.row_index, 2).setText('不可登录')    # 改变原先的‘不可登录’
            self.network_result.emit(response['message'])


# 设置用户-模块权限的表格
