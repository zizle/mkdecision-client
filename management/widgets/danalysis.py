# _*_ coding:utf-8 _*_
# __Author__： zizle


from PyQt5.QtChart import QChartView
from PyQt5.QtCore import pyqtSignal


class ChartView(QChartView):
    clicked = pyqtSignal(QChartView)

    def __init__(self):
        super(ChartView, self).__init__()
        
    def mousePressEvent(self, event):
        super(ChartView, self).mousePressEvent(event)
        self.clicked.emit(self)