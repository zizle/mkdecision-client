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
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QCursor

import config
from thread.request import RequestThread
from widgets.base import TableShow, NormalTable
from piece.base import PageController
from piece.home import ShowCommodity, Calendar, ShowFinance
from popup.base import ShowServerPDF


class Commodity(QWidget):
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
        self.set_start_date('today')
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
        print('piece.home.py {} 现货报表: '.format(str(sys._getframe().f_lineno)), signal)
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

    def set_start_date(self, date_name):
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
    def __init__(self, *args, **kwargs):
        super(Finance, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        self.setLayout(layout)


class Notice(QWidget):
    # 交易通知显示窗口
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
    # 常规报告显示窗口
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

    def get_reports(self, category, page=1, page_size=1):
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






class Finance1(QWidget):
    def __init__(self, *args, **kwargs):
        super(Finance, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(spacing=5)
        # calendar
        calendar_selection = Calendar()
        self.show_table = ShowFinance()
        # signal
        calendar_selection.click_date.connect(self.date_selected)
        layout.addWidget(calendar_selection)
        layout.addWidget(self.show_table)
        self.setLayout(layout)
        self.show_table.get_finance(url=config.SERVER_ADDR + 'homepage/finance/')  # query param date=None

    def date_selected(self, date):
        self.show_table.get_finance(url=config.SERVER_ADDR + 'homepage/finance/?date=' + str(date.toPyDate()))


