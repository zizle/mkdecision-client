# _*_ coding:utf-8 _*_
# __Author__： zizle
import xlrd
import json
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QGridLayout, QVBoxLayout, QTableWidget, QPushButton,\
    QComboBox, QFileDialog, QTableWidgetItem, QMessageBox, QHeaderView
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QBarSet, QBarSeries
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import pyqtSignal, Qt
import config
from thread.request import RequestThread


# 上传数据分析首页图表
class DANewHomeChart(QDialog):
    upload_new = pyqtSignal(dict)

    def __init__(self):
        super(DANewHomeChart, self).__init__()
        layout = QVBoxLayout()
        name = QLabel('图表名称:')
        self.name_edit = QLineEdit()
        self.name_en = QLabel('英文名称:')
        self.name_en_edit = QLineEdit()
        option = QLabel('图表类型:')
        self.type_selection = QComboBox()
        self.chart_type = list()
        chart_type_zh = list()
        for t in config.CHART_TYPE:
            self.chart_type.append(t[0])
            chart_type_zh.append(t[1])
        self.type_selection.addItems(chart_type_zh)
        edit_layout = QGridLayout()
        edit_layout.addWidget(name, 0, 0)
        edit_layout.addWidget(self.name_edit, 0, 1)
        edit_layout.addWidget(self.name_en, 1, 0)
        edit_layout.addWidget(self.name_en_edit, 1, 1)
        edit_layout.addWidget(option, 2, 0)
        edit_layout.addWidget(self.type_selection, 2, 1)
        new_data_btn = QPushButton('添加数据')
        new_data_btn.setObjectName("addDataButton")
        upload_button = QPushButton('确认新增')
        review_label = QLabel("预览")
        edit_layout.addWidget(new_data_btn, 3, 0)
        edit_layout.addWidget(review_label, 4, 0)
        layout.addLayout(edit_layout)
        # self.review_table = QTableWidget()
        # layout.addWidget(self.review_table)
        self.review_chart = QChartView()
        layout.addWidget(self.review_chart)
        layout.addWidget(upload_button)
        self.setLayout(layout)
        # style
        self.setMinimumSize(800, 560)
        new_data_btn.setCursor(Qt.PointingHandCursor)
        self.review_chart.setStyleSheet("""
            background-image: url('media/chartbg-watermark.png');
        """)
        self.setStyleSheet("""
        #addDataButton{
            border:1px solid gray;
            min-height:22px;
            color: rgb(20,10,220);
            padding:0 10px;
        }
        QComboBox {
            border: 1px solid gray;
            border-radius: 2px;
            padding: 1px 2px 1px 2px;
            min-width: 9em;
            min-height:18px;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: darkgray;
            border-left-style: solid; /* just a single line */
            border-top-right-radius: 2px; /* same radius as the QComboBox */
            border-bottom-right-radius: 3px;
        }
        QComboBox::down-arrow {
            image: url(media/drop-dowm.png);
        }
        """)
        # signal
        new_data_btn.clicked.connect(self.add_chart_data)
        self.type_selection.currentIndexChanged.connect(self.chart_type_changed)
        upload_button.clicked.connect(self.create_new_chart)
        # 数据源
        self.chart_labels = list()
        self.x1_axis = list()
        self.x2_axis = list()
        self.y1_axis = list()
        self.y2_axis = list()
        self.has_data = False

    def add_chart_data(self):
        # 获取数据
        # 弹窗选择文件
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files (*.xlsx)")
        if not file_path:
            return
        # 处理Excel数据写入表格预览
        rf = xlrd.open_workbook(filename=file_path)
        sheet1 = rf.sheet_by_index(0)
        self.chart_labels = sheet1.row_values(0)
        self.x1_axis.clear()
        self.x2_axis.clear()
        self.y1_axis.clear()
        self.y2_axis.clear()
        for row in range(1, sheet1.nrows):  # skip header
            row_content = sheet1.row_values(row)
            self.x1_axis.append(row_content[0])
            self.y1_axis.append(row_content[1])
            self.x2_axis.append(row_content[2])
            self.y2_axis.append(row_content[3])
        self.has_data = True
        self.chart_type_changed()

    def chart_type_changed(self):
        if self.has_data:
            if self.type_selection.currentIndex() == 0:
                chart = QChart()
                series = QLineSeries()
                for idx, x in enumerate(self.x1_axis):
                    series.append(x, self.y1_axis[idx])
                chart.addSeries(series)
                chart.setTitle(self.name_edit.text())
                self.review_chart.setChart(chart)
                self.review_chart.setRenderHint(QPainter.Antialiasing)
                chart.createDefaultAxes()
                chart.setBackgroundVisible(False)
            elif self.type_selection.currentIndex() == 1:
                chart = QChart()
                chart.setTitle(self.name_edit.text())
                # 添加水印背景图片
                chart.setBackgroundVisible(False)
                series = QBarSeries()
                bar = QBarSet('')
                for index in range(len(self.x1_axis)):
                    bar.append(self.y1_axis[index])
                series.append(bar)
                chart.addSeries(series)
                chart.createDefaultAxes()
                self.review_chart.setChart(chart)
            else:
                pass

    def create_new_chart(self):
        # 整理数据发出信号
        data = dict()
        chart_name = self.name_edit.text().strip(' ')
        chart_name_en = self.name_en_edit.text().strip(' ')
        if not chart_name or not chart_name_en:
            QMessageBox.information(self, '错误', '请填入图表名称和英文名称.', QMessageBox.Yes)
            return
        data['chart_name'] = chart_name
        data['chart_name_en'] = chart_name_en
        data['chart_type'] = self.chart_type[self.type_selection.currentIndex()]
        data['chart_labels'] = self.chart_labels
        data['x1'] = self.x1_axis
        data['y1'] = self.y1_axis
        data['x2'] = self.x2_axis
        data['y2'] = self.y2_axis
        self.upload_new.emit(data)


