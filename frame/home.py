# _*_ coding:utf-8 _*_
# __Author__： zizle
import os
import json
import requests
import chardet
from math import floor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QStackedWidget, QScrollArea, QPushButton, \
    QComboBox, QTableWidget, QHeaderView, QTableWidgetItem, QAbstractItemView, QDateEdit, QListView
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPoint, QDate
from PyQt5.QtGui import QPixmap, QBrush, QColor
import settings
from widgets.base import ScrollFoldedBox, PDFContentPopup, TextContentPopup, LoadedPage, TableRowReadButton, Paginator


""" 新闻公告栏相关 """


# 新闻公告条目Item
class NewsItem(QWidget):
    item_clicked = pyqtSignal(int)

    def __init__(self, title='', create_time='', item_id=None, *args, **kwargs):
        super(NewsItem, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0)
        title_label = QLabel(title, objectName='title')
        self.item_id = item_id
        time_label = QLabel(create_time, objectName='createTime')
        layout.addWidget(title_label, alignment=Qt.AlignLeft)
        layout.addWidget(time_label, alignment=Qt.AlignRight)
        self.setLayout(layout)
        # 样式
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        self.setMouseTracking(True)
        self.setObjectName('newsItem')
        self.initialStyleSheet()

    # 初始化样式
    def initialStyleSheet(self):
        self.setStyleSheet("""
        #newsItem{
            border-bottom: 1px solid rgb(200,200,200);
            min-height:25px;
            max-height:25px;
        }
        #title{
            border:none;
            font-size:13px;
            padding-left:2px;
        }
        #createTime{
            padding:0 5px;
            color:rgb(128,128,128)
        }
        """)

    # 鼠标进入样式
    def mouseEnterStyleSheet(self):
        self.setStyleSheet("""
        #newsItem{
            border-bottom: 1px solid rgb(200,200,200);
            min-height:25px;
            max-height:25px;
            background-color: rgb(180,180,180)
        }
        #title{
            border:none;
            font-size:13px;
            padding-left:2px;
        }
        #createTime{
            padding:0 5px;
            color:rgb(128,128,128)
        }
        """)

    # 鼠标进入设置
    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        # 设置背景色
        self.mouseEnterStyleSheet()

    # 鼠标移出设置
    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        self.initialStyleSheet()

    # 鼠标弹起事件
    def mouseReleaseEvent(self, event):
        super(NewsItem, self).mouseReleaseEvent(event)
        self.item_clicked.emit(self.item_id)


# 首页中新闻公告板块
class NewsBox(QWidget):
    news_item_clicked = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super(NewsBox, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0, spacing=0)  # spacing会影响子控件的高度，控件之间有间隔，视觉就影响高度
        # 更多按钮
        self.more_button = QPushButton('更多>>', objectName='moreNews')
        self.more_button.setCursor(Qt.PointingHandCursor)
        self.setLayout(layout)
        self.setObjectName('newsBox')
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        self.setStyleSheet("""
        #newsBox{
            /*min-width:420px;
            max-width:420px;*/
        }
        #moreNews{
            border:none;
            color:rgb(3,96,147);
            min-height:25px;
            max-height:25px;
        }
        """)

    # 添加新闻条目
    def addItems(self, item_list):
        for item in item_list:
            item.item_clicked.connect(self.news_item_clicked)
            self.layout().addWidget(item, alignment=Qt.AlignTop)

    # 设置当前显示的条目数
    def setItemCount(self, count):
        total_count = self.layout().count()
        if total_count >= count:
            for item_index in range(0, total_count - 1):
                widget = self.layout().itemAt(item_index).widget()
                if item_index < count:
                    widget.show()
                else:
                    widget.hide()

    # 设置更多按钮
    def setMoreNewsButton(self):
        count = self.layout().count()
        self.layout().insertWidget(count, self.more_button, alignment=Qt.AlignRight)
        return self.more_button


