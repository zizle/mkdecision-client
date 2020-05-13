# _*_ coding:utf-8 _*_
# __Author__： zizle
import os
import re
import xlrd
import json
import time
import datetime
import requests
import pickle
import sqlite3
import pandas as pd
import pyecharts.options as opts
from pyecharts.charts import Line, Bar, Page
from PyQt5.QtWidgets import QApplication,QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QComboBox, QTableWidget, \
    QPushButton, QAbstractItemView, QHeaderView, QTableWidgetItem, QDialog, QMessageBox, QLineEdit, QFileDialog,QMenu,\
    QGroupBox, QCheckBox, QTextEdit, QGridLayout, QTabWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QUrl, QThread, QTimer
from PyQt5.QtGui import QCursor
import settings
from widgets.base import LoadedPage, TableRowReadButton, TableRowDeleteButton, TableCheckBox
from popup.trendCollector import CreateNewTrendTablePopup, ShowTableDetailPopup, EditTableDetailPopup, CreateNewVarietyChartPopup, \
    ShowChartPopup
from settings import BASE_DIR

# sqlite3查询结果转为字典
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

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
        self.table_headers = []
        self.table_sources = None
        self.has_left_axis = False

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

        x_format_layout = QHBoxLayout(self)
        x_format_layout.addWidget(QLabel('格式:', self))
        self.date_format = QComboBox(self)
        self.date_format.addItem('年-月-日', '%Y-%m-%d')
        self.date_format.addItem('年-月', '%Y-%m')
        self.date_format.addItem('年', '%Y')
        x_format_layout.addWidget(self.date_format)
        target_layout.addLayout(x_format_layout)

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

        show_params_layout = QVBoxLayout()
        self.show_params = QGroupBox("已选指标", self)
        self.params_list = QListWidget(self)
        self.params_list.doubleClicked.connect(self.remove_target_index)
        show_params_layout.addWidget(self.params_list)
        self.show_params.setLayout(show_params_layout)

        target_layout.addWidget(self.show_params)

        graphic_layout = QHBoxLayout(self)
        graphic_layout.setSpacing(1)
        self.has_graphic = QCheckBox(self)
        self.has_graphic.setText("添加水印")
        self.water_graphic = QLineEdit(self)
        self.water_graphic.setText("瑞达期货研究院")
        graphic_layout.addWidget(self.has_graphic)
        graphic_layout.addWidget(self.water_graphic)
        graphic_layout.addStretch()
        target_layout.addLayout(graphic_layout)

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
        self.table_widget.setMinimumHeight(220)
        right_layout.addWidget(self.chart_widget)

        self.save_config = QPushButton('保存配置',self)
        self.save_config.clicked.connect(self.save_charts_config_to_server)
        right_layout.addWidget(self.save_config, alignment=Qt.AlignRight)
        right_layout.addWidget(self.table_widget)

        layout.addLayout(left_layout)
        layout.addLayout(right_layout)
        self.setLayout(layout)
        self._get_detail_table_data()

    def save_charts_config_to_server(self):
        def upload_configs():
            decipherment = text_edit.toPlainText()
            # 水印
            has_graphic = self.has_graphic.isChecked()
            graphic_text = self.water_graphic.text()
            print("解读:", decipherment)
            print("标题:", title)
            print("水印:", has_graphic, graphic_text)
            print('左轴参数:', left_axis)
            print('右轴参数:', right_axis)
            print('横轴参数:', bottom)
            print('数据表:', self.table_id)
            # 整理参数提交
            try:
                user_id = pickle.loads(settings.app_dawn.value('UKEY'))
                r = requests.post(
                    url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/trend/chart/',
                    headers={'Content-Type':'application/json;charset=utf8'},
                    data=json.dumps({
                        'table_id': self.table_id,
                        'title': title,
                        'bottom_axis': str(bottom),
                        'left_axis': str(left_axis),
                        'right_axis': str(right_axis),
                        'is_watermark': has_graphic,
                        'watermark': graphic_text,
                        'decipherment': decipherment
                    })
                )
                response = json.loads(r.content.decode('utf8'))
                if r.status_code != 201:
                    raise ValueError(response['message'])
            except Exception as e:
                QMessageBox.information(self, '错误', str(e))
            else:
                QMessageBox.information(self, '成功', '保存图表成功')
                chart_decipher.close()


        # 图表解读
        chart_decipher = QDialog(self)
        chart_decipher.setWindowTitle("解读")
        layout = QVBoxLayout(chart_decipher)
        chart_decipher.setAttribute(Qt.WA_DeleteOnClose)
        text_edit = QTextEdit(self)
        layout.addWidget(QLabel("图形解读:"), alignment=Qt.AlignLeft)
        layout.addWidget(text_edit)
        to_saved = QPushButton("确定", chart_decipher)
        to_saved.clicked.connect(upload_configs)
        layout.addWidget(to_saved, alignment=Qt.AlignRight)

        # 标题
        title = self.title_edit.text()
        x_axis = self.x_axis_combobox.currentData()
        if x_axis == 'column_0':
            bottom = {x_axis: self.date_format.currentData()}
        else:
            # 横轴
            bottom = {x_axis: ''}
        # 左轴
        left_axis = {}
        # 右轴
        right_axis = {}
        for index in range(self.params_list.count()):
            item = self.params_list.item(index)
            if item.axis_pos == 'left':
                left_axis[item.column_index] = item.chart_type
            else:
                right_axis[item.column_index] = item.chart_type

        if not all([title,bottom, left_axis]):
            QMessageBox.information(self, '错误', '请至少设置标题和一个左轴指标再进行保存')
            return
        chart_decipher.exec_()

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
            table_records = response['records']
            table_headers = table_records.pop(0)
            del table_headers['id']
            del table_headers['create_time']
            del table_headers['update_time']
            table_headers = [header for header in table_headers.values()]
            for index, header_text in enumerate(table_headers):
                self.x_axis_combobox.addItem(header_text, "column_{}".format(index))
                item = QListWidgetItem(header_text)
                item.index = "column_{}".format(index)
                self.target_list.addItem(item)
            # 表格展示数据
            self.table_show_data(table_headers, table_records)
            self.table_headers = table_headers
            self.table_sources = table_records

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
        text = current_index_item.text()
        if axis_name == 'left':
            item = QListWidgetItem("左轴" + self.CHARTS[axis_type] + " = " + text)
            item.axis_pos = 'left'
            item.column_index = col_index
            item.chart_type = axis_type
            self.has_left_axis = True
        elif axis_name == 'right':
            if not self.has_left_axis:
                QMessageBox.information(self, '错误', '请先添加一个左轴数据列')
                return
            item = QListWidgetItem("右轴" + self.CHARTS[axis_type] + " = " + text)
            item.axis_pos = 'right'
            item.column_index = col_index
            item.chart_type = axis_type
        else:
            QMessageBox.information(self, '错误', '内部发生一个未知错误')
            return
        self.params_list.addItem(item)

    def remove_target_index(self, index):
        self.params_list.takeItem(self.params_list.currentRow())
        # self.params_list.setCurrentIndex(index)
        # self.params_list.removeItemWidget(self.params_list.currentItem())

    def x_axis_changed(self):
        self.BOTTOM_AXIS = self.x_axis_combobox.currentData()

    def draw_chart(self):
        title = self.title_edit.text()
        bottom = self.x_axis_combobox.currentData()  # 横轴数据列名
        left_axis = {}
        right_axis = {}

        for index in range(self.params_list.count()):
            item = self.params_list.item(index)
            if item.axis_pos == 'left':
                left_axis[item.column_index] = item.chart_type
            else:
                right_axis[item.column_index] = item.chart_type

        if not all([bottom, left_axis]):
            QMessageBox.information(self, '错误', '请至少设置一个左轴指标再进行绘制')
            return
        print('标题:\n', title)
        print('左轴参数:\n', left_axis)
        print('右轴参数:\n', right_axis)
        print('横轴参数:\n', bottom)
        source_df = pd.DataFrame(self.table_sources)
        if bottom == 'column_0':
            source_df[bottom] = pd.to_datetime(source_df[bottom], format='%Y-%m-%d')
            source_df[bottom] = source_df[bottom].apply(lambda x: x.strftime(self.date_format.currentData()))
        # 对x轴进行排序
        sort_df = source_df.sort_values(by=bottom)
        # print('排序前:\n', source_df)
        # print('排序后:\n', sort_df)
        print("显示图形的空间:", self.chart_widget.width(), self.chart_widget.height())
        try:
            # 进行画图
            x_axis_data = sort_df[bottom].values.tolist()
            # 由于pyecharts改变了overlap方法,读取左轴第一个数据类型进行绘制
            left_axis_copy = {key: val for key, val in left_axis.items()}
            print("复制后的左轴参数:", left_axis_copy)
            first_key = list(left_axis_copy.keys())[0]
            first_datacol, first_type = first_key, left_axis_copy[first_key]
            del left_axis_copy[first_key]
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
                    label_opts=opts.LabelOpts(is_show=False),
                )
            else:
                return
            # 1 绘制其他左轴数据
            # 根据参数画图
            for col_name, chart_type in left_axis_copy.items():
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
            # 绘制其他右轴数据
            if right_axis:
                chart.extend_axis(
                    yaxis=opts.AxisOpts()
                )
            for col_name, chart_type in right_axis.items():
                if chart_type == 'line':
                    extra_c = (
                        Line()
                            .add_xaxis(xaxis_data=x_axis_data)
                            .add_yaxis(
                            series_name=self.table_headers[int(col_name[-1])],
                            y_axis=sort_df[col_name].values.tolist(),
                            label_opts=opts.LabelOpts(is_show=False),
                            z_level=9,
                            is_smooth=True,
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
                            label_opts=opts.LabelOpts(is_show=False),
                            yaxis_index=1
                        )
                    )
                else:
                    continue
                chart.overlap(extra_c)
            image_path = os.path.join(BASE_DIR, 'media/logo.png')
            if self.has_graphic.isChecked():
                water_graphic_opts = opts.GraphicGroup(
                    graphic_item=opts.GraphicItem(
                        width=200,
                        left=self.chart_widget.width() / 2 - 150,
                        top='center',
                        bounding='raw',
                        z=-1,
                    ),
                    children=[
                        opts.GraphicImage(
                            graphic_item=opts.GraphicItem(
                                left=0,
                                top='center',
                            ),
                            graphic_imagestyle_opts=opts.GraphicImageStyleOpts(
                                image=image_path,
                                width=40,
                                height=40,
                                opacity=0.3
                            ),
                        ),
                        opts.GraphicText(
                            graphic_item=opts.GraphicItem(
                                left=42, top="center", z=-1
                            ),
                            graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                                # 要显示的文本
                                text=self.water_graphic.text(),
                                font="bold 35px Microsoft YaHei",
                                graphic_basicstyle_opts=opts.GraphicBasicStyleOpts(
                                    fill="rgba(200,200,200,0.5)"
                                ),
                            )
                        )
                    ]
                )
            else:
                water_graphic_opts = None

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
                toolbox_opts=opts.ToolboxOpts(
                    is_show=True,
                    feature=opts.ToolBoxFeatureOpts(
                        save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(is_show=False),
                        data_zoom=opts.ToolBoxFeatureDataZoomOpts(is_show=True),
                        magic_type=opts.ToolBoxFeatureMagicTypeOpts(type_=['line','bar']),
                        brush=opts.ToolBoxFeatureBrushOpts(type_='clear'),
                    )
                ),
                graphic_opts=water_graphic_opts,
            )
            file_folder = os.path.join(BASE_DIR, 'cache/')
            file_path = os.path.join(file_folder, 'chars_stacked_drawer.html')

            page = Page(layout=Page.SimplePageLayout)
            page.add(
                chart,
            )
            file_url = page.render(file_path)
            # print(file_url)
            self.chart_widget.page().load(QUrl("file:///cache/chars_stacked_drawer.html"))
        except Exception as e:
            pass


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
            table_records = response['records']
            table_headers = table_records.pop(0)
            del table_headers['id']
            del table_headers['create_time']
            del table_headers['update_time']
            table_headers = [header for header in table_headers.values()]
            if self.option == 'modify':
                self._set_row_contents(table_headers, table_records)
            else:
                self._set_table_headers(table_headers)

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
        current_variety_id = self.variety_combobox.currentData()
        if current_group_id is None or current_variety_id is None:
            return
        try:
            user_id = int(pickle.loads(settings.app_dawn.value('UKEY')))
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/trend/table/?variety='+str(current_variety_id)+'&group=' + str(current_group_id)
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            pass
        else:
            self.trend_table.show_contents(response['tables'])


