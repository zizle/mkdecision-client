# _*_ coding:utf-8 _*_
"""
all tabs of data-maintenance module, in the home page
Create: 2019-07-25
Author: zizle
"""
import sys
import json
import requests
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

import config
from popup.maintain import CreateNewBulletin, CreateNewCarousel, CreateNewReport, CreateNewNotice, CreateNewCommodity, CreateNewFinance
from piece.maintain import TableCheckBox
from thread.request import RequestThread


class BulletinInfo(QWidget):
    def __init__(self):
        super(BulletinInfo, self).__init__()
        # layout
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        create_btn = QPushButton("设置")
        refresh_btn = QPushButton('刷新')
        create_btn.clicked.connect(self.create_new_bulletin)
        self.show_table = QTableWidget()
        # mount widget to show request message
        self.message_btn = QPushButton('刷新中...', self.show_table)
        self.message_btn.resize(100, 20)
        self.message_btn.move(100, 100)
        self.message_btn.setStyleSheet('text-align:center;border:none;background-color:rgb(210,210,210)')
        # style
        self.show_table.verticalHeader().setVisible(False)
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.show_table)
        self.setLayout(layout)
        # get bulletins
        self.get_all_bulletin()

    def bulletin_thread_back(self, content):
        # fill show table
        print('piece.home.py {} 维护公告: '.format(str(sys._getframe().f_lineno)), content)
        if content['error']:
            self.message_btn.setText('失败,请重试!')
            self.message_btn.setEnabled(True)
            return
        else:
            if not content['data']:
                self.message_btn.setText('完成,无数据.')
                return  # function finished
            else:
                self.message_btn.setText('刷新完成!')
                self.message_btn.hide()
        # fill table
        self.show_table.horizontalHeader().setVisible(True)
        keys = [('serial_num', '序号'), ('create_time', '上传时间'),('name', '名称'), ('raw_name', '文件'), ('content','内容'),('is_active', '展示')]
        bulletins = content['data']
        row = len(bulletins)
        self.show_table.setRowCount(row)
        self.show_table.setColumnCount(len(keys))  # 列数
        labels = []
        set_keys = []
        for key_label in keys:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        self.show_table.setHorizontalHeaderLabels(labels)
        self.show_table.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
        self.show_table.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
        for row in range(self.show_table.rowCount()):
            for col in range(self.show_table.columnCount()):
                if col == 0:
                    item = QTableWidgetItem(str(row+1))
                else:
                    label_key = set_keys[col]
                    if label_key == 'is_active':
                        checkbox = TableCheckBox(row=row, col=col, option_label=label_key)
                        checkbox.setChecked(int(bulletins[row][label_key]))
                        checkbox.clicked_changed.connect(self.update_bulletin_info)
                        self.show_table.setCellWidget(row, col, checkbox)
                    item = QTableWidgetItem(str(bulletins[row][set_keys[col]]))
                item.setTextAlignment(Qt.AlignCenter)
                item.bulletin_id = bulletins[row]['id']
                self.show_table.setItem(row, col, item)

    def create_new_bulletin(self):
        # dialog widget for edit bulletin information
        def update_bulletin(signal):
            # create new bulletin or update a bulletin in server
            print('frame.maintain.home.py {} : '.format(str(sys._getframe().f_lineno)), "公告信号:", signal)
            headers = config.CLIENT_HEADERS
            cookies = config.app_dawn.value('cookies')
            machine_code = config.app_dawn.value('machine')
            if signal["set_option"] == "new_bulletin":
                data = dict()
                data["name"] = signal["name"]
                data["show_type"] = signal["show_type"]
                data['machine_code'] = machine_code
                if signal["show_type"] == "show_file":
                    file_raw_name = signal["file"].rsplit("/", 1)
                    file = open(signal["file"], "rb")
                    file_content = file.read()
                    file.close()
                    data["file"] = (file_raw_name[1], file_content)
                elif signal["show_type"] == "show_text":
                    data["content"] = signal["content"]
                encode_data = encode_multipart_formdata(data)
                data = encode_data[0]
                headers['Content-Type'] = encode_data[1]
                try:
                    response = requests.post(
                        url=config.SERVER_ADDR + "homepage/bulletin/",
                        headers=headers,
                        data=data,
                        cookies=cookies
                    )
                except Exception as error:
                    QMessageBox.information(self, '提示', "发生了个错误!\n{}".format(error), QMessageBox.Yes)
                    return
                response_data = json.loads(response.content.decode('utf-8'))
                if response.status_code != 201:
                    QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
                    return
                else:
                    QMessageBox.information(self, '成功', '创建成功, 赶紧刷新看看吧.', QMessageBox.Yes)
                    popup.close()  # close the dialog
        popup = CreateNewBulletin()
        popup.new_data_signal.connect(update_bulletin)
        if not popup.exec():
            del popup

    def get_all_bulletin(self):
        self.message_btn.setText('刷新中...')
        self.message_btn.show()
        self.message_btn.setEnabled(False)
        self.show_table.clear()
        self.show_table.setRowCount(0)
        self.show_table.horizontalHeader().setVisible(False)
        self.bulletin_thread = RequestThread(
            url=config.SERVER_ADDR + 'homepage/bulletin/',
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"machine_code": config.app_dawn.value('machine'), "maintain": True, 'is_admin': True}),
            cookies=config.app_dawn.value('cookies'),
        )
        self.bulletin_thread.finished.connect(self.bulletin_thread.deleteLater)
        self.bulletin_thread.response_signal.connect(self.bulletin_thread_back)
        self.bulletin_thread.start()

    def update_bulletin_info(self, signal):
        # 获取机器码
        item = self.show_table.item(signal['row'], signal['col'])
        show = '显示' if signal['checked'] else '不显示'
        print('frame.maintain.base.py {} 修改公告：'.format(sys._getframe().f_lineno), item.bulletin_id, show)


