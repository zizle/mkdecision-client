# _*_ coding:utf-8 _*_
# __Author__： zizle
from PyQt5.QtWidgets import QPushButton, QVBoxLayout
from PyQt5.QtChart import QChartView
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPainter


class ChartView(QChartView):
    clicked = pyqtSignal(dict)

    def __init__(self, row, column, zoom_in=False):
        super(ChartView, self).__init__()
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
        self.zoom_in_out.setStyleSheet("QPushButton{border:none};")
        self.zoom_in_out.setCursor(Qt.PointingHandCursor)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("background-image: url('media/shuiyin.png');")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
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
