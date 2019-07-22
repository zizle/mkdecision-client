# _*_ coding:utf-8 _*_
# company: RuiDa Futures
# author: zizle

from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, Qt, QDate
from PyQt5.QtGui import QCursor

from widgets.public import TableWidget
from widgets.calendar import Calendar
from widgets.func_menu import FuncMenu
from widgets.table_widgets import StockReportEditTable, CalendarEditTable
from config import HOME_PAGE_MIDDLE_WINDOW_MIN_HEIGHT


class MiddleWindowZero(QWidget):  # 常规报告窗口
    def __init__(self, *args, **kwargs):
        super(MiddleWindowZero, self).__init__(*args, **kwargs)
        self.data_type = "all"
        self.__init_ui()

    def __init_ui(self):
        layout = QVBoxLayout(spacing=0, margin=0)
        # 添加报告
        option_layout = QHBoxLayout()
        self.add_report = QPushButton("+添加报告")
        self.func_menu = FuncMenu()
        # "全部", "日报", "周报", "月报", "年报", "专题", "投资报告", "其他"
        self.func_menu.addMenus(["全部", "日报", "周报", "月报", "年报", "专题", "投资报告", "其他"])
        self.func_menu.addSpacer()
        self.table = TableWidget()
        self.table.setVerticalHeaderVisible(False)
        self.table.setEditTriggers(False)  # 不可编辑
        self.table.set_height_signal.connect(self.set_fixed_height)
        option_layout.addWidget(self.add_report, alignment=Qt.AlignLeft)
        layout.addLayout(option_layout)
        layout.addWidget(self.func_menu)
        layout.addWidget(self.table)
        layout.addStretch()
        self.setLayout(layout)

    def set_fixed_height(self, height):
        height = height + 50  # 表格高度+功能按钮高度
        if height < HOME_PAGE_MIDDLE_WINDOW_MIN_HEIGHT:
            height = HOME_PAGE_MIDDLE_WINDOW_MIN_HEIGHT
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

    def table_hide(self):
        self.table.hide()

    def table_show(self):
        self.table.show()

    def set_menu_enable(self, flag):
        for menu in self.func_menu.menus:
            menu.setEnabled(flag)

class MiddleWindowOne(QWidget):  # 交易通知窗口
    def __init__(self, *args, **kwargs):
        super(MiddleWindowOne, self).__init__(*args, **kwargs)
        self.data_type = "all"
        self.__init_ui()

    def __init_ui(self):
        layout = QVBoxLayout(spacing=0, margin=0)
        option_layout = QHBoxLayout()
        self.add_notice = QPushButton("+添加通知")
        self.fun_menu = FuncMenu()
        self.fun_menu.addMenus(["全部", "交易所", "公司", "系统", "其他"])
        self.fun_menu.addSpacer()
        self.table = TableWidget()
        self.table.setVerticalHeaderVisible(False)
        self.table.setEditTriggers(False)  # 不可编辑
        self.table.set_height_signal.connect(self.set_fixed_height)
        option_layout.addWidget(self.add_notice, alignment=Qt.AlignLeft)
        layout.addLayout(option_layout)
        layout.addWidget(self.fun_menu)
        layout.addWidget(self.table)
        layout.addStretch()
        self.setLayout(layout)

    def set_fixed_height(self, height):
        height = height + 50
        if height < HOME_PAGE_MIDDLE_WINDOW_MIN_HEIGHT:
            height = HOME_PAGE_MIDDLE_WINDOW_MIN_HEIGHT
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

    def table_hide(self):
        self.table.hide()

    def table_show(self):
        self.table.show()

    def set_menu_enable(self, flag):
        for menu in self.fun_menu.menus:
            menu.setEnabled(flag)