class CarouselInfo(QWidget):
    def __init__(self):
        super(CarouselInfo, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        create_btn.clicked.connect(self.create_new_carousel)
        self.show_table = QTableWidget()
        # mount widget to show request message
        self.message_btn = QPushButton('刷新中...', self.show_table)
        self.message_btn.resize(100, 20)
        self.message_btn.move(100, 100)
        self.message_btn.setStyleSheet('text-align:center;border:none;background-color:rgb(210,210,210)')
        # style
        self.show_table.verticalHeader().setVisible(False)
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.show_table)
        self.setLayout(layout)
        # get all carousel information
        self.get_all_carousel()

    def create_new_carousel(self):
        # dialog for add new carousel
        def upload_carousel(signal):
            print('frame.maintain.py {} 轮播信号:'.format(str(sys._getframe().f_lineno)), signal)
            data = dict()
            data["name"] = signal["name"]
            data['machine_code'] = config.app_dawn.value('machine')
            # handler image data
            image_name_list = signal['image'].rsplit('/', 1)
            image = open(signal['image'], 'rb')
            image_content = image.read()
            image.close()
            data['image'] = (image_name_list[1], image_content)
            if signal['file']: # file show
                file_raw_name = signal["file"].rsplit("/", 1)
                file = open(signal["file"], "rb")
                file_content = file.read()
                file.close()
                data["file"] = (file_raw_name[1], file_content)
            data["content"] = signal["content"]
            data["redirect_url"] = signal['redirect']
            encode_data = encode_multipart_formdata(data)
            data = encode_data[0]
            headers = config.CLIENT_HEADERS
            headers['Content-Type'] = encode_data[1]
            try:
                response = requests.post(
                    url=config.SERVER_ADDR + "homepage/carousel/",
                    headers=headers,
                    data=data,
                    cookies=config.app_dawn.value('cookies')
                )
            except Exception as error:
                QMessageBox.information(self, '提示', "发生了个错误!\n{}".format(error), QMessageBox.Yes)
                return
            response_data = json.loads(response.content.decode('utf-8'))
            if response.status_code != 201:
                QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
                return
            else:
                QMessageBox.information(self, '成功', '创建成功, 赶紧刷新看看吧.', QMessageBox.Yes)
                popup.close()  # close the dialog
        popup = CreateNewCarousel()
        popup.new_data_signal.connect(upload_carousel)
        if not popup.exec():
            del popup

    def carousel_thread_back(self, content):
        # fill show table
        print('frame.maintain.home.py {} 维护轮播: '.format(str(sys._getframe().f_lineno)), content)
        if content['error']:
            self.message_btn.setText('失败,请重试!')
            self.message_btn.setEnabled(True)
            return
        else:
            if not content['data']:
                self.message_btn.setText('完成,无数据.')
                return  # function finished
            else:
                self.message_btn.setText('刷新完成!')
                self.message_btn.hide()
        # fill table
        self.show_table.horizontalHeader().setVisible(True)
        keys = [
            ('serial_num', '序号'),
            ('create_time', '上传时间'),
            ('name', '名称'),
            ('image_name', '图片'),
            ('file_name', '文件'),
            ('content', '内容'),
            ('redirect', '网址'),
            ('is_active', '展示')
        ]
        carousels = content['data']
        row = len(carousels)
        self.show_table.setRowCount(row)
        self.show_table.setColumnCount(len(keys))  # 列数
        labels = []
        set_keys = []
        for key_label in keys:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        self.show_table.setHorizontalHeaderLabels(labels)
        self.show_table.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
        self.show_table.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
        for row in range(self.show_table.rowCount()):
            for col in range(self.show_table.columnCount()):
                if col == 0:
                    item = QTableWidgetItem(str(row + 1))
                else:
                    label_key = set_keys[col]
                    if label_key == 'is_active':
                        checkbox = TableCheckBox(row=row, col=col, option_label=label_key)
                        checkbox.setChecked(int(carousels[row][label_key]))
                        checkbox.clicked_changed.connect(self.update_carousel_info)
                        self.show_table.setCellWidget(row, col, checkbox)
                    item = QTableWidgetItem(str(carousels[row][set_keys[col]]))
                item.setTextAlignment(Qt.AlignCenter)
                item.carousel_id = carousels[row]['id']
                self.show_table.setItem(row, col, item)

    def get_all_carousel(self):
        self.message_btn.setText('刷新中...')
        self.message_btn.show()
        self.message_btn.setEnabled(False)
        self.show_table.clear()
        self.show_table.setRowCount(0)
        self.show_table.horizontalHeader().setVisible(False)
        self.carousel_thread = RequestThread(
            url=config.SERVER_ADDR + 'homepage/carousel/',
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"machine_code": config.app_dawn.value('machine'), "maintain": True}),
            cookies=config.app_dawn.value('cookies'),
        )
        self.carousel_thread.finished.connect(self.carousel_thread.deleteLater)
        self.carousel_thread.response_signal.connect(self.carousel_thread_back)
        self.carousel_thread.start()

    def update_carousel_info(self, signal):
        item = self.show_table.item(signal['row'], signal['col'])
        show = '显示' if signal['checked'] else '不显示'
        print('frame.maintain.base.py {} 修改轮播：'.format(sys._getframe().f_lineno), item.carousel_id, show)


