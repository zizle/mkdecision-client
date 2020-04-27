# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
from PIL import Image
from PyQt5.QtWidgets import QWidget, QListWidget, QHBoxLayout, QVBoxLayout,QMessageBox, QTabWidget, QLabel, QComboBox, \
    QHeaderView, QPushButton, QTableWidgetItem, QLineEdit, QListView, QAbstractItemView, QTableWidget, QDialog, QMenu
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QUrl
from PyQt5.QtGui import QPainter, QBrush, QColor, QImage, QPixmap, QCursor, QIcon
from PyQt5.QtChart import QChartView
from popup.operator import EditUserInformationPopup, EditClientInformationPopup, CreateNewModulePopup,\
     ModuleSubsInformationPopup,CreateNewVarietyPopup, EditVarietyInformationPopup, CreateAdvertisementPopup
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import settings
from widgets.operator import ManageTable, EditButton
from widgets.base import TableCheckBox

""" 用户管理相关 """
class VarietyAuthDialog(QDialog):
    def __init__(self, user_id, *args):
        super(VarietyAuthDialog, self).__init__(*args)
        self.user_id = user_id
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("用户品种权限")
        self.setWindowIcon(QIcon("media/logo.png"))
        self.setFixedSize(1000, 600)
        layout = QVBoxLayout()
        layout.setParent(self)
        self.user_info_label = QLabel(self)
        layout.addWidget(self.user_info_label)
        self.variety_table = QTableWidget(self)
        self.variety_table.verticalHeader().hide()
        self.variety_table.cellClicked.connect(self.clickedCell_variety_table)
        layout.addWidget(self.variety_table)
        self.setLayout(layout)

    def get_varieties(self):
        try:
            r = requests.get(url=settings.SERVER_ADDR + 'variety/?way=group')
            response = json.loads(r.content.decode('utf8'))
        except Exception as e:
            pass
        else:
            self.setVarietyContents(response['variety'])

    def setVarietyContents(self, row_contents):
        print(row_contents)
        self.variety_table.clear()
        table_headers = ['序号', '品种', '权限']
        self.variety_table.setColumnCount(len(table_headers))
        self.variety_table.setHorizontalHeaderLabels(table_headers)
        self.variety_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.variety_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        current_row = 0
        for row_item in row_contents:
            self.variety_table.insertRow(current_row)
            item0 = QTableWidgetItem(str(current_row + 1))
            item0.setTextAlignment(Qt.AlignCenter)
            item0.id = row_item['id']
            self.variety_table.setItem(current_row, 0, item0)
            item1 = QTableWidgetItem(row_item['name'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.variety_table.setItem(current_row, 1, item1)
            for variety_item in row_item['subs']:
                current_row += 1
                self.variety_table.insertRow(current_row)
                item0 = QTableWidgetItem(str(current_row + 1))
                item0.setTextAlignment(Qt.AlignCenter)
                item0.id = variety_item['id']
                self.variety_table.setItem(current_row, 0, item0)
                item1 = QTableWidgetItem(variety_item['name'])
                item1.setTextAlignment(Qt.AlignCenter)
                self.variety_table.setItem(current_row, 1, item1)
                item2 = QTableWidgetItem("点击开启")
                item2.setTextAlignment(Qt.AlignCenter)
                item2.setForeground(QBrush(QColor(250,50,50)))
                self.variety_table.setItem(current_row, 2, item2)
            current_row += 1

    def getCurrentUserAccessVariety(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/' + str(self.user_id) + '/variety/'
            )
            response = json.loads(r.content.decode('utf8'))
        except Exception as e:
            pass
        else:
            user_info = response['user_info']
            userinfo_text = "用户名:" + user_info['username'] + '\t' + "手机:" + user_info['phone']
            self.setWindowTitle("【"+user_info["username"]+"】品种权限")
            self.user_info_label.setText(userinfo_text)
            # 修改权限的状态
            for variety_item in response['variety']:
                for row in range(self.variety_table.rowCount()):
                    row_vid = self.variety_table.item(row, 0).id
                    if row_vid == variety_item['variety_id'] and variety_item['is_active']:
                        item = self.variety_table.item(row, 2)
                        if item:
                            item.setText("点击关闭")
                            item.setForeground(QBrush(QColor(50,250,50)))


    def clickedCell_variety_table(self, row, col):
        if col != 2:
            return
        current_item = self.variety_table.item(row, col)
        if not current_item:
            return
        current_vid = self.variety_table.item(row, 0).id
        current_text = current_item.text()
        if current_text == "点击开启":
            is_active = 1
        else:
            is_active = 0
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'user/' + str(self.user_id) + '/variety/',
                headers={"Content-Type": "application/json;charset=utf8"},
                data=json.dumps({
                    "utoken": settings.app_dawn.value('AUTHORIZATION'),
                    "is_active": is_active,
                    "variety_id": current_vid,
                })
            )
            response = json.loads(r.content.decode('utf8'))
        except Exception as e:
            pass
        else:
            current_item.setText("点击关闭" if is_active else "点击开启")






# 显示用户表格
class UsersTable(QTableWidget):

    def __init__(self, *args, **kwargs):
        super(UsersTable, self).__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.NoFocus)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def setRowContents(self, row_contents):
        self.clear()
        table_headers = ["序号", "用户名","手机", "加入时间", "最近登录", "邮箱","角色"]
        self.setColumnCount(len(table_headers))
        self.setHorizontalHeaderLabels(table_headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.setRowCount(len(row_contents))
        for row,row_item in enumerate(row_contents):
            item0 = QTableWidgetItem(str(row + 1))
            item0.setTextAlignment(Qt.AlignCenter)
            item0.id = row_item['id']
            self.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item['username'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item1)
            item2 = QTableWidgetItem(row_item['phone'])
            item2.setTextAlignment(Qt.AlignCenter)
            self.setItem(row,2, item2)
            item3 = QTableWidgetItem(row_item['join_time'])
            item3.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 3, item3)
            item4 = QTableWidgetItem(row_item['update_time'])
            item4.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 4, item4)
            item5 = QTableWidgetItem(row_item['email'])
            item5.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 5, item5)
            item6 = QTableWidgetItem(row_item["role_text"])
            item6.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 6, item6)

    def mousePressEvent(self, event):
        if event.buttons() != Qt.RightButton:
            return
        index = self.indexAt(QPoint(event.x(), event.y()))
        current_row = index.row()
        self.setCurrentIndex(index)
        if current_row < 0 :
            return
        menu = QMenu()
        variety_auth_action = menu.addAction("品种权限")
        variety_auth_action.triggered.connect(self.setUserVarietyAuth)
        role_modify_action = menu.addAction("角色设置")
        role_modify_action.triggered.connect(self.modifyUserRole)
        menu.exec_(QCursor.pos())
        super(UsersTable, self).mousePressEvent(event)

    def setUserVarietyAuth(self):
        current_row = self.currentRow()
        user_id = self.item(current_row, 0).id
        # 弹窗设置品种权限
        popup = VarietyAuthDialog(user_id=user_id)
        popup.get_varieties()
        popup.getCurrentUserAccessVariety()
        popup.exec_()

    def modifyUserRole(self):
        def commit():
            role_num = role_combobox.currentData()
            try:
                r = requests.patch(
                    url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/',
                    headers={"Content-Type": "application/json;charset=utf8"},
                    data=json.dumps({
                        'utoken': settings.app_dawn.value("AUTHORIZATION"),
                        'role_to': role_num
                    })
                )
                response = json.loads(r.content.decode('utf8'))
                if r.status_code != 200:
                    raise ValueError(response['message'])
            except Exception as e:
                QMessageBox.information(popup, '错误', '修改错误{}'.format(e))
            else:
                QMessageBox.information(popup, '成功', "修改用户角色成功")
                self.item(current_row, 6).setText(response['role_text'])
            finally:
                popup.close()
        current_row = self.currentRow()
        username = self.item(current_row, 1).text()
        user_id = self.item(current_row, 0).id
        role_text = self.item(current_row, 6).text()
        popup = QDialog(parent=self)
        popup.setFixedSize(250, 80)
        popup.setAttribute(Qt.WA_DeleteOnClose)
        mainlayout = QVBoxLayout()
        layout = QHBoxLayout()
        popup.setWindowTitle("【"+ username+"】角色设置")
        layout.addStretch()
        layout.addWidget(QLabel("角色:", popup))
        role_combobox = QComboBox(popup)
        role_combobox.setFixedWidth(150)
        for role_item in [(1,"超级管理员"),(2,"运营管理员"),(3,"信息管理员"), (4,"研究员"),(5,"普通用户")]:
            role_combobox.addItem(role_item[1], role_item[0])
        role_combobox.setCurrentText(role_text)
        layout.addWidget(role_combobox)
        layout.addStretch()
        commit_button = QPushButton("确定")
        commit_button.clicked.connect(commit)
        mainlayout.addLayout(layout)
        mainlayout.addWidget(commit_button, alignment=Qt.AlignHCenter | Qt.AlignVCenter)
        popup.setLayout(mainlayout)
        popup.exec_()


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
        # self.users_table.network_result.connect(self.network_message.setText)
        layout.addWidget(self.users_table)
        self.setLayout(layout)
        self._addRoleComboItems()

    # 填充选择下拉框
    def _addRoleComboItems(self):
        for combo_item in [
            ('全部', 0),
            ('运营管理员', 2),  # 与后端对应
            ('信息管理员', 3),  # 与后端对应
            ('研究员', 4),  # 与后端对应
            ('普通用户', 5),
        ]:
            self.role_combo.addItem(combo_item[0], combo_item[1])

    # 获取相关用户
    def getCurrentUsers(self):
        current_data = self.role_combo.currentData()
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'users/?role_num='+str(current_data)+'&utoken=' + settings.app_dawn.value("AUTHORIZATION"),
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message.setText(str(e))
        else:
            self.network_message.setText(response['message'])
            self.users_table.setRowContents(response['users'])


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
class ModulesTable(QTableWidget):
    network_result = pyqtSignal(str)
    reload_module_data = pyqtSignal(bool)
    KEY_LABELS = [
        ('id', '序号'),
        ('name', '名称'),
    ]
    CHECK_COLUMNS = [2]

    def __init__(self, *args, **kwargs):
        super(ModulesTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setFocusPolicy(Qt.NoFocus)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.module_data = None
        self.cellClicked.connect(self.cell_item_clicked)

    # 设置表格数据
    def setRowContents(self, row_list):
        self.module_data = row_list
        self.clear()
        self.setRowCount(0)
        header_labels = ['序号', '名称', '排序']
        self.setColumnCount(len(header_labels))
        self.setHorizontalHeaderLabels(header_labels)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        current_row = 0
        for row, module_item in enumerate(self.module_data):
            self.insertRow(current_row)
            table_item0 = QTableWidgetItem(str(current_row + 1))
            table_item0.id = module_item['id']
            table_item0.setTextAlignment(Qt.AlignCenter)
            table_item0.setBackground(QBrush(QColor(218,233,231)))
            self.setItem(current_row, 0, table_item0)
            table_item1 = QTableWidgetItem(module_item['name'])
            table_item1.setTextAlignment(Qt.AlignCenter)
            table_item1.setBackground(QBrush(QColor(218,233,231)))
            self.setItem(current_row, 1, table_item1)
            current_row += 1
            for sub_module in module_item['subs']:
                self.insertRow(current_row)
                table_item0 = QTableWidgetItem(str(current_row + 1))
                table_item0.setTextAlignment(Qt.AlignCenter)
                table_item0.id = sub_module['id']
                self.setItem(current_row, 0, table_item0)
                table_item1 = QTableWidgetItem(sub_module['name'])
                table_item1.setTextAlignment(Qt.AlignCenter)
                self.setItem(current_row, 1, table_item1)
                current_row += 1


        # for row, user_item in enumerate(row_list):
        #     for col, header in enumerate(self.KEY_LABELS):
        #         if col == 0:
        #             table_item = QTableWidgetItem(str(row + 1))
        #             table_item.id = user_item[header[0]]
        #         else:
        #             table_item = QTableWidgetItem(str(user_item[header[0]]))
        #         if col in self.CHECK_COLUMNS:
        #             check_box = TableCheckBox(checked=user_item[header[0]])
        #             check_box.check_activated.connect(self.check_box_changed)
        #             self.setCellWidget(row, col, check_box)
        #         table_item.setTextAlignment(Qt.AlignCenter)
        #         self.setItem(row, col, table_item)
        #         # 增加排序控制按钮
        #         if col == len(self.KEY_LABELS) - 1:
        #             order_item = QTableWidgetItem('上移')
        #             order_item.setTextAlignment(Qt.AlignCenter)
        #             order_item.setForeground(QBrush(QColor(40, 100, 201)))
        #             self.setItem(row, col + 1, order_item)
        #         # 增加【查看子块】按钮
        #         if col == len(self.KEY_LABELS) - 1:
        #             show_subs_button = EditButton('子模块')
        #             show_subs_button.button_clicked.connect(self.show_subs_button_clicked)
        #             self.setCellWidget(row, col + 2, show_subs_button)

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

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()

    # 查看当前模块的子块
    def show_subs_button_clicked(self, edit_button):
        current_row, current_col = self.get_widget_index(edit_button)
        module_id = self.item(current_row, 0).id
        # 获取子模块
        subs_popup = None
        for module_dict_items in self.module_data:
            if module_dict_items['id'] == module_id:
                # 弹窗显示子模块信息
                subs_popup = ModuleSubsInformationPopup(
                    parent_id=module_id,
                    parent_name=module_dict_items['name'],
                    module_subs=module_dict_items['subs']
                )
                break
        if subs_popup:
            if not subs_popup.exec_():
                self.reload_module_data.emit(True)
                subs_popup.deleteLater()
                del subs_popup

    # 移动排序
    def cell_item_clicked(self, row, col):
        if col == 3:
            if row == 0:
                self.network_result.emit('已经到顶了.')
                return
            # 获取当前行的id
            current_item_id = self.item(row, 0).id
            # 上一行的item
            up_item_id = self.item(row - 1, 0).id
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
                self.network_result.emit(str(e))
            else:
                new_module_data = response['data']
                # 加入两行
                self.insertRow(row)
                self.insertRow(row)
                # 原两行删除
                self.removeRow(row + 2)
                self.removeRow(row - 1)
                # 新数据填入行 row-1, row
                for index, module_item in enumerate(new_module_data):
                    index = row - 1 if not index else row
                    for col, header in enumerate(self.KEY_LABELS):
                        if col == 0:
                            table_item = QTableWidgetItem(str(index + 1))
                            table_item.id = module_item[header[0]]
                        else:
                            table_item = QTableWidgetItem(str(module_item[header[0]]))
                        if col in self.CHECK_COLUMNS:
                            check_box = TableCheckBox(checked=module_item[header[0]])
                            check_box.check_activated.connect(self.check_box_changed)
                            self.setCellWidget(index, col, check_box)
                        table_item.setTextAlignment(Qt.AlignCenter)
                        self.setItem(index, col, table_item)
                        # 增加排序控制按钮
                        if col == len(self.KEY_LABELS) - 1:
                            order_item = QTableWidgetItem('上移')
                            order_item.setTextAlignment(Qt.AlignCenter)
                            order_item.setForeground(QBrush(QColor(40, 100, 201)))
                            self.setItem(index, col + 1, order_item)
                        # 增加【查看子块】按钮
                        if col == len(self.KEY_LABELS) - 1:
                            show_subs_button = EditButton('子模块')
                            show_subs_button.button_clicked.connect(self.show_subs_button_clicked)
                            self.setCellWidget(index, col + 2, show_subs_button)

    # 移动一行
    def move_row(self, from_row):
        if from_row <= 0:
            return
        row_count = self.rowCount()
        if from_row >= row_count - 1:
            return
        # 获取旧行的item
        item_list = list()
        for col_index in range(self.columnCount()):
            if col_index == len(self.columnCount() - 1):  # widget行
                item = self.cellWidget(from_row, col_index)
            else:
                item = self.item(from_row, col_index)
            item_list.append(item)
        print(item_list)
        # 加入新行
        self.insertRow(from_row - 1)
        # 新行加入item

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
        self.module_table.reload_module_data.connect(self.getCurrentModules)
        layout.addLayout(message_button_layout)
        layout.addWidget(self.module_table)
        self.setLayout(layout)

    # 获取系统模块信息
    def getCurrentModules(self):
        # 请求数据
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'module/?mc=' + settings.app_dawn.value('machine'),
                headers={"Content-Type":"application/json;charset=utf8"},
                data=json.dumps({
                    'utoken':settings.app_dawn.value('AUTHORIZATION')
                })

            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message.setText(str(e))
        else:
            self.network_message.setText(response['message'])
            self.module_table.setRowContents(response['modules'])

    # 新增系统模块
    def create_new_module(self):
        popup = CreateNewModulePopup(parent=self, module_combo=self.module_table.module_data)
        if not popup.exec_():
            self.getCurrentModules()


""" 品种管理相关 """

class VarietiesTable(QTableWidget):
    def __init__(self,*args, **kwargs):
        super(VarietiesTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setFocusPolicy(Qt.NoFocus)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def setRowContents(self, row_list):
        self.clear()
        self.setRowCount(0)
        header_labels = ['序号', '名称', '代码']
        self.setColumnCount(len(header_labels))
        self.setHorizontalHeaderLabels(header_labels)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        current_row = 0
        for row, variety_group in enumerate(row_list):
            self.insertRow(current_row)
            table_item0 = QTableWidgetItem(str(current_row + 1))
            table_item0.id = variety_group['id']
            table_item0.setTextAlignment(Qt.AlignCenter)
            table_item0.setBackground(QBrush(QColor(218, 233, 231)))
            self.setItem(current_row, 0, table_item0)
            table_item1 = QTableWidgetItem(variety_group['name'])
            table_item1.setTextAlignment(Qt.AlignCenter)
            table_item1.setBackground(QBrush(QColor(218, 233, 231)))
            self.setItem(current_row, 1, table_item1)
            table_item2 = QTableWidgetItem('')
            table_item2.setBackground(QBrush(QColor(218,233,231)))
            self.setItem(current_row, 2, table_item2)
            current_row += 1
            for sub_item in variety_group['subs']:
                self.insertRow(current_row)
                table_item0 = QTableWidgetItem(str(current_row + 1))
                table_item0.setTextAlignment(Qt.AlignCenter)
                table_item0.id = sub_item['id']
                self.setItem(current_row, 0, table_item0)
                table_item1 = QTableWidgetItem(sub_item['name'])
                table_item1.setTextAlignment(Qt.AlignCenter)
                self.setItem(current_row, 1, table_item1)
                table_item2 = QTableWidgetItem(sub_item['name_en'])
                table_item2.setTextAlignment(Qt.AlignCenter)
                self.setItem(current_row, 2, table_item2)
                current_row += 1

        return


#
# # 品种显示管理表格
# class VarietiesTable1(ManageTable):
#
#     KEY_LABELS = [
#         ('id', '序号'),
#         ('name', '名称'),
#         ('name_en', '英文代码'),
#         ('group', '所属组'),
#         ('is_active', '有效'),
#     ]
#     CHECK_COLUMNS = [4]
#
#     def resetTableMode(self, row_count):
#         super(VarietiesTable, self).resetTableMode(row_count)
#         self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
#         self.horizontalHeader().setSectionResizeMode(len(self.KEY_LABELS), QHeaderView.ResizeToContents)
#
#     def edit_button_clicked(self, edit_button):
#         current_row, current_col = self.get_widget_index(edit_button)
#         variety_id = self.item(current_row, 0).id
#         # print('修改品种', variety_id)
#         # 弹窗编辑信息
#         edit_popup = EditVarietyInformationPopup(variety_id=variety_id, parent=self)
#         edit_popup.getCurrentVariety()
#         if not edit_popup.exec_():
#             edit_popup.deleteLater()
#             del edit_popup
#
#     def check_box_changed(self, check_box):
#         current_row, current_col = self.get_widget_index(check_box)
#         variety_id = self.item(current_row, 0).id
#         try:
#             r = requests.put(
#                 url=settings.SERVER_ADDR + 'variety/' + str(variety_id) + '/?mc=' + settings.app_dawn.value(
#                     'machine'),
#                 headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
#                 data=json.dumps({'is_active': check_box.check_box.isChecked()})
#             )
#             response = json.loads(r.content.decode('utf-8'))
#             if r.status_code != 200:
#                 raise ValueError(response['message'])
#         except Exception as e:
#             self.network_result.emit(str(e))
#         else:
#             self.network_result.emit(response['message'])



# 品种管理页面


class VarietyManagePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(VarietyManagePage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # # 上方品种大类选择和信息提示
        combo_message_layout = QHBoxLayout()
        # # self.select_combo = QComboBox(activated=self.getCurrentVarieties)
        # # combo_message_layout.addWidget(self.select_combo)
        # self.network_message_label = QLabel()
        # combo_message_layout.addWidget(self.network_message_label)
        combo_message_layout.addStretch()
        # 新增品种按钮
        self.add_button = QPushButton('新增', clicked=self.create_new_variety)
        combo_message_layout.addWidget(self.add_button)
        layout.addLayout(combo_message_layout)
        # 下方显示管理表格
        self.variety_table = VarietiesTable(parent=self)
        layout.addWidget(self.variety_table)
        self.setLayout(layout)
        self.all_varieties = []

    # 获取品种
    def getCurrentVarieties(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'variety/?way=group',
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.all_varieties = response['variety']
            self.variety_table.setRowContents(response['variety'])

    # 新增品种
    def create_new_variety(self):
        groups = [(group_item['id'], group_item['name']) for group_item in self.all_varieties]
        popup = CreateNewVarietyPopup(parent=self, groups=groups)
        popup.exec_()


""" 运营数据分析相关 """


# 客户端记录表格显示
class ClientRecordTable(ManageTable):
    KEY_LABELS = [
        ('day', '日期'),
        ('client_name', '客户端'),
        ('category', '类型'),
        ('day_count', '开启次数'),
    ]

    # 设置表格数据
    def setRowContents(self, row_list):
        client_combo = dict()
        self.resetTableMode(len(row_list))
        for row, client_item in enumerate(row_list):
            for col, header in enumerate(self.KEY_LABELS):
                table_item = QTableWidgetItem(str(client_item[header[0]]))
                if col in self.CHECK_COLUMNS:
                    check_box = TableCheckBox(checked=client_item[header[0]])
                    check_box.check_activated.connect(self.check_box_changed)
                    self.setCellWidget(row, col, check_box)
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
            if client_item['client'] not in client_combo.keys():
                client_combo[client_item['client']] = client_item['client_name']
        return client_combo

    # 填充数据前初始化表格
    def resetTableMode(self, row_count):
        self.clear()
        self.setRowCount(row_count)
        self.setColumnCount(len(self.KEY_LABELS))
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)


# 模块记录表格显示
class ModuleRecordTable(ManageTable):
    KEY_LABELS = [
        ('day', '日期'),
        ('user_note', '用户'),
        ('module', '模块'),
        ('day_count', '访问次数'),
    ]

    # 设置表格数据
    def setRowContents(self, row_list):
        # 保存用户的选项
        user_combo = dict()
        self.resetTableMode(len(row_list))
        for row, user_item in enumerate(row_list):
            for col, header in enumerate(self.KEY_LABELS):
                table_item = QTableWidgetItem(str(user_item[header[0]]))
                if col in self.CHECK_COLUMNS:
                    check_box = TableCheckBox(checked=user_item[header[0]])
                    check_box.check_activated.connect(self.check_box_changed)
                    self.setCellWidget(row, col, check_box)
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
            # 加入用户选择的资料
            if user_item['user'] not in user_combo.keys():
                user_combo[user_item['user']] = user_item['user_note']
        return user_combo

    # 填充数据前初始化表格
    def resetTableMode(self, row_count):
        self.clear()
        self.setRowCount(row_count)
        self.setColumnCount(len(self.KEY_LABELS))
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)


# 数据查看主页
class OperateManagePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(OperateManagePage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        option_layout = QHBoxLayout()
        option_layout.addWidget(QPushButton('客户端数据', objectName='clientBtn',
                                            cursor=Qt.PointingHandCursor, clicked=self.getClientRecord))
        option_layout.addWidget(QPushButton('模块数据',
                                            objectName='moduleBtn',
                                            cursor=Qt.PointingHandCursor, clicked=self.getModuleRecord))
        option_layout.addStretch()
        line_edit = QLineEdit(readOnly=True)
        line_edit.setAlignment(Qt.AlignCenter)
        # 客户端记录
        self.client_combo = QComboBox(objectName='clientCombo', activated=self.getClientRecord)
        self.client_combo.setLineEdit(line_edit)
        option_layout.addWidget(self.client_combo)
        # 模块记录
        line_edit = QLineEdit(readOnly=True)  # 新实例化，不能共用
        line_edit.setAlignment(Qt.AlignCenter)
        self.user_combo = QComboBox(objectName='userCombo', activated=self.getModuleRecord)
        self.user_combo.setLineEdit(line_edit)
        option_layout.addWidget(self.user_combo)
        layout.addLayout(option_layout)
        self.record_chart_view = QChartView()  # 图表
        self.record_chart_view.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        self.client_table_view = ClientRecordTable()
        self.module_table_view = ModuleRecordTable()
        # layout.addWidget(self.record_chart_view)
        layout.addWidget(self.client_table_view)
        layout.addWidget(self.module_table_view)
        self.module_table_view.hide()
        self.setLayout(layout)
        self.setStyleSheet("""
        #clientBtn,#moduleBtn{
            border:none;
            color: rgb(75,175,190);
            padding: 1px;
            margin: 5px
        }
        #userCombo QAbstractItemView::item{
            height:22px;
            font-size:13px;
            color: rgb(22,212,126)
        }
        #clientCombo QAbstractItemView::item{
            height:22px;
            font-size:13px;
            color: rgb(22,212,126)
        }
        """)
        self.user_combo.setView(QListView())
        self.client_combo.setView(QListView())
        self.client_combo.hide()
        self.user_combo.hide()

    # 获取客户端数据记录
    def getClientRecord(self):
        print('请求客户端记录')
        current_client = self.client_combo.currentData()
        url = settings.SERVER_ADDR + 'client_record/?mc=' + settings.app_dawn.value('machine')
        if current_client:
            url += '&client=' + str(current_client)
        try:
            r = requests.get(
                url=url,
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            self.module_table_view.hide()
            self.user_combo.hide()
            self.client_table_view.show()
            self.client_combo.show()
            response_data = response['data']
            # print(response_data)
            client_combo_list = self.client_table_view.setRowContents(response_data)
            # self.draw_chart()
            # print(client_combo_list)
            # 在没有带客户端请求的时候才执行这些
            if not current_client:
                self.client_combo.clear()
                self.client_combo.addItem('全部', None)  # 加入全部的选项
                for client_id, client_name in client_combo_list.items():
                    self.client_combo.addItem(client_name, client_id)
                for i in range(self.client_combo.count()):
                    self.client_combo.view().model().item(i).setTextAlignment(Qt.AlignCenter)
                # 设置下拉框的大小
                self.client_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    # 获取模块数据记录
    def getModuleRecord(self):
        current_user = self.user_combo.currentData()
        url = settings.SERVER_ADDR + 'module_record/?mc=' + settings.app_dawn.value('machine')
        if current_user:
            url += '&user=' + str(current_user)
        try:
            r = requests.get(
                url=url,
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            self.client_table_view.hide()
            self.client_combo.hide()
            self.module_table_view.show()
            self.user_combo.show()
            response_data = response['data']
            user_combo_list = self.module_table_view.setRowContents(response_data)
            # self.draw_chart()
            # 在没有带用户请求的时候才执行这些
            if not current_user:
                self.user_combo.clear()
                self.user_combo.addItem('全部', None)  # 加入全部的选项
                for user_id, user_note in user_combo_list.items():
                    self.user_combo.addItem(user_note, user_id)
                for i in range(self.user_combo.count()):
                    self.user_combo.view().model().item(i).setTextAlignment(Qt.AlignCenter)
                # 设置下拉框的大小
                self.user_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)


""" 广告设置 """


# 查看图片按钮
class TableImageReadButton(QPushButton):
    button_clicked = pyqtSignal(QPushButton)

    def __init__(self, *args, **kwargs):
        super(TableImageReadButton, self).__init__(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(lambda: self.button_clicked.emit(self))
        self.setObjectName('tableDelete')
        self.setStyleSheet("""
        #tableDelete{
            border: none;
            padding: 1px 8px;
            color: rgb(100,150,180);
        }
        #tableDelete:hover{
            color: rgb(120,130,230)
        }
        """)


# 广告展示表格
class AdvertisementTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '标题'),
        ('create_time', '创建日期'),
    ]

    def __init__(self, *args, **kwargs):
        super(AdvertisementTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.cellClicked.connect(self.clickedCellEvent)

    def showRowContens(self, advertisement_list):
        self.clear()
        table_headers = ['序号', '创建日期','图片','内容']
        self.setColumnCount(len(table_headers))
        self.setHorizontalHeaderLabels(table_headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, row_item in enumerate(advertisement_list):
            self.insertRow(row)
            item0 = QTableWidgetItem(str(row + 1))
            item0.setTextAlignment(Qt.AlignCenter)
            item0.id = row_item['id']
            self.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item['create_time'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item1)
            item2 = QTableWidgetItem("查看")
            item2.image_url = row_item['image_url']
            item2.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, item2)
            item3 = QTableWidgetItem("查看")
            item3.file_url = row_item['file_url']
            item3.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 3, item3)


    def clickedCellEvent(self, row, col):
        if col == 2: # 查看图片
            item = self.item(row, col)
            image_url = item.image_url
            popup = QDialog(parent=self)
            popup.setFixedSize(660, 330)
            popup.setWindowTitle('图片')
            popup.setAttribute(Qt.WA_DeleteOnClose)
            layout = QVBoxLayout(popup)
            r = requests.get(url=settings.STATIC_PREFIX + image_url)
            image_label = QLabel(popup)
            image_label.setPixmap(QPixmap.fromImage(QImage.fromData(r.content)))
            image_label.setScaledContents(True)
            layout.addWidget(image_label)
            popup.setLayout(layout)
            popup.exec_()
        elif col == 3: # 查看内容
            item = self.item(row, col)
            file_url = item.file_url
            from widgets.base import PDFContentPopup
            popup = PDFContentPopup(title='广告内容',file=settings.STATIC_PREFIX + file_url)
            popup.exec_()
        else:
            pass

    # 查看图片
    def read_image_clicked(self, image_button):
        image_url = image_button.image
        popup = QDialog(parent=self)
        popup.setWindowTitle('广告的图片')
        layout = QVBoxLayout(margin=0)
        image_label = QLabel()
        r = requests.get(url=settings.STATIC_PREFIX + image_url)
        img = QImage.fromData(r.content)
        image_label.setPixmap(QPixmap.fromImage(img))
        image_label.setScaledContents(True)
        layout.addWidget(image_label)
        popup.setLayout(layout)
        self.network_result.emit('获取图片成功!')
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 查看内容
    def read_button_clicked(self, read_button):
        current_row, _ = self.get_widget_index(read_button)
        ad_id = self.item(current_row, 0).id
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/advertise/' + str(ad_id) + '/',
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            # 根据具体情况显示内容
            ad_data = response['data']
            self.network_result.emit(response['message'])
            if ad_data['file']:
                # 显示文件
                file = settings.STATIC_PREFIX + ad_data['file']
                popup = PDFContentPopup(title=ad_data['name'], file=file, parent=self)
            else:
                popup = TextContentPopup(title=ad_data['name'], content=ad_data['content'], parent=self)  # 显示内容
            if not popup.exec_():
                popup.deleteLater()
                del popup

    # 删除本条广告
    def delete_button_clicked(self, delete_button):
        def delete_row_advertisement():
            current_row, _ = self.get_widget_index(delete_button)
            ad_id = self.item(current_row, 0).id
            # 发起删除公告请求
            try:
                r = requests.delete(
                    url=settings.SERVER_ADDR + 'home/advertise/' + str(ad_id) + '/?mc=' + settings.app_dawn.value(
                        'machine'),
                    headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')}
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 200:
                    raise ValueError(response['message'])
            except Exception as e:
                self.network_result.emit(str(e))
            else:
                self.network_result.emit(response['message'])
                popup.close()
                # 移除本行
                self.removeRow(current_row)
        # 警示框
        popup = WarningPopup(parent=self)
        popup.confirm_button.connect(delete_row_advertisement)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()



# 广告设置
class AdvertisementPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(AdvertisementPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0, spacing=2)
        # 信息展示与新增按钮
        message_button_layout = QHBoxLayout()
        self.network_message_label = QLabel(self)
        message_button_layout.addWidget(self.network_message_label)
        message_button_layout.addWidget(QPushButton('新增', clicked=self.create_advertisement), alignment=Qt.AlignRight)
        layout.addLayout(message_button_layout)
        # 当前数据显示表格
        self.advertisement_table = AdvertisementTable()
        self.advertisement_table.network_result.connect(self.network_message_label.setText)
        layout.addWidget(self.advertisement_table)
        self.setLayout(layout)

    # 新增广告
    def create_advertisement(self):
        popup = CreateAdvertisementPopup(parent=self)
        popup.exec_()


    # 获取广告数据
    def getAdvertisements(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'ad/',
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            print(response)
            self.advertisement_table.showRowContens(response['adments'])
            self.network_message_label.setText(response['message'])





""" 运营管理主页 """


# 运营管理主页
class OperatorMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(OperatorMaintain, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=2)
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
        # u'运营数据', u'用户管理', u'客户端管理',
        self.operate_list.addItems([u'用户管理', u'功能管理', u'品种管理', u'广告管理'])

    # 点击左侧管理菜单
    def operate_list_clicked(self):
        text = self.operate_list.currentItem().text()
        # if text == u'运营数据':
        #     tab = OperateManagePage(parent=self)
        if text == u'用户管理':
            tab = UserManagePage(parent=self)
            tab.getCurrentUsers()
        # elif text == u'客户端管理':
        #     tab = ClientManagePage(parent=self)
        #     tab.getCurrentClients()
        elif text == u'功能管理':
            tab = ModuleManagePage(parent=self)
            tab.getCurrentModules()
        elif text == u'品种管理':
            tab = VarietyManagePage(parent=self)
            tab.getCurrentVarieties()
        elif text == u'广告管理':
            tab = AdvertisementPage(parent=self)
            tab.getAdvertisements()
        else:
            tab = QLabel(parent=self,
                         styleSheet='font-size:16px;font-weight:bold;color:rgb(230,50,50)',
                         alignment=Qt.AlignCenter)
            tab.setText("「" + text + "」正在加紧开放中...")
        self.frame_tab.clear()
        self.frame_tab.addTab(tab, text)
