# _*_ coding:utf-8 _*_
"""
homepage frame window made in tab
Update: 2019-07-25
Author: zizle
"""
import sys
import json
import datetime
import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox,QTableWidget,QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

import config
from thread.request import RequestThread
from widgets.base import TableShow, NormalTable
from piece.home import Calendar
from popup.base import ShowServerPDF


# 常规报告显示窗口
class HomeNormalReport(QWidget):
    def __init__(self, group_id, category_id, *args, **kwargs):
        super(HomeNormalReport, self).__init__(*args, **kwargs)
        self.group_id = group_id
        self.category_id = category_id
        layout = QVBoxLayout(margin=0)
        # 上方类别选择
        self.variety_combo = QComboBox()
        self.variety_combo.currentTextChanged.connect(self.report_variety_changed)
        # 下方表格展示
        self.report_table = QTableWidget(parent=self)
        self.report_table.verticalHeader().hide()
        layout.addWidget(self.variety_combo, alignment=Qt.AlignLeft)
        layout.addWidget(self.report_table)
        self.setLayout(layout)

    # 获取所有品种
    def getVarieties(self):
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'basic/variety/?mc=' + config.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            print(e)
        else:
            print(response['data'])
            # 先加入一个全部,id=0
            self.variety_combo.addItem('全部', 0)
            for variety_item in response['data']:
                self.variety_combo.addItem(variety_item['name'], variety_item['id'])

    # 选择某个类别显示当前的报告
    def report_variety_changed(self):
        variety_id = self.variety_combo.currentData()
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'home/normal-report/?mc=' + config.app_dawn.value('machine'),
                data=json.dumps({
                    'category': self.category_id,
                    'variety': variety_id
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            return
        else:
            self._table_show_reports(response['data'])

    # 表格显示结果
    def _table_show_reports(self, report_list):
        self.report_table.clear()
        self.report_table.setRowCount(len(report_list))
        self.report_table.setColumnCount(6)
        self.report_table.setHorizontalHeaderLabels(['序号', '名称', '品种', '报告类型', '报告日期', ''])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.report_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.report_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        if report_list:
            self.report_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        for row, report_item in enumerate(report_list):
            print(report_item)
            item_0 = QTableWidgetItem(str(row + 1))
            item_0.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(row, 0, item_0)
            item_1 = QTableWidgetItem(str(report_item['name']))
            item_1.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(row, 1, item_1)
            item_2 = QTableWidgetItem(str(report_item['variety']))
            item_2.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(row, 2, item_2)
            category_name = report_item['category'] if report_item['category'] else '其他'
            item_3 = QTableWidgetItem(category_name)
            item_3.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(row, 3, item_3)
            item_4 = QTableWidgetItem(str(report_item['date']))
            item_4.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(row, 4, item_4)


# 交易通知显示窗口
class HomeTransactionNotice(QWidget):
    def __init__(self, group_id, category_id, *args, **kwargs):
        super(HomeTransactionNotice, self).__init__(*args, **kwargs)
        self.group_id = group_id
        self.category_id = category_id
        layout = QVBoxLayout(margin=0)
        # 表格显示
        self.notice_table = QTableWidget(parent=self)
        self.notice_table.verticalHeader().hide()
        layout.addWidget(self.notice_table)
        self.setLayout(layout)

    # 获取所有通知
    def getNotices(self):
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'home/transaction-notice/?mc=' + config.app_dawn.value('machine'),
                data=json.dumps({
                    'category': self.category_id,
                })
            )
            response =  json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            return
        else:
            self._table_show_notices(response['data'])

    # 展示
    def _table_show_notices(self, notice_list):
        self.notice_table.clear()
        self.notice_table.setRowCount(len(notice_list))
        self.notice_table.setColumnCount(5)
        self.notice_table.setHorizontalHeaderLabels(['序号', '名称', '类型', '通知日期', ''])
        self.notice_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.notice_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.notice_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        if notice_list:
            self.notice_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        for row, notice_item in enumerate(notice_list):
            item_0 = QTableWidgetItem(str(row + 1))
            item_0.setTextAlignment(Qt.AlignCenter)
            self.notice_table.setItem(row, 0, item_0)
            item_1 = QTableWidgetItem(str(notice_item['name']))
            item_1.setTextAlignment(Qt.AlignCenter)
            self.notice_table.setItem(row, 1, item_1)
            category_name = notice_item['category'] if notice_item['category'] else '其他'
            item_2 = QTableWidgetItem(category_name)
            item_2.setTextAlignment(Qt.AlignCenter)
            self.notice_table.setItem(row, 2, item_2)
            item_3 = QTableWidgetItem(str(notice_item['date']))
            item_3.setTextAlignment(Qt.AlignCenter)
            self.notice_table.setItem(row, 3, item_3)




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
