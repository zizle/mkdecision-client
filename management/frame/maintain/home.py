# _*_ coding:utf-8 _*_
# Author: zizle QQ:462894999
import sys
import json
import requests
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QPoint

import config
from popup.maintain.home import NewHomeDataPopup


from popup.maintain import CreateNewBulletin, CreateNewCarousel, CreateNewReport, CreateNewNotice, CreateNewCommodity, CreateNewFinance
from piece.maintain import TableCheckBox
from thread.request import RequestThread

""" 常规报告相关 """


# 【常规报告管理删除按钮】
class DeleteButton(QPushButton):
    mouse_clicked = pyqtSignal(QPushButton)

    def __init__(self, did, *args, **kwargs):
        super(DeleteButton, self).__init__(*args, **kwargs)
        self.setText('删除')
        self.did = did  # did要删除的数据的id
        self.clicked.connect(lambda: self.mouse_clicked.emit(self))


# 【常规报告管理】
class NormalReportMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(NormalReportMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 选择条件
        option_layout = QHBoxLayout()
        option_layout.addWidget(QLabel('品种:', parent=self))
        self.variety_combo = QComboBox(parent=self)  # 品种选择
        self.variety_combo.currentTextChanged.connect(self.reports_show_changed)
        option_layout.addWidget(self.variety_combo)
        option_layout.addWidget(QLabel('报告类型:', parent=self))
        self.category_combo = QComboBox(parent=self)  # 类型选择
        self.category_combo.currentTextChanged.connect(self.reports_show_changed)
        option_layout.addWidget(self.category_combo)
        # 信息提示
        self.message_label = QLabel(parent=self)
        option_layout.addWidget(self.message_label)
        option_layout.addStretch()  # 伸缩
        # 管理表格
        self.maintain_table = QTableWidget(parent=self)
        self.maintain_table.verticalHeader().hide()
        layout.addLayout(option_layout)
        layout.addWidget(self.maintain_table)
        self.setLayout(layout)

    # 获取分类，获取品种
    def getGroupsVarieties(self):
        # 获取数据分类
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'home/groups-categories/?mc=' + config.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.message_label.setText(str(e))
        else:
            # 先加个【全部】选项
            self.category_combo.addItem('全部', 0)
            for group_item in response['data']:
                if group_item['name'] == u'常规报告':
                    for category_item in group_item['categories']:
                        self.category_combo.addItem(category_item['name'], category_item['id'])
        # 获取品种数据
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'basic/variety/?mc=' + config.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.message_label.setText(str(e))
        else:
            # 先加个【全部】选项
            self.variety_combo.addItem('全部', 0)
            for variety_item in response['data']:
                self.variety_combo.addItem(variety_item['name'], variety_item['id'])

    # 获取常规报告列表
    def getReports(self, category_id=0, variety_id=0):
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'home/normal-report/?mc=' + config.app_dawn.value('machine'),
                data=json.dumps({
                    'category': category_id,
                    'variety': variety_id
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.message_label.setText(str(e))
        else:
            # 表格展示数据
            self._show_reports(response['data'])

    # 类别、品种变化
    def reports_show_changed(self):
        variety = self.variety_combo.currentData()
        category = self.category_combo.currentData()
        variety = variety if variety else 0
        category = category if category else 0
        self.getReports(category_id=category, variety_id=variety)

    # 维护表格展示数据
    def _show_reports(self, report_list):
        self.maintain_table.clear()
        self.maintain_table.setRowCount(len(report_list))
        self.maintain_table.setColumnCount(6)
        self.maintain_table.setHorizontalHeaderLabels(['序号', '名称', '报告类型', '所属品种', '报告日期', ''])
        self.maintain_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.maintain_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.maintain_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        if report_list:
            self.maintain_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        for row, report_item in enumerate(report_list):
            item_0 = QTableWidgetItem(str(row + 1))
            item_0.setTextAlignment(Qt.AlignCenter)
            self.maintain_table.setItem(row, 0, item_0)
            # 名称
            item_1 = QTableWidgetItem(report_item['name'])
            item_1.setTextAlignment(Qt.AlignCenter)
            self.maintain_table.setItem(row, 1, item_1)
            # 报告类型
            item_2 = QTableWidgetItem(report_item['category'])
            item_2.setTextAlignment(Qt.AlignCenter)
            self.maintain_table.setItem(row, 2, item_2)
            # 所属品种
            item_3 = QTableWidgetItem(report_item['variety'])
            item_3.setTextAlignment(Qt.AlignCenter)
            self.maintain_table.setItem(row, 3, item_3)
            # 报告日期
            item_4 = QTableWidgetItem(report_item['date'])
            item_4.setTextAlignment(Qt.AlignCenter)
            self.maintain_table.setItem(row, 4, item_4)
            # 删除按钮
            item_5 = DeleteButton(did=report_item['id'])
            item_5.mouse_clicked.connect(self.report_deleted)
            self.maintain_table.setCellWidget(row, 5, item_5)

    # 删除某个报告
    def report_deleted(self, button):
        # 获取cellWidget所在的行
        table_index = self.maintain_table.indexAt(QPoint(button.frameGeometry().x(), button.frameGeometry().y()))
        row = table_index.row()  # 删除成功就删除此行
        try:
            r = requests.delete(
                url=config.SERVER_ADDR + 'home/normal-report/'+ str(button.did) + '/?mc=' + config.app_dawn.value('machine'),
                headers={
                    'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION'),
                },
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.message_label.setText(str(e))
        else:
            self.message_label.setText(response['message'])
            self.maintain_table.removeRow(row)


# 【交易通知管理】
class TransactionNoticeMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(TransactionNoticeMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 选择条件
        option_layout = QHBoxLayout()
        option_layout.addWidget(QLabel('类型:', parent=self))
        self.category_combo = QComboBox(parent=self)  # 类型
        option_layout.addWidget(self.category_combo)
        self.category_combo.currentTextChanged.connect(self.notices_show_changed)
        # 信息提示
        self.message_label = QLabel(parent=self)
        option_layout.addWidget(self.message_label)
        option_layout.addStretch()  # 伸缩
        # 管理表格
        self.maintain_table = QTableWidget(parent=self)
        self.maintain_table.verticalHeader().hide()
        layout.addLayout(option_layout)
        layout.addWidget(self.maintain_table)
        self.setLayout(layout)

    # 获取分类
    def getCategories(self):
        # 获取数据分类
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'home/groups-categories/?mc=' + config.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.message_label.setText(str(e))
        else:
            # 先加个【全部】选项
            self.category_combo.addItem('全部', 0)
            for group_item in response['data']:
                if group_item['name'] == u'交易通知':
                    for category_item in group_item['categories']:
                        self.category_combo.addItem(category_item['name'], category_item['id'])
            # 最后新增个【其他】选项
            self.category_combo.addItem('其他', -1)

    # 获取通知
    def getNotices(self, category_id):
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'home/transaction-notice/?mc=' + config.app_dawn.value('machine'),
                data=json.dumps({
                    'category': category_id,
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.message_label.setText(str(e))
        else:
            # 表格展示数据
            self._show_notices(response['data'])

    # 操作表格展示数据
    def _show_notices(self, notice_list):
        self.maintain_table.clear()
        self.maintain_table.setRowCount(len(notice_list))
        self.maintain_table.setColumnCount(5)
        self.maintain_table.setHorizontalHeaderLabels(['序号', '名称', '通知类型', '通知日期', ''])
        self.maintain_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.maintain_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.maintain_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        if notice_list:
            self.maintain_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        for row, notice_item in enumerate(notice_list):
            item_0 = QTableWidgetItem(str(row + 1))
            item_0.setTextAlignment(Qt.AlignCenter)
            self.maintain_table.setItem(row, 0, item_0)
            # 名称
            item_1 = QTableWidgetItem(notice_item['name'])
            item_1.setTextAlignment(Qt.AlignCenter)
            self.maintain_table.setItem(row, 1, item_1)
            # 通知类型
            category_text = notice_item['category'] if notice_item['category'] else '其他'
            item_2 = QTableWidgetItem(category_text)
            item_2.setTextAlignment(Qt.AlignCenter)
            self.maintain_table.setItem(row, 2, item_2)
            # 通知日期
            item_3 = QTableWidgetItem(notice_item['date'])
            item_3.setTextAlignment(Qt.AlignCenter)
            self.maintain_table.setItem(row, 3, item_3)
            # 删除按钮
            item_4 = DeleteButton(did=notice_item['id'])
            item_4.mouse_clicked.connect(self.notice_deleted)
            self.maintain_table.setCellWidget(row, 4, item_4)

    # 删除某个通知
    def notice_deleted(self, button):
        # 获取cellWidget所在的行
        table_index = self.maintain_table.indexAt(QPoint(button.frameGeometry().x(), button.frameGeometry().y()))
        row = table_index.row()  # 删除成功就删除此行
        try:
            r = requests.delete(
                url=config.SERVER_ADDR + 'home/transaction-notice/' + str(button.did) + '/?mc=' + config.app_dawn.value(
                    'machine'),
                headers={
                    'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION'),
                },
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.message_label.setText(str(e))
            print('删除id为%d通知-所在行%d' % (button.did, row))
        else:
            self.message_label.setText(response['message'])
            self.maintain_table.removeRow(row)

    # 类别变化
    def notices_show_changed(self):
        category = self.category_combo.currentData()
        category = category if category else 0
        self.getNotices(category_id=category)


# 首页数据管理维护
class HomepageMaintain(QWidget):
    network_result = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(HomepageMaintain, self).__init__(*args, **kwargs)
        # 新增数据按钮
        self.create_button = QPushButton('新增数据', clicked=self.upload_new_data)
        layout = QHBoxLayout(margin=0)
        # 左侧操作的功能列表
        self.left_group_list = QListWidget()
        self.left_group_list.clicked.connect(self.left_list_clicked)
        # 右侧上下布局
        rlayout = QVBoxLayout()
        # 右侧下方tab
        self.tab_show = QTabWidget()
        self.tab_show.tabBar().hide()
        self.tab_show.setDocumentMode(True)
        layout.addWidget(self.left_group_list, alignment=Qt.AlignLeft)
        rlayout.addWidget(self.tab_show)
        layout.addLayout(rlayout)

        # layout = QVBoxLayout(margin=0)
        # # 上端显示操作结果与新增布局
        # option_layout = QHBoxLayout(margin=0)
        # self.network_message_label = QLabel(parent=self)
        # self.create_new_button = QPushButton('新增数据', parent=self, clicked=self.upload_new_data)
        # option_layout.addWidget(self.network_message_label)
        # option_layout.addWidget(self.create_new_button, alignment=Qt.AlignRight)
        # # 中间横向布局
        # show_layout = QHBoxLayout(margin=0)
        # self.left_group_list = QListWidget()
        # self.left_group_list.clicked.connect(self.left_list_clicked)
        # self.tab_show = QTabWidget()
        # self.tab_show.tabBar().hide()
        # self.tab_show.setDocumentMode(True)
        # show_layout.addWidget(self.left_group_list, alignment=Qt.AlignLeft)
        # show_layout.addWidget(self.tab_show)
        # layout.addLayout(option_layout)
        # layout.addLayout(show_layout)
        self.setLayout(layout)
        self.get_groups()  # 初始化

    # 获取左侧分类数据(只要组不要内部分类)
    def get_groups(self):
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'home/data-groups/?mc=' + config.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
            return
        else:
            self.left_group_list.clear()
            # 填充分组列表
            for group_item in response['data']:
                item = QListWidgetItem(group_item['name'])
                item.gid = group_item['id']
                self.left_group_list.addItem(item)

    # 踢皮球，显示网络请求的结果
    def show_network_message(self, message):
        if message == 'hasNewGroup':  # 新增了分组
            self.get_groups()
        else:
            self.network_result.emit(message)

    # 新增上传数据
    def upload_new_data(self):
        popup = NewHomeDataPopup(parent=self)
        popup.network_result.connect(self.show_network_message)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 点击左侧列表
    def left_list_clicked(self):
        current_item = self.left_group_list.currentItem()
        if current_item.text() == u'常规报告':
            maintain_tab = NormalReportMaintain()
            maintain_tab.getGroupsVarieties()
        elif current_item.text() == u'交易通知':
            maintain_tab = TransactionNoticeMaintain()
            maintain_tab.getCategories()

        else:
            maintain_tab = QLabel('【'+current_item.text()+'】还不能进行数据管理', alignment=Qt.AlignCenter)
        self.tab_show.clear()
        self.tab_show.addTab(maintain_tab, '')












class BulletinMaintain(QWidget):
    # 维护【公告栏】数据
    def __init__(self, *args, **kwargs):
        super(BulletinMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        # widgets
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        self.table = QTableWidget()
        # signal
        create_btn.clicked.connect(self.create_new_bulletin)
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

    def create_new_bulletin(self):
        # dialog widget for edit bulletin information
        def update_bulletin(signal):
            # create new bulletin or update a bulletin in server
            print('frame.maintain.home.py {} 公告信号:": '.format(str(sys._getframe().f_lineno)), signal)
            headers = config.CLIENT_HEADERS
            data = dict()
            data["title"] = signal["name"]
            data["show_type"] = signal["show_type"]
            data['machine_code'] = config.app_dawn.value('machine')
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
        popup = CreateNewBulletin()
        popup.new_data_signal.connect(update_bulletin)
        if not popup.exec():
            del popup


class CarouselMaintain(QWidget):
    # 维护【轮播广告】数据
    def __init__(self, *args, **kwargs):
        super(CarouselMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        # widgets
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        self.table = QTableWidget()
        # signal
        create_btn.clicked.connect(self.create_new_carousel)
        # style
        self.table.verticalHeader().setVisible(False)
        # add to layout
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

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


class CommodityMaintain(QWidget):
    # 维护【现货报表】数据
    def __init__(self, *args, **kwargs):
        super(CommodityMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        # widgets
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        self.table = QTableWidget()
        # signal
        create_btn.clicked.connect(self.create_new_commodity)
        # style
        self.table.verticalHeader().setVisible(False)
        # add to layout
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def create_new_commodity(self):
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


class FinanceMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(FinanceMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        # widgets
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        self.table = QTableWidget()
        # signal
        create_btn.clicked.connect(self.create_new_finance)
        # style
        self.table.verticalHeader().setVisible(False)
        # add to layout
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def create_new_finance(self):
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



class NoticeMaintain(QWidget):
    # 维护【交易通知】数据
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
    # 维护【常规报告】数据
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
