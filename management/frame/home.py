# _*_ coding:utf-8 _*_
"""
homepage frame window will make in tab
Update: 2019-07-25
Author: zizle
"""
import sys
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QCursor

import config
from thread.request import RequestThread
from widgets.base import TableShow
from piece.base import MenuBar, PageController
from piece.home import ShowCommodity, Calendar, ShowFinance
from popup.base import ShowServerPDF

class Commodity(QWidget):
    def __init__(self, *args, **kwargs):
        super(Commodity, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        # date edit
        current_date = QDate.currentDate()
        self.date_selection = QDateEdit(current_date)
        # show table
        self.show_table = ShowCommodity()
        # style
        self.date_selection.setDisplayFormat("yyyy年MM月dd日")  # 时间选择
        self.date_selection.setCalendarPopup(True)
        self.date_selection.setCursor(QCursor(Qt.PointingHandCursor))
        # signal
        self.date_selection.dateChanged.connect(self.new_date_selected)
        # add layout
        layout.addWidget(self.date_selection, alignment=Qt.AlignLeft)
        layout.addWidget(self.show_table)
        self.setLayout(layout)
        # get commodity
        self.show_table.get_commodity(url=config.SERVER_ADDR + 'homepage/commodity/')  # query param date=None

    def new_date_selected(self):
        date = self.date_selection.date().toPyDate()
        self.show_table.get_commodity(url=config.SERVER_ADDR + 'homepage/commodity/?date=' + str(date))


class Finance(QWidget):
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


class Notice(QWidget):
    def __init__(self, category='all', *args, **kwargs):
        super(Notice, self).__init__(*args, *kwargs)
        self.category = category
        layout = QVBoxLayout()
        # widgets
        self.show_message = QLabel('请求中...')
        self.table = TableShow()
        self.page_controller = PageController()
        # signal
        self.page_controller.clicked.connect(self.page_number_changed)
        self.table.cellClicked.connect(self.show_notice_detail)
        # add layout
        layout.addWidget(self.show_message)
        layout.addWidget(self.table)
        layout.addWidget(self.page_controller, alignment=Qt.AlignCenter)
        # style
        self.page_controller.hide()
        self.setLayout(layout)
        # initial data
        self.notice_thread = None
        self.get_notices()

    def get_notices(self, page=1, page_size=20):
        self.show_message.setText('请求中...')
        if self.category == 'all':
            url = config.SERVER_ADDR + 'homepage/notice/'
        else:
            url = config.SERVER_ADDR + 'homepage/notice/?category=' + self.category
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
            self.show_message.setText('出错.\n{}'.format(signal['message']))
            return
        self.show_message.hide()
        if signal['page_num'] > 1:  # 数据大于1页设置页码控制器
            self.page_controller.set_total_page(signal['page_num'])
            self.page_controller.show()
        # 展示数据
        header_couple = [('serial_num', '序号'), ('title','标题'), ('type_zh', '类型'), ('create_time', '上传时间'), ('to_look', '')]
        self.table.show_content(contents=signal['data'], header_couple=header_couple)

    def page_number_changed(self, page):
        self.get_notices(page=page)

    def show_notice_detail(self, row, col):
        if col == 4:
            item = self.table.item(row, col)
            name_item = self.table.item(row, 1)
            popup = ShowServerPDF(file_url= config.SERVER_ADDR + item.file, file_name=name_item.text())
            popup.deleteLater()
            popup.exec()
            del popup


class Report(QWidget):
    def __init__(self, category='all', *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)
        self.category=category
        layout = QVBoxLayout()
        # widgets
        self.show_message = QLabel('请求中...')
        self.table = TableShow()
        self.page_controller = PageController()
        # signal
        self.page_controller.clicked.connect(self.page_number_changed)
        self.table.cellClicked.connect(self.show_report_detail)
        # add layout
        layout.addWidget(self.show_message)
        layout.addWidget(self.table)
        layout.addWidget(self.page_controller, alignment=Qt.AlignCenter)
        # style
        self.page_controller.hide()
        self.setLayout(layout)
        # initial data
        self.report_thread = None
        self.get_reports()

    def get_reports(self, page=1, page_size=20):
        self.show_message.setText('请求中...')
        if self.category == 'all':
            url = config.SERVER_ADDR + 'homepage/report/'
        else:
            url = config.SERVER_ADDR + 'homepage/report/?category=' + self.category
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
            self.show_message.setText('出错.{}'.format(signal['message']))
            return
        self.show_message.hide()
        if signal['page_num'] > 1:  # 数据大于1页设置页码控制器
            self.page_controller.set_total_page(signal['page_num'])
            self.page_controller.show()
        # 展示数据
        header_couple = [('serial_num', '序号'), ('title','标题'), ('type_zh', '类型'), ('create_time', '上传时间'), ('to_look', '')]
        self.table.show_content(contents=signal['data'], header_couple=header_couple)

    def page_number_changed(self, page):
        self.get_reports(page=page)

    def show_report_detail(self, row, col):
        if col == 4:
            item = self.table.item(row, col)
            name_item = self.table.item(row, 1)
            popup = ShowServerPDF(file_url= config.SERVER_ADDR + item.file, file_name=name_item.text())
            popup.deleteLater()
            popup.exec()
            del popup