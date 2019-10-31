# _*_ coding:utf-8 _*_
# __Author__： zizle
import sys
import json
import random
import requests
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTreeWidget, QTableWidget, QTreeWidgetItem,\
    QTabWidget, QGridLayout, QVBoxLayout, QTableWidgetItem, QHeaderView, QPushButton
from PyQt5.QtChart import QChartView, QChart, QLineSeries, QBarSeries, QBarSet
from PyQt5.QtGui import QPainter
from widgets.base import MenuScrollContainer
import config
from widgets.danalysis import ChartView
from thread.request import RequestThread


# 首页初始右侧图表区widget
class VHChartsWidgets(QWidget):
    def __init__(self, horizontal_count, *args, **kwargs):
        super(VHChartsWidgets, self).__init__(*args, **kwargs)
        self.horizontal_count = horizontal_count
        layout = QGridLayout()
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
        x_axes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        row_index = 0
        column_index = 0
        for chart_index, chart_data in enumerate(response_content['data']):
            y_axes = [random.randint(1, 100) for _ in range(len(x_axes))]
            chart_view = ChartView()
            chart_view.clicked.connect(self.chart_view_clicked)
            chart = QChart()
            series = QLineSeries()
            for idx, x in enumerate(x_axes):
                series.append(x, y_axes[idx])
            chart.addSeries(series)
            chart.setTitle(chart_data['name'])
            chart_view.setChart(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart.createDefaultAxes()
            chart.setBackgroundVisible(False)
            chart_view.setStyleSheet("""
                background-image: url('media/shuiyin.png');
            """)
            self.layout().addWidget(chart_view, row_index, column_index)
            # 计数处理
            column_index += 1
            if column_index >= self.horizontal_count:
                column_index = 0
                row_index += 1

    def chart_view_clicked(self, chart_view):
        # 图表被点击
        for i in range(self.layout().count()):
            view = self.layout().itemAt(i).widget()
            if view != chart_view:
                view.hide()


# 品种详情初始图表区(无分某项指标)
class VDChartsWidgets(QWidget):
    def __init__(self, variety, horizontal_count, *args, **kwargs):
        super(VDChartsWidgets, self).__init__(*args, **kwargs)
        self.variety = variety
        layout = QGridLayout()
        self.horizontal_count = horizontal_count
        self.setLayout(layout)
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
        for chart_index, chart_data in enumerate(response_content['data']):
            y_axes = [random.randint(1, 100) for _ in range(len(x_axes))]
            chart_view = QChartView()
            chart = QChart()
            series = QLineSeries()
            for idx, x in enumerate(x_axes):
                series.append(x, y_axes[idx])
            chart.addSeries(series)
            chart.setTitle(chart_data['name'])
            chart_view.setChart(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart.createDefaultAxes()
            chart.setBackgroundVisible(False)
            chart_view.setStyleSheet("""
                background-image: url('media/shuiyin.png');
            """)
            self.layout().addWidget(chart_view, row_index, column_index)
            # 计数处理
            column_index += 1
            if column_index >= self.horizontal_count:
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
            background-image: url('media/shuiyin.png');
        """)

        # pixmap = QPixmap('media/shuiyin.png')
        # label = QLabel("这是一个标签", self.chart_view)
        # label.setFixedSize(150, 50)
        # label.setPixmap(pixmap)
        # label.setScaledContents(True)

        series = QBarSeries()
        bar = QBarSet(series_name)
        for index in range(len(x_values)):
            bar.append(y_values[index])
        series.append(bar)
        chart.addSeries(series)
        chart.createDefaultAxes()
        self.chart_view.setChart(chart)
        # 表格数据
        self.chart_table.clear()
        self.fill_chart_data(x_values, y_values)

    def fill_chart_data(self, x_axes, y_axes):
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
        vh_charts = VHChartsWidgets(horizontal_count=2)  # 参数为横向展示的个数
        layout.addWidget(self.variety_menu)  # 左侧菜单
        layout.addWidget(vh_charts)  # 右侧图表区
        self.setLayout(layout)
        # style
        layout.setContentsMargins(0, 0, 0, 0)
        # 初始化品种菜单数据
        self.variety_menu.get_menu(url=config.SERVER_ADDR + 'danalysis/variety_menu/')


# 品种详情页(索引为1的tab)
class VarietyDetail(QWidget):
    def __init__(self, variety, width, *args, **kwargs):
        super(VarietyDetail, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        # widgets
        left_tab = QTabWidget()
        self.detail_tree = QTreeWidget()
        self.vd_charts = VDChartsWidgets(variety=variety, horizontal_count=2)
        # style
        left_tab.setMaximumWidth(width)
        left_tab.setMinimumWidth(width)
        self.detail_tree.setHeaderHidden(True)
        # widgets add tab
        left_tab.addTab(self.detail_tree, '行业数据')
        left_tab.addTab(QWidget(), "我的收藏")
        layout.addWidget(left_tab)
        layout.addWidget(self.vd_charts)
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

