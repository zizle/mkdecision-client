# _*_ coding:utf-8 _*_
# __Author__： zizle
import os
import re
import xlrd
import json
import datetime
import requests
import pickle
import pandas as pd
import pyecharts.options as opts
from pyecharts.charts import Line, Bar, Page
from PyQt5.QtWidgets import QApplication,QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QComboBox, QTableWidget, \
    QPushButton, QAbstractItemView, QHeaderView, QTableWidgetItem, QDialog, QMessageBox, QLineEdit, QFileDialog,QMenu, QGroupBox, QCheckBox, QScrollArea, QGridLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QUrl
from PyQt5.QtGui import QCursor
import settings
from widgets.base import LoadedPage, TableRowReadButton, TableRowDeleteButton, TableCheckBox
from popup.trendCollector import CreateNewTrendTablePopup, ShowTableDetailPopup, EditTableDetailPopup, CreateNewVarietyChartPopup, \
    ShowChartPopup
from settings import BASE_DIR


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
        ('origin_note', '数据来源'),
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
            # max_length_text = 2
            # 整理所有的表数据填充显示表格(减少初始化一次网络请求)
            all_tables = list()
            for group_item in response['data']:
                self.table_group_combo.addItem(group_item['name'], group_item['id'])
                # 调整宽度
                # if len(group_item['name']) > max_length_text:
                #     max_length_text = len(group_item['name'])
                all_tables += group_item['tables']
            # self.table_group_combo.view().setFixedWidth(max_length_text*12)
            self.table_group_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
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
        if not current_vid:
            return
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


