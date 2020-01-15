# _*_ coding:utf-8 _*_
# __Author__： zizle
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype
from PyQt5.QtChart import QChart, QLineSeries, QDateTimeAxis, QCategoryAxis, QValueAxis, QBarSeries, QBarSet
from PyQt5.QtCore import Qt, QDateTime, QMargins
from PyQt5.QtGui import QFont


# 将字符串转为浮点值
def covert_float(str_value):
    str_value = str_value.replace(",", "").replace("-", "")
    return float(str_value) if str_value else 0.0


# 画堆叠折线图
def draw_lines_stacked(name, table_df, x_bottom, y_left, legends, tick_count):
    """
    QChart画折接堆叠图
    :param name: 图表名称
    :param table_df: 画图的源数据 pandas DataFrame类型
    :param x_bottom: x轴列
    :param y_left: 左轴列
    :param legends: 图例(根据左轴的索引)名称
    :param tick_count: 轴点的个数
    :return: QChart object
    """
    chart = QChart()
    chart.layout().setContentsMargins(0, 0, 0, 0)  # chart的外边距
    chart.setMargins(QMargins(15, 5, 15, 0))
    chart.setTitle(name)
    x_bottom = x_bottom[0]
    if is_datetime64_any_dtype(table_df[x_bottom]):  # 如果x轴是时间轴
        # 计算处理x轴数据
        x_axis_data = table_df.iloc[:, [x_bottom]]  # 取得第一列数据
        min_x, max_x = x_axis_data.min(0).tolist()[0], x_axis_data.max(0).tolist()[0]  # 第一列时间数据(x轴)的最大值和最小值
        # 取数据画图
        for y_col in y_left:
            if is_datetime64_any_dtype(table_df[y_col]):  # 如果y轴数据是时间类型
                # print('y轴数据有时间类型， 未实现-跳过')
                continue
            table_df[y_col] = table_df[y_col].apply(covert_float)  # y轴列转为浮点数值
            line_data = table_df.iloc[:, [x_bottom, y_col]]  # 取得图线的源数据
            series = QLineSeries()
            series.setName(legends[y_col])
            for point_item in line_data.values.tolist():
                series.append(QDateTime(point_item[0]).toMSecsSinceEpoch(), point_item[1])  # 取出源数据后一条线就2列数据
            chart.addSeries(series)
        chart.createDefaultAxes()
        # 设置X轴文字格式
        axis_X = QDateTimeAxis()
        axis_X.setRange(min_x, max_x)
        axis_X.setFormat('yyyy-MM-dd')
        axis_X.setLabelsAngle(-90)
        axis_X.setTickCount(tick_count)
        font = QFont()
        font.setPointSize(7)
        axis_X.setLabelsFont(font)
        axis_X.setGridLineVisible(False)
        # 设置Y轴
        axix_Y = QValueAxis()
        axix_Y.setLabelsFont(font)
        series = chart.series()[0]
        chart.setAxisX(axis_X, series)
        min_y, max_y = int(chart.axisY().min()), int(chart.axisY().max())
        # 根据位数取整数
        axix_Y.setRange(min_y, max_y)
        axix_Y.setLabelFormat('%i')
        chart.setAxisY(axix_Y, series)
        chart.date_xaxis_category = True
    else:  # 非时间轴数据作图
        # 转化x轴数据转为字符串
        table_df[x_bottom] = table_df[x_bottom].apply(lambda x: str(x))
        # 取数据画图
        has_x_labels = False  # 收集x轴刻度的开关
        chart.x_labels = list()  # 绑定chart一个x轴的刻度列表
        for y_col in y_left:
            if is_datetime64_any_dtype(table_df[y_col]):  # 如果y轴数据是时间类型
                continue
            table_df[y_col] = table_df[y_col].apply(covert_float)  # y轴列转为浮点数值
            line_data = table_df.iloc[:, [x_bottom, y_col]]  # 取得图线的源数据
            series = QLineSeries()
            series.setName(legends[y_col])
            for index, point_item in enumerate(line_data.values.tolist()):
                series.append(index, point_item[1])  # 取出源数据后一条线就2列数据
                if not has_x_labels:
                    chart.x_labels.append(point_item[0])
            has_x_labels = True
            chart.addSeries(series)
        chart.createDefaultAxes()
        # 设置x轴刻度显示
        series = chart.series()[0]
        axis_X = QCategoryAxis(chart, labelsPosition=QCategoryAxis.AxisLabelsPositionOnValue)
        x_min, x_max = int(chart.axisX().min()), int(chart.axisX().max())
        step_x = int((x_max - x_min) / (tick_count - 1))  # 根据步长设置x轴
        if step_x != 0:
            for i in range(x_min, x_max, step_x):
                axis_X.append(chart.x_labels[i], i + 1)
        else:
            for i in range(x_min, x_max):
                axis_X.append(chart.x_labels[i], i + 1)
        font = QFont()
        font.setPointSize(7)
        axis_X.setLabelsFont(font)
        axis_X.setLabelsAngle(-90)
        chart.setAxisX(axis_X, series)
        # 设置Y轴
        axix_Y = QValueAxis()
        axix_Y.setLabelsFont(font)
        min_y, max_y = int(chart.axisY().min()), int(chart.axisY().max())
        # 根据位数取整数
        axix_Y.setRange(min_y, max_y)
        axix_Y.setLabelFormat('%i')
        chart.setAxisY(axix_Y, series)
        chart.date_xaxis_category = False
    chart.legend().setAlignment(Qt.AlignBottom)
    return chart

