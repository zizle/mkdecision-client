# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QTableWidget, QTextBrowser, \
    QAbstractItemView, QHeaderView, QTableWidgetItem
from widgets.base import ScrollFoldedBox, LoadedPage, Paginator, TableRowReadButton, PDFContentPopup, PDFContentShower
from PyQt5.QtCore import Qt, QDate, QTime, pyqtSignal, QPoint
import settings


""" 策略服务-套保方案相关 """


# 套保方案显示表格
class HedgePlanTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '文件名称'),
        ('update_time', '日期'),
    ]

    def __init__(self, *args, **kwargs):
        super(HedgePlanTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS) + 1)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + [''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
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
                # if col in self.COLUMNS_CHECKED:  # 复选框按钮
                #     check_button = TableCheckBox(checked=content_item[header[0]])
                #     check_button.check_activated.connect(self.checked_button_changed)
                #     self.setCellWidget(row, col, check_button)
                if col == len(self.KEY_LABELS) - 1:
                    # 增加【查看】按钮
                    read_button = TableRowReadButton('阅读')
                    read_button.button_clicked.connect(self.read_button_clicked)
                    self.setCellWidget(row, col + 1, read_button)
                    # # 增加【删除】按钮
                    # delete_button = TableRowDeleteButton('删除')
                    # delete_button.button_clicked.connect(self.delete_button_clicked)
                    # self.setCellWidget(row, col + 2, delete_button)

    # 查看一个专题研究
    def read_button_clicked(self, read_button):
        current_row, _ = self.get_widget_index(read_button)
        file = self.item(current_row, 0).file
        # 显示文件
        file = settings.STATIC_PREFIX + file
        popup = PDFContentPopup(title='阅读文件', file=file, parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 套保方案主页
class HedgePlanPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(HedgePlanPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 页码控制布局
        self.paginator = Paginator()
        self.paginator.setMargins(0, 10, 3, 0)
        self.paginator.clicked.connect(self.getCurrentPlanContents)
        layout.addWidget(self.paginator, alignment=Qt.AlignRight)
        self.table = InvestPlanTable()
        layout.addWidget(self.table)
        self.setLayout(layout)

    # 请求数据
    def getCurrentPlanContents(self):
        current_page = self.paginator.current_page
        try:
            url = settings.SERVER_ADDR + 'info/hedge-plan/?page='+str(current_page)+'&mc=' + settings.app_dawn.value('machine')
            r = requests.get(url=url)
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.paginator.setTotalPages(response['data']['total_page'])
            self.table.showRowContents(response['data']['contacts'])


""" 策略服务-投资方案相关 """


# 投资方案显示表格
class InvestPlanTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '文件名称'),
        ('update_time', '日期'),
    ]

    def __init__(self, *args, **kwargs):
        super(InvestPlanTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS) + 1)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + [''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
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
                # if col in self.COLUMNS_CHECKED:  # 复选框按钮
                #     check_button = TableCheckBox(checked=content_item[header[0]])
                #     check_button.check_activated.connect(self.checked_button_changed)
                #     self.setCellWidget(row, col, check_button)
                if col == len(self.KEY_LABELS) - 1:
                    # 增加【查看】按钮
                    read_button = TableRowReadButton('阅读')
                    read_button.button_clicked.connect(self.read_button_clicked)
                    self.setCellWidget(row, col + 1, read_button)
                    # # 增加【删除】按钮
                    # delete_button = TableRowDeleteButton('删除')
                    # delete_button.button_clicked.connect(self.delete_button_clicked)
                    # self.setCellWidget(row, col + 2, delete_button)

    # 查看一个专题研究
    def read_button_clicked(self, read_button):
        current_row, _ = self.get_widget_index(read_button)
        file = self.item(current_row, 0).file
        # 显示文件
        file = settings.STATIC_PREFIX + file
        popup = PDFContentPopup(title='阅读文件', file=file, parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 投资方案主页
class InvestPlanPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(InvestPlanPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 页码控制布局
        self.paginator = Paginator()
        self.paginator.setMargins(0, 10, 3, 0)
        self.paginator.clicked.connect(self.getCurrentPlanContents)
        layout.addWidget(self.paginator, alignment=Qt.AlignRight)
        self.table = InvestPlanTable()
        layout.addWidget(self.table)
        self.setLayout(layout)

    # 请求数据
    def getCurrentPlanContents(self):
        current_page = self.paginator.current_page
        try:
            url = settings.SERVER_ADDR + 'info/invest-plan/?page='+str(current_page)+'&mc=' + settings.app_dawn.value('machine')
            r = requests.get(url=url)
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.paginator.setTotalPages(response['data']['total_page'])
            self.table.showRowContents(response['data']['contacts'])



""" 策略服务-交易策略相关 """


# 交易策略控件
class TradePolicyWidget(QWidget):
    def __init__(self, policy_data, *args, **kwargs):
        super(TradePolicyWidget, self).__init__(*args, **kwargs)
        self.sms_id = policy_data['id']
        layout = QVBoxLayout(margin=0, spacing=1)
        date = QDate.fromString(policy_data['date'], 'yyyy-MM-dd')
        time = QTime.fromString(policy_data['time'], 'HH:mm:ss')
        date_time = date.toString('yyyy-MM-dd ') + time.toString('HH:mm') if date != QDate.currentDate() else time.toString('HH:mm')
        layout.addWidget(QLabel(date_time, objectName='timeLabel'))
        self.text_browser = QTextBrowser(objectName='textBrowser')
        self.text_browser.setText(policy_data['content'])
        layout.addWidget(self.text_browser)
        self.setLayout(layout)
        self.setStyleSheet("""
        #timeLabel{
            font-size:12px;
            color: rgb(50,70,100);
            font-weight: bold;
        }
        #textBrowser{
            margin:0 0 2px 25px;
            border:1px solid rgb(210,210,210);
            font-size:13px;
            color: rgb(0,0,0);
            border-radius: 5px;
            background-color:rgb(225,225,225)
        }
        """)


# 交易策略主页
class TradePolicyPage(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(TradePolicyPage, self).__init__(*args, **kwargs)
        self.container = QWidget()
        layout = QVBoxLayout()
        self.container.setLayout(layout)
        self.setWidget(self.container)
        self.setWidgetResizable(True)

    # 请求数据
    def getTradePolicyContents(self):
        try:
            r = requests.get(url=settings.SERVER_ADDR + 'info/trade-policy/?mc=' + settings.app_dawn.value('machine'))
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError('获取数据失败.')
        except Exception:
            return
        else:
            for policy_item in response['data']:
                self.container.layout().addWidget(TradePolicyWidget(policy_item))


""" 调研报告相关 """


# 调研报告显示表格
class SearchReportTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '文件名称'),
        ('update_time', '日期'),
    ]

    def __init__(self, *args, **kwargs):
        super(SearchReportTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS) + 1)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + [''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
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
                # if col in self.COLUMNS_CHECKED:  # 复选框按钮
                #     check_button = TableCheckBox(checked=content_item[header[0]])
                #     check_button.check_activated.connect(self.checked_button_changed)
                #     self.setCellWidget(row, col, check_button)
                if col == len(self.KEY_LABELS) - 1:
                    # 增加【查看】按钮
                    read_button = TableRowReadButton('阅读')
                    read_button.button_clicked.connect(self.read_button_clicked)
                    self.setCellWidget(row, col + 1, read_button)
                    # # 增加【删除】按钮
                    # delete_button = TableRowDeleteButton('删除')
                    # delete_button.button_clicked.connect(self.delete_button_clicked)
                    # self.setCellWidget(row, col + 2, delete_button)

    # 查看一个调研报告
    def read_button_clicked(self, read_button):
        current_row, _ = self.get_widget_index(read_button)
        file = self.item(current_row, 0).file
        # 显示文件
        file = settings.STATIC_PREFIX + file
        popup = PDFContentPopup(title='阅读文件', file=file, parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 调研报告主页
class SearchReportPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(SearchReportPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 页码控制布局
        self.paginator = Paginator()
        self.paginator.setMargins(0, 10, 3, 0)
        self.paginator.clicked.connect(self.getCurrentReportContents)
        layout.addWidget(self.paginator, alignment=Qt.AlignRight)
        self.table = TopicSearchTable()
        layout.addWidget(self.table)
        self.setLayout(layout)

    # 请求数据
    def getCurrentReportContents(self):
        current_page = self.paginator.current_page
        try:
            url = settings.SERVER_ADDR + 'info/search-report/?page='+str(current_page)+'&mc=' + settings.app_dawn.value('machine')
            r = requests.get(url=url)
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.paginator.setTotalPages(response['data']['total_page'])
            self.table.showRowContents(response['data']['contacts'])


""" 专题研究 """


# 专题研究显示表格
class TopicSearchTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '文件名称'),
        ('update_time', '日期'),
    ]

    def __init__(self, *args, **kwargs):
        super(TopicSearchTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS) + 1)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + [''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
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
                # if col in self.COLUMNS_CHECKED:  # 复选框按钮
                #     check_button = TableCheckBox(checked=content_item[header[0]])
                #     check_button.check_activated.connect(self.checked_button_changed)
                #     self.setCellWidget(row, col, check_button)
                if col == len(self.KEY_LABELS) - 1:
                    # 增加【查看】按钮
                    read_button = TableRowReadButton('阅读')
                    read_button.button_clicked.connect(self.read_button_clicked)
                    self.setCellWidget(row, col + 1, read_button)
                    # # 增加【删除】按钮
                    # delete_button = TableRowDeleteButton('删除')
                    # delete_button.button_clicked.connect(self.delete_button_clicked)
                    # self.setCellWidget(row, col + 2, delete_button)

    # 查看一个专题研究
    def read_button_clicked(self, read_button):
        current_row, _ = self.get_widget_index(read_button)
        file = self.item(current_row, 0).file
        # 显示文件
        file = settings.STATIC_PREFIX + file
        popup = PDFContentPopup(title='阅读文件', file=file, parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 专题研究主页
class TopicSearchPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(TopicSearchPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 页码控制布局
        self.paginator = Paginator()
        self.paginator.setMargins(0, 10, 3, 0)
        self.paginator.clicked.connect(self.getCurrentTopicContents)
        layout.addWidget(self.paginator, alignment=Qt.AlignRight)
        self.table = TopicSearchTable()
        layout.addWidget(self.table)
        self.setLayout(layout)

    # 请求数据
    def getCurrentTopicContents(self):
        current_page = self.paginator.current_page
        try:
            url = settings.SERVER_ADDR + 'info/topic-search/?page='+str(current_page)+'&mc=' + settings.app_dawn.value('machine')
            r = requests.get(url=url)
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.paginator.setTotalPages(response['data']['total_page'])
            self.table.showRowContents(response['data']['contacts'])


""" 市场分析 """


# 市场分析显示表格
class MarketAnalysisTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '文件名称'),
        ('update_time', '日期'),
    ]

    def __init__(self, *args, **kwargs):
        super(MarketAnalysisTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS) + 1)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + [''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
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
                # if col in self.COLUMNS_CHECKED:  # 复选框按钮
                #     check_button = TableCheckBox(checked=content_item[header[0]])
                #     check_button.check_activated.connect(self.checked_button_changed)
                #     self.setCellWidget(row, col, check_button)
                if col == len(self.KEY_LABELS) - 1:
                    # 增加【查看】按钮
                    read_button = TableRowReadButton('阅读')
                    read_button.button_clicked.connect(self.read_button_clicked)
                    self.setCellWidget(row, col + 1, read_button)
                    # # 增加【删除】按钮
                    # delete_button = TableRowDeleteButton('删除')
                    # delete_button.button_clicked.connect(self.delete_button_clicked)
                    # self.setCellWidget(row, col + 2, delete_button)

    # 查看一个市场分析
    def read_button_clicked(self, read_button):
        current_row, _ = self.get_widget_index(read_button)
        file = self.item(current_row, 0).file
        # 显示文件
        file = settings.STATIC_PREFIX + file
        popup = PDFContentPopup(title='阅读文件', file=file, parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 市场分析主页
class MarketAnalysisPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(MarketAnalysisPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 页码控制布局
        self.paginator = Paginator()
        self.paginator.setMargins(0, 10, 3, 0)
        self.paginator.clicked.connect(self.getCurrentMarketContents)
        layout.addWidget(self.paginator, alignment=Qt.AlignRight)
        self.table = MarketAnalysisTable()
        layout.addWidget(self.table)
        self.setLayout(layout)

    # 请求数据
    def getCurrentMarketContents(self):
        current_page = self.paginator.current_page
        try:
            url = settings.SERVER_ADDR + 'info/market-analysis/?page='+str(current_page)+'&mc=' + settings.app_dawn.value('machine')
            r = requests.get(url=url)
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.paginator.setTotalPages(response['data']['total_page'])
            self.table.showRowContents(response['data']['contacts'])


""" 短信通 """


# 短信通控件
class SMSLinkWidget(QWidget):
    def __init__(self, sms_data, *args, **kwargs):
        super(SMSLinkWidget, self).__init__(*args, **kwargs)
        self.sms_id = sms_data['id']
        layout = QVBoxLayout(margin=0, spacing=1)
        date = QDate.fromString(sms_data['date'], 'yyyy-MM-dd')
        time = QTime.fromString(sms_data['time'], 'HH:mm:ss')
        date_time = date.toString('yyyy-MM-dd ') + time.toString('HH:mm') if date != QDate.currentDate() else time.toString('HH:mm')
        layout.addWidget(QLabel(date_time, objectName='timeLabel'))
        self.text_browser = QTextBrowser(objectName='textBrowser')
        self.text_browser.setText(sms_data['content'])
        layout.addWidget(self.text_browser)
        self.setLayout(layout)
        self.setStyleSheet("""
        #timeLabel{
            font-size:12px;
            color: rgb(50,70,100);
            font-weight: bold;
        }
        #textBrowser{
            margin:0 0 2px 25px;
            border:1px solid rgb(210,210,210);
            font-size:13px;
            color: rgb(0,0,0);
            border-radius: 5px;
            background-color:rgb(225,225,225)
        }
        """)


# 短信通主页
class SMSLinkPage(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(SMSLinkPage, self).__init__(*args, **kwargs)
        self.container = QWidget()
        layout = QVBoxLayout()
        self.container.setLayout(layout)
        self.setWidget(self.container)
        self.setWidgetResizable(True)

    # 请求数据
    def getSMSContents(self):
        try:
            r = requests.get(url=settings.SERVER_ADDR + 'info/sms/?mc=' + settings.app_dawn.value('machine'))
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError('获取数据失败.')
        except Exception:
            return
        else:
            for sms_item in response['data']:
                self.container.layout().addWidget(SMSLinkWidget(sms_item))


# 产品服务主页
class InfoServicePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(InfoServicePage, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=2)
        self.variety_folded = ScrollFoldedBox()
        self.variety_folded.left_mouse_clicked.connect(self.enter_service)
        self.variety_folded.setMaximumWidth(250)
        layout.addWidget(self.variety_folded)
        self.frame = LoadedPage()
        layout.addWidget(self.frame)
        self.setLayout(layout)
        self._addServiceContents()

    # 获取所有品种组和品种
    def _addServiceContents(self):
        contents = [
            {
                'name': u'咨询服务',
                'subs': [
                    {'id': 1, 'name': u'短信通'},
                    {'id': 2, 'name': u'市场分析'},
                    {'id': 3, 'name': u'专题研究'},
                    {'id': 4, 'name': u'调研报告'},
                    {'id': 5, 'name': u'市场路演'},
                ]
            },
            {
                'name': u'顾问服务',
                'subs': [
                    {'id': 6, 'name': u'人才培养'},
                    {'id': 7, 'name': u'部门组建'},
                    {'id': 8, 'name': u'制度考核'},
                ]
            },
            {
                'name': u'策略服务',
                'subs': [
                    {'id': 9, 'name': u'交易策略'},
                    {'id': 10, 'name': u'投资方案'},
                    {'id': 11, 'name': u'套保方案'},
                ]
            },
            {
                'name': u'培训服务',
                'subs': [
                    {'id': 12, 'name': u'品种介绍'},
                    {'id': 13, 'name': u'基本分析'},
                    {'id': 14, 'name': u'技术分析'},
                    {'id': 15, 'name': u'制度规则'},
                    {'id': 16, 'name': u'交易管理'},
                    {'id': 17, 'name': u'经验分享'},
                ]
            },
        ]
        for group_item in contents:
            head = self.variety_folded.addHead(group_item['name'])
            body = self.variety_folded.addBody(head=head)
            body.addButtons(group_item['subs'])
        self.variety_folded.container.layout().addStretch()

    # 点击服务，显示页面
    def enter_service(self, sid, text):
        if sid == 1:  # 短信通
            page = SMSLinkPage(parent=self.frame)
            page.getSMSContents()
        elif sid == 2:  # 市场分析
            page = MarketAnalysisPage(parent=self.frame)
            page.getCurrentMarketContents()
        elif sid == 3:  # 专题研究
            page = TopicSearchPage(parent=self.frame)
            page.getCurrentTopicContents()
        elif sid == 4:  # 调研报告
            page = SearchReportPage(parent=self.frame)
            page.getCurrentReportContents()
        elif sid == 6:  # 顾问服务-人才培养
            page = PDFContentShower(file=settings.STATIC_PREFIX + 'info/personTra/产品服务_人才培养.pdf', parent=self.frame)
        elif sid == 7:  # 顾问服务-部门组建
            page = PDFContentShower(file=settings.STATIC_PREFIX + 'info/deptBuild/产品服务_部门组建.pdf', parent=self.frame)
        elif sid == 8:  # 顾问服务-制度考核
            page = PDFContentShower(file=settings.STATIC_PREFIX + 'info/instExamine/产品服务_制度考核.pdf', parent=self.frame)
        elif sid == 9:  # 策略服务-交易策略
            page = TradePolicyPage(parent=self.frame)
            page.getTradePolicyContents()
        elif sid == 10:  # 策略服务-投资方案
            page = InvestPlanPage(parent=self.frame)
            page.getCurrentPlanContents()
        elif sid == 11:  # 策略服务-套保方案
            page = HedgePlanPage(parent=self.frame)
            page.getCurrentPlanContents()
        else:
            page = QLabel('当前模块正在加紧开放...',
                          styleSheet='color:rgb(50,180,100); font-size:15px;font-weight:bold', alignment=Qt.AlignCenter)
        self.frame.clear()
        self.frame.addWidget(page)