class ReviewTable(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(ReviewTable, self).__init__(*args, **kwargs)
        self.setHorizontalHeaderLabels(['列头1'])
        self.horizontalHeader().sectionDoubleClicked.connect(self.horizontalHeaderClicked)

    def horizontalHeaderClicked(self, header_column):
        if header_column == -1:
            return

        def set_header_text():
            text = edit.text().strip()
            if text:
                header_item.setText(text)
            popup.close()
        header_item = self.horizontalHeaderItem(header_column)
        if not header_item:
            return
        popup = QDialog(self)
        popup.setWindowTitle("新列名")
        popup.setAttribute(Qt.WA_DeleteOnClose)
        layout = QVBoxLayout(popup)
        edit = QLineEdit(header_item.text(),popup)
        edit.setFocus()
        layout.addWidget(edit)
        layout.addWidget(QPushButton('确定', popup, clicked=set_header_text))
        popup.exec_()

    def insert_new_row(self):
        self.insertRow(self.rowCount())

    def insert_new_column(self):
        headers = []
        for col in range(self.columnCount()):
            headers.append(self.horizontalHeaderItem(col).text())
        headers.append("列头" + str(self.columnCount() + 1))
        self.insertColumn(self.columnCount())
        self.setHorizontalHeaderLabels(headers)

    def set_horizon_header_labels(self, labels):
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(len(labels))
        self.setHorizontalHeaderLabels(labels)

    def add_row_content(self, row, content):
        self.insertRow(row)
        for col,item in enumerate(content):
            self.setItem(row,col, QTableWidgetItem(str(item)))

    def values(self):
        headers = list()
        contents = list()
        for header_col in range(self.columnCount()):
            headers.append(self.horizontalHeaderItem(header_col).text())
        for row in range(self.rowCount()):
            row_content = list()
            for col in range(self.columnCount()):
                item = self.item(row, col)
                text = item.text() if item else ''
                row_content.append(text)
            if row_content:
                contents.append(row_content)
        return {
            'headers': headers,
            'contents': contents
        }


class NewTrendTablePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(NewTrendTablePage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("品种:", self))
        self.variety_combobox = QComboBox(self)

        options_layout.addWidget(self.variety_combobox)
        options_layout.addWidget(QLabel("数据组:", self))
        self.vtable_group = QComboBox(self)
        options_layout.addWidget(self.vtable_group)
        # 新增数据组
        self.add_new_tgroup = QPushButton("新建组?",self, clicked=self.create_new_group)
        options_layout.addWidget(self.add_new_tgroup)
        options_layout.addStretch()
        options_layout.addWidget(QLabel("数据时间基准:", self))
        self.date_standard = QComboBox(self)
        self.date_standard.addItem("年-月-日", 0)
        self.date_standard.addItem("年-月", 1)
        self.date_standard.addItem("年", 2)
        options_layout.addWidget(self.date_standard)
        options_layout.addWidget(QPushButton("文件", self, clicked=self.review_file_data))
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("标题:", self))
        self.title_edit = QLineEdit(self)
        info_layout.addWidget(self.title_edit)
        info_layout.addWidget(QLabel("数据来源:", self))
        self.origin_edit = QLineEdit(self)
        info_layout.addWidget(self.origin_edit)
        info_layout.addStretch()
        layout.addLayout(options_layout)
        layout.addLayout(info_layout)
        self.review_table = ReviewTable(self)
        layout.addWidget(self.review_table)
        table_option_layout = QHBoxLayout()
        table_option_layout.addWidget(QPushButton("增加一行", self, clicked=self.review_table.insert_new_row))
        table_option_layout.addWidget(QPushButton("增加一列", self, clicked=self.review_table.insert_new_column))
        self.status_label = QLabel(self)
        table_option_layout.addWidget(self.status_label)
        table_option_layout.addStretch()
        self.commit_button = QPushButton("确定增加", self, clicked=self.commit_new_datasheet)
        table_option_layout.addWidget(self.commit_button)
        layout.addLayout(table_option_layout)
        self.setLayout(layout)
        self._get_varieties()
        self._get_trend_group()
        self.variety_combobox.currentTextChanged.connect(self._get_trend_group)

    def _get_varieties(self):
        try:
            r = requests.get(settings.SERVER_ADDR + 'variety/?way=group')
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError("请求品种数据错误")
        except Exception as e:
            self.variety_combobox.clear()
        else:
            for variety_group in response['variety']:
                for variety_item in variety_group['subs']:
                    self.variety_combobox.addItem(variety_item['name'], variety_item['id'])

    def _get_trend_group(self):
        current_variety_id = self.variety_combobox.currentData()
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/group/?variety=' + str(current_variety_id),
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, "错误", str(e))
        else:
            self.vtable_group.clear()
            for group_item in response['groups']:
                self.vtable_group.addItem(group_item['name'], group_item['id'])

    def create_new_group(self):
        current_variety_name = self.variety_combobox.currentText()
        current_variety_id = self.variety_combobox.currentData()

        def commit_group_name():
            try:
                r = requests.post(
                    url=settings.SERVER_ADDR + 'trend/group/',
                    headers={"Content-Type":"application/json;charset=utf8"},
                    data=json.dumps({
                        'utoken':settings.app_dawn.value("AUTHORIZATION"),
                        'variety_id':current_variety_id,
                        'name': name_edit.text().strip()
                    })
                )
                response = json.loads(r.content.decode('utf8'))
                if r.status_code != 201:
                    raise ValueError(response['message'])
            except Exception as e:
                QMessageBox.information(popup, "错误", str(e))
            else:
                QMessageBox.information(popup, "成功", "成功添加数据组")
                popup.close()
        if not current_variety_name or not current_variety_id:
            QMessageBox.information(self, "未选择品种", "请选择品种")
            return

        popup = QDialog(self)
        popup.setAttribute(Qt.WA_DeleteOnClose)
        popup.setWindowTitle("增加【" + current_variety_name + "】数据组")
        popup.setFixedSize(250, 80)
        layout = QVBoxLayout(popup)
        name_layout = QHBoxLayout(popup)
        name_layout.addWidget(QLabel("名称:", popup))
        name_edit = QLineEdit(popup)
        name_layout.addWidget(name_edit)
        layout.addLayout(name_layout)
        commit_btn = QPushButton("确定", popup)
        commit_btn.clicked.connect(commit_group_name)
        layout.addWidget(commit_btn, alignment=Qt.AlignRight)
        popup.setLayout(layout)
        popup.exec_()

    def review_file_data(self):
        self.review_table.clear()
        self.status_label.setText("正在处理预览数据...")
        date_standards = {
            0: "%Y-%m-%d",
            1: "%Y-%m",
            2: "%Y",
        }
        current_date_format = date_standards.get(self.date_standard.currentData())
        file_path, _ = QFileDialog.getOpenFileName(self, '打开表格', '', "Excel file(*.xls *xlsx)")
        if file_path:
            work_book = xlrd.open_workbook(file_path)
            sheet = work_book.sheet_by_index(0)
            if work_book.sheet_loaded(0):
                self.review_table.set_horizon_header_labels(sheet.row_values(0))   # 表头
                for row in range(1, sheet.nrows):
                    row_content = list()
                    # 读取的数据类型ctype： 0 empty,1 string, 2 number, 3 date, 4 boolean, 5 error
                    for col in range(sheet.ncols):
                        value_type = sheet.cell(row, col).ctype
                        value = sheet.cell_value(row, col)
                        if value_type == 3:
                            value = datetime.datetime(*xlrd.xldate_as_tuple(value, 0))
                            value = value.strftime(current_date_format)
                        row_content.append(value)
                    self.review_table.add_row_content(row-1, row_content)
            self.status_label.setText("数据预览完成!")

    def commit_new_datasheet(self):
        self.commit_button.setEnabled(False)
        self.status_label.setText("正在提交处理数据...")
        data_values = self.review_table.values()
        current_variety_id = self.variety_combobox.currentData()
        current_group_id = self.vtable_group.currentData()
        try:
            user_id = int(pickle.loads(settings.app_dawn.value("UKEY")))
            r = requests.post(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/trend/table/',
                headers={"Content-Type":"application/json;charset=utf8"},
                data=json.dumps({
                    'utoken': settings.app_dawn.value("AUTHORIZATION"),
                    'variety_id':current_variety_id,
                    'group_id': current_group_id,
                    'table_values': data_values,
                    'title': self.title_edit.text().strip(),
                    'origin': self.origin_edit.text().strip()
                })
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            self.status_label.setText(str(e))
        else:
            self.status_label.setText("成功提交!")
            self.review_table.clear()
        finally:
            self.commit_button.setEnabled(True)


class ColumnCheckBox(QCheckBox):
    state_reverse = pyqtSignal(int, str, bool)

    def __init__(self, col, group, *args):
        super(ColumnCheckBox, self).__init__(*args)
        self.col = col
        self.group = group
        self.stateChanged.connect(self.emit_change_state)

    def emit_change_state(self):
        self.state_reverse.emit(self.col, self.group, self.isChecked())


class ChartAxisOptionButton(QPushButton):
    add_axis_target = pyqtSignal(str, str)

    def __init__(self, axis_name, axis_type, *args, **kwargs):
        super(ChartAxisOptionButton, self).__init__(*args, **kwargs)
        self.axis_name = axis_name
        self.axis_type = axis_type
        self.clicked.connect(self.emit_info)

    def emit_info(self):
        self.add_axis_target.emit(self.axis_name, self.axis_type)


class DrawChartsDialog(QDialog):
    CHARTS = {
        'line': '线形图',
        'bar': '柱状图'
    }   # 支持的图形

    def __init__(self, table_id, *args,**kwargs):
        super(DrawChartsDialog, self).__init__(*args, **kwargs)
        self.table_id = table_id
        self.resize(1200, 660)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.BOTTOM_AXIS = None
        self.LEFT_AXIS = {}
        self.RIGHT_AXIS = {}
        self.table_headers = []
        self.table_sources = None

        layout = QHBoxLayout(self)
        left_layout = QVBoxLayout(self)
        right_layout = QVBoxLayout(self)

        self.target_widget = QWidget(self)
        self.target_widget.setFixedWidth(250)
        target_layout = QVBoxLayout(self)

        title_layout = QHBoxLayout(self)
        title_layout.addWidget(QLabel('标题:',self))
        self.title_edit = QLineEdit(self)
        title_layout.addWidget(self.title_edit)
        target_layout.addLayout(title_layout)

        x_axis_layout = QHBoxLayout(self)
        x_axis_layout.addWidget(QLabel('横轴:', self))
        self.x_axis_combobox = QComboBox(self)
        self.x_axis_combobox.currentIndexChanged.connect(self.x_axis_changed)
        x_axis_layout.addWidget(self.x_axis_combobox)
        x_axis_layout.addStretch()
        target_layout.addLayout(x_axis_layout)

        add_target = QGroupBox("添加指标", self)
        add_target_layout = QVBoxLayout()
        self.target_list = QListWidget(self)
        add_target_layout.addWidget(self.target_list)
        options_layout = QGridLayout(self)
        self.button1 = ChartAxisOptionButton(axis_name='left',axis_type='line',text='左轴线形', parent=self)
        self.button1.add_axis_target.connect(self.add_target_index)
        self.button2 = ChartAxisOptionButton(axis_name='left',axis_type='bar',text='左轴柱状', parent=self)
        self.button2.add_axis_target.connect(self.add_target_index)
        self.button3 = ChartAxisOptionButton(axis_name='right',axis_type='line',text='右轴线形', parent=self)
        self.button3.add_axis_target.connect(self.add_target_index)
        self.button4 = ChartAxisOptionButton(axis_name='right',axis_type='bar',text='右轴柱状', parent=self)
        self.button4.add_axis_target.connect(self.add_target_index)
        options_layout.addWidget(self.button1, 0, 0)
        options_layout.addWidget(self.button2, 1, 0)
        options_layout.addWidget(self.button3, 0, 1)
        options_layout.addWidget(self.button4, 1, 1)
        add_target_layout.addLayout(options_layout)
        add_target.setLayout(add_target_layout)
        target_layout.addWidget(add_target)

        self.target_widget.setLayout(target_layout)
        target_layout.addStretch()
        left_layout.addWidget(self.target_widget)
        self.confirm_to_draw = QPushButton('确认绘制', self)
        self.confirm_to_draw.clicked.connect(self.draw_chart)
        left_layout.addWidget(self.confirm_to_draw)

        # 右侧显示图形和数据表格

        self.chart_widget = QWebEngineView()
        self.chart_widget.setParent(self)
        self.table_widget = QTableWidget(self)
        self.table_widget.setMinimumHeight(250)
        right_layout.addWidget(self.chart_widget)
        right_layout.addWidget(self.table_widget)

        layout.addLayout(left_layout)
        layout.addLayout(right_layout)
        self.setLayout(layout)
        self._get_detail_table_data()

    def _get_detail_table_data(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/table/' + str(self.table_id) + '/'
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            pass
        else:

            for index, header_text in enumerate(response['headers']):
                self.x_axis_combobox.addItem(header_text, "column_{}".format(index))
                item = QListWidgetItem(header_text)
                item.index = "column_{}".format(index)
                self.target_list.addItem(item)
            # 表格展示数据
            self.table_show_data(response['headers'], response['records'])
            self.table_headers = response['headers']
            self.table_sources = response['records']

    def table_show_data(self, headers, records):
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setRowCount(len(records))
        self.table_widget.setHorizontalHeaderLabels(headers)
        for row, row_item in enumerate(records):
            for col in range(self.table_widget.columnCount()):
                key = "column_{}".format(col)
                item = QTableWidgetItem(row_item[key])
                self.table_widget.setItem(row, col, item)

    def add_target_index(self, axis_name, axis_type):
        current_index_item = self.target_list.currentItem()
        if not current_index_item:
            QMessageBox.information(self, '错误', '先选择一个数据指标')
            return
        col_index = current_index_item.index
        if axis_name == 'left':
            self.LEFT_AXIS[col_index] = axis_type
        elif axis_name == 'right':
            self.RIGHT_AXIS[col_index] = axis_type
        else:
            QMessageBox.information(self, '错误', '内部发生一个未知错误')

    def x_axis_changed(self):
        self.BOTTOM_AXIS = self.x_axis_combobox.currentData()

    def draw_chart(self):
        title = self.title_edit.text()
        if not all([self.BOTTOM_AXIS, self.LEFT_AXIS]) and not all([self.BOTTOM_AXIS, self.RIGHT_AXIS]):
            QMessageBox.information(self, '错误', '请设置指标再进行绘制')
            return
        print('标题:\n', title)
        print('左轴参数:\n', self.LEFT_AXIS)
        print('右轴参数:\n', self.RIGHT_AXIS)
        print('横轴参数:\n', self.BOTTOM_AXIS)
        source_df = pd.DataFrame(self.table_sources)
        # 对x轴进行排序
        sort_df = source_df.sort_values(by=self.BOTTOM_AXIS)
        # print('排序前:\n', source_df)
        # print('排序后:\n', sort_df)
        print("显示图形的空间:", self.chart_widget.width(), self.chart_widget.height())
        try:
            # 进行画图
            x_axis_data = sort_df[self.BOTTOM_AXIS].values.tolist()
            # 去除一个y轴参数后移除该参数
            first_key = list(self.LEFT_AXIS.keys())[0]
            first_datacol,first_type = first_key, self.LEFT_AXIS[first_key]
            del self.LEFT_AXIS[first_key]  # 取出后删除
            init_opts = opts.InitOpts(
                width=str(self.chart_widget.width() - 20) + 'px',
                height=str(self.chart_widget.height() - 25) + 'px'
            )
            if first_type == 'line':
                chart = Line(
                    init_opts=init_opts
                )
                chart.add_xaxis(xaxis_data=x_axis_data)
                chart.add_yaxis(
                    series_name=self.table_headers[int(first_key[-1])],
                    y_axis=sort_df[first_key].values.tolist(),
                    label_opts=opts.LabelOpts(is_show=False),
                    # symbol='circle',
                    z_level=9,
                    is_smooth=True
                )
            elif first_type == 'bar':
                chart = Bar(
                    init_opts=init_opts
                )
                chart.add_xaxis(xaxis_data=x_axis_data)
                chart.add_yaxis(
                    series_name=self.table_headers[int(first_key[-1])],
                    yaxis_data=sort_df[first_key].values.tolist(),
                    label_opts = opts.LabelOpts(is_show=False),
                )
            else:
                return

            # 根据参数画图
            for col_name, chart_type in self.LEFT_AXIS.items():
                if chart_type == 'line':
                    extra_c = (
                        Line()
                        .add_xaxis(xaxis_data=x_axis_data)
                        .add_yaxis(
                            series_name=self.table_headers[int(col_name[-1])],
                            y_axis=sort_df[col_name].values.tolist(),
                            label_opts=opts.LabelOpts(is_show=False),
                            z_level=9,
                            is_smooth=True
                        )
                    )
                elif chart_type == 'bar':
                    extra_c = (
                        Bar()
                        .add_xaxis(xaxis_data=x_axis_data)
                        .add_yaxis(
                            series_name=self.table_headers[int(col_name[-1])],
                            yaxis_data=sort_df[col_name].values.tolist(),
                            label_opts=opts.LabelOpts(is_show=False),
                        )
                    )
                else:
                    continue
                chart.overlap(extra_c)
            # 根据参数画图
            for col_name, chart_type in self.RIGHT_AXIS.items():
                if chart_type == 'line':
                    extra_c = (
                        Line()
                            .add_xaxis(xaxis_data=x_axis_data)
                            .add_yaxis(
                            series_name=self.table_headers[int(col_name[-1])],
                            y_axis=sort_df[col_name].values.tolist(),
                            yaxis_index=1
                        )
                    )
                elif chart_type == 'bar':
                    extra_c = (
                        Bar()
                            .add_xaxis(xaxis_data=x_axis_data)
                            .add_yaxis(
                            series_name=self.table_headers[int(col_name[-1])],
                            yaxis_data=sort_df[col_name].values.tolist(),
                            yaxis_index=1
                        )
                    )
                else:
                    continue
                chart.overlap(extra_c)

            chart.set_global_opts(
                title_opts=opts.TitleOpts(
                    title=title,
                    pos_left='center',
                ),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type='cross'),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    # axislabel_opts=opts.LabelOpts(rotate=-135),
                 ),
                yaxis_opts=opts.AxisOpts(type_="value"),
                legend_opts=opts.LegendOpts(
                    type_='scroll',
                    pos_bottom=0,
                    item_gap=25,
                    item_width=30,
                    align='left',
                ),
            )
            # chart.add_xaxis(xaxis_data=x_axis_data)
            # # 根据参数画图
            # for col_name, chart_type in self.LEFT_AXIS.items():
            #     chart.add_yaxis(
            #         series_name=self.table_headers[int(col_name[-1])],
            #         y_axis=sort_df[col_name],
            #     )

            file_folder = os.path.join(BASE_DIR, 'cache/')
            file_path = os.path.join(file_folder, 'temperature_change_line_chart.html')

            page = Page(layout=Page.SimplePageLayout)
            page.add(
                chart,
            )
            file_url = page.render(file_path)
            print(file_url)
            self.chart_widget.page().load(QUrl("file:///cache/temperature_change_line_chart.html"))
        except Exception as e:
            import traceback
            traceback.print_exc()