class CommodityInfo(QWidget):
    def __init__(self):
        super(CommodityInfo, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        add_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        add_btn.clicked.connect(self.add_new_commodity)
        self.show_table = QTableWidget()
        # mount widget to show request message
        self.message_btn = QPushButton('刷新中...', self.show_table)
        self.message_btn.resize(100, 20)
        self.message_btn.move(100, 100)
        self.message_btn.setStyleSheet('text-align:center;border:none;background-color:rgb(210,210,210)')
        # style
        self.show_table.verticalHeader().setVisible(False)
        action_layout.addWidget(add_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.show_table)
        self.setLayout(layout)
        # get all commodity
        self.get_all_commodity()

    def add_new_commodity(self):
        def upload_commodity(signal):
            print('frame.maintain.home.py {} 新现货：'.format(sys._getframe().f_lineno), signal)
            data = dict()
            data['machine_code'] = config.app_dawn.value('machine')
            data['commodity_list'] = signal
            try:
                response = requests.post(
                    url=config.SERVER_ADDR + "homepage/commodity/",
                    headers=config.CLIENT_HEADERS,
                    data=json.dumps(data),
                    cookies=config.app_dawn.value('cookies')
                )
            except Exception as error:
                QMessageBox.information(self, '提示', "发生了个错误!\n{}".format(error), QMessageBox.Yes)
                return
            response_data = json.loads(response.content.decode('utf-8'))
            if response.status_code != 201:
                QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
                return
            else:
                QMessageBox.information(self, '成功', '添加成功, 赶紧刷新看看吧.', QMessageBox.Yes)
                popup.close()  # close the dialog
        popup = CreateNewCommodity()
        popup.new_data_signal.connect(upload_commodity)
        if not popup.exec():
            del popup

    def get_all_commodity(self):
        self.message_btn.setText('刷新中...')
        self.message_btn.show()
        self.message_btn.setEnabled(False)
        self.show_table.clear()
        self.show_table.setRowCount(0)
        self.show_table.horizontalHeader().setVisible(False)
        self.cmomodity_thread = RequestThread(
            url=config.SERVER_ADDR + 'homepage/commodity/',
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"machine_code": config.app_dawn.value('machine'), "maintain": True}),
            cookies=config.app_dawn.value('cookies'),
        )
        self.cmomodity_thread.finished.connect(self.cmomodity_thread.deleteLater)
        self.cmomodity_thread.response_signal.connect(self.commodity_thread_back)
        self.cmomodity_thread.start()

    def commodity_thread_back(self, content):
        # fill show table
        print('frame.maintain.home.py {} 维护现货报表: '.format(str(sys._getframe().f_lineno)), content)
        if content['error']:
            self.message_btn.setText('失败,请重试!')
            self.message_btn.setEnabled(True)
            return
        else:
            if not content['data']:
                self.message_btn.setText('完成,无数据.')
                return  # function finished
            else:
                self.message_btn.setText('刷新完成!')
                self.message_btn.hide()
        # fill table
        self.show_table.horizontalHeader().setVisible(True)
        keys = [
            ('serial_num', '序号'),
            ('create_time', '创建时间'),
            ('variety', '品种'),
            ('area', '地区'),
            ('level', '等级'),
            ('price', '价格'),
            ('date', '日期'),
            ('note', '备注'),
            ('is_active', '显示')
        ]
        commodities = content['data']
        row = len(commodities)
        self.show_table.setRowCount(row)
        self.show_table.setColumnCount(len(keys))  # 列数
        labels = []
        set_keys = []
        for key_label in keys:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        self.show_table.setHorizontalHeaderLabels(labels)
        self.show_table.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
        self.show_table.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
        for row in range(self.show_table.rowCount()):
            for col in range(self.show_table.columnCount()):
                if col == 0:
                    item = QTableWidgetItem(str(row + 1))
                else:
                    label_key = set_keys[col]
                    if label_key == 'is_active':
                        checkbox = TableCheckBox(row=row, col=col, option_label=label_key)
                        checkbox.setChecked(int(commodities[row][label_key]))
                        checkbox.clicked_changed.connect(self.update_commodity_info)
                        self.show_table.setCellWidget(row, col, checkbox)
                    item = QTableWidgetItem(str(commodities[row][set_keys[col]]))
                item.setTextAlignment(Qt.AlignCenter)
                item.commodity_id = commodities[row]['id']
                self.show_table.setItem(row, col, item)

    def update_commodity_info(self, signal):
        item = self.show_table.item(signal['row'], signal['col'])
        show = '显示' if signal['checked'] else '不显示'
        print('frame.maintain.base.py {} 修改现货：'.format(sys._getframe().f_lineno), item.commodity_id, show)