# 更多新闻页面
class MoreNewsPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(MoreNewsPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        self.news_scroll = QScrollArea(parent=self, objectName='newsScroll')
        self.news_scroll.setWidgetResizable(True)
        layout.addWidget(self.news_scroll)
        self.paginator = Paginator(parent=self)
        self.paginator.clicked.connect(self.getCurrentNews)
        layout.addWidget(self.paginator, alignment=Qt.AlignBottom | Qt.AlignCenter)
        # layout.addWidget(QLabel('暂无更多新闻，关注其他资讯...', styleSheet='font-size:18px;color:rgb(200,120,130)')
        #                  , alignment=Qt.AlignCenter)
        self.setLayout(layout)
        self.setStyleSheet("""
        #newsScroll{
            border:none;
        }
        """)

    # 获取新闻公告内容
    def getCurrentNews(self):
        current_page = self.paginator.current_page
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/news-more/?page=' + str(
                    current_page) + '&mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            self.resetNewsBox()
            news_data = response['data']['contacts']
            for news_obj in news_data:
                news_item = NewsItem(
                    title=news_obj['title'],
                    create_time=news_obj['create_time'],
                    item_id=news_obj['id'],
                    parent=self.news_box
                )
                news_item.item_clicked.connect(self.read_detail_news)
                self.news_box.layout().addWidget(news_item)
            self.news_box.layout().addStretch()
            self.paginator.setTotalPages(response['data']['total_page'])

    # 清除控件内的条目
    def resetNewsBox(self):
        if hasattr(self, 'news_box'):
            self.news_box.deleteLater()
        self.news_box = QWidget(parent=self.news_scroll)
        news_layout = QVBoxLayout(margin=0)
        self.news_box.setLayout(news_layout)
        self.news_scroll.setWidget(self.news_box)

    # 阅读新闻
    def read_detail_news(self, news_id):
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



""" 图片广告轮播相关 """

# 轮播图的label
class SliderLabel(QLabel):
    def __init__(self, name, *args, **kwargs):
        super(SliderLabel, self).__init__(*args, **kwargs)
        self.name = name