class TableDetailRecordOpts(QDialog):
    def __init__(self, table_id, option, *args, **kwargs):
        super(TableDetailRecordOpts, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize(1000, 630)
        self.table_id = table_id
        self.option = option
        layout = QVBoxLayout(self)
        self.tips_label = QLabel("双击单元格修改数据后,点击对应行【修改】按钮进行修改.", self)
        layout.addWidget(self.tips_label)
        self.paste_button = QPushButton("粘贴", self)
        self.paste_button.clicked.connect(self.paste_new_data)
        layout.addWidget(self.paste_button, alignment=Qt.AlignLeft)
        self.table = QTableWidget(self)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 选中时为一行
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)  # 只能选中一行
        self.table.cellClicked.connect(self.table_cell_clicked)
        layout.addWidget(self.table)
        self.commit_button = QPushButton("确定增加", self)
        self.commit_button.clicked.connect(self.commit_new_contents)
        layout.addWidget(self.commit_button, alignment=Qt.AlignRight)
        self.setLayout(layout)
        if option == 'modify':
            self.tips_label.show()
            self.paste_button.hide()
            self.commit_button.hide()
        else:
            self.tips_label.hide()
            self.paste_button.show()
            self.commit_button.show()
        self._get_detail_table_data()

    def _get_detail_table_data(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/table/' + str(self.table_id) + '/'
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            pass
        else:
            if self.option == 'modify':
                self._set_row_contents(response['headers'], response['records'])
            else:
                self._set_table_headers(response['headers'])

    def _set_row_contents(self, headers, contents):
        headers.append('')
        columns = len(headers)
        self.table.setColumnCount(columns)
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(contents))
        for row, row_item in enumerate(contents):
            for col in range(columns):
                if col == columns - 1:
                    item = QTableWidgetItem("修改这行")
                else:
                    key = 'column_{}'.format(col)
                    item = QTableWidgetItem(row_item[key])
                    if col == 0:
                        item.id = row_item['id']
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def _set_table_headers(self, headers):
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

    def table_cell_clicked(self, row, col):
        if self.option != 'modify':
            return
        if col != self.table.columnCount() - 1:
            return
        record_id = self.table.item(row, 0).id
        record_content = list()
        for col_index in range(self.table.columnCount() - 1):
            record_content.append(self.table.item(row, col_index).text())
        # 发起修改请求
        try:
            r = requests.put(
                url=settings.SERVER_ADDR + 'trend/table/' + str(self.table_id) + '/',
                headers={'Content-Type':'application/json;charset=utf8'},
                data=json.dumps({
                    'utoken': settings.app_dawn.value("AUTHORIZATION"),
                    'record_id':record_id,
                    'record_content':record_content
                })
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, '失败', response['message'])
        else:
            QMessageBox.information(self, '成功', response['message'])

    def paste_new_data(self):
        clipboard = QApplication.clipboard()  # 获取当前剪贴板的内容
        contents = re.split(r'\n', clipboard.text())  # 处理数据
        for row, row_item in enumerate(contents):
            row_content = re.split('\t', row_item)
            if not row_content[0]:
                continue
            self.table.insertRow(self.table.rowCount())
            for col, item_text in enumerate(row_content):
                if col > self.table.columnCount() - 1:
                    continue
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def _table_values(self):
        headers = list()
        contents = list()
        for col in range(self.table.columnCount()):
            headers.append(self.table.horizontalHeaderItem(col).text())
        for row in range(self.table.rowCount()):
            row_content = list()
            for col in range(self.table.columnCount()):
                row_content.append(self.table.item(row, col).text())
            if not row_content:
                continue
            contents.append(row_content)
        return {
            'headers': headers,
            'contents': contents
        }

    def commit_new_contents(self):
        self.commit_button.setEnabled(False)
        values = self._table_values()
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'trend/table/' + str(self.table_id) + '/',
                headers={'Content-Type':'application/json;charset=utf8'},
                data=json.dumps({
                    'utoken': settings.app_dawn.value('AUTHORIZATION'),
                    'new_header': values['headers'],
                    'new_contents': values['contents']
                })
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, '失败', str(e))
        else:
            self.table.clear()
            QMessageBox.information(self, '成功', response['message'])
        finally:
            self.commit_button.setEnabled(True)


