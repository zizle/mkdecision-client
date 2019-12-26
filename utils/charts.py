# _*_ coding:utf-8 _*_
# __Author__： zizle
from PyQt5.QtChart import QChart, QLineSeries, QDateTimeAxis, QValueAxis
from PyQt5.QtCore import Qt, QDateTime, QMargins
from PyQt5.QtGui import QFont


# 根据第一列时间轴画图
def draw_line_series(name, table_df, x_bottom, y_left, legends, tick_count):
    """
    QChart根据第一列时间轴画直接堆叠
    :param name: 图表名称
    :param table_df: 画图的源数据 pandas DataFrame类型
    :param x_bottom: x轴列（时间列,默认0）
    :param y_left: 左轴列
    :param legends: 图例(根据左轴的索引)名称
    :param tick_count: 轴点的个数
    :return: QChart object
    """
    chart = QChart()
    chart.layout().setContentsMargins(0, 0, 0, 0)  # chart的外边距
    chart.setMargins(QMargins(15,5,15,0))
    chart.setTitle(name)
    # 计算x轴的最值
    x_bottom = 0
    x_axis_data = table_df.iloc[:, [x_bottom]]  # 取得第一列数据
    min_x, max_x = x_axis_data.min(0).tolist()[0], x_axis_data.max(0).tolist()[0]  # 第一列时间数据(x轴)的最大值和最小值
    for line in y_left:
        line_data = table_df.iloc[:, [x_bottom, line]]  # 取得图线的源数据
        series = QLineSeries()
        series.setName(legends[line])
        for point_item in line_data.values.tolist():
            series.append(QDateTime(point_item[0]).toMSecsSinceEpoch(), float(point_item[1].replace(',', '')))
        chart.addSeries(series)
        # 设置X轴
        axis_X = QDateTimeAxis()
        axis_X.setRange(min_x, max_x)
        axis_X.setFormat('yyyy-MM-dd')
        axis_X.setLabelsAngle(-90)
        axis_X.setTickCount(tick_count)
        font = QFont()
        font.setPointSize(7)
        axis_X.setLabelsFont(font)
        # 设置Y轴
        axix_Y = QValueAxis()
        axix_Y.setLabelsFont(font)
        series = chart.series()[0]
        chart.createDefaultAxes()
        chart.setAxisX(axis_X, series)
        min_y, max_y = int(chart.axisY().min()), int(chart.axisY().max())
        # 根据位数取整数
        axix_Y.setRange(min_y, max_y)
        axix_Y.setLabelFormat('%i')
        chart.setAxisY(axix_Y, series)
        chart.legend().setAlignment(Qt.AlignBottom)
    return chart
