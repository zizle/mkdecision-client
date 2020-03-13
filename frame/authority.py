# _*_ coding:utf-8 _*_
# __Author__： zizle
import re
import json
import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLineEdit, QComboBox, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, \
    QAbstractItemView, QHeaderView, QListView, QDialog, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
import settings
from widgets.base import TableCheckBox, TableRowReadButton


# 【角色】下拉框选择
class UserRoleComboBox(QComboBox):
    # role_changed = pyqtSignal(QComboBox)

    def __init__(self, *args, **kwargs):
        super(UserRoleComboBox, self).__init__(*args, **kwargs)
        # self.blockSignals(True)  # 关闭信号
        line_edit = QLineEdit(readOnly=True)
        line_edit.setAlignment(Qt.AlignCenter)
        self.addItem('运营管理员', 'is_operator')
        self.addItem('信息管理员', 'is_collector')
        self.addItem('研究员', 'is_researcher')
        self.addItem('普通用户', 'normal')
        self.setLineEdit(line_edit)  # 居中显示
        # self.currentTextChanged.connect(lambda: self.role_changed.emit(self))
        # self.blockSignals(False)  # 开启信号
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

    # 设置当前的角色
    def setCurrentRole(self, role):
        # 设置当前项目
        for i in range(self.count()):
            if self.itemText(i) == role:
                self.setCurrentIndex(i)
            self.view().model().item(i).setTextAlignment(Qt.AlignCenter)


