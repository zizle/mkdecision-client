# _*_ coding:utf-8 _*_
# __Author__： zizle
from pandas.api.types import is_datetime64_any_dtype
from PyQt5.QtChart import QChart, QLineSeries, QCategoryAxis, QValueAxis, QBarSeries, QBarSet
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QFont, QPen


# 将字符串转为浮点值
def covert_float(str_value):
    str_value = str_value.replace(",", "").replace("-", "")
    return float(str_value) if str_value else 0.0


# 画折线堆叠图
def lines_stacked(name, table_df, x_bottom_cols, y_left_cols, y_right_cols, legend_labels, tick_count):
    """
    折线堆叠图
    :param name: 图表名称
    :param table_df: 用于画图的pandas DataFrame对象
    :param x_bottom_cols:  下轴列索引列表
    :param y_left_cols: 左轴列索引列表
    :param y_right_cols: 右轴列索引列表
    :param legend_labels: 图例名称标签列表
    :param tick_count: 横轴刻度标签数
    :return: QChart实例
    """
    """ 过滤轴 """
    for y_left_col in y_left_cols:
        if is_datetime64_any_dtype(table_df[y_left_col]):  # 如果是时间轴
            y_left_cols.remove(y_left_col)
    for y_right_col in y_right_cols:
        if is_datetime64_any_dtype(table_df[y_right_col]):  # 如果是时间轴
            y_right_cols.remove(y_right_col)
    # 将x轴转为字符串
    x_bottom = x_bottom_cols[0]  # x轴列
    if is_datetime64_any_dtype(table_df[x_bottom]):  # 如果x轴是时间轴
        table_df[x_bottom] = table_df[x_bottom].apply(lambda x: x.strftime('%Y-%m-%d'))
    else:  # x轴非时间轴
        table_df[x_bottom] = table_df[x_bottom].apply(lambda x: str(x))
    font = QFont()  # 轴文字风格
    font.setPointSize(7)  # 轴标签文字大小
    chart = QChart()  # 图表实例
    chart.layout().setContentsMargins(0, 0, 0, 0)  # chart的外边距
    chart.setMargins(QMargins(15, 5, 15, 0))  # chart内边距
    chart.setTitle(name)  # chart名称
    """ x轴 """
    axis_x_bottom = QCategoryAxis(chart, labelsPosition=QCategoryAxis.AxisLabelsPositionOnValue)
    axis_x_bottom.setLabelsAngle(-90)  # 逆时针旋转90度
    axis_x_bottom.setLabelsFont(font)  # 设置字体样式
    axis_x_bottom.setGridLineVisible(False)  # 竖向连接线不可见
    chart.addAxis(axis_x_bottom, Qt.AlignBottom)  # 加入坐标x轴
    has_x_labels = False  # 收集x轴刻度的开关
    chart.x_labels = list()  # 绑定chart一个x轴的刻度列表
    """ 左Y轴 """
    axis_y_left = QValueAxis()
    axis_y_left.setLabelsFont(font)
    axis_y_left.setLabelFormat('%i')
    chart.addAxis(axis_y_left, Qt.AlignLeft)  # 图表加入左轴
    """ 右Y轴 """
    axis_y_right = QValueAxis()
    axis_y_right.setLabelsFont(font)
    axis_y_right.setLabelFormat('%.2f')
    chart.addAxis(axis_y_right, Qt.AlignRight)
    # 记录各轴的最值
    x_bottom_min, x_bottom_max = 0, table_df.shape[0]
    y_left_min, y_left_max = 0, 0
    y_right_min, y_right_max = 0, 0
    """ 根据左轴画折线 """
    for y_left_col in y_left_cols:  # 根据左轴画折线
        # 计算做轴的最值用于设置范围
        table_df[y_left_col] = table_df[y_left_col].apply(covert_float)  # y轴列转为浮点数值
        # 获取最值
        y_min, y_max = table_df[y_left_col].min(), table_df[y_left_col].max()
        if y_min < y_left_min:
            y_left_min = y_min
        if y_max > y_left_max:
            y_left_max = y_max
        # 取得图线的源数据作折线图
        left_line_data = table_df.iloc[:, [x_bottom, y_left_col]]
        series = QLineSeries()
        series.setName(legend_labels[y_left_col])
        for position_index, point_item in enumerate(left_line_data.values.tolist()):
            series.append(position_index, point_item[1])  # 取出源数据后一条线就2列数据
            # 收集坐标标签
            if not has_x_labels:
                chart.x_labels.append(point_item[0])
        chart.addSeries(series)  # 折线入图
        series.attachAxis(axis_x_bottom)
        series.attachAxis(axis_y_left)
    # 左轴范围
    axis_y_left.setRange(y_left_min, y_left_max)
    """ 根据右轴画折线 """
    for y_right_col in y_right_cols:  # 根据右轴画折线
        # 计算做轴的最值用于设置范围
        table_df[y_right_col] = table_df[y_right_col].apply(covert_float)  # y轴列转为浮点数值
        # 获取最值
        y_min, y_max = table_df[y_right_col].min(), table_df[y_right_col].max()
        if y_min < y_right_min:
            y_right_min = y_min
        if y_max > y_right_max:
            y_right_max = y_max
        # 取得图线的源数据作折线图
        left_line_data = table_df.iloc[:, [x_bottom, y_right_col]]
        series = QLineSeries()
        series.setName(legend_labels[y_right_col])
        for position_index, point_item in enumerate(left_line_data.values.tolist()):
            series.append(position_index, point_item[1])  # 取出源数据后一条线就2列数据
        chart.addSeries(series)
        series.attachAxis(axis_x_bottom)
        series.attachAxis(axis_y_right)
    # 右轴范围
    axis_y_right.setRange(y_right_min, y_right_max)
    # 设置下轴刻度标签
    # print('x轴最大值', x_bottom_max)
    x_bottom_interval = int(x_bottom_max / (tick_count - 1))
    if x_bottom_interval == 0:
        for i in range(0, x_bottom_max):
            axis_x_bottom.append(chart.x_labels[i], i)
    else:
        for i in range(0, x_bottom_max, x_bottom_interval):
            axis_x_bottom.append(chart.x_labels[i], i)
    chart.legend().setAlignment(Qt.AlignBottom)
    return chart