class MiddleWindowTwo(QWidget):  # 现货报表
    add_new_data_signal = pyqtSignal()  # 添加数据确定按钮点击信号
    height_change_signal = pyqtSignal()  # 本控件窗口高度发生改变信号

    def __init__(self, menus, *args, **kwargs):
        super(MiddleWindowTwo, self).__init__(*args, **kwargs)
        self.menus = menus
        self.__init_ui()

    def __init_ui(self):
        layout = QVBoxLayout(spacing=0, margin=0)
        self.table = TableWidget()
        self.table.setVerticalHeaderVisible(False)
        self.table.set_height_signal.connect(self.set_fixed_height)
        self.add_data_table = StockReportEditTable()
        self.add_data_table.set_height_signal.connect(self.set_fixed_height)
        # 添加行按钮
        self.date = QDate.currentDate()  # 整个日历的date属性,获取日历当前的date
        self.date_edit = QDateEdit(self.date)
        self.date_edit.setStyleSheet("""
            QDateEdit{
                border:none;
                height:22px;
                background-color:rgb(240,240,240);
            }
            QDateEdit::drop-down{
               image:url(media/drop-down.png);
            }""")
        self.date_edit.setDisplayFormat("yyyy年MM月dd日")  #  时间选择
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setCursor(QCursor(Qt.PointingHandCursor))
        self.add_new_data = QPushButton("+添加数据")  # 添加按钮
        self.upload_file_data = QPushButton("Excel数据")
        self.upload_file_data.hide()
        self.add_new_data.clicked.connect(self.add_new_data_clicked)
        self.add_confirm = QPushButton("确定")
        self.add_confirm.clicked.connect(self.add_new_data_confirm)
        add_option_layout = QHBoxLayout(spacing=10, margin=0)
        add_option_layout.addWidget(self.date_edit)
        add_option_layout.addWidget(self.add_new_data)
        add_option_layout.addWidget(self.upload_file_data)
        add_option_layout.addStretch()
        layout.addLayout(add_option_layout)
        layout.addWidget(self.add_data_table)
        layout.addWidget(self.table)
        layout.addWidget(self.add_confirm, alignment=Qt.AlignRight)
        self.add_data_table.hide()  # 初始化隐藏
        self.add_confirm.hide()  # 初始化隐藏
        self.setLayout(layout)

    def add_new_data_clicked(self):
        """添加按钮点击"""
        if not self.add_data_table.isHidden():
            self.upload_file_data.hide()
            self.add_data_table.hide()
            self.add_confirm.hide()
            self.table.show()
            self.add_new_data.setText("+添加数据")
            self.set_fixed_height(35 + 35 * self.table.rowCount())  # 表格传出信号改变自身的固定高度
        else:
            self.upload_file_data.show()
            self.table.hide()
            self.add_data_table.show()
            self.add_confirm.show()
            self.add_new_data.setText("< 返回")
            self.set_fixed_height(35 + 35 * self.add_data_table.rowCount())

        self.height_change_signal.emit()

    def add_new_data_confirm(self):
        """添加新数据确定"""
        self.add_new_data_signal.emit()

    def set_fixed_height(self, height):
        height += 50
        if height < HOME_PAGE_MIDDLE_WINDOW_MIN_HEIGHT:
            height = HOME_PAGE_MIDDLE_WINDOW_MIN_HEIGHT
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)


class MiddleWindowThree(QWidget):  # 财经日历
    calendar_export = pyqtSignal()
    height_change_signal = pyqtSignal()
    add_new_calendar_signal = pyqtSignal()

    def __init__(self, menus, *args, **kwargs):
        super(MiddleWindowThree, self).__init__(*args, **kwargs)
        self.menus=menus
        self.__init_ui()

    def __init_ui(self):
        layout = QVBoxLayout(margin=0)
        # 操作按钮布局
        option_layout = QHBoxLayout()
        export_button = QPushButton("导出日历")
        export_button.clicked.connect(self.export_calendar_data)
        self.add_new_button = QPushButton("+添加日历")
        self.add_new_button.clicked.connect(self.add_new_calendar)
        self.upload_file_button = QPushButton("Excel数据")
        self.upload_file_button.hide()
        option_layout.addWidget(self.add_new_button)
        option_layout.addWidget(self.upload_file_button)
        option_layout.addWidget(export_button)
        option_layout.addStretch()
        # 创建一个日历
        self.calendar = Calendar()
        self.table = TableWidget()
        self.table.setVerticalHeaderVisible(False)
        self.table.set_height_signal.connect(self.set_fixed_height)
        # 添加数据的表格
        self.add_data_table = CalendarEditTable()
        self.add_data_table.set_height_signal.connect(self.set_fixed_height)
        self.add_confirm = QPushButton("确定提交")
        self.add_confirm.clicked.connect(self.add_new_calendar_confirm)
        self.add_data_table.hide()
        self.add_confirm.hide()
        layout.addLayout(option_layout)
        layout.addWidget(self.calendar)
        layout.addWidget(self.table)
        layout.addWidget(self.add_data_table)
        layout.addWidget(self.add_confirm, alignment=Qt.AlignRight)
        self.setLayout(layout)

    def add_new_calendar(self):
        """添加日历数据按钮点击"""
        if not self.add_data_table.isHidden():
            self.upload_file_button.hide()
            self.add_data_table.hide()
            self.add_confirm.hide()
            self.calendar.show()
            self.table.show()
            self.add_new_button.setText("+添加日历")
            self.set_fixed_height(35 + 35 * self.table.rowCount())
        else:
            self.upload_file_button.show()
            self.add_data_table.show()
            self.add_confirm.show()
            self.calendar.hide()
            self.table.hide()
            self.add_new_button.setText("< 返回")
            self.set_fixed_height(35 + 35 * self.add_data_table.rowCount())
        self.height_change_signal.emit()

    def add_new_calendar_confirm(self):
        """添加新数据确定"""
        # 设置表格控件
        # self.add_data_table
        self.add_new_calendar_signal.emit()

    def export_calendar_data(self):
        """导出日历信号传出"""
        self.calendar_export.emit()

    def set_fixed_height(self, height):
        height = height + 100
        if height < HOME_PAGE_MIDDLE_WINDOW_MIN_HEIGHT:
            height = HOME_PAGE_MIDDLE_WINDOW_MIN_HEIGHT
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)