# 用户信息编辑弹窗
class EditUserInfoPopup(QDialog):
    def __init__(self, user_id, *args, **kwargs):
        super(EditUserInfoPopup, self).__init__(*args, **kwargs)
        self.user_id = user_id
        layout = QGridLayout()
        # 用户名
        layout.addWidget(QLabel('昵称:'), 0, 0)
        self.username_edit = QLineEdit()
        layout.addWidget(self.username_edit, 0, 1)
        layout.addWidget(QLabel(parent=self, objectName='usernameError'), 1, 0, 1, 2)
        # 手机
        layout.addWidget(QLabel('手机:'), 2, 0)
        self.phone_edit = QLineEdit()
        layout.addWidget(self.phone_edit, 2, 1)
        layout.addWidget(QLabel(parent=self, objectName='phoneError'), 3, 0, 1, 2)
        # 邮箱
        layout.addWidget(QLabel('邮箱:'), 4, 0)
        self.email_edit = QLineEdit()
        layout.addWidget(self.email_edit, 4, 1)
        layout.addWidget(QLabel(parent=self, objectName='emailError'), 5, 0, 1, 2)
        # 备注
        layout.addWidget(QLabel('备注：'), 6, 0)
        self.note_edit = QLineEdit()
        layout.addWidget(self.note_edit, 6, 1)
        layout.addWidget(QLabel(parent=self, objectName='noteError'), 7, 0, 1, 2)
        # 角色
        self.role_edit = UserRoleComboBox()
        layout.addWidget(QLabel('角色：'), 8, 0)
        layout.addWidget(self.role_edit, 8, 1)
        layout.addWidget(QLabel(parent=self, objectName='roleError'), 9, 0, 1, 2)
        # 提交
        self.commit_button = QPushButton('确定', clicked=self.edit_user_info)
        layout.addWidget(self.commit_button, 10, 0, 1, 2)
        self.setLayout(layout)
        self.setWindowTitle('编辑用户信息')
        self.setMinimumSize(400,320)

    # 请求当前用户信息
    def getCurrentUserInfo(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/' + str(self.user_id) + '/baseInfo/?mc=' + settings.app_dawn.value(
                    'machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            el = self.findChild(QLabel, 'roleError')
            el.setText(str(e))
        else:
            user_data = response['data']
            self.username_edit.setText(user_data['username'])
            self.phone_edit.setText(user_data['phone'])
            self.email_edit.setText(user_data['email'])
            self.note_edit.setText(user_data['note'])
            self.role_edit.setCurrentRole(user_data['role'])

    # 编辑用户信息提交
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
        # 角色！！
        is_operator = False
        is_collector = False
        is_researcher = False
        current_role_data = self.role_edit.currentData()
        if current_role_data == 'is_researcher':
            is_researcher = True
        elif current_role_data == 'is_collector':
            is_researcher = True
            is_collector = True
        elif current_role_data == 'is_operator':
            is_researcher = True
            is_collector = True
            is_operator = True
        else:
            pass
        # 发起修改请求
        try:
            r = requests.patch(
                url=settings.SERVER_ADDR + 'user/' + str(self.user_id) + '/baseInfo/?mc=' + settings.app_dawn.value(
                    'machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'username': username,
                    'phone': phone.group(),
                    'email': email,
                    'note': note,
                    'is_operator': is_operator,
                    'is_collector': is_collector,
                    'is_researcher': is_researcher
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.findChild(QLabel, 'roleError').setText(str(e))
        else:
            self.findChild(QLabel, 'roleError').setText(response['message'])


# 显示用户的表格
class UserTable(QTableWidget):
    network_result = pyqtSignal(str)
    KEY_LABELS = [
        ('id', '序号'),
        ('username', '用户名/昵称'),
        ('phone', '手机'),
        ('email', '邮箱'),
        ('last_login', '最近登录'),
        ('note', '备注'),
        ('role', '角色'),
        ('is_active', '有效'),
    ]
    CHECK_COLUMNS = [7]

    def __init__(self, *args, **kwargs):
        super(UserTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setFocusPolicy(Qt.NoFocus)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # 设置表格数据
    def setRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS) + 1)
        self.setHorizontalHeaderLabels([l[1] for l in self.KEY_LABELS] + [''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(len(self.KEY_LABELS), QHeaderView.ResizeToContents)
        for row, user_item in enumerate(row_list):
            print(user_item)
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = user_item[header[0]]
                else:
                    table_item = QTableWidgetItem(str(user_item[header[0]]))
                # 选择框按钮
                if col in self.CHECK_COLUMNS:
                    check_box = TableCheckBox(checked=user_item[header[0]])
                    check_box.check_activated.connect(self.check_box_changed)
                    self.setCellWidget(row, col, check_box)
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
                # 增加【编辑】按钮
                if col == len(self.KEY_LABELS) - 1:
                    edit_button = TableRowReadButton('编辑')
                    edit_button.button_clicked.connect(self.edit_button_clicked)
                    self.setCellWidget(row, col + 1, edit_button)

    def check_box_changed(self, check_button):
        row, column = self.get_widget_index(check_button)
        user_id = self.item(row, 0).id
        print('改变id=%d的用户的为%s' % (user_id, '有效' if check_button.check_box.isChecked() else '无效'))
        # 修改用户有效的请求
        try:
            r = requests.patch(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/baseInfo/?mc=' + settings.app_dawn.value(
                    'machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({'is_active': check_button.check_box.isChecked()})
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            self.network_result.emit(response['message'])

    def edit_button_clicked(self, edit_button):
        current_row, _ = self.get_widget_index(edit_button)
        user_id = self.item(current_row, 0).id
        popup = EditUserInfoPopup(user_id=user_id, parent=self)
        popup.getCurrentUserInfo()
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 权限管理主页
class AuthorityMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(AuthorityMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=2, spacing=2)
        # 下拉框和网络信息提示布局
        combo_message_layout = QHBoxLayout()
        combo_message_layout.addWidget(QLabel('角色:'))
        self.user_role_combo = QComboBox(parent=self, activated=self.getCurrentUsers)
        combo_message_layout.addWidget(self.user_role_combo)
        self.network_message_label = QLabel()
        combo_message_layout.addWidget(self.network_message_label)
        combo_message_layout.addStretch()
        layout.addLayout(combo_message_layout)
        # 显示用户表格
        self.user_table = UserTable()
        self.user_table.network_result.connect(self.network_message_label.setText)
        layout.addWidget(self.user_table)
        self.setLayout(layout)
        self._addRoleCombo()

    # 添加下拉框的内容
    def _addRoleCombo(self):
        role_list = [
            {'role': '全部', 'flag': 'all'},
            {'role': '运营管理员', 'flag': 'is_operator'},
            {'role': '信息管理员', 'flag': 'is_collector'},
            {'role': '研究员', 'flag': 'is_researcher'},
            {'role': '普通用户', 'flag': 'normal'},
        ]
        for role_item in role_list:
            self.user_role_combo.addItem(role_item['role'], role_item['flag'])

    # 获取当前角色的用户
    def getCurrentUsers(self):
        params = {}
        current_role = self.user_role_combo.currentData()
        if current_role == 'all':
            pass
        elif current_role == 'normal':
            params['is_operator'] = False
            params['is_collector'] = False
            params['is_researcher'] = False
        else:
            params[current_role] = True
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
            self.network_message_label.setText(str(e))
        else:
            self.user_table.setRowContents(response['data'])
            self.network_message_label.setText(response['message'])
