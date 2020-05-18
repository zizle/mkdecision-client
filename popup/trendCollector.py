# _*_ coding:utf-8 _*_
# __Author__： zizle
import re
import json
import xlrd
import datetime
import requests
import pandas as pd
from xlrd import xldate_as_tuple
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QDialog, QTreeWidget, QWidget, QGridLayout, QLabel, QLineEdit,\
    QPushButton, QComboBox, QTableWidget, QTreeWidgetItem, QFileDialog, QHeaderView, QTableWidgetItem, QAbstractItemView, \
    QListWidget, QDateEdit, QCheckBox
from PyQt5.QtChart import QChartView, QChart
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QDate
from PyQt5.QtGui import QPainter
import settings
from widgets.base import TableRowDeleteButton, TableRowReadButton
from popup.tips import WarningPopup, InformationPopup
from utils.charts import lines_stacked, bars_stacked

""" 设置图表相关弹窗 """


# 设置图表详情的弹窗
class SetChartDetailPopup(QDialog):
    def __init__(self, table_id, *args, **kwargs):
        super(SetChartDetailPopup, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=2)
        # left_layout = QVBoxLayout()
        self.table_id = table_id
        self.table_data_frame = None  # 表格数据的pandas Data Frame对象
        # 图表参数设置的控件
        self.chart_parameter = QWidget(parent=self)
        parameter_layout = QVBoxLayout(margin=0)
        parameter_layout.addWidget(QLabel('参数设置', objectName='widgetTip'))
        # 图表名称
        chart_name_layout = QHBoxLayout()
        chart_name_layout.addWidget(QLabel('图表名称：', objectName='headTip'))
        self.chart_name = QLineEdit()
        chart_name_layout.addWidget(self.chart_name)
        parameter_layout.addLayout(chart_name_layout)
        # 图表类型
        chart_category_layout = QHBoxLayout()
        chart_category_layout.addWidget(QLabel('图表类型：', objectName='headTip'))
        self.chart_category_combo = QComboBox()
        self.chart_category_combo.addItems([u'折线图', u'柱形图'])
        chart_category_layout.addWidget(self.chart_category_combo)
        chart_category_layout.addStretch()
        parameter_layout.addLayout(chart_category_layout)
        # 选择X轴
        chart_xaxis_layout = QHBoxLayout()
        chart_xaxis_layout.addWidget(QLabel('X 轴列名：', objectName='headTip'))
        self.x_axis_combo = QComboBox(currentTextChanged=self.x_axis_changed)
        chart_xaxis_layout.addWidget(self.x_axis_combo)
        chart_xaxis_layout.addStretch()
        parameter_layout.addLayout(chart_xaxis_layout)
        # Y轴设置
        parameter_layout.addWidget(QLabel('Y 轴列名：', objectName='headTip'))
        yaxis_layout = QHBoxLayout()
        left_yaxis_layout = QVBoxLayout()
        self.column_header_list = QListWidget()
        self.column_header_list.setMaximumWidth(180)
        left_yaxis_layout.addWidget(self.column_header_list)
        yaxis_layout.addLayout(left_yaxis_layout)
        # 中间按钮
        middle_yasis_layout = QVBoxLayout()
        middle_yasis_layout.addWidget(QPushButton('左轴→', objectName='addAxis', clicked=self.add_y_left))
        middle_yasis_layout.addWidget(QPushButton('右轴→', objectName='addAxis', clicked=self.add_y_right))
        yaxis_layout.addLayout(middle_yasis_layout)
        # 右侧列头显示
        right_yaxis_layout = QVBoxLayout()
        self.right_top_list = QListWidget(doubleClicked=self.remove_toplist_item)
        self.right_top_list.setMaximumWidth(180)
        right_yaxis_layout.addWidget(self.right_top_list)
        self.right_bottom_list = QListWidget(doubleClicked=self.remove_bottomlist_item)
        self.right_bottom_list.setMaximumWidth(180)
        right_yaxis_layout.addWidget(self.right_bottom_list)
        yaxis_layout.addLayout(right_yaxis_layout)
        parameter_layout.addLayout(yaxis_layout)
        # 轴名称设置
        parameter_layout.addWidget(QLabel('轴名称设置：', objectName='headTip'), alignment=Qt.AlignLeft)
        # x轴
        bottom_xaxis_name_layout = QHBoxLayout()
        bottom_xaxis_name_layout.addWidget(QLabel('X 轴:'))
        self.bottom_x_label_edit = QLineEdit(placeholderText='请输入轴名称')
        bottom_xaxis_name_layout.addWidget(self.bottom_x_label_edit)
        parameter_layout.addLayout(bottom_xaxis_name_layout)
        # Y轴
        yaxis_name_layout = QHBoxLayout()
        yaxis_name_layout.addWidget(QLabel('左轴:'))
        self.left_y_label_edit = QLineEdit(placeholderText='请输入左轴名称')
        yaxis_name_layout.addWidget(self.left_y_label_edit)
        yaxis_name_layout.addWidget(QLabel('右轴:'))
        self.right_y_label_edit = QLineEdit(placeholderText='请输入右轴名称')
        yaxis_name_layout.addWidget(self.right_y_label_edit)
        parameter_layout.addLayout(yaxis_name_layout)
        # 数据范围
        parameter_layout.addWidget(QLabel('数据范围设置：', objectName='headTip'), alignment=Qt.AlignLeft)
        chart_scope_layout1 = QHBoxLayout()
        chart_scope_layout1.addWidget(QLabel('起始日期:'))
        self.scope_start_date = QDateEdit()
        self.scope_start_date.setCalendarPopup(True)
        self.scope_start_date.setEnabled(False)
        chart_scope_layout1.addWidget(self.scope_start_date)
        chart_scope_layout1.addWidget(QLabel('截止日期:'))
        self.scope_end_date = QDateEdit()
        self.scope_end_date.setCalendarPopup(True)
        self.scope_end_date.setEnabled(False)
        chart_scope_layout1.addWidget(self.scope_end_date)
        parameter_layout.addLayout(chart_scope_layout1)
        parameter_layout.addWidget(QPushButton('画图预览', clicked=self.review_chart_clicked), alignment=Qt.AlignRight)
        self.chart_parameter.setMaximumWidth(350)
        self.chart_parameter.setLayout(parameter_layout)
        # 参数设置控件加入布局
        layout.addWidget(self.chart_parameter)
        # 预览控件
        self.review_widget = QWidget(parent=self)
        review_layout = QVBoxLayout(margin=0)
        review_layout.addWidget(QLabel('图表预览', objectName='widgetTip'))
        self.review_chart = QChartView()
        self.review_chart.setRenderHint(QPainter.Antialiasing)
        review_layout.addWidget(self.review_chart)
        # # 图例显示区
        # self.legend_view = QWidget(parent=self.review_widget)
        # legend_layout = QGridLayout()
        # self.legend_view.setLayout(legend_layout)
        # review_layout.addWidget(self.legend_view)
        # 确认设置
        commit_layout = QHBoxLayout()
        commit_layout.addStretch()
        self.current_start = QCheckBox('当前起始')
        commit_layout.addWidget(self.current_start)
        self.current_end = QCheckBox('当前截止')
        commit_layout.addWidget(self.current_end)
        commit_layout.addWidget(QPushButton('确认设置', clicked=self.commit_add_chart))
        review_layout.addLayout(commit_layout)
        # 表详情数据显示
        self.detail_trend_table = QTableWidget()
        self.detail_trend_table.setMaximumHeight(200)
        review_layout.addWidget(self.detail_trend_table)
        self.review_widget.setLayout(review_layout)
        layout.addWidget(self.review_widget)
        self.setLayout(layout)
        self.setMinimumWidth(950)
        self.setMaximumHeight(550)
        self.has_review_chart = False
        self.setStyleSheet("""
        #widgetTip{
            color: rgb(50,80,180);
            font-weight:bold
        }
        #headTip{
            font-weight:bold
        }
        #addAxis{
            max-width:40px
        }
        """)

    # x轴选择改变
    def x_axis_changed(self):
        self.column_header_list.clear()
        for header_index in range(self.detail_trend_table.horizontalHeader().count()):
            text = self.detail_trend_table.horizontalHeaderItem(header_index).text()
            if text == self.x_axis_combo.currentText():
                continue
            self.column_header_list.addItem(text)
        # 清空左轴和右轴的设置
        self.right_top_list.clear()
        self.right_bottom_list.clear()

    # 移除当前列表中的item
    def remove_toplist_item(self, index):
        row = self.right_top_list.currentRow()
        self.right_top_list.takeItem(row)

    def remove_bottomlist_item(self, index):
        row = self.right_bottom_list.currentRow()
        self.right_bottom_list.takeItem(row)

    # 加入左轴
    def add_y_left(self):
        text_in = list()
        for i in range(self.right_top_list.count()):
            text_in.append(self.right_top_list.item(i).text())
        item = self.column_header_list.currentItem() # 获取item
        if item is not None:
            if item.text() not in text_in:
                self.right_top_list.addItem(item.text())

    # 加入右轴
    def add_y_right(self):
        text_in = list()
        for i in range(self.right_bottom_list.count()):
            text_in.append(self.right_bottom_list.item(i).text())
        item = self.column_header_list.currentItem()  # 获取item
        if item is not None:
            if item.text() not in text_in:
                self.right_bottom_list.addItem(item.text())

    # 预览数据
    def review_chart_clicked(self):
        try:
            chart_name = self.chart_name.text()
            chart_category = self.chart_category_combo.currentText()
            # 根据设置从表格中获取画图源数据
            x_axis = self.x_axis_combo.currentText()  # x轴
            left_y_axis = [self.right_top_list.item(i).text() for i in range(self.right_top_list.count())]
            right_y_axis = [self.right_bottom_list.item(i).text() for i in range(self.right_bottom_list.count())]
            # 根据表头将这些列名称换为索引
            x_axis_col = list()
            left_y_cols = list()
            right_y_cols = list()
            header_data = list()
            for header_index in range(self.detail_trend_table.horizontalHeader().count()):
                text = self.detail_trend_table.horizontalHeaderItem(header_index).text()
                header_data.append(text)
                if text == x_axis:
                    x_axis_col.append(header_index)
                for y_left in left_y_axis:
                    if y_left == text:
                        left_y_cols.append(header_index)
                for y_right in right_y_axis:
                    if y_right == text:
                        right_y_cols.append(header_index)
            # 判断是否选择了左轴
            if not left_y_cols:
                popup = InformationPopup(message='请至少选择一列左轴数据。', parent=self)
                if not popup.exec_():
                    popup.deleteLater()
                    del popup
                return
            # 根据设置画图
            start_date = self.scope_start_date.date().toString('yyyy-MM-dd')
            start_date = pd.to_datetime(start_date)
            end_date = self.scope_end_date.date().toString('yyyy-MM-dd')
            end_date = pd.to_datetime(end_date)
            df = self.table_data_frame.copy()
            final_df = df.loc[(df[0] >= start_date) & (df[0] <= end_date)].copy()  # 根据时间范围取数
            # 根据类型进行画图
            if chart_category == u'折线图':  # 折线图
                chart = lines_stacked(name=chart_name, table_df=final_df, x_bottom_cols=x_axis_col, y_left_cols=left_y_cols,
                                      y_right_cols=right_y_cols, legend_labels=header_data, tick_count=12)
                # 设置图例
                # chart.legend().hide()
                # markers = chart.legend().markers()
                # print(markers)
                # row_index = 0
                # col_index = 0
                # for marker in chart.legend().markers():
                #     print(marker.series().name())
                #     # from PyQt5.QtChart import QLineSeries
                #     # QLineSeries.name()
                #     # 每条线设置一个label
                #     legend_label = QLabel(marker.series().name())
                #     self.legend_view.layout().addWidget(legend_label, row_index, col_index)
                #     col_index += 1
                #     if col_index >= 3:
                #         row_index += 1
                #         col_index = 0

            elif chart_category == u'柱形图':
                chart = bars_stacked(name=chart_name, table_df=final_df, x_bottom_cols=x_axis_col,
                                      y_left_cols=left_y_cols, y_right_cols=right_y_cols, legend_labels=header_data, tick_count=12)
            else:
                popup = InformationPopup(message='当前设置不适合作图或系统暂不支持作图。', parent=self)
                if not popup.exec_():
                    popup.deleteLater()
                    del popup
                return
            self.review_chart.setChart(chart)
            self.has_review_chart = True
        except Exception as e:
            popup = InformationPopup(message=str(e), parent=self)
            if not popup.exec_():
                popup.deleteLater()
                del popup

    # 确认添加本张图表
    def commit_add_chart(self):
        if not self.has_review_chart:
            info = InformationPopup(message='请先预览图表，再进行设置!', parent=self)
            if not info.exec_():
                info.deleteLater()
                del info
            return
        category_dict = {
            '折线图': 'line',
            '柱形图': 'bar',
        }
        chart_name = re.sub(r'\s+', '', self.chart_name.text())
        category = category_dict.get(self.chart_category_combo.currentText(), None)
        if not all([chart_name, category]):
            info = InformationPopup(message='请设置图表名称和图表类型!',parent=self)
            if not info.exec_():
                info.deleteLater()
                del info
            return
        # 根据设置从表格中获取数据把选择的列头变为索引
        x_axis = self.x_axis_combo.currentText()  # x轴
        left_y_axis = [self.right_top_list.item(i).text() for i in range(self.right_top_list.count())]
        right_y_axis = [self.right_bottom_list.item(i).text() for i in range(self.right_bottom_list.count())]
        # 根据表头将这些列名称换为索引
        x_axis_cols = list()
        left_y_cols = list()
        right_y_cols = list()
        for header_index in range(self.detail_trend_table.horizontalHeader().count()):
            text = self.detail_trend_table.horizontalHeaderItem(header_index).text()
            if text == x_axis:
                x_axis_cols.append(header_index)
            for y_left in left_y_axis:
                if y_left == text:
                    left_y_cols.append(header_index)
            for y_right in right_y_axis:
                if y_right == text:
                    right_y_cols.append(header_index)
        if not x_axis_cols:
            info = InformationPopup(message='请设置图表X轴！', parent=self)
            if not info.exec_():
                info.deleteLater()
                del info
            return
        if not left_y_cols:
            info = InformationPopup(message='至少左轴要有一列数据!', parent=self)
            if not info.exec_():
                info.deleteLater()
                del info
            return
        # 获取轴名称
        x_bottom_labels = re.split(r';', self.bottom_x_label_edit.text())
        y_left_labels = re.split(r';', self.left_y_label_edit.text())
        y_right_labels = re.split(r';', self.right_y_label_edit.text())
        chart_params = dict()
        chart_params['table_id'] = self.table_id
        chart_params['name'] = chart_name
        chart_params['category'] = category
        chart_params['x_bottom'] = x_axis_cols
        chart_params['x_bottom_label'] = x_bottom_labels
        chart_params['x_top'] = []
        chart_params['x_top_label'] = []
        chart_params['y_left'] = left_y_cols
        chart_params['y_left_label'] = y_left_labels
        chart_params['y_right'] = right_y_cols
        chart_params['y_right_label'] = y_right_labels
        chart_params['is_top'] = False
        if self.current_start.isChecked():
            # print('设置当前起始范围')
            chart_params['start'] = self.scope_start_date.date().toString('yyyy-MM-dd')
        if self.current_end.isChecked():
            # print('设置当前截止')
            chart_params['end'] = self.scope_end_date.date().toString('yyyy-MM-dd')
        # print(chart_params)
        # 上传数据
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'trend/chart/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps(chart_params)
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
            message = response['message']
        except Exception as e:
            message = str(e)
        info = InformationPopup(message=message, parent=self)
        if not info.exec_():
            info.deleteLater()
            del info

    # 获取当前表的数据（预用来设置显示图的数据）
    def getCurrentTrendTable(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/table/' + str(
                    self.table_id) + '/?look=1&mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            column_headers = response['data']['header_data']
            column_headers.pop(0)
            self.x_axis_combo.addItems(column_headers)  # X轴选择
            for text in column_headers:
                if text in self.x_axis_combo.currentText():
                    continue
                self.column_header_list.addItem(text)  # 列头待选表
            # pandas处理数据
            self.table_data_frame = self.pd_handler_data(response['data']['table_data'])
            # 填充表格
            self.showTableData(column_headers, self.table_data_frame)

    # pandas 处理数据
    def pd_handler_data(self, table_data):
        # 转为DF
        table_df = pd.DataFrame(table_data)
        table_df.drop(columns=[0], inplace=True)  # 删除id列
        table_df.columns = [i for i in range(table_df.shape[1])]  # 重置列索引
        table_df[0] = pd.to_datetime(table_df[0])  # 第一列转为时间类型
        table_df.sort_values(by=0, inplace=True)  # 根据时间排序数据
        # 计算数据时间跨度大小显示在范围上
        min_x, max_x = table_df[0].min(), table_df[0].max()  # 第一列时间数据(x轴)的最大值和最小值
        self.scope_start_date.setDateRange(QDate(min_x), QDate(max_x))
        self.scope_end_date.setDateRange(QDate(min_x), QDate(max_x))
        self.scope_start_date.setEnabled(True)
        self.scope_end_date.setEnabled(True)
        self.scope_end_date.setDate(self.scope_end_date.maximumDate())
        return table_df

    # 设置表格显示表数据内容
    def showTableData(self, headers, table_df):
        # 设置行列
        self.detail_trend_table.setRowCount(table_df.shape[0])
        col_count = len(headers)
        self.detail_trend_table.setColumnCount(col_count)
        self.detail_trend_table.setHorizontalHeaderLabels(headers)
        self.detail_trend_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for row, row_content in enumerate(table_df.values.tolist()):
            for col, value in enumerate(row_content):
                if col == 0:  # 时间类
                    value = value.strftime('%Y-%m-%d')
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.detail_trend_table.setItem(row, col, item)


