# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
import pandas as pd
from PyQt5.QtWidgets import QWidget, QListWidget, QHBoxLayout, QVBoxLayout, QTabWidget, QLabel, QComboBox, \
    QHeaderView, QPushButton, QTableWidgetItem
from PyQt5.QtCore import Qt, QMargins, QDateTime
from PyQt5.QtGui import QFont, QPainter
from PyQt5.QtChart import QChartView, QChart, QLineSeries, QBarSeries, QBarSet, QDateTimeAxis, QValueAxis
from popup.operator import EditUserInformationPopup, EditClientInformationPopup, CreateNewModulePopup,\
    EditModuleInformationPopup, CreateNewVarietyPopup, EditVarietyInformationPopup
import settings
from widgets.operator import ManageTable
from widgets.base import TableCheckBox

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


""" 运营数据分析相关 """


# 客户端记录表格显示
class ClientRecordTable(ManageTable):
    KEY_LABELS = [
        ('day', '日期'),
        ('client', '客户端'),
        ('category', '类型'),
        ('day_count', '开启次数'),
    ]

    # 设置表格数据
    def setRowContents(self, row_list):
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

    # 填充数据前初始化表格
    def resetTableMode(self, row_count):
        self.clear()
        self.setRowCount(row_count)
        self.setColumnCount(len(self.KEY_LABELS))
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


# 模块记录表格显示
class ModuleRecordTable(ManageTable):
    KEY_LABELS = [
        ('day', '日期'),
        ('user', '用户'),
        ('module', '模块'),
        ('day_count', '访问次数'),
    ]

    # 设置表格数据
    def setRowContents(self, row_list):
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

    # 填充数据前初始化表格
    def resetTableMode(self, row_count):
        self.clear()
        self.setRowCount(row_count)
        self.setColumnCount(len(self.KEY_LABELS))
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


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
        """)

    # 获取客户端数据记录
    def getClientRecord(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'client_record/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            self.module_table_view.hide()
            self.client_table_view.show()
            self.client_table_view.setRowContents(response['data'])
            # self.draw_chart()

    # 获取模块数据记录
    def getModuleRecord(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'module_record/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            self.client_table_view.hide()
            self.module_table_view.show()
            self.module_table_view.setRowContents(response['data'])
            # self.draw_chart()

    # 画图展示
    def draw_chart(self):
        # 获取图表数据(客户端记录使用折线图， 模块记录采用柱形图，每个客户端一个DataFrame)
        # 画图
        chart = QChart()
        chart.layout().setContentsMargins(0, 0, 0, 0)  # chart的外边距
        chart.setMargins(QMargins(15, 5, 15, 0))
        if self.client_table_view.isHidden():  # 模块记录显示
            chart.setTitle('模块被访问次数统计图')
            self.record_chart_view.hide()

        elif self.module_table_view.isHidden():  # 客户端记录显示
            self.record_chart_view.show()
            # 获取数据
            rows = self.client_table_view.rowCount()
            cols = self.client_table_view.columnCount()
            data_dict = dict()
            for row in range(rows):
                row_content = list()
                row_key = ''
                for col in range(cols):
                    text = self.client_table_view.item(row, col).text()
                    if col == 1:
                        row_key = text
                        if text not in data_dict.keys():
                            data_dict[text] = list()
                    row_content.append(text)
                data_dict[row_key].append(row_content)
            chart.setTitle('客户端打开次数折线图')
            try:
                for key, value in data_dict.items():
                    chart_df = pd.DataFrame(value)
                    chart_df[0] = pd.to_datetime(chart_df[0])
                    chart_df.sort_values(by=0, inplace=True)  # 时间排序
                    chart_df[3] = chart_df[3].apply(lambda x: float(x))
                    # 计算处理x轴数据
                    x_axis_data = chart_df.iloc[:, [0]]  # 取得第一列数据
                    min_x, max_x = x_axis_data.min(0).tolist()[0], x_axis_data.max(0).tolist()[0]  # 第一列时间数据(x轴)的最大值和最小值
                    line_data = chart_df.iloc[:, [0, 3]]
                    series = QLineSeries()
                    series.setName(key)
                    for point_item in line_data.values.tolist():
                        series.append(QDateTime(point_item[0]).toMSecsSinceEpoch(), point_item[1])  # 取出源数据后一条线就2列数据
                    chart.addSeries(series)
                # chart.createDefaultAxes()
                # 设置X轴文字格式
                axis_X = QDateTimeAxis()
                # axis_X = chart.axisX()
                # axis_X.setRange(min_x, max_x)
                axis_X.setFormat('yyyy-MM-dd')
                axis_X.setLabelsAngle(-90)
                font = QFont()
                font.setPointSize(7)
                axis_X.setLabelsFont(font)
                axis_X.setGridLineVisible(False)
                # 设置Y轴
                axix_Y = QValueAxis()
                axix_Y.setLabelsFont(font)
                axix_Y.setLabelFormat('%i')
                series = chart.series()[0]
                for series in chart.series():
                    chart.setAxisX(axis_X, series)
                    chart.setAxisY(axix_Y, series)
                # min_y, max_y = 0, int(chart.axisY().max())
                # # 根据位数取整数
                # axix_Y.setRange(min_y, max_y)
                # axix_Y.setLabelFormat('%i')
                # chart.setAxisY(axix_Y, series)
            except Exception:
                pass
        else:
            pass
        self.record_chart_view.setChart(chart)



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
        self.operate_list.addItems([u'运营数据', u'用户管理', u'客户端管理', u'模块管理', u'品种管理'])

    # 点击左侧管理菜单
    def operate_list_clicked(self):
        text = self.operate_list.currentItem().text()
        if text == u'运营数据':
            tab = OperateManagePage(parent=self)
        elif text == u'用户管理':
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
        self.frame_tab.clear()
        self.frame_tab.addTab(tab, text)