class InformationTable(QTableWidget):
    def __init__(self, *args):
        super(InformationTable, self).__init__(*args)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)  # 开启交替行颜色
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # 选中时为一行
        self.setSelectionMode(QAbstractItemView.SingleSelection)  # 只能选中一行
        self.setStyleSheet("""
        font-size: 13px;
        selection-color: rgb(250,250,250);
        alternate-background-color: rgb(245, 250, 248);  /* 设置交替行颜色 */
        """)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.RightButton:
            index = self.indexAt(QPoint(event.x(), event.y()))
            current_row = index.row()
            self.setCurrentIndex(index)
            if current_row < 0:
                return
            menu = QMenu()
            charts_action = menu.addAction("进入绘图")
            charts_action.triggered.connect(self.enter_draw_charts)
            modify_action = menu.addAction("修改记录")
            modify_action.triggered.connect(self.modify_record)
            add_action = menu.addAction("增加记录")
            add_action.triggered.connect(self.add_new_records)
            menu.exec_(QCursor.pos())
        else:
            super(InformationTable, self).mousePressEvent(event)

    def modify_record(self):
        current_row = self.currentRow()
        table_id = self.item(current_row, 0).id
        table_name = self.item(current_row, 1).text()
        popup = TableDetailRecordOpts(table_id=table_id,option='modify', parent=self.parent())
        popup.setWindowTitle("修改【" + table_name + "】")
        popup.exec_()

    def add_new_records(self):
        current_row = self.currentRow()
        table_id = self.item(current_row, 0).id
        table_name = self.item(current_row, 1).text()
        popup = TableDetailRecordOpts(table_id=table_id, option='add', parent=self.parent())
        popup.setWindowTitle("新增【" + table_name + "】")
        popup.exec_()

    def enter_draw_charts(self):
        current_row = self.currentRow()
        table_id = self.item(current_row, 0).id
        table_name = self.item(current_row, 1).text()
        popup = DrawChartsDialog(table_id=table_id, parent=self.parent())
        popup.setWindowTitle("【" + table_name + "】绘图")
        popup.show()



    def show_contents(self, row_contents):
        self.clear()
        table_headers = ["序号", '标题', '创建日期', '最近更新']
        self.setColumnCount(len(table_headers))
        self.setRowCount(len(row_contents))
        self.setHorizontalHeaderLabels(table_headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        for row, row_item in enumerate(row_contents):
            item0 = QTableWidgetItem(str(row + 1))
            item0.setTextAlignment(Qt.AlignCenter)
            item0.id = row_item['id']
            self.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item['title'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item1)
            item2 = QTableWidgetItem(row_item['create_time'])
            item2.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, item2)
            item3 = QTableWidgetItem(row_item['update_time'])
            item3.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 3, item3)


class UpdateTrendTablePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(UpdateTrendTablePage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        opts_layout = QHBoxLayout()
        opts_layout.addWidget(QLabel("品种:", self))
        self.variety_combobox = QComboBox(self)
        opts_layout.addWidget(self.variety_combobox)
        opts_layout.addWidget(QLabel("数据组:", self))
        self.group_combobox = QComboBox(self)
        self.group_combobox.currentTextChanged.connect(self._get_current_tables)
        opts_layout.addWidget(self.group_combobox)
        opts_layout.addStretch()
        layout.addLayout(opts_layout)
        self.trend_table = InformationTable(self)
        layout.addWidget(self.trend_table)
        self.setLayout(layout)
        self._get_varieties()
        self._get_trend_group()
        self.variety_combobox.currentTextChanged.connect(self._get_trend_group)

    def _get_varieties(self):
        try:
            r = requests.get(settings.SERVER_ADDR + 'variety/?way=group')
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError("请求品种数据错误")
        except Exception as e:
            self.variety_combobox.clear()
        else:
            for variety_group in response['variety']:
                for variety_item in variety_group['subs']:
                    self.variety_combobox.addItem(variety_item['name'], variety_item['id'])

    def _get_trend_group(self):
        current_variety_id = self.variety_combobox.currentData()
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/group/?variety=' + str(current_variety_id),
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, "错误", str(e))
        else:
            self.group_combobox.clear()
            self.group_combobox.addItem("全部", 0)
            for group_item in response['groups']:
                self.group_combobox.addItem(group_item['name'], group_item['id'])

    def _get_current_tables(self):
        current_group_id = self.group_combobox.currentData()
        try:
            user_id = int(pickle.loads(settings.app_dawn.value('UKEY')))
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/trend/table/?group=' + str(current_group_id)
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            pass
        else:
            self.trend_table.show_contents(response['tables'])


# 数据分析管理主页
class TrendPageCollector(QWidget):
    def __init__(self, *args, **kwargs):
        super(TrendPageCollector, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0)
        # 左侧管理菜单列表
        self.left_list = QListWidget(clicked=self.left_list_clicked, objectName='leftList')
        layout.addWidget(self.left_list, alignment=Qt.AlignLeft)
        # 右侧显示的frame
        self.frame_loaded = LoadedPage(parent=self)
        layout.addWidget(self.frame_loaded)
        self.setLayout(layout)
        self._addLeftListMenu()
        self.setStyleSheet("""
        #leftList::item{
            height:22px
        }
        """)

    # 添加左侧管理菜单
    def _addLeftListMenu(self):
        for item in [u'数据表管理', '图表管理']:
            self.left_list.addItem(QListWidgetItem(item))
        for item in [u'新建数据表', u'我的数据表']:
            self.left_list.addItem(QListWidgetItem(item))

    # 点击左侧菜单列表
    def left_list_clicked(self):
        text = self.left_list.currentItem().text()
        if text == u'新建数据表':
            frame_page = NewTrendTablePage(parent=self)
        elif text == u'我的数据表':
            frame_page = UpdateTrendTablePage(parent=self)




        elif text == u'数据表管理':
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