# 更新数据组的线程
class UpdateVarietyTableGroupThread(QThread):
    process_finished = pyqtSignal(bool)
    updating = pyqtSignal(int)

    def __init__(self, variety_id,group_id,file_folder, *args,**kwargs):
        super(UpdateVarietyTableGroupThread, self).__init__(*args, **kwargs)
        self.variety_id = variety_id
        self.group_id = group_id
        self.file_folder = file_folder
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.time_out)
        self.index = -1

    def time_out(self):
        if self.index < 3:
            self.index += 1
        else:
            self.index = 0
        self.updating.emit(self.index)

    def run(self):
        # 读取文件夹内所有文件
        file_path_list = list()
        for file_path in os.listdir(self.file_folder):
            if os.path.splitext(file_path)[1] == '.xlsx':
                file_path_list.append(os.path.join(self.file_folder, file_path))
        # 遍历将每个文件和文件内的sheet，读取，发起更新或创建，提交后发出一个信号
        for file_path in file_path_list:
            file = xlrd.open_workbook(file_path)
            for sheet_name in file.sheet_names():
                time.sleep(0.3)
                sheet = file.sheet_by_name(sheet_name)
                if not file.sheet_loaded(sheet_name) or sheet.nrows < 2:  # 读取失败就继续，或是空数据表
                    continue
                headers = sheet.row_values(1)  # 第一行读取，即表格中第二行
                if len(headers) <= 0:  # 无读到表头，跳过这个sheet
                    continue
                contents = [headers]
                for row in range(2, sheet.nrows):  # 读取表格数据
                    row_content = []
                    if sheet.cell(row, 0).ctype == 3 and sheet.cell_value(row, 0) == 0:  # 如果这行是1900年，跳过
                        continue
                    for col in range(sheet.ncols):
                        cell_type = sheet.cell(row, col).ctype
                        if col == 0 and cell_type != 3:  # 第一列不是时间类型的，忽略本行数据（非时间行跳过）
                            break
                        cell_value = sheet.cell_value(row, col)
                        if cell_type == 3:  # 时间列数据转为时间格式
                            cell_value = datetime.datetime(*xlrd.xldate_as_tuple(cell_value, 0)).strftime("%Y-%m-%d")
                        row_content.append(cell_value)
                    if len(row_content) == len(headers):  # 与表头同样大小
                        contents.append(row_content)
                # 发起请求向服务器增加或更新数据
                try:
                    # print('上传或更新数据:',file_path, sheet_name)
                    self.send_data_to_server(
                        variety_id=self.variety_id,
                        group_id=self.group_id,
                        title=sheet_name,
                        table_values=contents
                    )
                except Exception:
                    pass
            file.release_resources()  # 释放资源
            del file
        # 全部完成执行完成后，发出完成的信号True
        # self.timer.stop()
        self.process_finished.emit(True)

    def send_data_to_server(self, variety_id, group_id, title, table_values):
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            requests.post(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/trend/table/',
                headers={'Content-type': 'application/json;charset=utf8'},
                data=json.dumps({
                    'utoken': settings.app_dawn.value('AUTHORIZATION'),
                    'variety_id': variety_id,
                    'group_id': group_id,
                    'title': title,
                    'table_values':table_values
                })
            )
        except Exception:
            pass


