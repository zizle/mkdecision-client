# _*_ coding:utf-8 _*_
# Author:zizle QQ:462894999

import json
import requests
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QLabel, QTableWidgetItem, QPushButton, QHeaderView,\
    QCheckBox, QDateTimeEdit, QComboBox, QLineEdit, QListView
from PyQt5.QtCore import Qt, pyqtSignal, QDateTime, QPoint
import config
from utils.maintain import change_user_information
from popup.tips import InformationPopup


# 【进入】按钮
class EnterAuthorityButton(QPushButton):
    button_clicked = pyqtSignal(QPushButton)

    def __init__(self, uid, *args, **kwargs):
        super(EnterAuthorityButton, self).__init__(*args, **kwargs)
        self.setText('进入→')
        self.uid = uid
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(lambda: self.button_clicked.emit(self))


# 【有效】复选框
class CheckBox(QWidget):
    check_changed = pyqtSignal(QCheckBox)

    def __init__(self, checked, *args, **kwargs):
        super(CheckBox, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        self.check_button = QCheckBox(parent=self, checked=checked)
        self.check_button.setMinimumHeight(13)
        layout.addWidget(self.check_button, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        self.check_button.stateChanged.connect(lambda: self.check_changed.emit(self))


# 【角色】下拉框选择
class UserRoleComboBox(QComboBox):
    role_changed = pyqtSignal(QComboBox)

    def __init__(self, role, *args, **kwargs):
        super(UserRoleComboBox, self).__init__(*args, **kwargs)
        self.blockSignals(True)  # 关闭信号
        line_edit = QLineEdit(readOnly=True)
        line_edit.setAlignment(Qt.AlignCenter)
        self.addItem('运营管理员', 'is_operator')
        self.addItem('信息管理员', 'is_collector')
        self.addItem('研究员', 'is_researcher')
        self.addItem('普通用户', '')
        self.setLineEdit(line_edit)  # 居中显示
        self.currentTextChanged.connect(lambda: self.role_changed.emit(self))
        # 设置当前项目
        for i in range(self.count()):
            if self.itemData(i) == role:
                self.setCurrentIndex(i)
            self.view().model().item(i).setTextAlignment(Qt.AlignCenter)
        self.blockSignals(False)  # 开启信号
        self.setStyleSheet("""
        QComboBox{
            border:none
        }
        QComboBox QAbstractItemView::item{
            height:25px;
            font-size:15px
        }
        /*
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 30px;
            border-left-width: 0px;
            border-left-color: gray;
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
            }
        QComboBox::down-arrow {
            image: url(media/combo/dd-close.png);
        }
        QComboBox::down-arrow:hover{
            
        }
        QComboBox::down-arrow:pressed {
            border-image: url(media/combo/dd-open.png);
        }*/
        """)
        self.setView(QListView())


# 【权限】按钮
class AuthButton(QPushButton):
    auth_clicked = pyqtSignal(QPushButton)

    def __init__(self, *args, **kwargs):
        super(AuthButton, self).__init__(*args, **kwargs)
        self.setText('权限')
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(lambda: self.auth_clicked.emit(self))


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
    network_result = pyqtSignal(str)
    enter_detail_authenticated = pyqtSignal(int, dict)
    # 表头key字典列表
    HEADER_LABELS = [
        ('index', '序号'),
        ('username', '用户名/昵称'),
        ('phone', '手机号'),
        ('email', '邮箱'),
        ('role', '角色'),
        ('last_login', '最近登录'),
        ('is_active', '有效'),
        ('note', '备注名'),
    ]
    NO_EDIT_COLUMNS = [0, 5]  # 不可编辑的列
    CHECKBOX_COLUMNS = [6]  # 复选框的列
    COMBOBOX_COLUMNS = [4]  # 下拉框的列

    def __init__(self, *args, **kwargs):
        super(UserTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self._initialTableMode()
        self.itemChanged.connect(self.changed_table_text)
        self.setFocusPolicy(Qt.NoFocus)
        self.text_ready_to_changed = ''
        self.cellDoubleClicked.connect(self.cell_double_clicked)

    # 设置表格头和列宽模式
    def _initialTableMode(self):
        self.setColumnCount(len(self.HEADER_LABELS) + 1)
        self.setHorizontalHeaderLabels([h[1] for h in self.HEADER_LABELS] + [''])  # 加个空列头
        # 列宽模式
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(self.columnCount() - 1, QHeaderView.ResizeToContents)

    # 重写clear
    def clear(self):
        super(UserTable, self).clear()
        self._initialTableMode()
        print('阻止表格修改信号')
        self.blockSignals(True)  # 阻止信号

    # 添加显示用户
    def showUsers(self, json_list):
        self.clear()
        self.setRowCount(len(json_list))  # 设置行
        # 设置内容
        for row, user_item in enumerate(json_list):
            print('加入用户：', user_item)
            for col, couple_item in enumerate(self.HEADER_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.user_id = user_item['id']
                else:
                    table_item = QTableWidgetItem(str(user_item[self.HEADER_LABELS[col][0]]))
                if col in self.NO_EDIT_COLUMNS:
                    table_item.setFlags(Qt.ItemIsEnabled)
                if col in self.CHECKBOX_COLUMNS:  # 选择框的列
                    check_box = CheckBox(checked=int(table_item.text()))
                    check_box.check_changed.connect(self.set_active_checked)
                    self.setCellWidget(row, col, check_box)
                if col in self.COMBOBOX_COLUMNS:  # 下拉框的列
                    combo_box = UserRoleComboBox(role=table_item.text())
                    combo_box.role_changed.connect(self.set_user_role)
                    self.setCellWidget(row, col, combo_box)
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
            # 设置权限按钮和tableItem
            auth_button = AuthButton()
            auth_button.auth_clicked.connect(self.enter_user_authority)
            self.setCellWidget(row, len(self.HEADER_LABELS), auth_button)
            table_item = QTableWidgetItem('')
            self.setItem(row, len(self.HEADER_LABELS), table_item)
        print('恢复表格修改信号')
        self.blockSignals(False)  # 恢复信号

    # 单元格被双击时保存未修改前的内容
    def cell_double_clicked(self, row, col):
        if col in self.NO_EDIT_COLUMNS:
            return
        else:
            print('单元格被双击')
            self.text_ready_to_changed = self.item(row, col).text()  # 保存未修改前的数据

    # 有效修改处理
    def set_active_checked(self, check_widget):
        # 获取控件所在的行和列
        index = self.indexAt(QPoint(check_widget.frameGeometry().x(), check_widget.frameGeometry().y()))
        row = index.row()
        column = index.column()
        print('改变第%d行%d列的复选框状态' %(row,column))
        text = '1' if check_widget.check_button.isChecked() else '0'
        self.item(row, column).setText(text)

    # 用户角色修改处理
    def set_user_role(self, combo_widget):
        # 获取控件所在的行和列
        row, column = self._get_widget_index(combo_widget)
        current_role = combo_widget.currentData()
        print('改变第%d行%d列的角色为%s' % (row, column, current_role))
        self.item(row, column).setText(combo_widget.currentData())

    # 进入用户权限管理
    def enter_user_authority(self, button):
        row, column = self._get_widget_index(button)
        user_id = self.item(row, 0).user_id
        # 按钮的位置
        button_center = {
            'center_x':  button.frameGeometry().center().x(),
            'center_y': button.frameGeometry().center().y() + 40
        }
        self.enter_detail_authenticated.emit(user_id, button_center)

    # 获取控件所在行和列
    def _get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()

    # 修改表格内容处理
    def changed_table_text(self, item):
        current_row = item.row()
        current_column = item.column()
        user_id = self.item(current_row, 0).user_id
        print('修改id=%d的用户%s为:%s' % (user_id, self.HEADER_LABELS[current_column][1], item.text()))
        modify_content = int(item.text()) if current_column in self.CHECKBOX_COLUMNS else item.text()
        field = {self.HEADER_LABELS[current_column][0]: modify_content}
        if current_column in self.COMBOBOX_COLUMNS:
            if item.text():
                field = {item.text(): True}
            else:
                field = {
                    'is_operator': False,
                    'is_collector': False,
                    'is_researcher': False,
                }
        user_data = self._modify_user_data(user_id=user_id, field=field)
        # 关闭信号再修改单元格内容，防止继续向后端发送请求
        self.blockSignals(True)
        if user_data:
            # 修改单元格内容
            self.item(current_row, current_column).setText(str(user_data[self.HEADER_LABELS[current_column][0]]))
        else:
            self.item(current_row, current_column).setText(self.text_ready_to_changed)
        # 恢复信号
        self.blockSignals(False)

    # 修改用户信息
    def _modify_user_data(self, user_id, field):
        print('修改用户信息：', field)
        try:
            r = requests.patch(
                url=config.SERVER_ADDR + 'user/' + str(user_id) + '/?mc=' + config.app_dawn.value(
                    'machine'),
                headers={
                    'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')
                },
                data=json.dumps(field)
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
            return {}
        else:
            self.network_result.emit(response['message'])
            return response['data']

    # 点击进入权限管理
    def enter_authority(self, button):
        self.enter_detail.emit(button.uid)


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
class UserModuleTable(QTableWidget):
    network_result = pyqtSignal(str)

    def __init__(self, uid, *args, **kwargs):
        super(UserModuleTable, self).__init__(*args, **kwargs)
        self.uid = uid
        self.verticalHeader().hide()

    # 获取所有模块
    def getModules(self):
        # 获取模块信息
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'basic/modules-authorization/?mc=' + config.app_dawn.value('machine'),
                data=json.dumps({'uid': self.uid})
            )
            response = json.loads(r.content.decode('utf-8'))
        except Exception as e:
            print(e)
            return
        print('请求可进入模块成功', response)
        self.addModules(response['data'])

    # 展示所有模块和当前用户可进入状态(可进入含有效期)
    def addModules(self, module_list):
        self.clear()
        self.setRowCount(len(module_list))
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(['序号', '模块名称', '可进入', '有效期'])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, module_item in enumerate(module_list):
            item_0 = QTableWidgetItem(str(row + 1))
            item_1 = QTableWidgetItem()
            item_2 = QTableWidgetItem()
            item_3 = QTableWidgetItem()
            item_0.setTextAlignment(Qt.AlignCenter)
            item_1.setTextAlignment(Qt.AlignCenter)
            item_2.setTextAlignment(Qt.AlignCenter)
            item_3.setTextAlignment(Qt.AlignCenter)

            if module_item['accessed'] == 0 or module_item['accessed'] == 1:  # 勾选可进入的情况
                # 创建选择框
                accessed_box = CheckBox(cid=module_item['id'], checked=module_item['accessed'], row_index=row)
                accessed_box.check_changed.connect(self.change_user_access_module)
                self.setCellWidget(row, 2, accessed_box)  # 可登录选择框
                # 创建【有效期】时间编辑框item2
                if module_item['accessed'] == 0:  # 是勾选框，但是为不可登录状态
                    item_3.setText('不可进入')
                    self.setItem(row, 3, item_3)
                else:  # 是勾选框，为可登录状态
                    expire_date_box = ExpireDateBox(client_id=module_item['id'], expire_date=module_item['expire_date'])
                    expire_date_box.expire_date_setting.connect(self.setting_expire_date)
                    self.setCellWidget(row, 3, expire_date_box)
            else:  # 都可登录的情况
                item_2.setText(str(module_item['accessed']))
                item_3.setText('长期')
            item_1.setText(str(module_item['name']))
            self.setItem(row, 0, item_0)
            self.setItem(row, 1, item_1)
            self.setItem(row, 2, item_2)
            self.setItem(row, 3, item_3)

    # 改变用户可进入模块的状态
    def change_user_access_module(self, check_button):
        try:
            # 发起请求
            r = requests.post(
                url=config.SERVER_ADDR + 'limit/user-module/?mc=' + config.app_dawn.value('machine'),
                headers={"AUTHORIZATION": config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'uid': self.uid,
                    'mid': check_button.cid,
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
                self.item(check_button.row_index, 3).setText('')  # 改变原先的‘不可进入’
                self.removeCellWidget(check_button.row_index, 3)  # 移除单元格上的控件
                self.setCellWidget(check_button.row_index, 3, expire_date_box)  # 设置控件
            else:
                self.removeCellWidget(check_button.row_index, 3)  # 移除单元格上的控件
                self.item(check_button.row_index, 3).setText('不可进入')    # 改回原先的‘不可进入’
            self.network_result.emit(response['message'])

    # 设置用户可进入模块的有效期
    def setting_expire_date(self, data_list):
        # 发起请求
        try:
            r = requests.put(
                url=config.SERVER_ADDR + 'limit/user-module/?mc=' + config.app_dawn.value('machine'),
                headers={"AUTHORIZATION": config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'uid': self.uid,
                    'mid': data_list[0],
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
