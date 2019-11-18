# _*_ coding:utf-8 _*_
# __Author__： zizle
import sys
import json
import random
import requests
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTreeWidget, QTableWidget, QTreeWidgetItem,\
    QTabWidget, QGridLayout, QVBoxLayout, QTableWidgetItem, QHeaderView, QGraphicsOpacityEffect
# from PyQt5.QtChart import QChartView, QChart, QLineSeries, QBarSeries, QBarSet
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QPropertyAnimation, QRect, Qt
from widgets.base import MenuScrollContainer
import config
from widgets.danalysis import ChartView
from thread.request import RequestThread


# 首页初始右侧区域widget
class VHRightWidgets(QWidget):
    def __init__(self, chart_horizontal_count, *args, **kwargs):
        super(VHRightWidgets, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()  # 根据需求灵活做布局
        self.chart_horizontal_count = chart_horizontal_count
        self.chart_layout = QGridLayout()
        layout.addLayout(self.chart_layout)
        # layout.addWidget(QPushButton('测试控件'))
        # 设置遮罩层
        self.opacity = QGraphicsOpacityEffect()
        self.opacity.setOpacity(0.4)
        self.cover = QWidget(self)
        self.cover.setGraphicsEffect(self.opacity)
        self.cover.setStyleSheet("background-color: rgb(150,150,150);")
        self.cover.setAutoFillBackground(True)
        self.cover.close()
        self.setLayout(layout)
        # 请求图表名称及其数据
        self.get_charts(url=config.SERVER_ADDR + 'danalysis/charts/home/')

    def get_charts(self, url):
        if not url:
            return
        try:
            response = requests.get(
                url=url,
                headers=config.CLIENT_HEADERS,
                data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
                cookies=config.app_dawn.value('cookies')
            )
            response_content = json.loads(response.content.decode('utf-8'))
        except Exception:
            return
        if response_content['error']:
            return
        # 布局个数处理
        row_index = 0
        column_index = 0
        for chart_index, chart_item in enumerate(response_content['data']):
            # 创建图表容器和图表控件
            chart_view = ChartView(row=row_index, column=column_index)
            chart_view.clicked.connect(self.chart_view_enlarge)
            chart = QChart()
            # 根据图表类别创建图表(默认折线图)
            chart.setTitle(chart_item['name'])
            chart.legend().hide()  # 单一数据隐藏图例
            if chart_item['chart_type'] == config.CHART_TYPE[0][0]:  # 折线图
                series = QLineSeries()
                for data_item in chart_item['data']:
                    series.append(float(data_item[0]), float(data_item[1]))
                chart.addSeries(series)
            elif chart_item['chart_type'] == config.CHART_TYPE[1][0]:  # 柱状图
                series = QBarSeries()
                bar = QBarSet('')
                for data_item in chart_item['data']:
                    bar.append(float(data_item[1]))
                series.append(bar)
                chart.addSeries(series)
                chart.createDefaultAxes()
                chart_view.setWatermarkButtonVisible(False)
            else:
                chart.setTitle('暂无法显示该数据图.')
            chart_view.setChart(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart.createDefaultAxes()
            chart.setBackgroundVisible(False)
            chart_view.setStyleSheet("""
                background-image: url('media/chartbg-watermark.png');
            """)
            self.chart_layout.addWidget(chart_view, row_index, column_index)
            # 计数处理
            column_index += 1
            if column_index >= self.chart_horizontal_count:
                column_index = 0
                row_index += 1

    def chart_view_enlarge(self, data):
        title = data['title']
        if not hasattr(self, 'chart_view'):
            self.chart_view = ChartView(row=0, column=0, zoom_in=True)
            self.chart_view.clicked.connect(self.chart_view_enlarge)
        if self.chart_view.zoom_in_out.zoom_in:
            # 重新实例化一个chart
            chart = QChart(title=title)
            for series in data['series']:
                line = QLineSeries()
                for index, x, in enumerate(series['x_values']):
                    line.append(x, series['y_values'][index])
                chart.addSeries(line)
            chart.createDefaultAxes()
            chart.setBackgroundVisible(False)
            self.chart_view.setChart(chart)
            # 删除原来的widget
            if hasattr(self, 'new_widget'):
                self.new_widget.deleteLater()
                del self.new_widget
            # 重新设置一个widget
            self.new_widget = QWidget(self)
            # 显示数据的表格
            self.series_value_table = QTableWidget()
            # 填充第一条线的数据
            self.fill_chart_value_table(data['series'][0]['x_values'], data['series'][0]['y_values'])
            layout = QVBoxLayout(spacing=0)
            layout.setContentsMargins(0,0,0,0)
            self.new_widget.setLayout(layout)
            self.new_widget.layout().addWidget(self.chart_view)
            self.new_widget.layout().addWidget(self.series_value_table)
            # 设置new widget变大的动画
            self.anim = QPropertyAnimation(self.new_widget, b"geometry")
            self.anim.setDuration(400)
            width = self.width()
            height = self.height()
            self.anim.setStartValue(QRect(width/2 - 150, height/2 - 150, 300, 300))  # 大小100*100
            self.anim.setEndValue(QRect(0, 0, width, height))  # 大小200*200
            self.anim.start()
            # self.new_widget.resize(self.width(), self.height())
            self.cover.resize(self.width(), self.height())
            self.cover.show()
            self.new_widget.show()
            self.raise_()
            self.cover.raise_()
            self.new_widget.raise_()
        else:  # 当前为扩大状态，那么就缩小
            # 设置new widget变小的动画
            self.anim = QPropertyAnimation(self.new_widget, b"geometry")
            self.anim.setDuration(200)
            width = self.width()
            height = self.height()
            self.anim.setStartValue(QRect(0, 0, width, height))
            self.anim.setEndValue(QRect(width / 2, height / 2, 0, 0))
            self.anim.start()
            self.new_widget.show()
            self.cover.close()
            self.chart_view.zoom_in_out.zoom_in = True  # 重置为True才可再次点击别的图表

    # 点击某个图表显示的数据详情表格
    def fill_chart_value_table(self, x_axis, y_axis):
        self.series_value_table.clear()
        self.series_value_table.setRowCount(len(x_axis))
        self.series_value_table.setColumnCount(3)  # 列数
        self.series_value_table.setHorizontalHeaderLabels(['x值', 'y值', '增减'])
        for row in range(len(x_axis)):
            for col in range(3):
                if col == 0:
                    item = QTableWidgetItem(str(x_axis[row]))
                elif col == 1:
                    item = QTableWidgetItem(str(y_axis[row]))
                else:
                    if row == 0:
                        value = y_axis[row] - 0
                    else:
                        value = y_axis[row] - y_axis[row - 1]
                    item = QTableWidgetItem(str(value))
                item.setTextAlignment(132)
                self.series_value_table.setItem(row, col, item)
        self.series_value_table.setFixedHeight(340)
        self.series_value_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def resizeEvent(self, event):
        # 监听窗口大小变化
        if hasattr(self, 'new_widget'):
            self.new_widget.resize(self.width(), self.height())


# 品种详情右侧widget(无分某项指标)
class VDRightWidgets(VHRightWidgets):
    def __init__(self, variety, chart_horizontal_count, *args, **kwargs):
        super(VDRightWidgets, self).__init__(chart_horizontal_count, *args, **kwargs)
        self.variety = variety
        # layout = QHBoxLayout()
        # self.chart_layout = QGridLayout()
        # self.chart_horizontal_count = chart_horizontal_count
        # layout.addLayout(self.chart_layout)
        # self.setLayout(layout)
        self.get_charts(url=config.SERVER_ADDR + 'danalysis/charts/variety/')

    def get_charts(self, url):
        if not url:
            return
        try:
            response = requests.get(
                url=url,
                headers=config.CLIENT_HEADERS,
                data=json.dumps({"machine_code": config.app_dawn.value("machine"), 'variety': self.variety}),
                cookies=config.app_dawn.value('cookies')
            )
            response_content = json.loads(response.content.decode('utf-8'))
        except Exception:
            return
        if response_content['error']:
            return
        x_axes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        row_index = 0
        column_index = 0
        for chart_index, chart_item in enumerate(response_content['data']):
            # 创建图表容器和图表控件
            chart_view = ChartView(row=row_index, column=column_index)
            chart_view.clicked.connect(self.chart_view_enlarge)
            chart = QChart()
            # 根据图表类别创建图表(默认折线图)
            chart.setTitle(chart_item['name'])
            chart.legend().hide()  # 单一数据隐藏图例
            if chart_item['chart_type'] == config.CHART_TYPE[0][0]:  # 折线图
                series = QLineSeries()
                for data_item in chart_item['data']:
                    series.append(float(data_item[0]), float(data_item[1]))
                chart.addSeries(series)
            elif chart_item['chart_type'] == config.CHART_TYPE[1][0]:  # 柱状图
                series = QBarSeries()
                bar = QBarSet('')
                for data_item in chart_item['data']:
                    bar.append(float(data_item[1]))
                series.append(bar)
                chart.addSeries(series)
                chart.createDefaultAxes()
                chart_view.setWatermarkButtonVisible(False)
            else:
                chart.setTitle('暂无法显示该数据图.')
            chart_view.setChart(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart.createDefaultAxes()
            chart.setBackgroundVisible(False)
            chart_view.setStyleSheet("""
                background-image: url('media/chartbg-watermark.png');
            """)
            self.chart_layout.addWidget(chart_view, row_index, column_index)
            # 计数处理
            column_index += 1
            if column_index >= self.chart_horizontal_count:
                column_index = 0
                row_index += 1


# 品种具体某项指标详情页
class DetailWidgetShow(QWidget):
    def __init__(self, *args, **kwargs):
        super(DetailWidgetShow, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        # 初始化图表
        self.chart_view = QChartView()
        # 表格数据
        self.chart_table = QTableWidget()
        layout.addWidget(self.chart_view)
        layout.addWidget(self.chart_table)
        self.setLayout(layout)
        
    def draw_series(self, x_values, y_values, series_name):
        chart = QChart()
        # 添加水印背景图片
        chart.setBackgroundVisible(False)
        self.chart_view.setStyleSheet("""
            background-image: url('media/chartbg-watermark.png');
        """)
        series = QBarSeries()
        bar = QBarSet(series_name)
        for index in range(len(x_values)):
            bar.append(y_values[index])
        series.append(bar)
        chart.addSeries(series)
        chart.createDefaultAxes()
        self.chart_view.setChart(chart)
        # 表格数据
        self.fill_chart_data(x_values, y_values)

    def fill_chart_data(self, x_axes, y_axes):
        self.chart_table.clear()
        self.chart_table.setRowCount(len(x_axes))
        self.chart_table.setColumnCount(3)  # 列数
        self.chart_table.setHorizontalHeaderLabels(['月份', '产量(万吨)', '增减(万吨)'])
        for row in range(len(x_axes)):
            for col in range(3):
                if col == 0:
                    item = QTableWidgetItem(str(x_axes[row]))
                elif col == 1:
                    item = QTableWidgetItem(str(y_axes[row]))
                else:
                    if row == 0:
                        value = y_axes[row] - 0
                    else:
                        value = y_axes[row] - y_axes[row - 1]
                    item = QTableWidgetItem(str(value))
                item.setTextAlignment(132)
                self.chart_table.setItem(row, col, item)
        self.chart_table.setFixedHeight(340)
        self.chart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # chart_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)


# 品种首页(初始页面,索引为0的tab)
class VarietyHome(QWidget):
    def __init__(self, *args, **kwargs):
        super(VarietyHome, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        self.variety_menu = MenuScrollContainer(column=3)
        vh_right = VHRightWidgets(chart_horizontal_count=2)  # 参数为横向展示的个数
        layout.addWidget(self.variety_menu)  # 左侧菜单
        layout.addWidget(vh_right)  # 右侧区域widget
        self.setLayout(layout)
        # style
        layout.setContentsMargins(0, 0, 0, 0)
        # 初始化品种菜单数据
        self.variety_menu.get_menu(url=config.SERVER_ADDR + 'danalysis/variety/')


# 品种详情页(索引为1的tab)
class VarietyDetail(QWidget):
    def __init__(self, variety, width, *args, **kwargs):
        super(VarietyDetail, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        # widgets
        left_tab = QTabWidget()
        self.detail_tree = QTreeWidget()
        self.vd_right = VDRightWidgets(variety=variety, chart_horizontal_count=2)
        # style
        left_tab.setMaximumWidth(width)
        left_tab.setMinimumWidth(width)
        self.detail_tree.setHeaderHidden(True)
        # widgets add tab
        left_tab.addTab(self.detail_tree, '行业数据')
        left_tab.addTab(QWidget(), "我的收藏")
        layout.addWidget(left_tab)
        layout.addWidget(self.vd_right)
        self.setLayout(layout)
        # signal
        self.detail_tree.clicked.connect(self.tree_item_clicked)
        # style
        self.detail_tree.setStyleSheet("""
        QTreeWidget{
            font-size: 13px;
        }
        QTreeWidget::item{
            min-height: 30px;
            border: none;
            padding-left: 5px;
        }
        QTreeWidget::item:selected {
            border:none;
            color: rgb(0,0,0)
        }
        QTreeWidget::item:!selected{
            
        }
        QTreeWidget::item:hover {
            background-color: rgb(230,230,230);
            cursor: pointer;
        }
        """)
        # initial data
        self.menu_thread = None
        self.get_detail_menu(url=config.SERVER_ADDR + 'danalysis/detail_menu/' + variety + '/')

    # 请求品种的详细菜单
    def get_detail_menu(self, url=None):
        if not url:
            return
        if self.menu_thread:
            del self.menu_thread
        self.menu_thread = RequestThread(
            url=url,
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.menu_thread.response_signal.connect(self.menu_thread_back)
        self.menu_thread.finished.connect(self.menu_thread.deleteLater)
        self.menu_thread.start()

    def menu_thread_back(self, content):
        print('piece.danalysis.py {} 请求到品种详细菜单: '.format(str(sys._getframe().f_lineno)), content)
        if content['error']:
            return
        for menu_item in content['data']:
            menu = QTreeWidgetItem(self.detail_tree)
            menu.setText(0, menu_item['name'])
            # menu.setTextAlignment(0, Qt.AlignCenter)
            menu.name_en = menu_item['name_en']
            # 添加子节点
            for sub_module in menu_item['subs']:
                child = QTreeWidgetItem()
                child.name_en = sub_module['name_en']
                child.setText(0, sub_module['name'])
                menu.addChild(child)
        self.detail_tree.expandAll()

    def tree_item_clicked(self):
        item = self.detail_tree.currentItem()
        if item.childCount():  # has children open the root
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        else:
            parent = item.parent()
            name_text = item.text(0)
            name_en = item.name_en
            # 一级菜单无功能
            if not parent:
                return
            # 先去除主页默认显示的详情页面
            if not hasattr(self, 'detail_show'):
                self.detail_show = DetailWidgetShow()
            self.detail_show.show()
            if self.layout().itemAt(1).widget() != self.detail_show:
                self.layout().itemAt(1).widget().close()
                self.layout().removeWidget(self.layout().itemAt(1).widget())
                self.layout().addWidget(self.detail_show)
            # 生成数据
            x_axes = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月', '一月', '二月']
            y_axes = [random.randint(1, 1000) for _ in range(len(x_axes))]
            # 更新数据
            self.detail_show.draw_series(x_axes, y_axes, series_name=name_text)


