# _*_ coding:utf-8 _*_
# __Author__： zizle
from PyQt5.QtWidgets import QWidget, QGraphicsLineItem, QGraphicsProxyWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtChart import QChartView
from PyQt5.QtCore import Qt, pyqtSignal, QPointF, QPoint, QRectF, QDateTime
from PyQt5.QtGui import QPainter


# 自定义图表容器
class ChartView(QChartView):
    clicked = pyqtSignal(dict)

    def __init__(self, chart_data, *args, **kwargs):
        super(ChartView, self).__init__(*args, **kwargs)
        self.chart_data = chart_data
        self.setRenderHint(QPainter.Antialiasing)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.clicked.emit(self.chart_data)


class ToolTipItem(QWidget):
    def __init__(self, color, text, parent=None):
        super(ToolTipItem, self).__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(self)
        label.setMinimumSize(12, 12)
        label.setMaximumSize(12, 12)
        label.setStyleSheet("border-radius:6px;background: rgba(%s,%s,%s,%s);" % (
            color.red(), color.green(), color.blue(), color.alpha()))
        layout.addWidget(label)
        self.textLabel = QLabel(text, self, styleSheet="color:white;")
        layout.addWidget(self.textLabel)

    def setText(self, text):
        self.textLabel.setText(text)
        print('改变显示', text)


class ToolTipWidget(QWidget):
    Cache = {}

    def __init__(self, *args, **kwargs):
        super(ToolTipWidget, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "ToolTipWidget{background: rgba(50, 50, 50, 100);}")
        layout = QVBoxLayout(self)
        self.titleLabel = QLabel(self, styleSheet="color:white;")
        layout.addWidget(self.titleLabel)

    def updateUi(self, title, points):
        self.titleLabel.setText(title)
        for serie, point in points:
            if serie not in self.Cache:
                print('不在')
                item = ToolTipItem(
                    serie.color(),
                    (serie.name() or "-") + ":" + str(point.y()), self)
                self.layout().addWidget(item)
                self.Cache[serie] = item
            else:
                self.Cache[serie].setText(
                    (serie.name() or "-") + ":" + str(point.y()))
            self.Cache[serie].setVisible(serie.isVisible())  # 隐藏那些不可用的项
        self.adjustSize()  # 调整大小


class GraphicsProxyWidget(QGraphicsProxyWidget):
    def __init__(self, *args, **kwargs):
        super(GraphicsProxyWidget, self).__init__(*args, **kwargs)
        self.setZValue(999)
        self.tipWidget = ToolTipWidget()
        self.setWidget(self.tipWidget)
        self.hide()

    def width(self):
        return self.size().width()

    def height(self):
        return self.size().height()

    def show(self, title, points, pos):
        self.setGeometry(QRectF(pos, self.size()))
        self.tipWidget.updateUi(title, points)
        super(GraphicsProxyWidget, self).show()


