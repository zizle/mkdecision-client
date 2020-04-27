# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
import pickle
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout,QProgressBar, QListWidget, QLabel, QDialog, QComboBox, \
    QPushButton, QHeaderView, QTableWidget, QAbstractItemView, QTableWidgetItem, QDateEdit, QMenu, QMessageBox, QStackedWidget
from PyQt5.Qt import Qt, pyqtSignal, QPoint, QDate
from PyQt5.QtGui import QPixmap, QImage, QCursor
from widgets.base import LoadedPage, PDFContentPopup, TextContentPopup
from popup.homeCollector import CreateNewsPopup, CreateReportPopup, CreateTransactionNoticePopup, \
    CreateNewSpotTablePopup, CreateNewFinanceCalendarPopup
import settings
from widgets.base import TableRowDeleteButton, TableRowReadButton
from popup.tips import WarningPopup, InformationPopup

""" 【首页】数据管理相关 """

""" 新闻公告 """


# 新闻公告显示的表格
class NewsBulletinTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('title', '标题'),
        ('create_time', '创建时间')
    ]

    def __init__(self, *args, **kwargs):
        super(NewsBulletinTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    # 显示数据
    def showRowContens(self, news_list):
        self.clear()
        table_headers = ["序号", "标题"]
        self.setColumnCount(len(table_headers))
        self.setHorizontalHeaderLabels(table_headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, row_item in enumerate(news_list):
            self.insertRow(row)
            item0 = QTableWidgetItem(str(row + 1))
            item0.id = row_item['id']
            item0.file_url = row_item['file_url']
            item0.setTextAlignment(Qt.AlignCenter)
            self.setItem(row,0, item0)
            item1 = QTableWidgetItem(row_item['title'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item1)

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
        self.current_page = 1
        self.total_page = 1
        self.page_size = 50

    # 获取所有的新闻公告内容
    def getNewsBulletins(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'bulletin/?page={}&page_size={}'.format(self.current_page, self.page_size),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.news_table.showRowContens(response['bulletins'])
            self.network_message_label.setText(response['message'])

    # 新增新闻
    def create_news(self):
        popup = CreateNewsPopup(parent=self)
        popup.exec_()


""" 常规报告 """


# 常规报告表格
class ReportTable(QTableWidget):
    network_result = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(ReportTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def setRowContents(self, contents):
        self.clear()
        table_headers = ['序号', '日期', '标题']
        self.setColumnCount(len(table_headers))
        self.setHorizontalHeaderLabels(table_headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.setRowCount(len(contents))
        for row, row_item in enumerate(contents):
            item0 = QTableWidgetItem(str(row + 1))
            item0.setTextAlignment(Qt.AlignCenter)
            item0.id = row_item['id']
            item0.file_url = row_item['file_url']
            self.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item['custom_time'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item1)
            item2 = QTableWidgetItem(row_item['title'])
            item2.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, item2)

    def mousePressEvent(self, event):
        index = self.indexAt(QPoint(event.pos().x(), event.pos().y()))
        row, _ = index.row(), index.column()
        if row < 0:
            return
        self.setCurrentIndex(index)
        if event.buttons() == Qt.RightButton:
            rmenu = QMenu()
            rmenu.setAttribute(Qt.WA_DeleteOnClose)
            view_action = rmenu.addAction("查看")
            view_action.triggered.connect(self.view_report_detail)
            delete_action = rmenu.addAction("删除")
            delete_action.triggered.connect(self.delete_row_record)
            rmenu.exec_(QCursor.pos())
            
        # super(ReportTable, self).mousePressEvent(event)  # 事件不再往外传了

    def view_report_detail(self):
        row = self.currentRow()
        title = self.item(row, 2).text()
        itemfile = self.item(row, 0).file_url
        file_addr = settings.STATIC_PREFIX + itemfile
        popup = PDFContentPopup(title=title, file=file_addr)
        popup.exec_()

    def delete_row_record(self):
        delete_action = QMessageBox.warning(self, "提示", "删除将不可恢复!", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if delete_action != QMessageBox.Yes:
            return
        row = self.currentRow()
        itemid = self.item(row, 0).id
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            r = requests.delete(
                url=settings.SERVER_ADDR + 'user/'+ str(user_id) + '/report/' + str(itemid) + '/?utoken=' + settings.app_dawn.value("AUTHORIZATION")
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, "错误", str(e))
        else:
            self.removeRow(row)
            QMessageBox.information(self, "成功", '删除成功!')


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
        message_button_layout.addWidget(QPushButton('新增', clicked=self.create_new_report), alignment=Qt.AlignRight)
        layout.addLayout(message_button_layout)
        # 当前数据显示表格
        self.report_table = ReportTable()
        # self.report_table.network_result.connect(self.network_message_label.setText)
        layout.addWidget(self.report_table)
        self.setLayout(layout)
        self.variety_info = []

    def getVariety(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'variety/?way=group',
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError("请求数据失败")
        except Exception as e:
            pass
        else:
            self.variety_info = response['variety']
            for index, group_item in enumerate(self.variety_info):
                self.category_combo.addItem(group_item['name'], group_item['id'])
                if index == 0:
                    for variety_item in group_item['subs']:
                        self.variety_combo.addItem(variety_item['name'], variety_item['id'])

    # 获取当前用户的报告
    def getCurrentReports(self):
        # 获取身份证明
        user_id = settings.app_dawn.value('UKEY', None)
        if not user_id:
            QMessageBox.warning(self, "错误", "软件内部发生错误.")
            return
        user_id = pickle.loads(user_id)
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/report/'
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText("获取报告失败!")
        else:
            self.report_table.setRowContents(response['reports'])
            self.network_message_label.setText("获取报告成功!")

    def create_new_report(self):
        popup = CreateReportPopup(variety_info=self.variety_info,parent=self)
        popup.exec_()



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
    def getCurrentReports1(self):
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
            self.report_table.showRowContents(response['data']['contacts'])
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
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '名称'),
        ('category', '通知类型'),
        ('date', '通知日期'),
        ('uploader', '上传者'),
    ]

    def __init__(self, *args, **kwargs):
        super(TransactionNoticeTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        table_headers = ['序号', '创建日期', '标题']
        self.setColumnCount(len(table_headers))
        self.setRowCount(len(row_list))
        self.setHorizontalHeaderLabels(table_headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, row_item in enumerate(row_list):
            item0 = QTableWidgetItem(str(row + 1))
            item0.setTextAlignment(Qt.AlignCenter)
            item0.id = row_item['id']
            item0.file_url = row_item['file_url']
            self.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item['create_time'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item1)
            item2 = QTableWidgetItem(row_item['title'])
            item2.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, item2)

    def mousePressEvent(self, event):
        index = self.indexAt(QPoint(event.pos().x(), event.pos().y()))
        row, _ = index.row(), index.column()
        if row < 0:
            return
        self.setCurrentIndex(index)
        if event.buttons() == Qt.RightButton:
            rmenu = QMenu()
            rmenu.setAttribute(Qt.WA_DeleteOnClose)
            view_action = rmenu.addAction("查看")
            view_action.triggered.connect(self.view_notice_detail)
            delete_action = rmenu.addAction("删除")
            delete_action.triggered.connect(self.delete_row_record)
            rmenu.exec_(QCursor.pos())

        # super(ReportTable, self).mousePressEvent(event)  # 事件不再往外传了

    def view_notice_detail(self):
        row = self.currentRow()
        title = self.item(row, 2).text()
        itemfile = self.item(row, 0).file_url
        file_addr = settings.STATIC_PREFIX + itemfile
        popup = PDFContentPopup(title=title, file=file_addr)
        popup.exec_()

    def delete_row_record(self):
        delete_action = QMessageBox.warning(self, "提示", "删除将不可恢复!", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if delete_action != QMessageBox.Yes:
            return
        row = self.currentRow()
        itemid = self.item(row, 0).id
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            r = requests.delete(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/exnotice/' + str(
                    itemid) + '/?utoken=' + settings.app_dawn.value("AUTHORIZATION")
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, "错误", str(e))
        else:
            self.removeRow(row)
            QMessageBox.information(self, "成功", '删除成功!')




# 交易通知管理页面
class TransactionNoticePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(TransactionNoticePage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0, spacing=2)
        # 分类选择、信息展示与新增按钮
        message_button_layout = QHBoxLayout()
        self.network_message_label = QLabel()
        message_button_layout.addWidget(self.network_message_label)
        message_button_layout.addStretch()  # 伸缩
        message_button_layout.addWidget(QPushButton('新增', clicked=self.create_transaction_notice), alignment=Qt.AlignRight)
        layout.addLayout(message_button_layout)
        # 当前数据显示表格
        self.notice_table = TransactionNoticeTable()
        self.notice_table.network_result.connect(self.network_message_label.setText)
        layout.addWidget(self.notice_table)
        self.setLayout(layout)

    # 获取当前交易通知
    def getCurrentTransactionNotce(self):
        try:
            user_id = pickle.loads(settings.app_dawn.value("UKEY"))
            # 发起请求当前数据
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/'+str(user_id)+'/exnotice/',
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.notice_table.showRowContents(response['exnotices'])
            self.network_message_label.setText(response['message'])

    # 新建交易通知
    def create_transaction_notice(self):
        popup = CreateTransactionNoticePopup(parent=self)
        popup.exec_()


""" 现货报表相关 """


# 现货报表管理表格
class SpotCommodityTable(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(SpotCommodityTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        table_headers = ['序号','日期', '名称', '地区', '等级', '价格', '增减']
        self.setColumnCount(len(table_headers))
        self.setRowCount(len(row_list))
        self.setHorizontalHeaderLabels(table_headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, row_item in enumerate(row_list):
            item0 = QTableWidgetItem(str(row + 1))
            item0.setTextAlignment(Qt.AlignCenter)
            item0.id = row_item['id']
            self.setItem(row,0,item0)
            item1 = QTableWidgetItem(row_item['custom_time'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item1)
            item2 = QTableWidgetItem(row_item['name'])
            item2.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, item2)
            item3 = QTableWidgetItem(row_item['area'])
            item3.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 3, item3)
            item4 = QTableWidgetItem(row_item['level'])
            item4.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 4, item4)
            item5 = QTableWidgetItem(row_item['price'])
            item5.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 5, item5)
            item6 = QTableWidgetItem(row_item['increase'])
            item6.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 6, item6)

    def mousePressEvent(self, event):
        index = self.indexAt(QPoint(event.pos().x(), event.pos().y()))
        row, _ = index.row(), index.column()
        if row < 0:
            return
        self.setCurrentIndex(index)
        if event.buttons() == Qt.RightButton:
            rmenu = QMenu()
            rmenu.setAttribute(Qt.WA_DeleteOnClose)
            delete_action = rmenu.addAction("删除")
            delete_action.triggered.connect(self.delete_row_record)
            rmenu.exec_(QCursor.pos())

    def delete_row_record(self):
        delete_action = QMessageBox.warning(self, "提示", "删除将不可恢复!", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if delete_action != QMessageBox.Yes:
            return
        row = self.currentRow()
        itemid = self.item(row, 0).id
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            r = requests.delete(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/spot/' + str(
                    itemid) + '/?utoken=' + settings.app_dawn.value("AUTHORIZATION")
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, "错误", str(e))
        else:
            self.removeRow(row)
            QMessageBox.information(self, "成功", '删除成功!')


# 现货报表管理页面
class SpotCommodityPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(SpotCommodityPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0, spacing=2)
        # 日期选择、信息展示与新增按钮
        message_button_layout = QHBoxLayout()
        self.date_edit = QDateEdit(QDate.currentDate(), dateChanged=self.getCurrentSpotCommodity)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        self.date_edit.setCalendarPopup(True)
        message_button_layout.addWidget(QLabel('日期:'))
        message_button_layout.addWidget(self.date_edit)
        self.network_message_label = QLabel()
        message_button_layout.addWidget(self.network_message_label)
        message_button_layout.addStretch()  # 伸缩
        message_button_layout.addWidget(QPushButton('新增', clicked=self.create_spot_table), alignment=Qt.AlignRight)
        layout.addLayout(message_button_layout)
        # 当前数据显示表格
        self.spot_table = SpotCommodityTable()
        layout.addWidget(self.spot_table)
        self.setLayout(layout)

        # 上传数据的进度条
        self.process_widget = QWidget(self)
        self.process_widget.resize(self.width(), self.height())
        process_layout = QVBoxLayout(self.process_widget)
        process_layout.addStretch()
        self.process_message = QLabel("数据上传处理中..", self.process_widget)
        process_layout.addWidget(self.process_message)
        process = QProgressBar(parent=self.process_widget)
        process.setMinimum(0)
        process.setMaximum(0)
        process.setTextVisible(False)
        process_layout.addWidget(process)
        process_layout.addStretch()
        self.process_widget.setLayout(process_layout)
        self.process_widget.hide()
        self.process_widget.setStyleSheet("background:rgb(200,200,200);opacity:0.6")

    # 获取当前时间的现货报表
    def getCurrentSpotCommodity(self):
        current_date = self.date_edit.text()
        current_page = 1
        try:
            user_id = pickle.loads(settings.app_dawn.value("UKEY"))
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/'+str(user_id) + '/spot/?page=' +str(current_page) +'&page_size=50&date=' + current_date
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            print(response)
            self.spot_table.showRowContents(response['spots'])
            self.network_message_label.setText(response['message'])

    # 新增现货报表数据
    def create_spot_table(self):
        self.popup = CreateNewSpotTablePopup(parent=self)
        self.popup.exec_()


""" 财经日历相关 """


# 财经日历显示表格
class FinanceCalendarTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('date', '日期'),
        ('time', '时间'),
        ('country', '地区'),
        ('event', '事件'),
        ('expected', '预期值'),
        ('uploader', '上传者'),
    ]

    def __init__(self, *args, **kwargs):
        super(FinanceCalendarTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        table_headers = ["序号","日期", "时间", "事件", "预期值"]
        self.setColumnCount(len(table_headers))
        self.setRowCount(len(row_list))
        self.setHorizontalHeaderLabels(table_headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row,row_item in enumerate(row_list):
            item0 = QTableWidgetItem(str(row + 1))
            item0.setTextAlignment(Qt.AlignCenter)
            item0.id = row_item['id']
            self.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item['date'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item1)
            item2 = QTableWidgetItem(row_item['time'])
            item2.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, item2)
            item3 = QTableWidgetItem(row_item['event'])
            item3.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 3, item3)
            item4 = QTableWidgetItem(row_item['expected'])
            item4.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 4, item4)

    def mousePressEvent(self, event):
        index = self.indexAt(QPoint(event.pos().x(), event.pos().y()))
        row, _ = index.row(), index.column()
        if row < 0:
            return
        self.setCurrentIndex(index)
        if event.buttons() == Qt.RightButton:
            rmenu = QMenu()
            rmenu.setAttribute(Qt.WA_DeleteOnClose)
            delete_action = rmenu.addAction("删除")
            delete_action.triggered.connect(self.delete_row_record)
            rmenu.exec_(QCursor.pos())

    def delete_row_record(self):
        delete_action = QMessageBox.warning(self, "提示", "删除将不可恢复!", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if delete_action != QMessageBox.Yes:
            return
        row = self.currentRow()
        itemid = self.item(row, 0).id
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            r = requests.delete(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/fecalendar/' + str(
                    itemid) + '/?utoken=' + settings.app_dawn.value("AUTHORIZATION")
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, "错误", str(e))
        else:
            self.removeRow(row)
            QMessageBox.information(self, "成功", '删除成功!')


# 财经日历管理页面
class FinanceCalendarPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(FinanceCalendarPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0, spacing=2)

        # 日期选择、信息展示与新增按钮
        message_button_layout = QHBoxLayout()
        self.date_edit = QDateEdit(QDate.currentDate(), dateChanged=self.getCurrentFinanceCalendar)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        self.date_edit.setCalendarPopup(True)
        message_button_layout.addWidget(QLabel('日期:'))
        message_button_layout.addWidget(self.date_edit)
        self.network_message_label = QLabel()
        message_button_layout.addWidget(self.network_message_label)
        message_button_layout.addStretch()  # 伸缩
        message_button_layout.addWidget(QPushButton('新增', clicked=self.create_finance_calendar), alignment=Qt.AlignRight)
        layout.addLayout(message_button_layout)
        # 当前数据显示表格
        self.finance_table = FinanceCalendarTable()
        self.finance_table.network_result.connect(self.network_message_label.setText)
        layout.addWidget(self.finance_table)
        self.setLayout(layout)

    # 获取当前日期财经日历
    def getCurrentFinanceCalendar(self):
        current_date = self.date_edit.text()
        current_page = 1
        try:
            user_id = pickle.loads(settings.app_dawn.value("UKEY"))
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/fecalendar/?page=' +str(current_page)+'&page_size=50&date=' + current_date,

            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.finance_table.showRowContents(response['fecalendar'])
            self.network_message_label.setText(response['message'])

    # 新增财经日历数据
    def create_finance_calendar(self):
        popup = CreateNewFinanceCalendarPopup(parent=self)
        popup.exec_()


""" 首页管理主页 """


# 首页管理主页
class HomePageCollector(QWidget):
    network_result = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(HomePageCollector, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0)
        # 左侧菜单列表
        self.left_list = QListWidget(parent=self, clicked=self.left_menu_clicked, objectName='leftList')
        layout.addWidget(self.left_list, alignment=Qt.AlignLeft)
        # 右侧显示具体操作窗体
        self.operate_frame = LoadedPage()
        layout.addWidget(self.operate_frame)
        self.setLayout(layout)
        self._addListMenu()
        self.setStyleSheet("""
        #leftList::item{
            height:22px;
        }
        """)

    # 添加菜单按钮
    def _addListMenu(self):
        # 获取身份证明
        user_key = settings.app_dawn.value('UROLE', 0)
        user_key = pickle.loads(user_key)
        if user_key <= 3:  # 信息管理以上
            actions = [u'新闻公告', u'常规报告', u'交易通知', u'现货报表', u'财经日历']
        else:
            actions = [u'常规报告']
        for item in actions:
            self.left_list.addItem(item)

    # 点击左侧按钮
    def left_menu_clicked(self):
        text = self.left_list.currentItem().text()
        if text == u'新闻公告':
            frame_page = NewsBulletinPage(parent=self.operate_frame)
            frame_page.getNewsBulletins()
        elif text == u'常规报告':
            frame_page = NormalReportPage(parent=self.operate_frame)
            frame_page.getVariety()
            frame_page.getCurrentReports()
        elif text == u'交易通知':
            frame_page = TransactionNoticePage(parent=self.operate_frame)
            # frame_page.getCategoryCombo()
            frame_page.getCurrentTransactionNotce()
        elif text == u'现货报表':
            frame_page = SpotCommodityPage(parent=self.operate_frame)
            frame_page.getCurrentSpotCommodity()
        elif text == u'财经日历':
            frame_page = FinanceCalendarPage(parent=self.operate_frame)
            frame_page.getCurrentFinanceCalendar()
        else:
            frame_page = QLabel('【' + text + '】正在加紧开发中...')
        self.operate_frame.clear()
        self.operate_frame.addWidget(frame_page)