# 创建品种页的数据选择设置表
class VarietyTrendTablesShow(QTableWidget):
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
        super(VarietyTrendTablesShow, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS) + 1)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + [''])
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
                    # 增加【设置】按钮
                    option_button = TableRowReadButton('设置')
                    option_button.button_clicked.connect(self.option_button_clicked)
                    self.setCellWidget(row, col + 1, option_button)

    # 设置图表
    def option_button_clicked(self, option_button):
        current_row, _ = self.get_widget_index(option_button)
        table_id = self.item(current_row, 0).id
        table_text = self.item(current_row, 1).text()
        # 弹窗设置
        try:
            popup = SetChartDetailPopup(table_id, parent=self)
            popup.setWindowTitle(table_text)
            popup.getCurrentTrendTable()
            if not popup.exec_():
                popup.deleteLater()
                del popup
        except Exception as e:
            # print(e)
            pass

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()




# 显示图表
class ShowChartPopup(QDialog):
    def __init__(self, chart_data, *args, **kwargs):
        super(ShowChartPopup, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        chart = self._initial_chart(chart_data)
        chart_view = QChartView()
        chart_view.setChart(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        layout.addWidget(chart_view)
        self.resize(880, 380)
        self.setLayout(layout)

    # 初始化图表
    def _initial_chart(self, chart_data):
        self.setWindowTitle(chart_data['name'])
        header_data = chart_data['header_data']
        header_data.pop(0)  # 去掉id
        table_data = chart_data['table_data']
        # 转为pandas DataFrame
        table_df = pd.DataFrame(table_data)
        table_df.drop(columns=[0], inplace=True)  # 删除id列
        table_df.columns = [i for i in range(table_df.shape[1])]  # 重置列索引
        table_df[0] = pd.to_datetime(table_df[0])  # 第一列转为时间类型
        table_df.sort_values(by=0, inplace=True)
        try:
            if chart_data['start'] and chart_data['end']:
                start_date = pd.to_datetime(chart_data['start'])
                end_date = pd.to_datetime(chart_data['end'])
                table_df = table_df[(start_date <= table_df[0]) & (table_df[0] <= end_date)]
            elif chart_data['start']:
                start_date = pd.to_datetime(chart_data['start'])
                table_df = table_df[(start_date <= table_df[0])]
            elif chart_data['end']:
                end_date = pd.to_datetime(chart_data['end'])
                table_df = table_df[(table_df[0] <= end_date)]
            else:
                pass
            # print(chart_data)
            x_bottom = (json.loads(chart_data['x_bottom']))
            y_left = json.loads(chart_data['y_left'])
            y_right = json.loads(chart_data['y_right'])
            # 根据图表类型画图
            if chart_data['category'] == 'line':
                chart = lines_stacked(name=chart_data['name'], table_df=table_df, x_bottom_cols=x_bottom, y_left_cols=y_left,
                                      y_right_cols=y_right, legend_labels=header_data, tick_count=40)
            elif chart_data['category'] == 'bar':
                chart = bars_stacked(name=chart_data['name'], table_df=table_df, x_bottom_cols=x_bottom, y_left_cols=y_left,
                                      y_right_cols=y_right, legend_labels=header_data, tick_count=40)
            else:
                chart = QChart()
        except Exception:
            chart = QChart()
        return chart
