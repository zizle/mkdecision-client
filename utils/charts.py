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
        # 设置X轴
        axis_X = QDateTimeAxis()
        axis_X.setRange(min_x, max_x)
        axis_X.setFormat('yyyy-MM-dd')
        axis_X.setLabelsAngle(-90)
        axis_X.setTickCount(tick_count)
        font = QFont()
        font.setPointSize(7)
        axis_X.setLabelsFont(font)
        # 取数据画图
        for y_col in y_left:
            if is_datetime64_any_dtype(table_df[y_col]):  # 如果y轴数据是时间类型
                print('y轴数据有时间类型， 未实现-跳过')
                continue
            table_df[y_col] = table_df[y_col].apply(covert_float)  # y轴列转为浮点数值
            line_data = table_df.iloc[:, [x_bottom, y_col]]  # 取得图线的源数据
            series = QLineSeries()
            series.setName(legends[y_col])
            for point_item in line_data.values.tolist():
                series.append(QDateTime(point_item[0]).toMSecsSinceEpoch(), point_item[1])  # 取出源数据后一条线就2列数据
            chart.addSeries(series)
        if chart.series():  # 有图线才设置轴
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
    else:  # 非时间轴数据作图
        print('非时间轴作折线图，正在实现')
        # 转化x轴数据为浮点值
        table_df[x_bottom] = table_df[x_bottom].apply(covert_float)  # 转为浮点数值
        # 按大小排序
        table_df.sort_values(by=x_bottom, inplace=True)
        x_axis_data = table_df.iloc[:, [x_bottom]]  # 取得x轴数据
        # 取数据画图
        for y_col in y_left:
            if is_datetime64_any_dtype(table_df[y_col]):  # 如果y轴数据是时间类型
                print('y轴数据有时间类型， 未实现-跳过')
                continue
            table_df[y_col] = table_df[y_col].apply(covert_float)  # y轴列转为浮点数值
            line_data = table_df.iloc[:, [x_bottom, y_col]]  # 取得图线的源数据
            series = QLineSeries()
            series.setName(legends[y_col])
            for index, point_item in enumerate(line_data.values.tolist()):
                series.append(index, point_item[1])  # 取出源数据后一条线就2列数据
            chart.addSeries(series)
        if chart.series():  # 有图线才设置轴
            chart.createDefaultAxes()
            series = chart.series()[0]
            # 设置X轴
            axis_X = QCategoryAxis(chart, labelsPosition=QCategoryAxis.AxisLabelsPositionOnValue)
            min_x = chart.axisX().min()
            max_x = chart.axisX().max()
            x_axis_data = x_axis_data.values.tolist()  # 转为列表
            chart.axisX().setTickCount(tick_count)
            step_x = (max_x - min_x) / (tick_count - 1)
            x_axis_data = x_axis_data[::int(step_x)]  # 按步长取得x轴标记
            for i in range(tick_count):
                axis_X.append("%s" % int(x_axis_data[i][0]), min_x + i * step_x)
            axis_X.setLabelsAngle(-90)
            font = QFont()
            font.setPointSize(7)
            axis_X.setLabelsFont(font)
            chart.setAxisX(axis_X, series)
            # 设置Y轴
            axix_Y = QValueAxis()
            axix_Y.setLabelsFont(font)
            min_y, max_y = int(chart.axisY().min()), int(chart.axisY().max())
            # 根据位数取整数
            axix_Y.setRange(min_y, max_y)
            axix_Y.setLabelFormat('%i')
            chart.setAxisY(axix_Y, series)
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
    # 根据x轴的列，进行大小排序
    x_bottom = x_bottom[0]
    # 计算步长取数据
    if table_df.shape[0] > 100:
        step_x = table_df.shape[0] / 99
        rows = [int(i*step_x) - 1 if (int(i*step_x) - 1) > 0 else 0 for i in range(100)]  # 计算行
        table_df = table_df.iloc[rows, :].copy()  # copy一下防止之后赋值的警告
    if is_datetime64_any_dtype(table_df[x_bottom]):  # 如果x轴是时间轴
        # 进行数据画图
        series = QBarSeries()
        for y_col in y_left:
            if is_datetime64_any_dtype(table_df[y_col]):  # 如果y轴数据是时间类型
                print('y轴数据有时间类型， 未实现-跳过')
                continue
            bar = QBarSet(legends[y_col])
            table_df[y_col] = table_df[y_col].apply(covert_float)
            bar_data = table_df.iloc[:, [x_bottom, y_col]]  # 取得柱形图的源数据
            for point_item in bar_data.values.tolist():
                bar.append(point_item[1])
            series.append(bar)
        chart.addSeries(series)
        chart.createDefaultAxes()
        series = chart.series()[0]
        # x轴数据
        x_axis_labels = table_df[x_bottom].apply(lambda x: x.strftime('%Y-%m-%d'))  # 转为字符串
        x_axis_labels = x_axis_labels.values.tolist()
        axis_X = QCategoryAxis(chart, labelsPosition=QCategoryAxis.AxisLabelsPositionOnValue)
        # 根据tick_count设置x轴
        min_x = chart.axisX().min()
        max_x = chart.axisX().max()
        # chart.axisX().setTickCount(tick_count)
        step_x = (max_x - min_x) / (tick_count - 1)
        x_axis_labels = x_axis_labels[::int(step_x)]  # 按步长取得x轴标记
        for i in range(tick_count):
            axis_X.append("%s" % x_axis_labels[i], min_x + i * step_x)
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
        chart.legend().setAlignment(Qt.AlignBottom)
    else:
        print('非时间轴画柱形图')
    return chart




