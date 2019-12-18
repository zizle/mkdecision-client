# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout,QGridLayout, QListWidget, QLabel, QDialog, QComboBox, \
    QTextEdit, QPushButton, QHeaderView, QTableWidget, QAbstractItemView, QTableWidgetItem
from PyQt5.Qt import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPixmap, QImage
from widgets.base import LoadedPage, PDFContentPopup, TextContentPopup
from popup.collectorPages import CreateNewsPopup, CreateAdvertisementPopup, CreateReportPopup, CreateTransactionNoticePopup
import settings
from widgets.base import TableRowDeleteButton, TableRowReadButton
from popup.tips import WarningPopup

""" 【首页】数据管理相关 """

""" 新闻公告 """


# 新闻公告显示的表格
class NewsBulletinTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('title', '标题'),
        ('create_time', '创建时间'),
        ('creator', '创建者'),
    ]

    def __init__(self, *args, **kwargs):
        super(NewsBulletinTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    # 显示数据
    def showRowContens(self, news_list):
        self.clear()
        self.setRowCount(len(news_list))
        self.setColumnCount(len(self.KEY_LABELS) + 2)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + ['', ''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        for row, news_item in enumerate(news_list):
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = news_item[header[0]]
                else:
                    table_item = QTableWidgetItem(str(news_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
                # 添加阅读按钮
                if col == len(self.KEY_LABELS) - 1:
                    read_button = TableRowReadButton('阅读')
                    read_button.button_clicked.connect(self.read_button_clicked)
                    self.setCellWidget(row, col + 1, read_button)
                # 增加【删除】按钮
                if col == len(self.KEY_LABELS) - 1:
                    delete_button = TableRowDeleteButton('删除')
                    delete_button.button_clicked.connect(self.delete_button_clicked)
                    self.setCellWidget(row, col + 2, delete_button)

    # 删除一条公告
    def delete_button_clicked(self, delete_button):
        def delete_row_news():
            current_row, _ = self.get_widget_index(delete_button)
            news_id = self.item(current_row, 0).id
            # 发起删除公告请求
            try:
                r = requests.delete(
                    url=settings.SERVER_ADDR + 'home/news/' + str(news_id) + '/?mc=' + settings.app_dawn.value('machine'),
                    headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')}
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 200:
                    raise ValueError(response['message'])
            except Exception as e:
                self.network_result.emit(str(e))
            else:
                self.network_result.emit(response['message'])
            popup.close()
            # 移除本行
            self.removeRow(current_row)

        # 警示框
        popup = WarningPopup(parent=self)
        popup.confirm_button.connect(delete_row_news)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 阅读一条公告
    def read_button_clicked(self, read_button):
        current_row, _ = self.get_widget_index(read_button)
        news_id = self.item(current_row, 0).id
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/news/' + str(news_id) + '/',
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            # 根据具体情况显示内容
            news_data = response['data']
            if news_data['file']:
                # 显示文件
                file = settings.STATIC_PREFIX + news_data['file']
                popup = PDFContentPopup(title=news_data['title'], file=file, parent=self)
            else:
                popup = TextContentPopup(title=news_data['title'], content=news_data['content'], parent=self)  # 显示内容
            if not popup.exec_():
                popup.deleteLater()
                del popup

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 新闻公告页面
class NewsBulletinPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(NewsBulletinPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0, spacing=2)
        # 信息展示与新增按钮
        message_button_layout = QHBoxLayout()
        self.network_message_label = QLabel()
        message_button_layout.addWidget(self.network_message_label)
        message_button_layout.addWidget(QPushButton('新增', clicked=self.create_news), alignment=Qt.AlignRight)
        layout.addLayout(message_button_layout)
        # 当前数据显示表格
        self.news_table = NewsBulletinTable()
        self.news_table.network_result.connect(self.network_message_label.setText)
        layout.addWidget(self.news_table)
        self.setLayout(layout)

    # 获取所有的新闻公告内容
    def getNewsBulletins(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/news/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.news_table.showRowContens(response['data'])
            self.network_message_label.setText(response['message'])

    # 新增新闻
    def create_news(self):
        popup = CreateNewsPopup(parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup


""" 广告设置 """


# 查看图片按钮
class TableImageReadButton(QPushButton):
    button_clicked = pyqtSignal(QPushButton)

    def __init__(self, *args, **kwargs):
        super(TableImageReadButton, self).__init__(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(lambda: self.button_clicked.emit(self))
        self.setObjectName('tableDelete')
        self.setStyleSheet("""
        #tableDelete{
            border: none;
            padding: 1px 8px;
            color: rgb(100,150,180);
        }
        #tableDelete:hover{
            color: rgb(120,130,230)
        }
        """)


# 广告展示表格
class AdvertisementTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '标题'),
        ('create_time', '创建时间'),
        ('creator', '创建者'),
    ]

    def __init__(self, *args, **kwargs):
        super(AdvertisementTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContens(self, advertisement_list):
        self.clear()
        self.setRowCount(len(advertisement_list))
        self.setColumnCount(len(self.KEY_LABELS) + 3)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + ['', '', ''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        for row, advertise_item in enumerate(advertisement_list):
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = advertise_item[header[0]]
                else:
                    table_item = QTableWidgetItem(str(advertise_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
                if col == len(self.KEY_LABELS) - 1:
                    # 添加查看图片按钮
                    read_image = TableImageReadButton('查看图片')
                    read_image.image = advertise_item['image']
                    read_image.button_clicked.connect(self.read_image_clicked)
                    self.setCellWidget(row, col + 1, read_image)
                    # 添加查看内容按钮
                    read_button = TableRowReadButton('查看内容')
                    read_button.button_clicked.connect(self.read_button_clicked)
                    self.setCellWidget(row, col + 2, read_button)
                    # 增加【删除】按钮
                    delete_button = TableRowDeleteButton('删除')
                    delete_button.button_clicked.connect(self.delete_button_clicked)
                    self.setCellWidget(row, col + 3, delete_button)

    # 查看图片
    def read_image_clicked(self, image_button):
        image_url = image_button.image
        popup = QDialog(parent=self)
        popup.setWindowTitle('广告的图片')
        layout = QVBoxLayout(margin=0)
        image_label = QLabel()
        r = requests.get(url=settings.STATIC_PREFIX + image_url)
        img = QImage.fromData(r.content)
        image_label.setPixmap(QPixmap.fromImage(img))
        image_label.setScaledContents(True)
        layout.addWidget(image_label)
        popup.setLayout(layout)
        self.network_result.emit('获取图片成功!')
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 查看内容
    def read_button_clicked(self, read_button):
        current_row, _ = self.get_widget_index(read_button)
        ad_id = self.item(current_row, 0).id
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/advertise/' + str(ad_id) + '/',
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            # 根据具体情况显示内容
            ad_data = response['data']
            self.network_result.emit(response['message'])
            if ad_data['file']:
                # 显示文件
                file = settings.STATIC_PREFIX + ad_data['file']
                popup = PDFContentPopup(title=ad_data['name'], file=file, parent=self)
            else:
                popup = TextContentPopup(title=ad_data['name'], content=ad_data['content'], parent=self)  # 显示内容
            if not popup.exec_():
                popup.deleteLater()
                del popup

    # 删除本条广告
    def delete_button_clicked(self, delete_button):
        def delete_row_advertisement():
            current_row, _ = self.get_widget_index(delete_button)
            ad_id = self.item(current_row, 0).id
            # 发起删除公告请求
            try:
                r = requests.delete(
                    url=settings.SERVER_ADDR + 'home/advertise/' + str(ad_id) + '/?mc=' + settings.app_dawn.value(
                        'machine'),
                    headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')}
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 200:
                    raise ValueError(response['message'])
            except Exception as e:
                self.network_result.emit(str(e))
            else:
                self.network_result.emit(response['message'])
                popup.close()
                # 移除本行
                self.removeRow(current_row)
        # 警示框
        popup = WarningPopup(parent=self)
        popup.confirm_button.connect(delete_row_advertisement)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 广告设置
class AdvertisementPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(AdvertisementPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0, spacing=2)
        # 信息展示与新增按钮
        message_button_layout = QHBoxLayout()
        self.network_message_label = QLabel()
        message_button_layout.addWidget(self.network_message_label)
        message_button_layout.addWidget(QPushButton('新增', clicked=self.create_advertisement), alignment=Qt.AlignRight)
        layout.addLayout(message_button_layout)
        # 当前数据显示表格
        self.advertisement_table = AdvertisementTable()
        self.advertisement_table.network_result.connect(self.network_message_label.setText)
        layout.addWidget(self.advertisement_table)
        self.setLayout(layout)

    # 新增广告
    def create_advertisement(self):
        popup = CreateAdvertisementPopup(parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 获取广告数据
    def getAdvertisements(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/advertise/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.advertisement_table.showRowContens(response['data'])
            self.network_message_label.setText(response['message'])


""" 常规报告 """


# 常规报告表格
class ReportTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '报告名'),
        ('category', '报告类型'),
        ('date', '报告日期'),
        ('varieties', '关联品种'),
        ('uploader', '上传者'),
    ]

    def __init__(self, *args, **kwargs):
        super(ReportTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS) + 2)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + ['', ''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(len(self.KEY_LABELS), QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(len(self.KEY_LABELS) + 1, QHeaderView.ResizeToContents)
        for row, content_item in enumerate(row_list):
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = content_item[header[0]]
                    table_item.file = content_item['file']
                else:
                    table_item = QTableWidgetItem(str(content_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
                if col == len(self.KEY_LABELS) - 1:
                    # 添加阅读按钮
                    if col == len(self.KEY_LABELS) - 1:
                        read_button = TableRowReadButton('阅读')
                        read_button.button_clicked.connect(self.read_button_clicked)
                        self.setCellWidget(row, col + 1, read_button)
                    # 增加【删除】按钮
                    delete_button = TableRowDeleteButton('删除')
                    delete_button.button_clicked.connect(self.delete_button_clicked)
                    self.setCellWidget(row, col + 2, delete_button)

    # 删除一个报告
    def delete_button_clicked(self, delete_button):
        def delete_row_report():
            current_row, _ = self.get_widget_index(delete_button)
            report_id = self.item(current_row, 0).id
            # 发起删除报告请求
            try:
                r = requests.delete(
                    url=settings.SERVER_ADDR + 'home/normal-report/' + str(report_id) + '/?mc=' + settings.app_dawn.value('machine'),
                    headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')}
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 200:
                    raise ValueError(response['message'])
            except Exception as e:
                self.network_result.emit(str(e))
            else:
                self.network_result.emit(response['message'])
            popup.close()
            # 移除本行
            self.removeRow(current_row)
        # 警示框
        popup = WarningPopup(parent=self)
        popup.confirm_button.connect(delete_row_report)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 阅读一个报告
    def read_button_clicked(self, read_button):
        current_row, _ = self.get_widget_index(read_button)
        report_file = self.item(current_row, 0).file
        # 显示文件
        file = settings.STATIC_PREFIX + report_file
        popup = PDFContentPopup(title='阅读报告', file=file, parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 常规报告
class NormalReportPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(NormalReportPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0, spacing=2)
        # 分类选择、信息展示与新增按钮
        message_button_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        message_button_layout.addWidget(QLabel('类别:'))
        message_button_layout.addWidget(self.category_combo)
        message_button_layout.addWidget(QLabel('品种:'))
        self.variety_combo = QComboBox(activated=self.getCurrentReports)
        message_button_layout.addWidget(self.variety_combo)
        self.network_message_label = QLabel()
        message_button_layout.addWidget(self.network_message_label)
        message_button_layout.addStretch()  # 伸缩
        message_button_layout.addWidget(QPushButton('新增', clicked=self.create_report), alignment=Qt.AlignRight)
        layout.addLayout(message_button_layout)
        # 当前数据显示表格
        self.report_table = ReportTable()
        # self.report_table.network_result.connect(self.network_message_label.setText)
        layout.addWidget(self.report_table)
        self.setLayout(layout)

    # 获取分类选框内容
    def getCategoryCombo(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/data-category/normal_report/?mc=' + settings.app_dawn.value(
                    'machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.category_combo.clear()
            # 加入全部
            self.category_combo.addItem('全部', 0)
            for category_item in response['data']:
                self.category_combo.addItem(category_item['name'], category_item['id'])
            # 加入其它
            self.category_combo.addItem('其它', -1)

    # 获取品种选框内容
    def getVarietyCombo(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'group-varieties/?mc=' + settings.app_dawn.value(
                    'machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.variety_combo.clear()
            # 加入全部
            self.variety_combo.addItem('全部', 0)
            for variety_group in response['data']:
                for variety_item in variety_group['varieties']:
                    self.variety_combo.addItem(variety_item['name'], variety_item['id'])

    # 获取当前分类的报告
    def getCurrentReports(self):
        current_category_id = self.category_combo.currentData()
        current_variety_id = self.variety_combo.currentData()
        try:
            # 发起上传请求
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/normal-report/?mc=' + settings.app_dawn.value('machine'),
                data=json.dumps({'category': current_category_id, 'variety': current_variety_id})
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.report_table.showRowContents(response['data'])
            self.network_message_label.setText(response['message'])

    # 新增报告
    def create_report(self):
        popup = CreateReportPopup(parent=self)
        popup.geTreeVarieties()
        popup.getCategoryCombo()
        if not popup.exec_():
            popup.deleteLater()
            del popup


""" 交易通知 """


# 交易通知表格
class TransactionNoticeTable(QTableWidget):
    pass

# 交易通知管理页面
class TransactionNoticePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(TransactionNoticePage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0, spacing=2)
        # 分类选择、信息展示与新增按钮
        message_button_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        message_button_layout.addWidget(QLabel('类别:'))
        message_button_layout.addWidget(self.category_combo)
        self.network_message_label = QLabel()
        message_button_layout.addWidget(self.network_message_label)
        message_button_layout.addStretch()  # 伸缩
        message_button_layout.addWidget(QPushButton('新增', clicked=self.create_transaction_notice), alignment=Qt.AlignRight)
        layout.addLayout(message_button_layout)
        # 当前数据显示表格
        self.notice_table = TransactionNoticeTable()
        # self.report_table.network_result.connect(self.network_message_label.setText)
        layout.addWidget(self.notice_table)
        self.setLayout(layout)


    # 新建交易通知
    def create_transaction_notice(self):
        popup = CreateTransactionNoticePopup(parent=self)
        popup.getCategoryList()
        if not popup.exec_():
            popup.deleteLater()
            del popup


""" 首页管理主页 """


# 首页管理主页
class HomePageCollector(QWidget):
    network_result = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(HomePageCollector, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0)
        # 左侧菜单列表
        self.left_list = QListWidget(parent=self, clicked=self.left_menu_clicked)
        layout.addWidget(self.left_list, alignment=Qt.AlignLeft)
        # 右侧显示具体操作窗体
        self.operate_frame = LoadedPage()
        layout.addWidget(self.operate_frame)
        self.setLayout(layout)
        self._addListMenu()

    # 添加菜单按钮
    def _addListMenu(self):
        for item in [u'新闻公告', u'广告设置', u'常规报告', u'交易通知', u'现货报表', u'财经日历']:
            self.left_list.addItem(item)

    # 点击左侧按钮
    def left_menu_clicked(self):
        text = self.left_list.currentItem().text()
        try:
            if text == u'新闻公告':
                frame_page = NewsBulletinPage(parent=self.operate_frame)
                frame_page.getNewsBulletins()
            elif text == u'广告设置':
                frame_page = AdvertisementPage(parent=self.operate_frame)
                frame_page.getAdvertisements()
            elif text == u'常规报告':
                frame_page = NormalReportPage(parent=self.operate_frame)
                frame_page.getCategoryCombo()
                frame_page.getVarietyCombo()
            elif text == u'交易通知':
                frame_page = TransactionNoticePage(parent=self.operate_frame)
            else:
                frame_page = QLabel('【' + text + '】正在加紧开发中...')
            self.operate_frame.clear()
            self.operate_frame.addWidget(frame_page)
        except Exception as e:
            print(e)
