# _*_ coding:utf-8 _*_
# Author: zizle QQ:462894999
import json
import requests
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QComboBox, QHeaderView, QHBoxLayout,\
    QCheckBox, QLabel, QDateTimeEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QDateTime
import config


# 【有效】选择按钮
class CheckBox(QWidget):
    check_changed = pyqtSignal(QCheckBox)

    def __init__(self, vid, checked, row_index, *args, **kwargs):
        super(CheckBox, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        check_button = QCheckBox(parent=self)
        check_button.vid = vid
        check_button.row_index = row_index
        check_button.setChecked(checked)
        check_button.setMinimumHeight(13)
        layout.addWidget(check_button, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        check_button.stateChanged.connect(lambda: self.check_changed.emit(check_button))


# 【有效期】设置控件
class ExpireDateBox(QWidget):
    expire_date_setting = pyqtSignal(list)

    def __init__(self, variety_id, expire_date=None, *args, **kwargs):
        super(ExpireDateBox, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0, spacing=2)
        self.variety_id = variety_id
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
            self.expire_date_setting.emit([self.variety_id, expire_date])
            # 改变当前label的显示
            self.label_show.setText(expire_date)


# 用户-品种权限管理
class UserVarietyAuth(QWidget):
    network_result = pyqtSignal(str)

    def __init__(self, uid, *args, **kwargs):
        super(UserVarietyAuth, self).__init__(*args, **kwargs)
        self.user_id = uid
        layout = QVBoxLayout(margin=0)
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
                url=config.SERVER_ADDR + 'limit/user-varieties/' + str(current_gid) + '/?mc=' + config.app_dawn.value('machine'),
                data=json.dumps({
                    'uid': self.user_id
                }),
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
        self.auth_table.setHorizontalHeaderLabels(['序号', '名称', '英文代码', '权限', '有效期', '所属组'])
        for row, variety_item in enumerate(variety_list):
            # 序号
            item_0 = QTableWidgetItem(str(row + 1))
            item_0.setTextAlignment(Qt.AlignCenter)
            self.auth_table.setItem(row, 0, item_0)
            # 名称
            item_1 = QTableWidgetItem()
            item_1.setTextAlignment(Qt.AlignCenter)
            item_1.setText(str(variety_item['name']))
            self.auth_table.setItem(row, 1, item_1)
            # 英文代码
            item_2 = QTableWidgetItem()
            item_2.setTextAlignment(Qt.AlignCenter)
            item_2.setText(str(variety_item['name_en']))
            self.auth_table.setItem(row, 2, item_2)
            # 权限、有效期文字显示
            item_3 = QTableWidgetItem()  # 权限文字显示
            item_4 = QTableWidgetItem()  # 有效期文字显示
            item_3.setTextAlignment(Qt.AlignCenter)
            item_4.setTextAlignment(Qt.AlignCenter)
            self.auth_table.setItem(row, 3, item_3)
            self.auth_table.setItem(row, 4, item_4)
            # 选择框和有效期编辑
            if variety_item['accessed'] == 0 or variety_item['accessed'] == 1:  # 勾选可操作的情况
                # 创建选择框
                accessed_box = CheckBox(vid=variety_item['id'], checked=variety_item['accessed'], row_index=row)
                accessed_box.check_changed.connect(self.change_user_access_variety)
                self.auth_table.setCellWidget(row, 3, accessed_box)  # 可操作选择框
                # 创建【有效期】时间编辑框item2
                if variety_item['accessed'] == 0:  # 是勾选框，但是为不可操作状态
                    item_4.setText('不可操作')
                else:  # 是勾选框，为可操作状态
                    expire_date_box = ExpireDateBox(variety_id=variety_item['id'],
                                                    expire_date=variety_item['expire_date'])
                    expire_date_box.expire_date_setting.connect(self.setting_expire_date)
                    self.auth_table.setCellWidget(row, 4, expire_date_box)
            else:  # 都可登录的情况
                item_3.setText(str(variety_item['accessed']))
                item_4.setText('长期')

    # 改变用户的品种权限
    def change_user_access_variety(self, check_button):
        try:
            # 发起请求
            r = requests.post(
                url=config.SERVER_ADDR + 'limit/user-variety/?mc=' + config.app_dawn.value('machine'),
                headers={"AUTHORIZATION": config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'uid': self.user_id,
                    'vid': check_button.vid,
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
                expire_date_box = ExpireDateBox(variety_id=check_button.vid, expire_date=None)
                expire_date_box.expire_date_setting.connect(self.setting_expire_date)  # 连接设置有效期信号
                self.auth_table.item(check_button.row_index, 4).setText('')  # 改变原先的‘不可操作’
                self.auth_table.removeCellWidget(check_button.row_index, 4)  # 移除单元格上的控件
                self.auth_table.setCellWidget(check_button.row_index, 4, expire_date_box)  # 设置控件
            else:
                self.auth_table.removeCellWidget(check_button.row_index, 4)  # 移除单元格上的控件
                self.auth_table.item(check_button.row_index, 4).setText('不可操作')  # 改变原先的‘不可操作’
            self.network_result.emit(response['message'])

    # 设置有效期
    def setting_expire_date(self, data_list):
        # 发起请求
        try:
            r = requests.put(
                url=config.SERVER_ADDR + 'limit/user-variety/?mc=' + config.app_dawn.value('machine'),
                headers={"AUTHORIZATION": config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'uid': self.user_id,
                    'vid': data_list[0],
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