class FinanceInfo(QWidget):
    def __init__(self):
        super(FinanceInfo, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        add_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        add_btn.clicked.connect(self.add_new_finance)
        self.show_table = QTableWidget()
        # mount widget to show request message
        self.message_btn = QPushButton('刷新中...', self.show_table)
        self.message_btn.resize(100, 20)
        self.message_btn.move(100, 100)
        self.message_btn.setStyleSheet('text-align:center;border:none;background-color:rgb(210,210,210)')
        # style
        self.show_table.verticalHeader().setVisible(False)
        action_layout.addWidget(add_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.show_table)
        self.setLayout(layout)
        # get all finance
        self.get_all_finance()

    def add_new_finance(self):
        def upload_finance(signal):
            print('frame.maintain.home.py {} 新财经：'.format(sys._getframe().f_lineno), signal)
            data = dict()
            data['machine_code'] = config.app_dawn.value('machine')
            data['finance_list'] = signal
            try:
                response = requests.post(
                    url=config.SERVER_ADDR + "homepage/finance/",
                    headers=config.CLIENT_HEADERS,
                    data=json.dumps(data),
                    cookies=config.app_dawn.value('cookies')
                )
            except Exception as error:
                QMessageBox.information(self, '提示', "发生了个错误!\n{}".format(error), QMessageBox.Yes)
                return
            response_data = json.loads(response.content.decode('utf-8'))
            if response.status_code != 201:
                QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
                return
            else:
                QMessageBox.information(self, '成功', '添加成功, 赶紧刷新看看吧.', QMessageBox.Yes)
                popup.close()  # close the dialog
        popup = CreateNewFinance()
        popup.new_data_signal.connect(upload_finance)
        if not popup.exec():
            del popup

    def get_all_finance(self):
        self.message_btn.setText('刷新中...')
        self.message_btn.show()
        self.message_btn.setEnabled(False)
        self.show_table.clear()
        self.show_table.setRowCount(0)
        self.show_table.horizontalHeader().setVisible(False)
        self.finance_thread = RequestThread(
            url=config.SERVER_ADDR + 'homepage/finance/',
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"machine_code": config.app_dawn.value('machine'), "maintain": True}),
            cookies=config.app_dawn.value('cookies'),
        )
        self.finance_thread.finished.connect(self.finance_thread.deleteLater)
        self.finance_thread.response_signal.connect(self.finance_thread_back)
        self.finance_thread.start()

    def finance_thread_back(self, content):
        # fill show table
        try:
            print('frame.maintain.home.py {} 维护财经日历: '.format(str(sys._getframe().f_lineno)), content)
            if content['error']:
                self.message_btn.setText('失败,请重试!')
                self.message_btn.setEnabled(True)
                return
            else:
                if not content['data']:
                    self.message_btn.setText('完成,无数据.')
                    return  # function finished
                else:
                    self.message_btn.setText('刷新完成!')
                    self.message_btn.hide()
            # fill table
            self.show_table.horizontalHeader().setVisible(True)
            keys = [
                ('serial_num', '序号'),
                ('create_time', '创建时间'),
                ('country', '地区'),
                ('event', '事件'),
                ('expected', '预期值'),
                ('date', '日期'),
                ('time', '时间'),
                ('is_active', '显示')
            ]
            finance = content['data']
            row = len(finance)
            self.show_table.setRowCount(row)
            self.show_table.setColumnCount(len(keys))  # 列数
            labels = []
            set_keys = []
            for key_label in keys:
                set_keys.append(key_label[0])
                labels.append(key_label[1])
            self.show_table.setHorizontalHeaderLabels(labels)
            self.show_table.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
            self.show_table.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
            for row in range(self.show_table.rowCount()):
                for col in range(self.show_table.columnCount()):
                    if col == 0:
                        item = QTableWidgetItem(str(row + 1))
                    else:
                        label_key = set_keys[col]
                        if label_key == 'is_active':
                            checkbox = TableCheckBox(row=row, col=col, option_label=label_key)
                            checkbox.setChecked(int(finance[row][label_key]))
                            checkbox.clicked_changed.connect(self.update_finance_info)
                            self.show_table.setCellWidget(row, col, checkbox)
                        item = QTableWidgetItem(str(finance[row][set_keys[col]]))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.finance_id = finance[row]['id']
                    self.show_table.setItem(row, col, item)
        except Exception as e:
            print(e)

    def update_finance_info(self, signal):
        item = self.show_table.item(signal['row'], signal['col'])
        show = '显示' if signal['checked'] else '不显示'
        print('frame.maintain.base.py {} 修改财经：'.format(sys._getframe().f_lineno), item.finance_id, show)