# 详情图表容器
class DetailChartView(QChartView):
    def __init__(self, *args, **kwargs):
        super(DetailChartView, self).__init__(*args, **kwargs)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMaximumHeight(320)
        self.c_chart = None  # customer chart

    def installMouseHoverEvent(self):
        for series in self.chart().series():
            series.hovered.connect(self.series_hovered)  # 鼠标悬停信号连接
        # 线条对象
        self.line_item = QGraphicsLineItem(self.c_chart)
        # # 提示块
        self.tips_tool = GraphicsProxyWidget(self.c_chart)

        axis_X = self.c_chart.axisX()
        axis_Y = self.c_chart.axisY()
        self.min_x, self.max_x = axis_X.min().toMSecsSinceEpoch(), axis_X.max().toMSecsSinceEpoch()
        self.min_y, self.max_y = axis_Y.min(), axis_Y.max()

    def series_hovered(self, point, state):
        # 鼠标悬停信号槽函数：state表示鼠标是否在线上(布尔值)
        series = self.sender()  # 获取获得鼠标信号的那条线
        pen = series.pen()
        if not pen:
            return
        pen.setWidth(pen.width() + (1 if state else -1))
        series.setPen(pen)

    def setChart(self, chart):
        super(DetailChartView, self).setChart(chart)
        self.c_chart = chart

    def mouseMoveEvent(self, event):
        super(DetailChartView, self).mouseMoveEvent(event)  # 原先的hover事件
        pos = event.pos()
        # 鼠标位置转为坐标点
        x = self.c_chart.mapToValue(pos).x()
        y = self.c_chart.mapToValue(pos).y()
        # start_time = QDateTime.fromMSecsSinceEpoch(self.min_x).toTime_t()
        # current_time = QDateTime.fromMSecsSinceEpoch(x).toTime_t()
        # days = (current_time - start_time) / (86400) + ((current_time - start_time) % (86400) + (86400 - 1)) / (86400) - 1
        # index = round(days / self.step_x)
        # print(days, index)
        points = list()
        for series in self.c_chart.series():
            series_points = list()
            if self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y:
                for i in range(series.count()):
                    series_points.append((series, series.at(i)))
            points += series_points
        # points = [(series, series.at(i)) for i in range(series.count()) for series in self.c_chart.series()
        #           if self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y
        #           ]
        # points  是当前鼠标位置所有可用的点

        if points:
            pos_x = self.c_chart.mapToPosition(QPointF(x, self.min_y))  # 算出当前鼠标所在的x位置
            # 自定义指示线
            self.line_item.setLine(pos_x.x(), self.point_top.y(),
                                   pos_x.x(), self.point_bottom.y())
            self.line_item.show()
            try:
                title = QDateTime.fromMSecsSinceEpoch(x).toString("yyyy-MM-dd")
            except Exception:
                title = ''
            tips_width = self.tips_tool.width()
            tips_height = self.tips_tool.height()
            # 如果鼠标位置离右侧的距离小于tip宽度
            x = pos.x() - tips_width if self.width() - \
                                        pos.x() - 20 < tips_width else pos.x()
            # 如果鼠标位置离底部的高度小于tip高度
            y = pos.y() - tips_height if self.height() - \
                                         pos.y() - 20 < tips_height else pos.y()
            print(title, points, QPoint(x, y))
            self.tips_tool.show(
                title, points, QPoint(x, y))

        else:
            self.tips_tool.hide()
            self.line_item.hide()
        return
        # print(self.chart.axisX().tickCount(), self.min_x, self.max_x)
        # step_x = (self.max_x - self.min_x) / (self.chart.axisX().tickCount() - 1)
        index = round((x - self.min_x) / self.step_x)
        # 坐标系中的所有正常显示的series的类型和点
        points = [(serie, serie.at(index))
                  for serie in self.c_chart.series()
                  if self.min_x <= x <= self.max_x and
                  self.min_y <= y <= self.max_y]
        # point_top = self.chart.mapToPosition(QPointF(self.min_x, self.max_y))  # y轴最高点
        # point_bottom = self.chart.mapToPosition(QPointF(self.min_x, self.min_y))
        if points:
            pos_x = self.c_chart.mapToPosition(QPointF(index * self.step_x + self.min_x, self.min_y))  # 算出当前鼠标所在的x位置
            # 自定义指示线
            self.line_item.setLine(pos_x.x(), self.point_top.y(),
                                   pos_x.x(), self.point_bottom.y())
            self.line_item.show()
            try:
                title = self.x_category[index]
            except Exception:
                title = ''
            tips_width = self.tips_tool.width()
            tips_height = self.tips_tool.height()
            # 如果鼠标位置离右侧的距离小于tip宽度
            x = pos.x() - tips_width if self.width() - \
                                        pos.x() - 20 < tips_width else pos.x()
            # 如果鼠标位置离底部的高度小于tip高度
            y = pos.y() - tips_height if self.height() - \
                                         pos.y() - 20 < tips_height else pos.y()
            # print(title, points, QPoint(x, y))
            self.tips_tool.show(
                title, points, QPoint(x, y))

        else:
            self.tips_tool.hide()
            self.line_item.hide()

    def resizeEvent(self, event):
        super(DetailChartView, self).resizeEvent(event)
        # 当窗口大小改变时需要重新计算
        # 坐标系中左上角顶点
        self.point_top = self.c_chart.mapToPosition(
            QPointF(self.min_x, self.max_y))
        # 坐标原点坐标
        self.point_bottom = self.c_chart.mapToPosition(
            QPointF(self.min_x, self.min_y))
        start_time = QDateTime.fromMSecsSinceEpoch(self.min_x).toTime_t()
        end_time = QDateTime.fromMSecsSinceEpoch(self.max_x).toTime_t()
        days = (end_time - start_time) / (86400) + ((end_time - start_time) % (86400) + (86400 - 1)) / (86400) - 1
        print(days)
        self.step_x = days / 1




