# _*_ coding:utf-8 _*_
"""
homepage frame window made in tab
Update: 2019-07-25
Author: zizle
"""
import sys
import json
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

import config
from thread.request import RequestThread
from widgets.base import TableShow, NormalTable
from piece.home import Calendar
from popup.base import ShowServerPDF


class Commodity(QWidget):
    # 现货报表
    def __init__(self, *args, **kwargs):
        super(Commodity, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        # widgets
        self.date_selection = QDateEdit()
        date_confirm = QPushButton('确定')
        self.table = NormalTable()
        # style
        layout.setContentsMargins(0,0,0,0)
        action_layout.setContentsMargins(0,0,0,0)
        self.date_selection.setDisplayFormat("yyyy年MM月dd日")  # 时间选择
        self.date_selection.setCalendarPopup(True)
        self.date_selection.setCursor(QCursor(Qt.PointingHandCursor))
        # signal
        date_confirm.clicked.connect(self.get_commodity)
        # add to layout
        action_layout.addWidget(self.date_selection)
        action_layout.addWidget(date_confirm)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)
        # initial data
        self.commodity_thread = None

    def get_commodity(self):
        date = self.date_selection.date().toPyDate()
        url = config.SERVER_ADDR + 'homepage/commodity/?date=' + str(date)
        if self.commodity_thread:
            del self.commodity_thread
        self.commodity_thread = RequestThread(
            url=url,
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.commodity_thread.response_signal.connect(self.commodity_thread_back)
        self.commodity_thread.finished.connect(self.commodity_thread.deleteLater)
        self.commodity_thread.start()

    def commodity_thread_back(self, signal):
        print('frame.home.py {} 现货报表: '.format(str(sys._getframe().f_lineno)), signal)
        if signal['error']:
            return
        # 展示数据
        header_couple = [
            ('serial_num', '序号'),
            ('variety', '品种'),
            ('area', '地区'),
            ('level', '等级'),
            ('price', '价格'),
            ('note', '备注'),
            ('date', '日期'),
        ]
        self.table.show_content(contents=signal['data'], header_couple=header_couple)
        self.table.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
        self.table.horizontalHeader().setSectionResizeMode(self.table.columnCount() - 1, 3)  # 最后1列随文字宽度

    def set_current_date(self, date_name):
        if date_name == 'today':
            date = datetime.datetime.now()
        elif date_name == 'yesterday':
            date = datetime.datetime.now() + datetime.timedelta(days=-1)
        elif date_name == 'tomorrow':
            date = datetime.datetime.now() + datetime.timedelta(days=1)
        else:
            date = datetime.datetime.now()
        self.date_selection.setDate(date)


class Finance(QWidget):
    # 财经日历
    def __init__(self, *args, **kwargs):
        super(Finance, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        # widgets
        self.calendar_selection = Calendar()
        self.table = NormalTable()
        # signal
        self.calendar_selection.click_date.connect(self.mouse_select_date)
        # style
        layout.setContentsMargins(0,0,0,0)
        # add to layout
        layout.addWidget(self.calendar_selection)
        layout.addWidget(self.table)
        self.setLayout(layout)
        # initial data
        self.finance_thread = None

    def get_finance(self):
        date = self.calendar_selection.date_edit.date().toPyDate()
        url = config.SERVER_ADDR + 'homepage/finance/?date=' + str(date)
        if self.finance_thread:
            del self.finance_thread
        self.finance_thread = RequestThread(
            url=url,
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.finance_thread.response_signal.connect(self.finance_thread_back)
        self.finance_thread.finished.connect(self.finance_thread.deleteLater)
        self.finance_thread.start()

    def finance_thread_back(self, signal):
        print('frame.home.py {} 财经日历: '.format(str(sys._getframe().f_lineno)), signal)
        if signal['error']:
            return
        # 展示数据
        header_couple = [
            ('serial_num', '序号'),
            ('date', '日期'),
            ('time', '时间'),
            ('country', '地区'),
            ('event', '事件描述'),
            ('expected', '预期值'),
        ]
        self.table.show_content(contents=signal['data'], header_couple=header_couple)
        self.table.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
        self.table.horizontalHeader().setSectionResizeMode(1, 3)
        self.table.horizontalHeader().setSectionResizeMode(2, 3)

    def mouse_select_date(self, date):
        self.calendar_selection.date_edit.setDate(date)
        self.get_finance()

    def set_current_date(self, date_name):
        if date_name == 'today':
            date = datetime.datetime.now()
        elif date_name == 'yesterday':
            date = datetime.datetime.now() + datetime.timedelta(days=-1)
        elif date_name == 'tomorrow':
            date = datetime.datetime.now() + datetime.timedelta(days=1)
        else:
            date = datetime.datetime.now()
        self.calendar_selection.set_current_date(date)


class Notice(QWidget):
    # 交易通知
    def __init__(self, *args, **kwargs):
        super(Notice, self).__init__(*args, *kwargs)
        layout = QVBoxLayout()
        # widgets
        self.table = TableShow()
        self.page_controller = PageController()
        # signal
        self.page_controller.clicked.connect(self.page_number_changed)
        self.table.cellClicked.connect(self.show_notice_detail)
        # add layout
        layout.addWidget(self.table)
        layout.addWidget(self.page_controller, alignment=Qt.AlignCenter)
        # style
        layout.setContentsMargins(0,0,0,0)
        self.page_controller.hide()
        self.setLayout(layout)
        # initial data
        self.category = 'all'
        self.notice_thread = None

    def get_notices(self, category, page=1, page_size=20):
        if category in ["changelib", "company", "system", "others"]:
            self.category = category
        url = config.SERVER_ADDR + 'homepage/notice/'
        if self.category != 'all':
            url += '?category=' + self.category
        print('frame.home.py {} 请求通知：'.format(sys._getframe().f_lineno), url)
        if self.notice_thread:
            del self.notice_thread
        self.notice_thread = RequestThread(
            url=url,
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({
                "machine_code": config.app_dawn.value("machine"),
                'page': page,
                'page_size': page_size
            }),
            cookies=config.app_dawn.value('cookies')
        )
        self.notice_thread.response_signal.connect(self.notice_thread_back)
        self.notice_thread.finished.connect(self.notice_thread.deleteLater)
        self.notice_thread.start()

    def notice_thread_back(self, signal):
        print('frame.home.py {} 通知数据：'.format(sys._getframe().f_lineno), signal)
        if signal['error']:
            return
        if signal['page_num'] > 1:  # 数据大于1页设置页码控制器
            self.page_controller.set_total_page(signal['page_num'])
            self.page_controller.show()
        # 展示数据
        header_couple = [('serial_num', '序号'), ('title','标题'), ('type_zh', '类型'), ('create_time', '上传时间'), ('to_look', '')]
        self.table.show_content(contents=signal['data'], header_couple=header_couple)

    def page_number_changed(self, page):
        self.get_notices(category=self.category, page=page)

    def show_notice_detail(self, row, col):
        if col == 4:
            item = self.table.item(row, col)
            name_item = self.table.item(row, 1)
            popup = ShowServerPDF(file_url= config.SERVER_ADDR + item.file, file_name=name_item.text())
            popup.deleteLater()
            popup.exec()
            del popup


class Report(QWidget):
    # 常规报告
    def __init__(self, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        # widgets
        self.table = TableShow()
        self.page_controller = PageController()
        # signal
        self.page_controller.clicked.connect(self.page_number_changed)
        self.table.cellClicked.connect(self.show_report_detail)
        # add layout
        layout.addWidget(self.table)
        layout.addWidget(self.page_controller, alignment=Qt.AlignCenter)
        # style
        layout.setContentsMargins(0,0,0,0)
        self.page_controller.hide()
        self.setLayout(layout)
        # initial data
        self.category = 'all'
        self.report_thread = None

    def get_reports(self, category, page=1, page_size=20):
        if category in ["daily", "weekly", "monthly", "annual", "special", "invest", "others"]:
            self.category = category
        url = config.SERVER_ADDR + 'homepage/report/'
        if self.category != 'all':
            url += '?category=' + self.category
        print('frame.home.py {} 请求报告：'.format(sys._getframe().f_lineno), url)
        if self.report_thread:
            del self.report_thread
        self.report_thread = RequestThread(
            url=url,
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({
                "machine_code": config.app_dawn.value("machine"),
                'page': page,
                'page_size': page_size
            }),
            cookies=config.app_dawn.value('cookies')
        )
        self.report_thread.response_signal.connect(self.report_thread_back)
        self.report_thread.finished.connect(self.report_thread.deleteLater)
        self.report_thread.start()

    def report_thread_back(self, signal):
        print('frame.home.py {} 报告数据：'.format(sys._getframe().f_lineno), signal)
        if signal['error']:
            return
        if signal['page_num'] > 1:  # 数据大于1页设置页码控制器
            self.page_controller.set_total_page(signal['page_num'])
            self.page_controller.show()
        # 展示数据
        header_couple = [('serial_num', '序号'), ('title','标题'), ('type_zh', '类型'), ('create_time', '上传时间'), ('to_look', '')]
        self.table.show_content(contents=signal['data'], header_couple=header_couple)

    def page_number_changed(self, page):
        self.get_reports(category=self.category, page=page)

    def show_report_detail(self, row, col):
        if col == 4:
            item = self.table.item(row, col)
            name_item = self.table.item(row, 1)
            popup = ShowServerPDF(file_url= config.SERVER_ADDR + item.file, file_name=name_item.text())
            popup.deleteLater()
            popup.exec()
            del popup