class NoticeMaintain(QWidget):
    def __init__(self):
        super(NoticeMaintain, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        # widgets
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        self.table = QTableWidget()
        # signal
        create_btn.clicked.connect(self.create_new_notice)
        # style
        self.table.verticalHeader().setVisible(False)
        # add layout
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)
        # initial data

    def create_new_notice(self):
        def upload_notice(signal):
            print('frame.maintain.home.py {} 新通知:'.format(str(sys._getframe().f_lineno)), signal)
            data = dict()
            data['machine_code'] = config.app_dawn.value('machine')
            data['type_en'] = signal['type_en']
            data['type_zh'] = signal['type_zh']
            data['title'] = signal['title']
            file_raw_name = signal["file_path"].rsplit("/", 1)
            file = open(signal["file_path"], "rb")
            file_content = file.read()
            file.close()
            data["file"] = (file_raw_name[1], file_content)
            encode_data = encode_multipart_formdata(data)
            data = encode_data[0]
            headers = config.CLIENT_HEADERS
            headers['Content-Type'] = encode_data[1]
            try:
                response = requests.post(
                    url=config.SERVER_ADDR + "homepage/notice/",
                    headers=headers,
                    data=data,
                    cookies=config.app_dawn.value('cookies')
                )
            except Exception as error:
                QMessageBox.information(self, '提示', "发生了个错误!\n{}".format(error), QMessageBox.Yes)
                return
            response_data = json.loads(response.content.decode('utf-8'))
            if response.status_code != 201:
                QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
                return
            else:
                QMessageBox.information(self, '成功', '添加成功, 赶紧刷新看看吧.', QMessageBox.Yes)
                popup.close()  # close the dialog
        popup = CreateNewNotice()
        popup.new_data_signal.connect(upload_notice)
        if not popup.exec():
            del popup