# 配置数据源、更新数据的窗口
class UpdateTableConfigPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(UpdateTableConfigPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(self)
        opts_layout = QHBoxLayout(self)
        opts_layout.addWidget(QLabel('当前配置', self))
        opts_layout.addStretch()
        self.new_config_button = QPushButton('配置', self)
        self.new_config_button.clicked.connect(self.add_new_update_config)
        opts_layout.addWidget(self.new_config_button)
        layout.addLayout(opts_layout)
        self.config_table = QTableWidget(self)
        self.config_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.config_table.cellClicked.connect(self.config_table_cell_clicked)
        layout.addWidget(self.config_table)
        self.setLayout(layout)
        self._read_configs()

    # 读取当前的配置
    def _read_configs(self):
        self.config_table.clear()
        self.config_table.setColumnCount(5)
        self.config_table.setHorizontalHeaderLabels(['品种', '数据组', '数据文件夹', '上次更新',''])
        self.config_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.config_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        db_path = os.path.join(BASE_DIR, 'dawn/tupdate.db')
        connection = sqlite3.connect(db_path)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM `table_update_config`;")
        fetch_all = cursor.fetchall()
        cursor.close()
        connection.close()
        self.config_table.setRowCount(len(fetch_all))
        for row,item in enumerate(fetch_all):
            item0 = QTableWidgetItem(item['variety_name'])
            item0.variety_id = item['variety_id']
            item0.setTextAlignment(Qt.AlignCenter)
            self.config_table.setItem(row, 0, item0)
            item1 = QTableWidgetItem(item['group_name'])
            item1.group_id = item['group_id']
            item1.setTextAlignment(Qt.AlignCenter)
            self.config_table.setItem(row, 1, item1)
            item2 = QTableWidgetItem(item['file_folder'])
            item2.setTextAlignment(Qt.AlignCenter)
            self.config_table.setItem(row, 2, item2)
            item3 = QTableWidgetItem()
            if item['update_time']:
                item3.setText(item['update_time'])
            item3.setTextAlignment(Qt.AlignCenter)
            self.config_table.setItem(row, 3, item3)
            item4 = QTableWidgetItem('点击更新')
            item4.setTextAlignment(Qt.AlignCenter)
            self.config_table.setItem(row, 4, item4)

    def add_new_update_config(self):
        def choose_file_folder():  # 选择文件夹
            folder = QFileDialog.getExistingDirectory()
            if not folder:
                return
            folder_path.setText(folder + '/')

        def add_new_config():
            current_vid = variety_combobox.currentData()
            current_vname = variety_combobox.currentText()
            current_gname = group_combobox.currentText()
            current_gid = group_combobox.currentData()
            current_folder = folder_path.text()
            if not current_folder:
                return
            new_config = [current_vname, current_vid,current_gname, current_gid, current_folder]
            db_path = os.path.join(BASE_DIR, 'dawn/tupdate.db')
            connection = sqlite3.connect(db_path)
            connection.row_factory = dict_factory
            cursor = connection.cursor()
            # 查询当前品种是否配置了
            exist_record = "SELECT `id` FROM `table_update_config` WHERE `variety_id`=? AND `group_id`=?;"
            cursor.execute(exist_record, (current_vid, current_gid))
            fetch_ret = cursor.fetchone()
            if fetch_ret:  # 更新
                update_record = "UPDATE `table_update_config` SET `file_folder`=? " \
                                "WHERE `variety_id`=? AND `group_id`=?;"
                cursor.execute(update_record, (current_folder, current_vid, current_gid))
                connection.commit()
            else:  # 添加
                insert_statement = "INSERT INTO `table_update_config` " \
                                   "(`variety_name`,`variety_id`,`group_name`,`group_id`, `file_folder`) " \
                                   "VALUES (?,?,?,?,?);"
                cursor.execute(insert_statement, new_config)
                connection.commit()
            cursor.close()
            connection.close()
            QMessageBox.information(popup, '成功', '配置成功.')
            popup.close()

        def get_current_trend_group():
            # 获取当前品种数据组
            try:
                current_vid = variety_combobox.currentData()
                r = requests.get(url=settings.SERVER_ADDR + 'trend/group/?variety=' + str(current_vid))
                response = json.loads(r.content.decode('utf8'))
                if r.status_code != 200:
                    raise ValueError(response['message'])
            except Exception:
                pass
            else:
                group_combobox.clear()
                for group_item in response['groups']:
                    group_combobox.addItem(group_item['name'], group_item['id'])

        # 获取所有品种
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            r = requests.get(url=settings.SERVER_ADDR + 'user/'+str(user_id) + '/variety/')
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            pass
        else:
            popup = QDialog(self.parent())
            popup.setWindowTitle("配置路径")
            popup.setAttribute(Qt.WA_DeleteOnClose)
            popup.setFixedSize(320, 160)
            layout = QGridLayout(popup)
            layout.addWidget(QLabel("品种:", popup), 0, 0)
            variety_combobox = QComboBox(popup)
            variety_combobox.currentTextChanged.connect(get_current_trend_group)

            layout.addWidget(variety_combobox, 0, 1, 1, 2)
            group_combobox = QComboBox(popup)
            layout.addWidget(QLabel('数据组'), 1, 0)
            layout.addWidget(group_combobox, 1, 1,1,2)
            for variety_item in response['variety']:
                if variety_item['is_active']:
                    variety_combobox.addItem(variety_item['name'], variety_item['variety_id'])
            layout.addWidget(QLabel('路径:', popup), 2, 0)
            folder_path = QLineEdit(popup)
            layout.addWidget(folder_path, 2, 1)
            button = QPushButton('选择', popup)
            button.clicked.connect(choose_file_folder)
            layout.addWidget(button, 2, 2)
            add_config = QPushButton('确定添加',popup)
            add_config.clicked.connect(add_new_config)
            layout.addWidget(add_config, 3, 0, 1, 3)
            popup.setLayout(layout)
            if not popup.exec_():
                self._read_configs()

    def config_table_cell_clicked(self, row, col):
        updating_text = ['正在更新 ', '在更新 正', '更新 正在', '新 正在更']
        current_text = self.config_table.item(row, 4).text()
        if col != 4 or current_text != '点击更新':
            return

        def process_finished(ret):  # 更新结束
            self.update_thread.timer.stop()
            self.config_table.item(row, 4).setText('更新完成')
            self.update_thread.deleteLater()
            del self.update_thread
            # 更新时间修改
            db_path = os.path.join(BASE_DIR, 'dawn/tupdate.db')
            connection = sqlite3.connect(db_path)
            connection.row_factory = dict_factory
            cursor = connection.cursor()
            today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            update_statement = "UPDATE `table_update_config` SET " \
                               "`update_time`=? WHERE `variety_id`=? AND `group_id`=?;"
            cursor.execute(update_statement, (today, variety_id, group_id))
            connection.commit()
            cursor.close()
            connection.close()

        def updating_show(index):  # 提示正在更新
            self.config_table.item(row, 4).setText(updating_text[index])
        variety_id = self.config_table.item(row, 0).variety_id
        group_id = self.config_table.item(row, 1).group_id
        file_folder = self.config_table.item(row, 2).text()
        # 开启线程更新数据
        self.update_thread = UpdateVarietyTableGroupThread(variety_id,group_id,file_folder)
        self.update_thread.updating.connect(updating_show)
        self.update_thread.process_finished.connect(process_finished)
        self.update_thread.timer.start(700)  # 开启提示
        self.update_thread.start()


class MyTrendChartTableManage(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(MyTrendChartTableManage, self).__init__(*args)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.cellClicked.connect(self.click_table_cell)

    def click_table_cell(self,row, col):
        chart_id = self.item(row, 0).id
        if col == 3:
            print('编辑解说')
            decipherment = self.item(row, 3).text()
            self.edit_decipherment(decipherment=decipherment, chart_id=chart_id)
        elif col == 4:
            print('删除')
            self.delete_chart(row=row, chart_id=chart_id)
        else:
            return

    def edit_decipherment(self, decipherment, chart_id):
        print(decipherment)

        def upload_decipherment():
            text = text_edit.toPlainText()
            try:
                utoken = settings.app_dawn.value('AUTHORIZATION')
                r = requests.patch(
                    url=settings.SERVER_ADDR + 'trend/chart/' + str(chart_id) + '/?utoken=' + utoken,
                    headers={'Content-Type': 'application/json;charset=utf8'},
                    data=json.dumps({'decipherment': text})
                )
                response = json.loads(r.content.decode('utf8'))
                if r.status_code != 200:
                    raise ValueError(response['message'])
            except Exception as e:
                QMessageBox.information(self, '失败', str(e))
            else:
                QMessageBox.information(self, '成功', '修改成功')
                popup.close()
        popup = QDialog(self)
        popup.setWindowTitle("编辑图形解说")
        popup.resize(400, 200)
        popup.setAttribute(Qt.WA_DeleteOnClose)
        layout = QVBoxLayout(popup)
        text_edit = QTextEdit(decipherment, popup)
        layout.addWidget(text_edit)
        confirm = QPushButton('确定',popup)
        confirm.clicked.connect(upload_decipherment)
        layout.addWidget(confirm, alignment=Qt.AlignRight)
        popup.setLayout(layout)
        popup.show()

    def delete_chart(self, row, chart_id):
        if QMessageBox.Yes == QMessageBox.warning(self, '提醒', '删除将无法恢复?', QMessageBox.Yes|QMessageBox.No):
            try:
                utoken = settings.app_dawn.value('AUTHORIZATION')
                r = requests.delete(
                    url=settings.SERVER_ADDR + 'trend/chart/' + str(chart_id) + '/?utoken=' + utoken
                )
                response = json.loads(r.content.decode('utf8'))
                if r.status_code != 200:
                    raise ValueError(response['message'])
            except Exception as e:
                QMessageBox.information(self, '失败', str(e))
            else:
                QMessageBox.information(self, '成功', '删除成功')
                self.removeRow(row)

    def show_charts_info(self, contents):
        table_headers = ['标题','创建时间', '更新时间', '图形解说', '']
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(table_headers)
        self.setRowCount(len(contents))
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        for row, row_item in enumerate(contents):
            item0 = QTableWidgetItem(row_item['title'])
            item0.setTextAlignment(Qt.AlignCenter)
            item0.id = row_item['id']
            self.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item['create_time'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item1)
            item2 = QTableWidgetItem(row_item['update_time'])
            item2.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, item2)
            item3 = QTableWidgetItem(row_item['decipherment'])
            item3.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 3, item3)
            item4 = QTableWidgetItem("删除")
            item4.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 4, item4)


