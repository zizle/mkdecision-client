# _*_ coding:utf-8 _*_
# author: zizle
# Date: 20190529

from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal


class CalendarEditTable(QTableWidget):
    set_height_signal = pyqtSignal(int)

    def __init__(self, *args):
        super(CalendarEditTable, self).__init__(*args)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["日期", "时间", "地区", "事件描述", "预期值"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 列自适应
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionBehavior(1)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def set_rc_labels(self, row, col, labels):
        self.setRowCount(row)
        self.setColumnCount(col)
        self.setHorizontalHeaderLabels(labels)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 第一列根据文字宽自适应
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 第一列根据文字宽自适应

    def set_row_content(self, row_index, content):
        for col, col_data in enumerate(content):
            item = QTableWidgetItem(str(col_data))
            item.setTextAlignment(132)
            self.setItem(row_index, col, item)
        # 设置表格高度
        self.set_height_signal.emit(35 + self.rowCount() * 32)


class StockReportEditTable(QTableWidget):
    set_height_signal = pyqtSignal(int)

    def __init__(self, *args):
        super(StockReportEditTable, self).__init__(*args)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["品种", "地区", "等级", "报价", "日期", "备注"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 列自适应
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionBehavior(1)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def set_rc_labels(self, row, col, labels):
        self.setRowCount(row)
        self.setColumnCount(col)
        self.setHorizontalHeaderLabels(labels)

    def set_row_content(self, row_index, content):
        for col, col_data in enumerate(content):
            item = QTableWidgetItem(str(col_data))
            item.setTextAlignment(132)
            self.setItem(row_index, col, item)
        # 设置表格高度
        self.set_height_signal.emit(35 + self.rowCount() * 32)


class TableComboBox(QComboBox):
    text_changed_signal = pyqtSignal(list)

    def __init__(self, row, col):
        super(TableComboBox, self).__init__()
        self.rowIndex = row  # 在表格中的行
        self.colIndex = col   # 在表格中的列
        self.activated[str].connect(self.combo_text_changed)
        self.__init_ui()

    def __init_ui(self):
        level = ["一级", "二级", "三级", "四级", "五级"]
        self.addItems(level)
        self.setCurrentIndex(-1)

    def combo_text_changed(self):
        self.text_changed_signal.emit([self, self.rowIndex, self.colIndex])

    def wheelEvent(self, QWheelEvent):
        pass


class TableDateEdit(QDateEdit):
    date_changed_signal = pyqtSignal(list)

    def __init__(self, row, col, *args):
        super(TableDateEdit, self).__init__(*args)
        self.rowIndex = row
        self.colIndex = col
        self.dateChanged.connect(self.date_changed)
        self.__init_ui()

    def __init_ui(self):
        self.setDisplayFormat("yyyy-MM-dd")
        self.setCalendarPopup(True)

    def date_changed(self):
        self.date_changed_signal.emit([self, self.rowIndex, self.colIndex])

    def wheelEvent(self, *args, **kwargs):
        pass


class TimeEdit(QTimeEdit):
    time_change_signal = pyqtSignal(list)

    def __init__(self, row, col, *args):
        super(TimeEdit, self).__init__(*args)
        self.rowIndex = row
        self.colIndex = col
        self.timeChanged.connect(self.time_changed)
        self.__init_ui()

    def __init_ui(self):
        self.setDisplayFormat("HH:mm")

    def time_changed(self):
        self.time_change_signal.emit([self, self.rowIndex, self.colIndex])










