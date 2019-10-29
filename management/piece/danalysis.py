# _*_ coding:utf-8 _*_
# __Author__： zizle
import sys
import json
import random
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTreeWidget, QTableWidget, QTreeWidgetItem,\
    QTabWidget, QGridLayout, QVBoxLayout, QTableWidgetItem, QHeaderView
from PyQt5.QtChart import QChartView, QChart, QLineSeries, QBarSeries, QBarSet
from PyQt5.QtGui import QPainter
from widgets.base import MenuScrollContainer
import config
from thread.request import RequestThread


# 首页初始右侧图表区widget
class VHChartsWidgets(QWidget):
    def __init__(self, *args, **kwargs):
        super(VHChartsWidgets, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        # 实例化各种图表
        chart_names = ['文华指数', '有色金属指数', '黒链指数', '化工指数', '农产品指数']
        x_axes = [0,1,2,3,4,5,6,7,8,9,10]
        for i in range(5):
            y_axes = [random.randint(1, 100) for _ in range(len(x_axes))]
            chart_view = QChartView()
            chart = QChart()
            series = QLineSeries()
            for idx, x in enumerate(x_axes):
                series.append(x, y_axes[idx])
            chart.addSeries(series)
            chart.setTitle(chart_names[i])
            chart_view.setChart(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart.createDefaultAxes()
            if i <= 1:
                layout.addWidget(chart_view, 0, i)
            elif 1 < i <= 3:
                layout.addWidget(chart_view, 1, i-2)
            else:
                layout.addWidget(chart_view, 2, i-4)
        self.setLayout(layout)


# 品种详情初始图表区
class VDChartsWidgets(QWidget):
    def __init__(self, *args, **kwargs):
        super(VDChartsWidgets, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        # 实例化各种图表
        chart_names = ['现货价格', '期货价格', '产量', '进出口', '库存', '持仓排名']
        x_axes = [0,1,2,3,4,5,6,7,8,9,10]
        for i in range(6):
            y_axes = [random.randint(1, 1000) for _ in range(len(x_axes))]
            chart_view = QChartView()
            chart = QChart()
            series = QLineSeries()
            for idx, x in enumerate(x_axes):
                series.append(x, y_axes[idx])
            chart.addSeries(series)
            chart.setTitle(chart_names[i])
            chart_view.setChart(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart.createDefaultAxes()
            if i <= 1:
                layout.addWidget(chart_view, 0, i)
            elif 1 < i <= 3:
                layout.addWidget(chart_view, 1, i-2)
            else:
                layout.addWidget(chart_view, 2, i-4)
        self.setLayout(layout)


class DetailDWidgetShow(QWidget):
    def __init__(self, option, *args, **kwargs):
        super(DetailDWidgetShow, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        # 初始化图表
        chart_view = QChartView()
        chart = QChart()
        x_axes = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
        y_axes = [random.randint(1, 1000) for _ in range(len(x_axes))]
        series_names = [option]
        series = QBarSeries()
        for name in series_names:
            bar = QBarSet(name)
            for index in range(len(x_axes)):
                bar.append(y_axes[index])
            series.append(bar)
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart_view.setChart(chart)
        # 表格数据
        chart_table = QTableWidget()
        chart_table.setRowCount(len(x_axes))
        chart_table.setColumnCount(3)  # 列数
        chart_table.setHorizontalHeaderLabels(['月份', '产量(万吨)', '增减(万吨)'])
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
                chart_table.setItem(row, col, item)
        chart_table.setFixedHeight(340)
        chart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # chart_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(chart_view)
        layout.addWidget(chart_table)
        self.setLayout(layout)


# 品种首页(初始页面,索引为0的tab)
class VarietyHome(QWidget):
    def __init__(self, *args, **kwargs):
        super(VarietyHome, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        self.variety_menu = MenuScrollContainer(column=3)
        vh_charts = VHChartsWidgets()
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
        self.vd_charts = VDChartsWidgets()
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
            print(item.name_en)
            self.vd_charts.hide()
            if hasattr(self, 'detail_show'):
                self.detail_show.hide()
                del self.detail_show
            self.detail_show = DetailDWidgetShow(option=name_text)
            self.layout().addWidget(self.detail_show)
