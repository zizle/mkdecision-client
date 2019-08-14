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
from piece.home import ShowReport, ShowNotice, ShowCommodity, Calendar, ShowFinance

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


class Report(QWidget):
    def __init__(self, category=None, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)
        self.category=category
        layout = QVBoxLayout()
        self.show_message = QLabel('请求中...')
        self.table = TableShow()
        layout.addWidget(self.show_message)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.get_reports()

    def get_reports(self, page=1, page_size=20):
        self.show_message.setText('请求中...')
        if self.category == 'all':
            url = config.SERVER_ADDR + 'homepage/report/'
        else:
            url = config.SERVER_ADDR + 'homepage/report/?category=' + self.category
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
        if signal['error']:
            self.show_message.setText('出错.\n{}'.format(signal['error']))
            return
        self.show_message.hide()
        if signal['page_num'] > 1:  # 数据大于1页添加页码控制器
            self.page_controller = PageController()
            self.page_controller.set_total_page(signal['page_num'])
            self.layout().addWidget(self.page_controller, alignment=Qt.AlignCenter)
        # 展示数据






class Report1(QWidget):
    def __init__(self, *args, **kwargs):
        super(Report, self).__init__(*args, *kwargs)
        layout = QVBoxLayout(spacing=5)
        # report table
        self.show_table = ShowReport()
        # page controller
        self.page_controller = PageController()
        # signal
        self.page_controller.clicked.connect(self.page_number_changed)
        self.show_table.page_num.connect(self.set_total_page)
        layout.addWidget(self.show_table)
        layout.addWidget(self.page_controller, alignment=Qt.AlignCenter)
        self.setStyleSheet("""
        MenuBar {
            background-color:rgb(255,255,255);
        }
        """)
        self.setLayout(layout)
        # get report
        self.show_table.get_report(url=config.SERVER_ADDR + 'homepage/report/')  # query param type=None

    def menu_clicked(self, menu):
        print('frame.home.py {} 点击类别:'.format(str(sys._getframe().f_lineno)), menu.text())
        type_dict = {
            "日报": "daily",
            "周报": "weekly",
            "月报": "monthly",
            "年报": "annual",
            "专题": "special",
            "投资报告": "invest",
            "其他": "others"
        }
        type_en = type_dict.get(menu.text())
        url = config.SERVER_ADDR + 'homepage/report/'
        if type_en:
            url += '?category=' + type_en
        self.show_table.get_report(url=url)

    def page_number_changed(self, page):
        self.show_table.get_report(url=config.SERVER_ADDR + 'homepage/report/', page=page)  # query param type=None

    def set_total_page(self, pages_num):
        print('frame.home.py {} 总页码信号:'.format(sys._getframe().f_lineno), pages_num)
        self.page_controller.set_total_page(pages_num)


class Notice(QWidget):
    def __init__(self, *args, **kwargs):
        super(Notice, self).__init__(*args, *kwargs)
        layout = QVBoxLayout(spacing=5)
        menu_bar = MenuBar()
        menu_bar.setContentsMargins(0, 0, 0, 0)
        menu_bar.addMenuButtons(["全部", "交易所", "公司", "系统", "其他"])
        menu_bar.addStretch()
        menu_bar.menu_btn_clicked.connect(self.menu_clicked)
        # report table
        self.show_table = ShowNotice()
        # page controller
        self.page_controller = PageController()
        # signal
        self.page_controller.clicked.connect(self.page_number_changed)
        self.show_table.page_num.connect(self.set_total_page)
        layout.addWidget(menu_bar)
        layout.addWidget(self.show_table)
        layout.addWidget(self.page_controller, alignment=Qt.AlignCenter)
        self.setStyleSheet("""
        MenuBar {
            background-color:rgb(255,255,255);
        }
        """)
        self.setLayout(layout)
        self.show_table.get_notice(url=config.SERVER_ADDR + 'homepage/notice/')  # query param type=None

    def menu_clicked(self, menu):
        print('frame.home.py {} 点击类别:'.format(str(sys._getframe().f_lineno)), menu.text())
        type_dict = {
            "公司": "company",
            "交易所": "change",
            "系统": "system",
            "其他": "others"
        }
        type_en = type_dict.get(menu.text())
        url = config.SERVER_ADDR + 'homepage/notice/'
        if type_en:
            url += '?category=' + type_en
        self.show_table.get_notice(url=url)

    def page_number_changed(self, page):
        self.show_table.get_notice(url=config.SERVER_ADDR + 'homepage/notice/', page=page)  # query param type=None

    def set_total_page(self, pages_num):
        print('frame.home.py {} 总页码信号:'.format(sys._getframe().f_lineno), pages_num)
        self.page_controller.set_total_page(pages_num)