class MyTrendTableChartPage(QTabWidget):
    def __init__(self, *args, **kwargs):
        super(MyTrendTableChartPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(self)
        opts_layout = QHBoxLayout(self)
        opts_layout.addWidget(QLabel('品种:', self))
        self.variety_combobox = QComboBox(self)
        self.variety_combobox.currentTextChanged.connect(self.get_current_charts_info)
        opts_layout.addWidget(self.variety_combobox)
        self.switchover = QPushButton("图形管理", self)
        self.switchover.clicked.connect(self.switch_show_widget)
        opts_layout.addWidget(self.switchover)
        opts_layout.addStretch()
        layout.addLayout(opts_layout)
        self.show_charts = QWebEngineView(self)
        layout.addWidget(self.show_charts)

        self.manage_table = MyTrendChartTableManage(self)
        layout.addWidget(self.manage_table)
        self.manage_table.hide()
        self.setLayout(layout)

        self._get_accessed_variety()

    def _get_accessed_variety(self):
        # 获取有权限的品种信息
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            r = requests.get(settings.SERVER_ADDR + 'user/' + str(user_id) + '/variety/')
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            pass
        else:
            self.variety_combobox.clear()
            self.variety_combobox.addItem('全部', 0)
            accessed_variety = response['variety']
            for variety_item in accessed_variety:
                self.variety_combobox.addItem(variety_item['name'], variety_item['variety_id'])

    def switch_show_widget(self):
        if self.manage_table.isHidden():
            self.show_charts.hide()
            self.manage_table.show()
            self.switchover.setText('图形总览')
        else:
            self.show_charts.show()
            self.manage_table.hide()
            self.switchover.setText('图形管理')
        self.get_current_charts_info()

    def get_current_charts_info(self):
        current_variety = self.variety_combobox.currentData()
        user_id = pickle.loads(settings.app_dawn.value('UKEY'))
        if self.manage_table.isHidden():
            self.show_charts.load(QUrl(settings.SERVER_ADDR + 'user/' + str(user_id) + '/trend/chart/?variety=' + str(current_variety) + '&is_render=1'))
        else:
            # 请求当前用户的所有表信息
            try:
                r = requests.get(
                    url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/trend/chart/?variety=' + str(current_variety)
                )
                response = json.loads(r.content.decode('utf8'))
                if r.status_code != 200:
                    raise ValueError(response['message'])
            except Exception:
                pass
            else:
                self.manage_table.show_charts_info(response['charts_info'])


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
        # for item in [u'数据表管理', '图表管理']:
        #     self.left_list.addItem(QListWidgetItem(item))
        for item in [u'数据源配置',u'新建数据表', u'我的数据表', u'我的数据图']:
            self.left_list.addItem(QListWidgetItem(item))

    # 点击左侧菜单列表
    def left_list_clicked(self):
        text = self.left_list.currentItem().text()
        if text == u'新建数据表':
            frame_page = NewTrendTablePage(parent=self)
        elif text == u'我的数据表':
            frame_page = UpdateTrendTablePage(parent=self)
        elif text == u'数据源配置':
            frame_page = UpdateTableConfigPage(parent=self)
        elif text == u'我的数据图':
            frame_page = MyTrendTableChartPage(parent=self)



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