# 上传某个品种的图表
class DANewVarietyChart(QDialog):
    upload_new = pyqtSignal(dict)

    def __init__(self):
        super(DANewVarietyChart, self).__init__()
        layout = QVBoxLayout()
        name = QLabel('图表名称:')
        self.name_edit = QLineEdit()
        name_en = QLabel('英文名称:')
        self.name_en_edit = QLineEdit()
        option = QLabel('图表类型:')
        self.type_selection = QComboBox()
        self.chart_type = list()
        chart_type_zh = list()
        for t in config.CHART_TYPE:
            self.chart_type.append(t[0])
            chart_type_zh.append(t[1])
        self.type_selection.addItems(chart_type_zh)
        variety_label = QLabel('所属品种:')
        self.variety_selection = QComboBox()
        edit_layout = QGridLayout()
        edit_layout.addWidget(name, 0, 0, 1, 3)
        edit_layout.addWidget(self.name_edit, 0, 1, 1, 3)
        edit_layout.addWidget(name_en, 1, 0, 1, 3)
        edit_layout.addWidget(self.name_en_edit, 1, 1, 1, 3)
        edit_layout.addWidget(option, 2, 0)
        edit_layout.addWidget(self.type_selection, 2, 1)
        edit_layout.addWidget(variety_label, 2, 2)
        edit_layout.addWidget(self.variety_selection, 2, 3)
        new_data_btn = QPushButton('添加数据')
        new_data_btn.setObjectName("addDataButton")
        upload_button = QPushButton('确认新增')
        review_label = QLabel("预览")
        edit_layout.addWidget(new_data_btn, 3, 0)
        edit_layout.addWidget(review_label, 4, 0)
        layout.addLayout(edit_layout)
        # self.review_table = QTableWidget()
        # layout.addWidget(self.review_table)
        self.review_chart = QChartView()
        layout.addWidget(self.review_chart)
        layout.addWidget(upload_button)
        self.setLayout(layout)
        # style
        name.setMaximumWidth(60)
        name_en.setMaximumWidth(60)
        variety_label.setMaximumWidth(60)
        option.setMaximumWidth(60)
        self.setMinimumSize(800, 560)
        self.review_chart.setStyleSheet("""
            background-image: url('media/chartbg-watermark.png');
        """)
        self.setStyleSheet("""
        #addDataButton{
            border:1px solid gray;
            min-height:22px;
            color: rgb(20,10,220);
            padding:0 10px;
        }
        QComboBox {
            border: 1px solid gray;
            border-radius: 2px;
            padding: 1px 2px 1px 2px;
            min-width: 9em;
            min-height:18px;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: darkgray;
            border-left-style: solid; /* just a single line */
            border-top-right-radius: 2px; /* same radius as the QComboBox */
            border-bottom-right-radius: 3px;
        }
        QComboBox::down-arrow {
            image: url(media/drop-dowm.png);
        }
        """)
        # signal
        new_data_btn.clicked.connect(self.add_chart_data)
        self.type_selection.currentIndexChanged.connect(self.chart_type_changed)
        upload_button.clicked.connect(self.create_new_chart)
        # 数据源
        self.chart_labels = list()
        self.x1_axis = list()
        self.x2_axis = list()
        self.y1_axis = list()
        self.y2_axis = list()
        self.has_data = False
        self.variety_thread = None
        self.varieties = list()
        # 获取品种数据
        self.get_variety_selection(url=config.SERVER_ADDR + 'danalysis/variety_menu/')
        
    def get_variety_selection(self, url):
        if not url:
            return
        if self.variety_thread:
            del self.variety_thread
        self.variety_thread = RequestThread(
            url=url,
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.variety_thread.response_signal.connect(self.variety_thread_back)
        self.variety_thread.finished.connect(self.variety_thread.deleteLater)
        self.variety_thread.start()

    def variety_thread_back(self, content):
        if content['error']:
            return
        for item in content['data']:
            self.varieties += item['subs']
        for variety_item in self.varieties:
            self.variety_selection.addItem(variety_item['name'])

    def add_chart_data(self):
        # 弹窗选择文件，获取数据
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files (*.xlsx)")
        if not file_path:
            return
        # 处理Excel数据写入表格预览
        rf = xlrd.open_workbook(filename=file_path)
        sheet1 = rf.sheet_by_index(0)
        self.chart_labels = sheet1.row_values(0)
        self.x1_axis.clear()
        self.x2_axis.clear()
        self.y1_axis.clear()
        self.y2_axis.clear()
        for row in range(1, sheet1.nrows):  # skip header
            row_content = sheet1.row_values(row)
            self.x1_axis.append(row_content[0])
            self.y1_axis.append(row_content[1])
            self.x2_axis.append(row_content[2])
            self.y2_axis.append(row_content[3])
        self.has_data = True
        self.chart_type_changed()

    def chart_type_changed(self):
        if self.has_data:
            if self.type_selection.currentIndex() == 0:
                chart = QChart()
                series = QLineSeries()
                for idx, x in enumerate(self.x1_axis):
                    series.append(x, self.y1_axis[idx])
                chart.addSeries(series)
                chart.setTitle(self.name_edit.text())
                self.review_chart.setChart(chart)
                self.review_chart.setRenderHint(QPainter.Antialiasing)
                chart.createDefaultAxes()
                chart.setBackgroundVisible(False)
            elif self.type_selection.currentIndex() == 1:
                chart = QChart()
                chart.setTitle(self.name_edit.text())
                # 添加水印背景图片
                chart.setBackgroundVisible(False)
                series = QBarSeries()
                bar = QBarSet('')
                for index in range(len(self.x1_axis)):
                    bar.append(self.y1_axis[index])
                series.append(bar)
                chart.addSeries(series)
                chart.createDefaultAxes()
                self.review_chart.setChart(chart)
            else:
                pass

    def create_new_chart(self):
        # 整理数据发出信号
        data = dict()
        chart_name = self.name_edit.text().strip(' ')
        chart_name_en = self.name_en_edit.text().strip(' ')
        if not chart_name or not chart_name_en:
            QMessageBox.information(self, '错误', '请填入图表名称和英文名称.', QMessageBox.Yes)
            return
        data['chart_name'] = chart_name
        data['chart_name_en'] = chart_name_en
        data['chart_type'] = self.chart_type[self.type_selection.currentIndex()]
        data['chart_labels'] = self.chart_labels
        data['variety'] = self.varieties[self.variety_selection.currentIndex()]['name_en']
        data['x1'] = self.x1_axis
        data['y1'] = self.y1_axis
        data['x2'] = self.x2_axis
        data['y2'] = self.y2_axis
        self.upload_new.emit(data)