class ReportMaintain(QWidget):
    def __init__(self):
        super(ReportMaintain, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        # widgets
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        self.table = QTableWidget()
        # signal
        create_btn.clicked.connect(self.create_new_report)
        # style
        self.table.verticalHeader().setVisible(False)
        # add layout
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)
        # initial data

    def create_new_report(self):
        def upload_report(signal):
            print('frame.maintain.home.py {} 新报告:'.format(str(sys._getframe().f_lineno)), signal)
            data=dict()
            data['machine_code'] = config.app_dawn.value('machine')
            data['type_en'] = signal['type_en']
            data['type_zh'] = signal['type_zh']
            data['title'] = signal['title']
            file_raw_name = signal["file_path"].rsplit("/", 1)
            file = open(signal["file_path"], "rb")
            file_content = file.read()
            file.close()
            data["file"] = (file_raw_name[1], file_content)
            encode_data = encode_multipart_formdata(data)
            data = encode_data[0]
            headers = config.CLIENT_HEADERS
            headers['Content-Type'] = encode_data[1]
            try:
                response = requests.post(
                    url=config.SERVER_ADDR + "homepage/report/",
                    headers=headers,
                    data=data,
                    cookies=config.app_dawn.value('cookies')
                )
            except Exception as error:
                QMessageBox.information(self, '提示', "发生了个错误!\n{}".format(error), QMessageBox.Yes)
                return
            response_data = json.loads(response.content.decode('utf-8'))
            if response.status_code != 201:
                QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
                return
            else:
                QMessageBox.information(self, '成功', '添加成功, 赶紧刷新看看吧.', QMessageBox.Yes)
                popup.close()  # close the dialog
        popup = CreateNewReport()
        popup.new_data_signal.connect(upload_report)
        if not popup.exec():
            del popup
