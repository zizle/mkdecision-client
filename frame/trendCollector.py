# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QComboBox, QTableWidget, \
    QPushButton, QAbstractItemView, QHeaderView, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
import settings
from widgets.base import LoadedPage, TableRowReadButton, TableRowDeleteButton, TableCheckBox
from popup.trendCollector import CreateNewTrendTablePopup, ShowTableDetailPopup, EditTableDetailPopup, CreateNewVarietyChartPopup, \
    ShowChartPopup


""" 数据表管理相关 """


# 数据表显示表格
class TrendDataTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '名称'),
        ('start_date', '起始时间'),
        ('end_date', '结束时间'),
        ('update_time', '最近更新'),
        ('editor', '更新者'),
        ('group', '所属组'),
    ]

    def __init__(self, *args, **kwargs):
        super(TrendDataTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS) + 2)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + ['', ''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        for row, content_item in enumerate(row_list):
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = content_item[header[0]]
                else:
                    table_item = QTableWidgetItem(str(content_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
                if col == len(self.KEY_LABELS) - 1:
                    # 增加【查看】按钮
                    read_button = TableRowReadButton('查看')
                    read_button.button_clicked.connect(self.read_button_clicked)
                    self.setCellWidget(row, col + 1, read_button)
                    # 增加【编辑】按钮
                    edit_button = TableRowReadButton('编辑')
                    edit_button.button_clicked.connect(self.edit_button_clicked)
                    self.setCellWidget(row, col + 2, edit_button)

    # 查看表详细数据
    def read_button_clicked(self, read_button):
        current_row, _ = self.get_widget_index(read_button)
        table_id = self.item(current_row, 0).id
        table_text = self.item(current_row, 1).text()
        # 获取表详细数据
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/table/' + str(table_id) + '/?look=1&mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            popup = ShowTableDetailPopup(parent=self)
            popup.setWindowTitle(table_text)
            popup.showTableData(headers=response['data']['header_data'], table_contents=response['data']['table_data'])
            self.network_result.emit(response['message'])
            if not popup.exec_():
                popup.deleteLater()
                del popup

    # 编辑详情表格
    def edit_button_clicked(self, edit_button):
        current_row, _ = self.get_widget_index(edit_button)
        table_id = self.item(current_row, 0).id
        table_text = self.item(current_row, 1).text()
        # 获取表详细数据最后20条
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/table/' + str(table_id) + '/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')}
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            popup = EditTableDetailPopup(table_id=table_id, parent=self)
            popup.setWindowTitle(table_text)
            table_contents = response['data']['table_data']
            table_contents.reverse()
            popup.showTableData(headers=response['data']['header_data'], table_contents=table_contents)
            self.network_result.emit(response['message'])
            if not popup.exec_():
                popup.deleteLater()
                del popup

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 数据表管理页面
class TrendTableManagePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(TrendTableManagePage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 品种三联动菜单
        combo_link_layout = QHBoxLayout(spacing=2)
        combo_link_layout.addWidget(QLabel('类别:'))
        self.variety_group_combo = QComboBox(activated=self.getCurrentVarieties)
        combo_link_layout.addWidget(self.variety_group_combo)
        combo_link_layout.addWidget(QLabel('品种:'))
        self.variety_combo = QComboBox(activated=self.getCurrentTrendGroup)
        combo_link_layout.addWidget(self.variety_combo)
        combo_link_layout.addWidget(QLabel('数据:'))
        self.table_group_combo = QComboBox(activated=self.getCurrentTrendTable)
        combo_link_layout.addWidget(self.table_group_combo)
        # 网络请求信息
        self.network_message_label = QLabel()
        combo_link_layout.addWidget(self.network_message_label)
        combo_link_layout.addStretch()
        # 新建表
        self.create_trend_table = QPushButton('新建表', clicked=self.create_new_trend_table)
        combo_link_layout.addWidget(self.create_trend_table, alignment=Qt.AlignRight)
        layout.addLayout(combo_link_layout)
        # 数据表显示
        self.trend_data_table = TrendDataTable()
        self.trend_data_table.network_result.connect(self.network_message_label.setText)
        layout.addWidget(self.trend_data_table)
        self.setLayout(layout)

    # 获取品种分组
    def getGroups(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'group-varieties/?mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.variety_group_combo.clear()
            self.variety_combo.clear()
            self.table_group_combo.clear()
            for index, group_item in enumerate(response['data']):
                self.variety_group_combo.addItem(group_item['name'], group_item['id'])
                if index == 0:  # 填充第一个品种组下的品种数据(初始化时少一次网络请求)
                    for variety_item in group_item['varieties']:
                        self.variety_combo.addItem(variety_item['name'], variety_item['id'])
            self.network_message_label.setText(response['message'])

    # 当前组下的品种(当组点击时调用)
    def getCurrentVarieties(self):
        current_gid = self.variety_group_combo.currentData()
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'group-varieties/'+str(current_gid)+'/?mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.variety_combo.clear()
            self.table_group_combo.clear()
            for variety_item in response['data']:
                self.variety_combo.addItem(variety_item['name'], variety_item['id'])
            self.network_message_label.setText(response['message'])

    # 获取当前品种下的数据组
    def getCurrentTrendGroup(self):
        current_vid = self.variety_combo.currentData()
        if not current_vid:
            return
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/' + str(current_vid) + '/group-tables/?mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.table_group_combo.clear()
            self.table_group_combo.addItem('全部', 0)  # 填充第一个为【全部】
            # 记录最长的的下拉选择
            max_length_text = 2
            # 整理所有的表数据填充显示表格(减少初始化一次网络请求)
            all_tables = list()
            for group_item in response['data']:
                self.table_group_combo.addItem(group_item['name'], group_item['id'])
                # 调整宽度
                if len(group_item['name']) > max_length_text:
                    max_length_text = len(group_item['name'])
                all_tables += group_item['tables']
            self.table_group_combo.view().setFixedWidth(max_length_text*12)
            # 放到表格展示
            self.trend_data_table.showRowContents(all_tables)
            self.network_message_label.setText(response['message'])

    # 获取当前数据组下的所有数据表(当数据组点击时调用)
    def getCurrentTrendTable(self):
        current_gid = self.table_group_combo.currentData()
        if current_gid is None:
            return
        if current_gid == 0:  # 获取当前品种所有分组及表
            self.getCurrentTrendGroup()
            return
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/group/' + str(current_gid) + '/table/?mc=' + settings.app_dawn.value(
                    'machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.trend_data_table.showRowContents(response['data'])
            self.network_message_label.setText(response['message'])

    # 新建数据表
    def create_new_trend_table(self):
        popup = CreateNewTrendTablePopup(parent=self)
        popup.getVarietyTableGroups()  # 获取左侧内容
        if not popup.exec_():
            popup.deleteLater()
            del popup


""" 品种图表管理相关 """


# 显示图表信息的表格
class VarietyChartsInfoTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '图表名称'),
        ('variety', '所属品种'),
        ('is_top', '主页展示'),
        ('is_show', '品种页展示'),
        ('creator', '创建者'),
    ]

    COLUMNS_CHECKED = [3, 4]

    def __init__(self, *args, **kwargs):
        super(VarietyChartsInfoTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS) + 2)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + ['', ''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        for row, content_item in enumerate(row_list):
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = content_item[header[0]]
                else:
                    table_item = QTableWidgetItem(str(content_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
                if col in self.COLUMNS_CHECKED:  # 复选框按钮
                    check_button = TableCheckBox(checked=content_item[header[0]])
                    check_button.check_activated.connect(self.checked_button_changed)
                    self.setCellWidget(row, col, check_button)
                if col == len(self.KEY_LABELS) - 1:
                    # 增加【查看】按钮
                    read_button = TableRowReadButton('查看图表')
                    read_button.button_clicked.connect(self.read_button_clicked)
                    self.setCellWidget(row, col + 1, read_button)
                    # # 增加【删除】按钮
                    delete_button = TableRowDeleteButton('删除')
                    delete_button.button_clicked.connect(self.delete_button_clicked)
                    self.setCellWidget(row, col + 2, delete_button)

    # 查看图表
    def read_button_clicked(self, read_button):
        current_row, _ = self.get_widget_index(read_button)
        chart_id = self.item(current_row, 0).id
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/chart/' + str(chart_id) + '/?mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            # 弹窗显示图表
            popup = ShowChartPopup(chart_data=response['data'], parent=self)
            if not popup.exec_():
                popup.deleteLater()
                del popup

    # 删除一张图表
    def delete_button_clicked(self, delete_button):
        current_row, _ = self.get_widget_index(delete_button)
        chart_id = self.item(current_row, 0).id
        try:
            r = requests.delete(
                url=settings.SERVER_ADDR + 'trend/chart/' + str(chart_id) + '/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')}
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            self.removeRow(current_row)

    # 主页显示复选框状态
    def checked_button_changed(self, checked_button):
        current_row, current_column = self.get_widget_index(checked_button)
        chart_id = self.item(current_row, 0).id
        operate = self.KEY_LABELS[current_column][0]
        # 请求改变主页展示状态
        try:
            r = requests.patch(
                url=settings.SERVER_ADDR + 'trend/chart/' + str(chart_id) + '/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({operate: checked_button.check_box.isChecked()})
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


# 品种图表管理主页
class VarietyChartsManagePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(VarietyChartsManagePage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 品种选择
        select_variety_layout = QHBoxLayout()
        select_variety_layout.addWidget(QLabel('分类:'))
        self.variety_group_combo = QComboBox(activated=self.getCurrentVarieties)
        select_variety_layout.addWidget(self.variety_group_combo)
        select_variety_layout.addWidget(QLabel('品种:'))
        self.variety_combo = QComboBox(activated=self.getCurrentVarietyCharts)
        select_variety_layout.addWidget(self.variety_combo)
        self.network_message_label = QLabel()
        select_variety_layout.addWidget(self.network_message_label)
        select_variety_layout.addStretch()
        # 新增按钮
        self.create_chart_button = QPushButton('新增', clicked=self.create_variety_chart)
        select_variety_layout.addWidget(self.create_chart_button)
        layout.addLayout(select_variety_layout)
        # 显示信息的表格
        self.chart_info_table = VarietyChartsInfoTable()
        self.chart_info_table.network_result.connect(self.network_message_label.setText)
        layout.addWidget(self.chart_info_table)
        self.setLayout(layout)

    # 请求组
    def getGroups(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'group-varieties/?mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.variety_group_combo.clear()
            self.variety_combo.clear()
            for index, group_item in enumerate(response['data']):
                self.variety_group_combo.addItem(group_item['name'], group_item['id'])
                if index == 0:  # 填充第一个品种组下的品种数据(初始化时少一次网络请求)
                    for variety_item in group_item['varieties']:
                        self.variety_combo.addItem(variety_item['name'], variety_item['id'])
            self.network_message_label.setText(response['message'])

    # 当前组下的品种(当组点击时调用)
    def getCurrentVarieties(self):
        current_gid = self.variety_group_combo.currentData()
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'group-varieties/' + str(
                    current_gid) + '/?mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.variety_combo.clear()
            for variety_item in response['data']:
                self.variety_combo.addItem(variety_item['name'], variety_item['id'])
            self.network_message_label.setText(response['message'])

    # 获取当前品种的所有图表
    def getCurrentVarietyCharts(self):
        current_vid = self.variety_combo.currentData()
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/' + str(
                    current_vid) + '/chart/?all=1&mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.chart_info_table.showRowContents(response['data'])
            self.network_message_label.setText(response['message'])

    # 新增品种页图表
    def create_variety_chart(self):
        current_variety = self.variety_combo.currentText()
        current_vid = self.variety_combo.currentData()
        # 弹窗设置
        popup = CreateNewVarietyChartPopup(variety_id=current_vid, variety_text=current_variety, parent=self)
        popup.getCurrentVarietyTables()
        if not popup.exec_():
            popup.deleteLater()
            del popup


# 数据分析管理主页
class TrendPageCollector(QWidget):
    def __init__(self, *args, **kwargs):
        super(TrendPageCollector, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0)
        # 左侧管理菜单列表
        self.left_list = QListWidget(clicked=self.left_list_clicked)
        layout.addWidget(self.left_list, alignment=Qt.AlignLeft)
        # 右侧显示的frame
        self.frame_loaded = LoadedPage(parent=self)
        layout.addWidget(self.frame_loaded)
        self.setLayout(layout)
        self._addLeftListMenu()

    # 添加左侧管理菜单
    def _addLeftListMenu(self):
        for item in [u'数据表管理', '图表管理']:
            self.left_list.addItem(QListWidgetItem(item))

    # 点击左侧菜单列表
    def left_list_clicked(self):
        text = self.left_list.currentItem().text()
        if text == u'数据表管理':
            frame_page = TrendTableManagePage(parent=self.frame_loaded)
            frame_page.getGroups()  # 获取当前分组（连带品种,可填充第一个组的品种）
            frame_page.getCurrentTrendGroup()  # 获取当前品种下的数据组
            frame_page.getCurrentTrendTable()  # 获取当前数据组下的数据表
        elif text == u'图表管理':
            frame_page = VarietyChartsManagePage(parent=self.frame_loaded)
            frame_page.getGroups()  # 获取当前品种组
            frame_page.getCurrentVarietyCharts()  # 获取当前的品种下的数据表
        else:
            frame_page = QLabel('【' + text + '】正在加紧开发中...')
        self.frame_loaded.clear()
        self.frame_loaded.addWidget(frame_page)


