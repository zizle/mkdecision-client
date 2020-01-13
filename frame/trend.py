# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
import pandas as pd
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QPushButton, QScrollArea, QVBoxLayout, QLabel, \
    QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPainter, QFont, QBrush, QColor
from PyQt5.QtChart import QChart
from widgets.chart import ChartView, DetailChartView
from widgets.base import ScrollFoldedBox, LoadedPage
import settings
from utils.charts import draw_lines_stacked, draw_bars_stacked


# 展示图表的线程
class ChartShownThread(QThread):
    receive_table_data = pyqtSignal(int)

    def __init__(self, chart_view_list, *args, **kwargs):
        super(ChartShownThread, self).__init__(*args, **kwargs)
        self.chart_view_list = chart_view_list

    def run(self):
        for chart_view in self.chart_view_list:
            chart_data = chart_view.chart_data
            # 根据chart_data 请求源数据
            try:
                table_id = chart_data['table']
                r = requests.get(
                    url=settings.SERVER_ADDR + 'trend/table/' + str(
                        table_id) + '/?look=1&mc=' + settings.app_dawn.value('machine')
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 200:
                    raise ValueError(response['message'])
            except Exception:
                continue
            else:
                # 处理表数据信号传出
                # header_data = response['data']['header_data']
                # table_data = response['data']['table_data']
                chart_data['header_data'] = response['data']['header_data']
                chart_data['table_data'] = response['data']['table_data']
                self.receive_table_data.emit(chart_view.index_id)


# 图表详情页
class DetailChartWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(DetailChartWidget, self).__init__(*args, **kwargs)
        # 详细页布局
        layout = QVBoxLayout(margin=0,spacing=0)
        message_button_layout = QHBoxLayout(margin=0,spacing=0)

        font = QFont()
        font.setFamily('Webdings')
        self.close_button = QPushButton('r', parent=self, font=font, objectName='closeButton', cursor=Qt.PointingHandCursor)
        message_button_layout.addWidget(self.close_button, alignment=Qt.AlignLeft)
        self.network_message_label = QLabel('', parent=self)
        message_button_layout.addWidget(self.network_message_label)
        layout.addLayout(message_button_layout)
        # 图表展示区
        self.chart_view = DetailChartView()
        # 图表数据显示区
        self.table_view = QTableWidget()
        self.table_view.verticalHeader().hide()
        layout.addWidget(self.chart_view)
        layout.addWidget(self.table_view)
        self.setLayout(layout)
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        self.setObjectName('chartDetail')
        self.setStyleSheet("""
        
        #closeButton{
            border:none;
            min-width: 10px;
            max-width: 10px;
            min-height: 10px;
            max-height: 10px;
            background-color: rgb(220, 220, 220)
        }
        #closeButton:hover{
            background-color: rgb(220, 120, 100);
            border-radius: 5px;
        }
        """)


# 图表展示Widget,
class ChartsFrameView(QScrollArea):
    def __init__(self, charts, *args, **kwargs):
        super(ChartsFrameView, self).__init__(*args, **kwargs)
        self.container = QWidget(parent=self)
        self.charts = charts
        layout = QGridLayout(margin=0, spacing=5)
        self.setWidgetResizable(True)
        self.container.setLayout(layout)
        self.setWidget(self.container)
        self.chart_view_list = list()
        self.chart_detail = None

    # 设置chartView在布局里
    def show_charts(self):
        row_index, col_index = 0, 0  # 记录布局的行数和列数
        for index, chart_item in enumerate(self.charts):
            chart_view = ChartView(chart_data=chart_item)
            chart_view.setMinimumHeight(280)
            chart_view.index_id = index
            chart_view.clicked.connect(self.chart_enlarge_clicked)
            self.container.layout().addWidget(chart_view, row_index, col_index)
            col_index += 1
            if col_index >= 2:
                row_index += 1
                col_index = 0
            self.chart_view_list.append(chart_view)
        self.container.setMinimumHeight(self.container.layout().rowCount() * 280)
        self.container.layout().setRowStretch(self.container.layout().rowCount(), 1)
        # 开启线程请求数据
        self.thread_get_table()

    # 线程请求charts数据并显示
    def thread_get_table(self):
        if hasattr(self, 'draw_charts'):
            del self.draw_charts
        self.draw_charts = ChartShownThread(chart_view_list=self.chart_view_list)
        self.draw_charts.finished.connect(self.draw_charts.deleteLater)
        self.draw_charts.receive_table_data.connect(self.draw_chart)
        self.draw_charts.start()

    # 画图
    def draw_chart(self, index_id):
        for chart_view in self.chart_view_list:
            try:
                if chart_view.index_id == index_id:
                    chart, _ = self.data_to_chart(chart_view.chart_data, tick_count=10)
                    chart_view.setChart(chart)
                    break
            except Exception:
                continue

    # 点击图表放大
    def chart_enlarge_clicked(self, chart_data):
        self.chart_detail = DetailChartWidget(parent=self)
        self.chart_detail.resize(self.width(), self.height())
        self.chart_detail.close_button.clicked.connect(self.delete_chart_detail)  # 关闭删除控件
        # 数据画图，将图和数据展示在相应的控件中
        chart, table_df = self.data_to_chart(chart_data, tick_count=40)
        self.chart_detail.chart_view.setChart(chart)
        self.chart_detail.chart_view.installMouseHoverEvent()
        # 数据入表
        header_data = chart_data['header_data'][1:]
        self.chart_detail.table_view.clear()
        self.chart_detail.table_view.setRowCount(table_df.shape[0])  # 行
        self.chart_detail.table_view.setColumnCount(table_df.shape[1])  # 列
        self.chart_detail.table_view.setHorizontalHeaderLabels(header_data)
        for row, row_content in enumerate(table_df.to_numpy()):
            for col in range(len(header_data)):
                if col == 0:
                    item = QTableWidgetItem(row_content[col].strftime('%Y-%m-%d'))
                else:
                    item = QTableWidgetItem(str(row_content[col]))
                item.setTextAlignment(Qt.AlignCenter)
                if (row & 1) == 1:  # 奇数行
                    item.setBackground(QBrush(QColor(218, 233, 231)))
                self.chart_detail.table_view.setItem(row, col, item)
                self.chart_detail.table_view.setRowHeight(row, 23)  # 行高
        self.chart_detail.show()


    # 删除掉详情页
    def delete_chart_detail(self):
        if self.chart_detail:
            self.chart_detail.deleteLater()
        self.chart_detail = None

    def resizeEvent(self, event):
        super(ChartsFrameView, self).resizeEvent(event)
        if self.chart_detail:
            print('存在，变化')
            self.chart_detail.resize(self.parent().width(), self.parent().height())

    # 使用数据画图
    @staticmethod
    def data_to_chart(chart_data, tick_count):
        header_data = chart_data['header_data'][1:]
        table_data = chart_data['table_data']
        # 转为pandas DataFrame
        table_df = pd.DataFrame(table_data)
        table_df.drop(columns=[0], inplace=True)  # 删除id列
        table_df.columns = [i for i in range(table_df.shape[1])]  # 重置列索引
        table_df[0] = pd.to_datetime(table_df[0])  # 第一列转为时间类型
        table_df.sort_values(by=0, inplace=True)
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
        x_bottom = (json.loads(chart_data['x_bottom']))
        y_left = json.loads(chart_data['y_left'])
        # 根据图表类型画图
        if chart_data['category'] == 'line':
            chart = draw_lines_stacked(name=chart_data['name'], table_df=table_df, x_bottom=x_bottom,
                                       y_left=y_left, legends=header_data, tick_count=tick_count)
        elif chart_data['category'] == 'bar':
            chart = draw_bars_stacked(name=chart_data['name'], table_df=table_df, x_bottom=x_bottom,
                                      y_left=y_left, legends=header_data, tick_count=tick_count)
        else:
            chart = QChart()
        return chart, table_df


# 数据分析主页
class TrendPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(TrendPage, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=2)
        self.variety_folded = ScrollFoldedBox()
        self.variety_folded.left_mouse_clicked.connect(self.variety_clicked)
        self.variety_folded.setMaximumWidth(250)
        layout.addWidget(self.variety_folded)
        self.frame = LoadedPage()
        layout.addWidget(self.frame)
        self.setLayout(layout)

    # 获取所有品种组和品种
    def getGroupVarieties(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'group-varieties/?mc=' + settings.app_dawn.value('machine')
            )
            if r.status_code != 200:
                raise ValueError('获取失败!')
            response = json.loads(r.content.decode('utf-8'))
        except Exception:
            pass
        else:
            for group_item in response['data']:
                head = self.variety_folded.addHead(group_item['name'])
                body = self.variety_folded.addBody(head=head)
                body.addButtons(group_item['varieties'])
            self.variety_folded.container.layout().addStretch()

    # 获取主页的图表
    def getTrendPageCharts(self):
        try:
            r = requests.get(url=settings.SERVER_ADDR + 'trend/chart/?mc=' + settings.app_dawn.value('machine'))
            if r.status_code != 200:
                raise ValueError('获取主页图表失败!')
            response = json.loads(r.content.decode('utf-8'))
        except Exception:
            pass
        else:
            # 展示图表
            self.frame.clear()
            charts_frame = ChartsFrameView(charts=response['data'])
            charts_frame.show_charts()
            self.frame.addWidget(charts_frame)

    # 点击了品种,请求当前品种下的品种页显示图表
    def variety_clicked(self, vid, text):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/' + str(
                    vid) + '/chart/?mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            # 展示图表
            self.frame.clear()
            charts_frame = ChartsFrameView(charts=response['data'])
            charts_frame.show_charts()
            self.frame.addWidget(charts_frame)