# 轮播图控件
class ImageSlider(QStackedWidget):
    image_clicked = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(ImageSlider, self).__init__(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        self.timer = QTimer()
        self.timer.timeout.connect(self.slider_image_label)
        self.setObjectName('imageSlider')
        self.setStyleSheet("""
        #imageSlider{
            background-color: rgb(120,150,120)
        }
        """)

    # 添加图片
    def addImages(self, url_list):
        self.clear()
        for img_path in url_list:
            # 获取名称
            img_name = img_path.rsplit('/', 1)[1]
            pix_map = QPixmap(img_path)
            image_container = SliderLabel(name=img_name, parent=self, objectName='imageContainer')
            image_container.setScaledContents(True)
            image_container.setPixmap(pix_map)
            self.addWidget(image_container)
        if self.count() > 1 and not self.timer.isActive():
            self.timer.start(settings.IMAGE_SLIDER_RATE)

    # 清空
    def clear(self):
        widget = None
        for i in range(self.count()):
            widget = self.widget(i)
            self.removeWidget(widget)
            if widget:
                widget.deleteLater()
        del widget

    def mouseReleaseEvent(self, event):
        super(ImageSlider, self).mouseReleaseEvent(event)
        current_label = self.currentWidget()
        self.image_clicked.emit(current_label.name)

    # 改变图片显示
    def slider_image_label(self):
        current_index = self.currentIndex()
        if current_index + 1 >= self.count():
            self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(current_index + 1)


""" 常规报告显示相关 """


# 常规报告展示表格
class NormalReportTable(QTableWidget):
    KEY_LABELS = [
        ('id', '序号'),
        ('name', '报告名'),
        ('category', '报告类型'),
        ('date', '报告日期'),
        ('varieties', '关联品种'),
    ]

    def __init__(self, *args, **kwargs):
        super(NormalReportTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 内容不可更改
        self.setFocusPolicy(Qt.NoFocus)
        self.cellClicked.connect(self.read_report)  # 点击事件
        self.setAlternatingRowColors(True)  # 开启交替行颜色
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # 选中时为一行
        self.setSelectionMode(QAbstractItemView.SingleSelection)  # 只能选中一行
        self.horizontalHeader().setStyleSheet("""
        QHeaderView::section,
        QTableCornerButton::section {
            min-height: 25px;
            padding: 1px;border: none;
            border-right: 1px solid rgb(211,212,212);
            border-bottom: 1px solid rgb(211,212,212);
            background-color:rgb(243,245,248);
            font-weight: bold;
            font-size: 14px;
        }""")
        self.setStyleSheet("""
        font-size: 14px;
        selection-color: red;
        alternate-background-color: rgb(245, 250, 248);  /* 设置交替行颜色 */
        """)

    # 显示报告内容
    def showRowContents(self, report_list):
        self.clear()
        self.setRowCount(len(report_list))
        self.setColumnCount(len(self.KEY_LABELS))
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自动拉伸大小
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 随表头文字宽度
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)  # 自定义设置
        self.setColumnWidth(1, 400)  # 第一列(标题列)自定义宽度
        for row, content_item in enumerate(report_list):
            self.setRowHeight(row, 32)  # 设置固定行高
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = content_item[header[0]]
                    table_item.file = content_item['file']
                else:
                    table_item = QTableWidgetItem(str(content_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
        # 设置表格高度
        self.setMinimumHeight(self.rowCount() * 33 + 30)
        # 竖向自动拉伸
        if self.rowCount() >= 45:
            self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        else:
            self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)  # 固定行高，设置的大小

    def read_report(self, row, col):
        if col == 1:
            report_file = self.item(row, 0).file
            file_name = self.item(row, col).text()
            # 显示文件
            file = settings.STATIC_PREFIX + report_file
            popup = PDFContentPopup(title=file_name, file=file, parent=self)
            if not popup.exec_():
                popup.deleteLater()
                del popup

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 显示常规报告
class NormalReportPage(QWidget):
    def __init__(self, category_id, *args, **kwargs):
        super(NormalReportPage, self).__init__(*args, **kwargs)
        self.category_id = category_id
        layout = QVBoxLayout(margin=0, spacing=1)
        # 相关品种选框
        variety_widget = QWidget(parent=self, objectName='varietyCombo')
        variety_widget.setFixedHeight(22)
        relate_variety_layout = QHBoxLayout(margin=0, spacing=2)
        relate_variety_layout.addWidget(QLabel('相关品种:'))
        self.variety_combo = QComboBox(activated=self.varietyChanged, objectName='combo')
        self.variety_combo.setCursor(Qt.PointingHandCursor)
        self.variety_combo.setMinimumWidth(60)
        relate_variety_layout.addWidget(self.variety_combo)
        relate_variety_layout.addStretch()
        # 页码控制
        self.paginator = Paginator(parent=self)
        self.paginator.clicked.connect(self.getCurrentReports)
        relate_variety_layout.addWidget(self.paginator)
        variety_widget.setLayout(relate_variety_layout)
        layout.addWidget(variety_widget)
        self.report_table = NormalReportTable()
        layout.addWidget(self.report_table)
        self.setLayout(layout)
        self.setStyleSheet("""
        #varietyCombo{
            background-color: rgb(178,200,187)
        }
        #varietyCombo #combo{
            background-color: rgb(178,200,187);
            border: 1px solid rgb(200, 200, 200);
            color: rgb(7,99,109);
            font-weight: bold;
        }
        #varietyCombo #combo QAbstractItemView::item{
            height:20px;
        }
        #varietyCombo #combo::drop-down{
            border: 0px;
        }
        #varietyCombo #combo::down-arrow{
            image:url("media/more.png");
            width: 15px;
            height:15px;
        }
        """)
        self.variety_combo.setView(QListView())

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
            self.getCurrentReports()  # 获取当前报告

    # 选择了品种
    def varietyChanged(self):
        self.paginator.clearPages()
        self.getCurrentReports()

    # 获取当前显示的报告
    def getCurrentReports(self):
        current_page = self.paginator.current_page
        current_variety_id = self.variety_combo.currentData()
        try:
            # 发起上传请求
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/normal-report/?page='+str(current_page)+'&mc=' + settings.app_dawn.value('machine'),
                data=json.dumps({'category': self.category_id, 'variety': current_variety_id})
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            self.report_table.showRowContents(response['data']['contacts'])
            self.paginator.setTotalPages(response['data']['total_page'])


""" 交易通知显示相关 """


# 交易通知表格
class TransactionNoticeTable(QTableWidget):
    KEY_LABELS = [
        ('id', '序号'),
        ('name', '通知文件'),
        ('category', '通知类型'),
        ('date', '通知日期'),
    ]

    def __init__(self, *args, **kwargs):
        super(TransactionNoticeTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.cellClicked.connect(self.read_notice)
        self.horizontalHeader().setStyleSheet("""
        QHeaderView::section,
        QTableCornerButton::section {
            min-height: 25px;
            padding: 1px;border: none;
            border-right: 1px solid rgb(211,212,212);
            border-bottom: 1px solid rgb(211,212,212);
            background-color:rgb(243,245,248);
            font-weight: bold;
            font-size: 14px;
        }""")
        self.setStyleSheet("""
        font-size: 14px;
        selection-color: red;
        alternate-background-color: rgb(245, 250, 248);  /* 设置交替行颜色 */
        """)

    # 显示报告内容
    def showRowContents(self, report_list):
        self.clear()
        self.setRowCount(len(report_list))
        self.setColumnCount(len(self.KEY_LABELS))
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.setColumnWidth(1, 450)
        for row, content_item in enumerate(report_list):
            self.setRowHeight(row, 32)
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = content_item[header[0]]
                    table_item.file = content_item['file']
                else:
                    table_item = QTableWidgetItem(str(content_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
        # 设置表格高度
        self.setMinimumHeight(self.rowCount() * 32 + 45)
        if self.rowCount() >= 45:
            # 竖向自动拉伸
            self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        else:
            self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)  # 固定行高，设置的大小

    # 阅读一个通知
    def read_notice(self, row, col):
        if col == 1:
            notice_file = self.item(row, 0).file
            notice_name = self.item(row, col).text()
            # 显示文件
            file = settings.STATIC_PREFIX + notice_file
            popup = PDFContentPopup(title=notice_name, file=file, parent=self)
            if not popup.exec_():
                popup.deleteLater()
                del popup

    # 阅读一个通知
    def read_button_clicked(self, read_button):
        current_row, _ = self.get_widget_index(read_button)
        report_file = self.item(current_row, 0).file
        # 显示文件
        file = settings.STATIC_PREFIX + report_file
        popup = PDFContentPopup(title='阅读通知', file=file, parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 显示交易通知
class TransactionNoticePage(QWidget):
    def __init__(self, category_id, *args, **kwargs):
        super(TransactionNoticePage, self).__init__(*args, **kwargs)
        self.category_id = category_id
        layout = QVBoxLayout(margin=0, spacing=1)
        # 页码器
        contro_widget = QWidget(parent=self, objectName='controlWidget')
        contro_widget.setFixedHeight(22)
        controller_layout = QHBoxLayout(margin=0)
        self.paginator = Paginator(parent=contro_widget)
        self.paginator.clicked.connect(self.getCurrentNotices)
        controller_layout.addWidget(self.paginator, alignment=Qt.AlignRight)
        contro_widget.setLayout(controller_layout)
        layout.addWidget(contro_widget)
        self.notice_table = TransactionNoticeTable()
        layout.addWidget(self.notice_table)
        self.setLayout(layout)
        self.setStyleSheet("""
        #controlWidget{
            background-color: rgb(178,200,187);
            min-height: 20px;
        }
        """)

    # 获取当前通知
    def getCurrentNotices(self):
        current_page = self.paginator.current_page
        try:
            # 发起请求当前数据
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/transaction_notice/?page='+str(current_page)+'&mc=' + settings.app_dawn.value('machine'),
                data=json.dumps({'category_id': self.category_id})
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            self.notice_table.showRowContents(response['data']['contacts'])
            self.paginator.setTotalPages(response['data']['total_page'])

""" 现货报表相关 """


# 现货报表表格
class SpotCommodityTable(QTableWidget):
    KEY_LABELS = [
        ('id', '序号'),
        ('name', '名称'),
        ('area', '地区'),
        ('level', '等级'),
        ('price', '价格'),
        ('increase', '增减'),
        ('note', '备注'),
        ('date', '日期'),
    ]

    def __init__(self, *args, **kwargs):
        super(SpotCommodityTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAlternatingRowColors(True)  # 开启交替行颜色
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # 选中时为一行
        self.setSelectionMode(QAbstractItemView.SingleSelection)  # 只能选中一行
        self.horizontalHeader().setStyleSheet("""
        QHeaderView::section,
        QTableCornerButton::section {
            min-height: 25px;
            padding: 1px;border: none;
            border-right: 1px solid rgb(211,212,212);
            border-bottom: 1px solid rgb(211,212,212);
            background-color:rgb(243,245,248);
            font-weight: bold;
            font-size: 14px;
        }""")
        self.setStyleSheet("""
        font-size: 14px;
        selection-color: red;
        alternate-background-color: rgb(245, 250, 248);  /* 设置交替行颜色 */
        """)

    def showRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS))
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, content_item in enumerate(row_list):
            self.setRowHeight(row, 32)
            for col, header in enumerate(self.KEY_LABELS):
                color = QBrush(QColor(0,0,0))
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = content_item[header[0]]
                else:
                    if header[0] == 'price':
                        text = str(int(content_item[header[0]]))
                    elif header[0] == 'increase':
                        num = int(content_item[header[0]])
                        text = str(num)
                        if num > 0:
                            # print('数大于0')
                            color.setColor(QColor(220, 100, 100))
                        elif num < 0:
                            # print('数《0')
                            color.setColor(QColor(100, 220, 100))
                        else:
                            pass
                    else:
                        text = content_item[header[0]]
                    table_item = QTableWidgetItem(text)
                    table_item.setForeground(color)
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
        # 设置表格高度
        self.setMinimumHeight(self.rowCount() * 33 + 30)
        # 竖向自动拉伸
        if self.rowCount() >= 45:
            self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        else:
            self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)  # 固定行高，设置的大小


# 现货报表显示主页
class SpotCommodityPage(QWidget):
    def __init__(self, delta_days, *args, **kwargs):
        super(SpotCommodityPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0, spacing=2)
        # 日期选择
        date_widget = QWidget(parent=self, objectName='dateWidget')
        date_widget.setFixedHeight(22)
        message_button_layout = QHBoxLayout(margin=0, spacing=0)
        self.date_edit = QDateEdit(QDate.currentDate().addDays(delta_days), parent=date_widget, dateChanged=self.getCurrentSpotCommodity, objectName='dateEdit')
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        self.date_edit.setCalendarPopup(True)
        message_button_layout.addWidget(QLabel('日期:'))
        message_button_layout.addWidget(self.date_edit)
        message_button_layout.addStretch()  # 伸缩
        date_widget.setLayout(message_button_layout)
        layout.addWidget(date_widget, alignment=Qt.AlignTop)
        # 当前数据显示表格
        self.spot_table = SpotCommodityTable()
        layout.addWidget(self.spot_table)
        # 无数据的显示
        self.no_data_label = QLabel('暂无相关数据...', styleSheet='color:rgb(200,100,50)', alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.no_data_label.hide()
        layout.addWidget(self.no_data_label)
        self.setLayout(layout)
        self.setStyleSheet("""
        #dateWidget{
            background-color: rgb(178,200,187)
        }
        #dateWidget #dateEdit{
            background-color: rgb(250, 250, 250);
            margin:0;
            padding:0;
            border:1px solid rgb(250, 250, 250);
        }
        #dateWidget #dateEdit::drop-down{
            background-color: rgb(178,210,197);
        }
        #dateWidget #dateEdit::down-arrow{
            image:url("media/more.png");
            width: 15px;
            height:15px;
        }
        """)

    def getCurrentSpotCommodity(self):
        current_date = self.date_edit.text()
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/spot-commodity/?date=' + current_date + '&mc=' + settings.app_dawn.value(
                    'machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            self.spot_table.hide()
            self.no_data_label.show()
        else:
            if response['data']:
                self.spot_table.showRowContents(response['data'])
                self.spot_table.show()
                self.no_data_label.hide()
            else:
                self.spot_table.hide()
                self.no_data_label.show()


""" 财经日历相关 """


# 财经日历显示表格
class FinanceCalendarTable(QTableWidget):
    KEY_LABELS = [
        ('id', '序号'),
        ('date', '日期'),
        ('time', '时间'),
        ('country', '地区'),
        ('event', '事件'),
        ('expected', '预期值'),
    ]

    def __init__(self, *args, **kwargs):
        super(FinanceCalendarTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAlternatingRowColors(True)  # 开启交替行颜色
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # 选中时为一行
        self.setSelectionMode(QAbstractItemView.SingleSelection)  # 只能选中一行
        self.horizontalHeader().setStyleSheet("""
        QHeaderView::section,
        QTableCornerButton::section {
            min-height: 25px;
            padding: 1px;border: none;
            border-right: 1px solid rgb(211,212,212);
            border-bottom: 1px solid rgb(211,212,212);
            background-color:rgb(243,245,248);
            font-weight: bold;
            font-size: 14px;
        }""")
        self.setStyleSheet("""
        font-size: 14px;
        selection-color: red;
        alternate-background-color: rgb(245, 250, 248);  /* 设置交替行颜色 */
        """)

    def showRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS))
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.Interactive)
        self.setColumnWidth(4, 350)
        for row, content_item in enumerate(row_list):
            self.setRowHeight(row, 32)
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = content_item[header[0]]
                else:
                    table_item = QTableWidgetItem(str(content_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
        # 设置表格高度
        self.setMinimumHeight(self.rowCount() * 33 + 30)
        # 竖向自动拉伸
        if self.rowCount() >= 45:
            self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        else:
            self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)  # 固定行高，设置的大小

# 财经日历显示主页
class FinanceCalendarPage(QWidget):
    def __init__(self, delta_days, *args, **kwargs):
        super(FinanceCalendarPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0, spacing=2)
        # 日期选择
        date_widget = QWidget(parent=self, objectName='dateWidget')
        date_widget.setFixedHeight(22)
        message_button_layout = QHBoxLayout(margin=0, spacing=0)
        self.date_edit = QDateEdit(QDate.currentDate().addDays(delta_days), parent=date_widget, dateChanged=self.getCurrentFinanceCalendar, objectName='dateEdit')
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        self.date_edit.setCalendarPopup(True)
        message_button_layout.addWidget(QLabel('日期:'))
        message_button_layout.addWidget(self.date_edit)
        message_button_layout.addStretch()  # 伸缩
        date_widget.setLayout(message_button_layout)
        layout.addWidget(date_widget, alignment=Qt.AlignTop)
        # 当前数据显示表格
        self.finance_table = FinanceCalendarTable()
        layout.addWidget(self.finance_table)
        # 无数据的显示
        self.no_data_label = QLabel('暂无相关数据...', styleSheet='color:rgb(200,100,50)', alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.no_data_label.hide()
        layout.addWidget(self.no_data_label)
        self.setLayout(layout)
        self.setStyleSheet("""
        #dateWidget{
            background-color: rgb(178,200,187)
        }
        #dateWidget #dateEdit{
            background-color: rgb(250,250,250);
            margin:0;
            padding:0;
            border: 1px solid rgb(250,250,250);
        }
        #dateWidget #dateEdit::drop-down{
            border:2px;
            background-color:rgb(178,210,197);
        }
        #dateWidget #dateEdit::down-arrow{
            image:url("media/more.png");
            width: 15px;
            height:15px;
        }
        """)


    # 获取当前日期财经日历
    def getCurrentFinanceCalendar(self):
        current_date = self.date_edit.text()
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/finance-calendar/?date=' + current_date + '&mc=' + settings.app_dawn.value(
                    'machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            self.finance_table.hide()
            self.no_data_label.show()
        else:
            if response['data']:
                self.finance_table.showRowContents(response['data'])
                self.finance_table.show()
                self.no_data_label.hide()
            else:
                self.finance_table.hide()
                self.no_data_label.show()


# 首页主页面(可滚动)
class HomePage(QScrollArea):
    more_news_signal = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        super(HomePage, self).__init__(*args, **kwargs)
        container = QWidget(parent=self)  # 页面容器
        layout = QVBoxLayout(margin=2)
        news_slider_layout = QHBoxLayout()  # 新闻-轮播布局
        # 新闻公告栏
        self.news_box = NewsBox(parent=self)
        self.news_box.news_item_clicked.connect(self.read_news_item)
        news_slider_layout.addWidget(self.news_box, alignment=Qt.AlignLeft)
        # 广告图片轮播栏
        self.image_slider = ImageSlider(parent=self)
        self.image_slider.image_clicked.connect(self.read_advertisement)
        news_slider_layout.addWidget(self.image_slider)
        layout.addLayout(news_slider_layout)
        # 左下角菜单折叠窗
        # 菜单-显示窗布局
        box_frame_layout = QHBoxLayout()
        # 菜单滚动折叠窗
        self.folded_box = ScrollFoldedBox(parent=self)
        # self.folded_box.getFoldedBoxMenu()  # 初始化获取它的内容再加入布局
        self.folded_box.left_mouse_clicked.connect(self.folded_box_clicked)
        box_frame_layout.addWidget(self.folded_box, alignment=Qt.AlignLeft)
        # 显示窗
        self.frame_window = LoadedPage(parent=self)
        box_frame_layout.addWidget(self.frame_window)
        layout.addLayout(box_frame_layout)
        container.setLayout(layout)
        self.setWidget(container)
        self.setWidgetResizable(True)  # 内部控件可随窗口调整大小
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 设置折叠窗的样式
        self.folded_box.setFoldedStyleSheet("""
        #foldedHead{
            background-color: rgb(145,202,182);
            border-bottom: 1px solid rgb(200,200,200);
            max-height: 30px;
        }
        #headLabel{
            padding:8px 5px;
            font-weight: bold;
            font-size: 15px;
        }
        #foldedBody{
            background-color: rgb(240, 240, 240);
        }
        """)
        # 设置滚动条样式
        with open("media/ScrollBar.qss", "rb") as fp:
            content = fp.read()
            encoding = chardet.detect(content) or {}
            content = content.decode(encoding.get("encoding") or "utf-8")
        self.setStyleSheet(content)

    def resizeEvent(self, event):
        super(HomePage, self).resizeEvent(event)
        # 控制新闻控件的大小
        box_width = self.parent().width() * 0.3
        box_height = box_width / 8 * 3
        self.news_box.setFixedSize(box_width, box_height)
        # 计算当前控件能容纳的条目数
        self.news_box.setItemCount(floor(box_height / 25))
        # 控制广告图形的高度
        self.image_slider.setFixedHeight(box_height)
        # 控制左下角折叠窗的宽度
        self.folded_box.setMinimumWidth(box_width)
        # 重新设置body的排序数量
        self.folded_box.setBodyHorizationItemCount()
    # 阅读更多新闻
    def read_more_news(self):
        page = MoreNewsPage()
        self.parent().clear()
        self.parent().addWidget(page)
        page.getCurrentNews()  # 请求数据

    # 阅读一条新闻
    def read_news_item(self, news_id):
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

    # 根据当前需求显示获取新闻公告数据
    def getCurrentNews(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/news/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            news_list = [NewsItem(title=news_item['title'],
                                  create_time=news_item['create_time'],
                                  item_id=news_item['id'], parent=self) for news_item in response['data']]
            self.news_box.addItems(news_list)
            more_button = self.news_box.setMoreNewsButton()
            more_button.clicked.connect(self.read_more_news)  # 阅读更多新闻

    # 获取当前广告轮播数据
    def getCurrentSliderAdvertisement(self):
        self.image_slider.addImages(['media/slider/' + path for path in os.listdir('media/slider')])

    # 点击阅读广告
    def read_advertisement(self, name):
        # 请求广告数据
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/advertise/' + name + '/?mc=' +settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            # 根据具体情况显示内容
            ad_data = response['data']
            if ad_data['file']:
                # 显示文件
                file = settings.STATIC_PREFIX + ad_data['file']
                popup = PDFContentPopup(title=ad_data['name'], file=file, parent=self)
            else:
                popup = TextContentPopup(title=ad_data['name'], content=ad_data['content'], parent=self)  # 显示内容
            if not popup.exec_():
                popup.deleteLater()
                del popup

    # 获取折叠窗的数据
    def getFoldedBoxContent(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/data-category/all/?mc=' + settings.app_dawn.value('machine')
            )
            if r.status_code != 200:
                raise ValueError('获取折叠窗数据失败.')
            response = json.loads(r.content.decode('utf-8'))
        except Exception:
            pass
        else:
            # 重新组织数据
            data_category = dict()
            for category_item in response['data']:
                group = category_item['group']
                if group not in data_category.keys():
                    data_category[group] = list()
                data_category[group].append({'id': category_item['id'], 'name': category_item['name']})
            for key, values in data_category.items():
                data_category[key].append({'id': -1, 'name': '其他'})  # 加入其他选项
                head = self.folded_box.addHead(key)  # 一个group就得一个Head
                body = self.folded_box.addBody(head=head)
                body.addButtons(values)
                # body.setHead(head)
            # 加入现货报表和财经日历
            spot_head = self.folded_box.addHead('现货报表')
            finance_head = self.folded_box.addHead('财经日历')
            spot_body = self.folded_box.addBody(head=spot_head)
            spot_body.addButtons([{'id': -1, 'name': '昨日数据'}, {'id': 0, 'name': '今日数据'}])
            # spot_body.setHead(spot_head)
            finance_body = self.folded_box.addBody(head=finance_head)
            finance_body.addButtons([{'id': -1, 'name': '昨日数据'}, {'id': 0, 'name': '今日数据'}])
            self.folded_box.container.layout().addStretch()

    # 折叠盒子被点击
    def folded_box_clicked(self, category_id, head_text):
        # print('点击折叠盒子', category_id, head_text)
        # 根据头部text显示窗口
        if head_text == u'常规报告':
            page = NormalReportPage(category_id=category_id, parent=self.frame_window)
            page.getVarietyCombo()
        elif head_text == u'交易通知':
            page = TransactionNoticePage(category_id=category_id, parent=self.frame_window)
            page.getCurrentNotices()
        elif head_text == u'现货报表':
            page = SpotCommodityPage(delta_days=category_id, parent=self.frame_window)
            page.getCurrentSpotCommodity()
        elif head_text == u'财经日历':
            page = FinanceCalendarPage(delta_days=category_id, parent=self.frame_window)
            page.getCurrentFinanceCalendar()
        else:
            page = QLabel('暂无相关数据...', styleSheet='color:rgb(200,100,50)', alignment=Qt.AlignCenter)
        self.frame_window.clear()
        self.frame_window.addWidget(page)



