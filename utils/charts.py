# _*_ coding:utf-8 _*_
# __Author__： zizle
from pandas.api.types import is_datetime64_any_dtype
from PyQt5.QtChart import QChart, QLineSeries, QDateTimeAxis, QCategoryAxis, QValueAxis, QBarSeries, QBarSet
from PyQt5.QtCore import Qt, QDateTime, QMargins, QDate, QTime
from PyQt5.QtGui import QFont


# 将字符串转为浮点值
def covert_float(str_value):
    str_value = str_value.replace(",", "").replace("-", "")
    return float(str_value) if str_value else 0.0


# 计算数据个数，超出隔行读取
def filter_data(table_df):
    if table_df.shape[0] <= 600:
        return table_df
    row = [i for i in range(0, table_df.shape[0], 2)]
    table_df = table_df.iloc[row, :]
    return filter_data(table_df)


# 画折线堆叠图
def draw_lines_stacked(name, table_df, x_bottom_cols, y_left_cols, y_right_cols, legend_labels, tick_count):
    """
    折线堆叠图
    :param name: 图表名称
    :param table_df: 用于画图的pandas DataFrame对象
    :param x_bottom_cols:  下轴列索引列表
    :param y_left_cols: 左轴列索引列表
    :param y_right_cols: 右轴列索引列表
    :param legend_labels: 图例名称标签列表
    :param interval_count: 横轴标签间隔数
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
    # 设置下轴刻度间距
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












# 画堆叠折线图
def draw_lines_stacked1(name, table_df, x_bottom, y_left, legends, tick_count, y_right=[]):
    """
    QChart画折接堆叠图
    :param name: 图表名称
    :param table_df: 画图的源数据 pandas DataFrame类型
    :param x_bottom: x轴列
    :param y_left: 左轴列
    :param y_right: 右轴列
    :param legends: 图例(根据左轴的索引)名称
    :param tick_count: 轴点的个数
    :return: QChart object
    """
    font = QFont()
    font.setPointSize(7)
    chart = QChart()
    chart.layout().setContentsMargins(0, 0, 0, 0)  # chart的外边距
    chart.setMargins(QMargins(15, 5, 15, 0))
    chart.setTitle(name)
    x_bottom = x_bottom[0]
    if is_datetime64_any_dtype(table_df[x_bottom]):  # 如果x轴是时间轴
        """ x轴 """
        min_x, max_x = table_df[x_bottom].min(), table_df[x_bottom].max(0)  # 计算处理x轴数据最值
        print('添加x轴', min_x, max_x)
        start_x = QDateTime()
        year, month, day = int(min_x.strftime('%Y')), int(min_x.strftime('%m')), int(min_x.strftime('%d'))
        start_x.setDate(QDate(year, month, day))
        end_x = QDateTime()
        year, month, day = int(max_x.strftime('%Y')), int(max_x.strftime('%m')), int(max_x.strftime('%d'))
        end_x.setDate(QDate(year, month, day))
        axis_X = QDateTimeAxis()
        # axis_X.setRange(start_x, end_x)
        # axis_X.setTitleText('标题')
        axis_X.setFormat('yyyy-MM-dd HH:mm:ss')
        axis_X.setLabelsAngle(-90)
        print(table_df.shape[0]/tick_count, int(table_df.shape[0]/tick_count))
        # axis_X.setTickCount(int(table_df.shape[0]/tick_count))
        axis_X.setLabelsFont(font)
        axis_X.setGridLineVisible(False)
        chart.addAxis(axis_X, Qt.AlignBottom)  # 加入坐标x轴
        """ 左轴 """
        print('画左轴')
        # 1 实例化左轴
        left_axis_Y = QValueAxis()
        left_axis_Y.setTitleText('数量')
        left_axis_Y.setLabelsFont(font)
        left_axis_Y.setLabelFormat('%i')
        chart.addAxis(left_axis_Y, Qt.AlignLeft)  # 图表加入左轴
        # 2 计算左轴数据最值添加左轴
        left_min_Y, left_max_Y = 0, 0
        # 取数据画图
        for yleft_col in y_left:
            if is_datetime64_any_dtype(table_df[yleft_col]):  # 如果y轴数据是时间类型
                # print('y轴数据有时间类型， 未实现-跳过')
                continue
            table_df[yleft_col] = table_df[yleft_col].apply(covert_float)  # y轴列转为浮点数值
            # 获取最值
            left_min, left_max = table_df[yleft_col].min(), table_df[yleft_col].max()
            if left_min < left_min_Y:
                left_min_Y = left_min
            if left_max > left_max_Y:
                left_max_Y = left_max
            # 取得图线的源数据作折线图
            left_line_data = table_df.iloc[:, [x_bottom, yleft_col]]
            series = QLineSeries()
            series.setName(legends[yleft_col])
            for point_item in left_line_data.values.tolist():
                # print(point_item[0], type(point_item[0]), QDateTime(point_item[0]).toMSecsSinceEpoch(), QDateTime(point_item[0]).currentMSecsSinceEpoch())
                # print(point_item[0].strftime('%Y'), point_item[0].strftime('%m'), point_item[0].strftime('%d'))
                dateTime = QDateTime()
                year, month, day = int(point_item[0].strftime('%Y')), int(point_item[0].strftime('%m')), int(point_item[0].strftime('%d'))
                dateTime.setDate(QDate(year, month, day))
                dateTime.setTime(QTime(12, 0))
                print(dateTime, point_item[1])
                series.append(dateTime.toMSecsSinceEpoch(), point_item[1])  # 取出源数据后一条线就2列数据
            chart.addSeries(series)
            series.attachAxis(axis_X)  # 数据线关联x轴
            series.attachAxis(left_axis_Y)  # 数据线关联左轴

        print('左轴范围：', left_min_Y,left_max_Y)
        left_axis_Y.setRange(left_min_Y, left_max_Y)  # 左轴刻度范围

        """ 右轴 """
        # 1 实例化数值型的右轴
        print('画右轴')
        right_axis_Y = QValueAxis()
        right_axis_Y.setTitleText('比率')
        right_axis_Y.setLabelsFont(font)
        right_axis_Y.setLabelFormat('%.2f')
        chart.addAxis(right_axis_Y, Qt.AlignRight)  # 图表加入右轴
        # 2 计算右轴数据添加右轴
        right_min_Y, right_max_Y = 0, 0
        for yright_col in y_right:
            if is_datetime64_any_dtype(table_df[yright_col]):  # 如果右y轴数据是时间类型
                # print('y轴数据有时间类型， 未实现-跳过')
                continue
            table_df[yright_col] = table_df[yright_col].apply(covert_float)  # 右y轴列转为浮点数值
            # 计算最值
            right_min, right_max = table_df[yright_col].min(), table_df[yright_col].max()
            if right_min < right_min_Y:
                right_min_Y = right_min
            if right_max > right_max_Y:
                right_max_Y = right_max
            # 图线数据作折线图
            right_line_data = table_df.iloc[:, [x_bottom, yright_col]]  # 取得图线的源数据
            series = QLineSeries()
            series.setName(legends[yright_col])
            for point_item in right_line_data.values.tolist():
                series.append(QDateTime(point_item[0]).toMSecsSinceEpoch(), point_item[1])  # 取出源数据后,一条线就2列数据
            chart.addSeries(series)
            series.attachAxis(axis_X)  # 数据线关联x轴
            series.attachAxis(right_axis_Y)  # 数据线关联右轴
        print('右轴范围：', right_min_Y, right_max_Y)
        right_axis_Y.setRange(right_min_Y, right_max_Y)  # 右轴刻度范围
        # chart.addAxis(right_axis_Y, Qt.AlignRight)  # 添加右轴
        # chart.createDefaultAxes()
        # chart.axisX().setLabelFormat('%i')
        # chart.axisX().setFormat('yyyy-MM-dd')
        # # 设置X轴文字格式
        # axis_X = QDateTimeAxis()
        # axis_X.setRange(min_x, max_x)
        # axis_X.setFormat('yyyy-MM-dd')
        # axis_X.setLabelsAngle(-90)
        # axis_X.setTickCount(tick_count)
        # font = QFont()
        # font.setPointSize(7)
        # axis_X.setLabelsFont(font)
        # axis_X.setGridLineVisible(False)
        # # 设置Y轴
        # axix_Y = QValueAxis()
        # axix_Y.setLabelsFont(font)
        # series = chart.series()[0]
        # chart.setAxisX(axis_X, series)
        # # chart.addAxis(axis_X, Qt.AlignLeft)
        # min_y, max_y = int(chart.axisY().min()), int(chart.axisY().max())
        # # 根据位数取整数
        # axix_Y.setRange(min_y, max_y)
        # axix_Y.setLabelFormat('%i')
        # # chart.setAxisY(axix_Y, series)
        # chart.addAxis(axix_Y, Qt.AlignLeft)
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
        axis_X.setGridLineVisible(False)
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
    # 过滤数据个数
    table_df = filter_data(table_df)
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
            print(i)
            axis_X.append(chart.x_labels[i - 1], i - 1)
        axis_X.append(chart.x_labels[-1], x_max - 1)
    else:
        for i in range(x_min, x_max):
            axis_X.append(chart.x_labels[i - 1], i - 1)
        axis_X.append(chart.x_labels[-1], x_max - 1)
    font = QFont()
    font.setPointSize(7)
    axis_X.setLabelsFont(font)
    axis_X.setLabelsAngle(-90)
    axis_X.setGridLineVisible(False)
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