# 画堆叠柱状图
def draw_bars_stacked(name, table_df, x_bottom, y_left, legends, tick_count):
    """
    绘制柱形图
    :param name: 图表名称
    :param table_df: 画图的源数据Data Frame，已根据时间列排序过
    :param x_bottom: x轴的列
    :param y_left: 左轴数据(每组柱形图个数)
    :param legends: 图例
    :param tick_count: 轴点个数
    :return: QChart object
    """
    chart = QChart()
    chart.layout().setContentsMargins(0, 0, 0, 0)  # chart的外边距
    chart.setMargins(QMargins(15, 5, 15, 0))
    chart.setTitle(name)
    chart.x_labels = list()  # 绑定chart一个x轴的刻度列表
    # 根据x轴的列，进行大小排序
    x_bottom = x_bottom[0]
    # if is_datetime64_any_dtype(table_df[x_bottom]):  # 如果x轴是时间轴
    chart.date_xaxis_category = False
    # 进行数据画图
    table_df[0] = table_df[0].apply(lambda x: x.strftime('%Y-%m-%d'))  # 将0列转为时间字符串
    series = QBarSeries()
    has_x_labels = False  # 收集x轴刻度的开关
    for y_col in y_left:
        if is_datetime64_any_dtype(table_df[y_col]):  # 如果y轴数据是时间类型
            print('y轴数据有时间类型， 未实现-跳过')
            continue
        bar = QBarSet(legends[y_col])
        table_df[y_col] = table_df[y_col].apply(covert_float)
        bar_data = table_df.iloc[:, [x_bottom, y_col]]  # 取得柱形图的源数据
        for point_item in bar_data.values.tolist():
            bar.append(point_item[1])
            if not has_x_labels:
                chart.x_labels.append(point_item[0])
        has_x_labels = True
        series.append(bar)
    chart.addSeries(series)
    chart.createDefaultAxes()
    # 自定义x轴
    series = chart.series()[0]
    axis_X = QCategoryAxis(chart, labelsPosition=QCategoryAxis.AxisLabelsPositionOnValue)
    x_min, x_max = int(chart.axisX().min()), int(chart.axisX().max())
    step_x = int((x_max - x_min) / (tick_count - 1))  # 根据步长设置x轴
    if step_x != 0:
        for i in range(x_min, x_max, step_x):
            axis_X.append(chart.x_labels[i], i + 1)
    else:
        for i in range(x_min, x_max):
            axis_X.append(chart.x_labels[i], i + 1)
    font = QFont()
    font.setPointSize(7)
    axis_X.setLabelsFont(font)
    axis_X.setLabelsAngle(-90)
    chart.setAxisX(axis_X, series)
    # 设置Y轴
    axix_Y = QValueAxis()
    axix_Y.setLabelsFont(font)
    min_y, max_y = int(chart.axisY().min()), int(chart.axisY().max())
    axix_Y.setRange(min_y, max_y)
    axix_Y.setLabelFormat('%i')  # 根据位数取整数
    chart.setAxisY(axix_Y, series)
    chart.legend().setAlignment(Qt.AlignBottom)
    return chart




