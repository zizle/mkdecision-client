# _*_ coding:utf-8 _*_
# __Author__： zizle
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget
# from PyQt5.QtChart import QChartView
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPainter

import config


class ChartView(QWidget):
    clicked = pyqtSignal(dict)

    def __init__(self, row, column, zoom_in=False):
        super(ChartView, self).__init__()
        # 管理端有去除水印按钮
        if config.IDENTIFY:
            self.watermark_wiped = QPushButton('去除水印', self)
            self.watermark_wiped.setStyleSheet(
                'color:rgb(120,120,120);border:none;font-size:10px;max-width:40px;max-height:20px}')
            self.watermark_wiped.clicked.connect(self.wipe_watermark)
        self.has_watermark = True
        self.row = row
        self.column = column
        self.zoom_in_out = QPushButton()
        self.zoom_in_out.zoom_in = zoom_in
        # style
        if not zoom_in:
            btn_pixmap = 'media/zoomin.png'
        else:
            btn_pixmap = 'media/zoomout.png'
        self.zoom_in_out.setIcon(QIcon(btn_pixmap))
        self.zoom_in_out.setCursor(Qt.PointingHandCursor)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("background-image: url('media/chartbg-watermark.png');")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.zoom_in_out.setStyleSheet('border:none')
        layout.addWidget(self.zoom_in_out, alignment=Qt.AlignTop | Qt.AlignRight)
        self.zoom_in_out.clicked.connect(self.click_chart_view)

    def click_chart_view(self):
        if self.zoom_in_out.zoom_in:
            self.zoom_in_out.zoom_in = False
        else:
            self.zoom_in_out.zoom_in = True
        # 传递数据出去，重新绘制图表展示
        series_set = self.chart().series()
        # {'title': xxx, 'series': [{'x_values': [1,2,3,], 'y_values': [1,2,3]}]}
        value_data = dict()
        value_data['title'] = self.chart().title()
        value_data['series'] = list()
        for series in series_set:
            xy_dict = dict()
            xy_dict['x_values'] = list()
            xy_dict['y_values'] = list()
            for i in range(series.count()):
                xy_dict['x_values'].append(series.at(i).x())
                xy_dict['y_values'].append(series.at(i).y())
            value_data['series'].append(xy_dict)
        self.clicked.emit(value_data)

    def wipe_watermark(self):
        if self.has_watermark:
            self.setStyleSheet("background-image: url('media/chartbg.png');")
            self.has_watermark = False
            self.watermark_wiped.setText('附加水印')
        else:
            self.setStyleSheet("background-image: url('media/chartbg-watermark.png');")
            self.has_watermark = True
            self.watermark_wiped.setText('清除水印')

    def setWatermarkButtonVisible(self, b=True):
        if not b:
            self.zoom_in_out.hide()