# 画柱形堆叠图
def bars_stacked(name, table_df, x_bottom_cols, y_left_cols, y_right_cols, legend_labels, tick_count):
    """
    柱形堆叠图
    :param name: 图表名称
    :param table_df: 用于画图的pandas DataFrame对象
    :param x_bottom_cols:  下轴列索引列表
    :param y_left_cols: 左轴列索引列表
    :param y_right_cols: 右轴列索引列表
    :param legend_labels: 图例名称标签列表
    :param tick_count: 横轴刻度标签数
    :return: QChart实例
    """
    """ 过滤轴 """
    for y_left_col in y_left_cols:
        if is_datetime64_any_dtype(table_df[y_left_col]):  # 如果是时间轴
            y_left_cols.remove(y_left_col)
    for y_right_col in y_right_cols:
        if is_datetime64_any_dtype(table_df[y_right_col]):  # 如果是时间轴
            y_right_cols.remove(y_right_col)
    # 将x轴转为字符串
    x_bottom = x_bottom_cols[0]  # x轴列
    if is_datetime64_any_dtype(table_df[x_bottom]):  # 如果x轴是时间轴
        table_df[x_bottom] = table_df[x_bottom].apply(lambda x: x.strftime('%Y-%m-%d'))
    else:  # x轴非时间轴
        table_df[x_bottom] = table_df[x_bottom].apply(lambda x: str(x))
    font = QFont()  # 轴文字风格
    font.setPointSize(7)  # 轴标签文字大小
    chart = QChart()  # 图表实例
    chart.layout().setContentsMargins(0, 0, 0, 0)  # chart的外边距
    chart.setMargins(QMargins(15, 5, 15, 0))  # chart内边距
    chart.setTitle(name)  # chart名称
    """ x轴 """
    axis_x_bottom = QCategoryAxis(chart, labelsPosition=QCategoryAxis.AxisLabelsPositionOnValue)
    axis_x_bottom.setLabelsAngle(-90)  # 逆时针旋转90度
    axis_x_bottom.setLabelsFont(font)  # 设置字体样式
    axis_x_bottom.setGridLineVisible(False)  # 竖向连接线不可见
    # chart.addAxis(axis_x_bottom, Qt.AlignBottom)  # 加入坐标x轴
    has_x_labels = False  # 收集x轴刻度的开关
    chart.x_labels = list()  # 绑定chart一个x轴的刻度列表
    """ 左Y轴 """
    axis_y_left = QValueAxis()
    axis_y_left.setLabelsFont(font)
    axis_y_left.setLabelFormat('%i')
    chart.addAxis(axis_y_left, Qt.AlignLeft)  # 图表加入左轴
    """ 右Y轴 """
    axis_y_right = QValueAxis()
    axis_y_right.setLabelsFont(font)
    axis_y_right.setLabelFormat('%.2f')
    chart.addAxis(axis_y_right, Qt.AlignRight)
    # 记录各轴的最值
    x_bottom_min, x_bottom_max = 0, table_df.shape[0]
    y_left_min, y_left_max = 0, 0
    y_right_min, y_right_max = 0, 0
    # 柱形图
    left_bars = QBarSeries()
    """ 根据左轴画柱形 """
    for y_left_col in y_left_cols:  # 根据左轴画折线
        # 计算做轴的最值用于设置范围
        table_df[y_left_col] = table_df[y_left_col].apply(covert_float)  # y轴列转为浮点数值
        # 获取最值
        y_min, y_max = table_df[y_left_col].min(), table_df[y_left_col].max()
        if y_min < y_left_min:
            y_left_min = y_min
        if y_max > y_left_max:
            y_left_max = y_max
        # 取得图表的源数据作柱形
        left_bar_data = table_df.iloc[:, [x_bottom, y_left_col]]
        bar = QBarSet(legend_labels[y_left_col])
        bar.setPen(QPen(Qt.transparent))  # 设置画笔轮廓线透明(数据量大会出现空白遮住柱形)
        for index, point_item in enumerate(left_bar_data.values.tolist()):
            bar.append(point_item[1])
            if not has_x_labels:
                chart.x_labels.append(point_item[0])
        has_x_labels = True  # 关闭添加轴标签
        left_bars.append(bar)  # 柱形加入系列
    left_bars.attachAxis(axis_y_left)
    # 左轴的范围
    axis_y_left.setRange(y_left_min, y_left_max)
    """ 根据右轴画柱形 """
    right_bars = QBarSeries()
    for y_right_col in y_right_cols:  # 根据右轴画柱形
        # 计算做轴的最值用于设置范围
        table_df[y_right_col] = table_df[y_right_col].apply(covert_float)  # y轴列转为浮点数值
        # 获取最值
        y_min, y_max = table_df[y_right_col].min(), table_df[y_right_col].max()
        if y_min < y_right_min:
            y_right_min = y_min
        if y_max > y_right_max:
            y_right_max = y_max
        # 取得图线的源数据作折线图
        right_bar_data = table_df.iloc[:, [x_bottom, y_right_col]]
        bar = QBarSet(legend_labels[y_right_col])
        bar.setPen(QPen(Qt.transparent))
        for position_index, point_item in enumerate(right_bar_data.values.tolist()):
            bar.append(point_item[1])  # 取出源数据后一条线就2列数据
        right_bars.append(bar)
        right_bars.attachAxis(axis_x_bottom)
        right_bars.attachAxis(axis_y_right)
    # 右轴范围
    axis_y_right.setRange(y_right_min, y_right_max)
    chart.addSeries(left_bars)  # 左轴的柱形图加入图表
    # print(right_bars.count())
    if right_bars.count() != 0:  # 为空时加入会导致空位
        chart.addSeries(right_bars)
    chart.setAxisX(axis_x_bottom, left_bars)  # 关联设置x轴
    # 横轴标签设置
    x_bottom_interval = int(x_bottom_max / (tick_count - 1))
    if x_bottom_interval == 0:
        for i in range(0, x_bottom_max):
            axis_x_bottom.append(chart.x_labels[i], i)
    else:
        for i in range(0, x_bottom_max, x_bottom_interval):
            axis_x_bottom.append(chart.x_labels[i], i)
    chart.legend().setAlignment(Qt.AlignBottom)
    return chart
