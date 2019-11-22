# _*_ coding:utf-8 _*_
"""
all customer-widget in home page
Create: 2019-07-25
Author: zizle
"""
import sys
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QTableWidget, QLabel
from PyQt5.QtGui import QFont, QColor, QBrush, QPixmap, QCursor
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QDate, QRect

import config
from thread.request import RequestThread


# 新闻公告板块
class NewsBox(QWidget):
    def __init__(self, *args, **kwargs):
        super(NewsBox, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0,spacing=0)  # spacing会影响子控件的高度，控件之间有间隔，视觉就影响高度
        # 更多按钮
        self.more_button = QPushButton('更多>>', objectName='moreNews')
        self.more_button.setCursor(Qt.PointingHandCursor)
        self.setLayout(layout)
        self.setObjectName('newsBox')
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        self.setStyleSheet("""
        #newsBox{
            background-color: rgb(100,180,200)
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
            self.layout().addWidget(item, alignment=Qt.AlignTop)

    # 设置更多按钮
    def setMoreNewsButton(self):
        count = self.layout().count()
        self.layout().insertWidget(count, self.more_button, alignment=Qt.AlignRight)
        return self.more_button


# 轮播图控件
class ImageSlider(QWidget):
    def __init__(self, *args, **kwargs):
        super(ImageSlider, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        self.image_stacked = QStackedWidget(parent=self)
        layout.addWidget(self.image_stacked)
        self.pre_button = QPushButton('前', parent=self)
        self.next_button = QPushButton('后', parent=self)
        self.setLayout(layout)
        self.addImages()
        print(self.image_stacked.widget(0).width())
        print(self.pos().x(), self.pos().y())
        print(self.width(),self.height())
        print(self.sizeIncrement())
        print(layout.contentsRect().getRect())

    # 添加图片
    def addImages(self):
        pixmap = QPixmap('media/start.png')
        label = QLabel()
        label.setPixmap(pixmap)
        label.setScaledContents(True)
        self.image_stacked.addWidget(label)




        # 前后按钮的布局

        pre_next_layout = QHBoxLayout(self)
        pre_button = QPushButton('前', parent=self)
        next_button = QPushButton('后', parent=self)
        pre_next_layout.addWidget(pre_button, alignment=Qt.AlignLeft)
        pre_next_layout.addWidget(next_button, alignment=Qt.AlignRight)
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        self.setObjectName('imageSlider')
        self.setStyleSheet("""
        #imageSlider{
            background-color: rgb(120,130,130)
        }

        """)








class Calendar(QWidget):
    click_date = pyqtSignal(QDate)

    def __init__(self):
        super(Calendar, self).__init__()
        self.__dateItems = []
        layout = QVBoxLayout(spacing=10, margin=0)
        # 头布局
        self.headers_layout = QHBoxLayout()
        self.date = QDate.currentDate()  # 整个日历的date属性,获取日历当前的date
        self.date_edit = QDateEdit(self.date)
        self.date_edit.setStyleSheet("""
        QDateEdit{
            border:none;
            height:22px;
            background-color:rgb(240,240,240);
        }
        QDateEdit::drop-down{
           image:url(media/drop-down.png);
        }""")
        self.date_edit.setDisplayFormat("yyyy年MM月dd日")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.dateChanged.connect(self.date_edit_changed)
        self.date_edit.setCursor(QCursor(Qt.PointingHandCursor))
        back_today = QPushButton("回到今日")
        back_today.setCursor(QCursor(Qt.PointingHandCursor))
        back_today.setStyleSheet("border:1px solid rgb(208,177,133);padding:5px 15px;margin-left:15px;")
        back_today.clicked.connect(self.back_today_clicked)
        self.headers_layout.addWidget(self.date_edit)
        self.headers_layout.addWidget(back_today)
        self.headers_layout.addStretch()
        # 内容布局
        contents_layout = QHBoxLayout()
        last_week = QPushButton("< 上周")
        last_week.setCursor(QCursor(Qt.PointingHandCursor))
        last_week.setStyleSheet("border: none;font-size: 12px;font-weight:bold")
        last_week.clicked.connect(self.last_week_clicked)
        # 分割线1
        splitter_line_0 = QFrame()
        splitter_line_0.setEnabled(True)
        splitter_line_0.setGeometry(QRect(110, 170, 3, 61))
        splitter_line_0.setFrameShape(QFrame.VLine)
        splitter_line_0.setFrameShadow(QFrame.Sunken)
        # 分割线2
        splitter_line_1 = QFrame()
        splitter_line_1.setEnabled(True)
        splitter_line_1.setGeometry(QRect(110, 170, 3, 61))
        splitter_line_1.setFrameShape(QFrame.VLine)
        splitter_line_1.setFrameShadow(QFrame.Sunken)
        next_week = QPushButton("下周 >")
        next_week.setCursor(QCursor(Qt.PointingHandCursor))
        next_week.setStyleSheet("border: none;font-size: 12px;font-weight:bold")
        next_week.clicked.connect(self.next_week_clicked)
        contents_layout.addWidget(last_week)
        contents_layout.addWidget(splitter_line_0)
        current_day = QDate.currentDate()  # 当前时间
        sunday = self.__get_sunday(current_day)  # 获取前日期所在周的周日
        monday = sunday.addDays(1)
        tuesday = sunday.addDays(2)
        wednesday = sunday.addDays(3)
        thursday = sunday.addDays(4)
        friday = sunday.addDays(5)
        saturday = sunday.addDays(6)
        self.date_btn_7 = QPushButton(str(sunday.day()) + "\n周日")
        self.date_btn_1 = QPushButton(str(monday.day()) + "\n周一")
        self.date_btn_2 = QPushButton(str(tuesday.day()) + "\n周二")
        self.date_btn_3 = QPushButton(str(wednesday.day()) + "\n周三")
        self.date_btn_4 = QPushButton(str(thursday.day()) + "\n周四")
        self.date_btn_5 = QPushButton(str(friday.day()) + "\n周五")
        self.date_btn_6 = QPushButton(str(saturday.day()) + "\n周六")
        self.date_btn_7.date = sunday
        self.date_btn_1.date = monday
        self.date_btn_2.date = tuesday
        self.date_btn_3.date = wednesday
        self.date_btn_4.date = thursday
        self.date_btn_5.date = friday
        self.date_btn_6.date = saturday
        self.__dateItems.append(self.date_btn_7)
        self.__dateItems.append(self.date_btn_1)
        self.__dateItems.append(self.date_btn_2)
        self.__dateItems.append(self.date_btn_3)
        self.__dateItems.append(self.date_btn_4)
        self.__dateItems.append(self.date_btn_5)
        self.__dateItems.append(self.date_btn_6)
        # 改变今日的样式
        self.__today_style_change()
        contents_layout.addWidget(self.date_btn_7)
        contents_layout.addWidget(self.date_btn_1)
        contents_layout.addWidget(self.date_btn_2)
        contents_layout.addWidget(self.date_btn_3)
        contents_layout.addWidget(self.date_btn_4)
        contents_layout.addWidget(self.date_btn_5)
        contents_layout.addWidget(self.date_btn_6)
        contents_layout.addWidget(splitter_line_1)
        contents_layout.addWidget(next_week)
        layout.addLayout(self.headers_layout)
        layout.addLayout(contents_layout)
        # 点击事件
        self.date_btn_7.clicked.connect(lambda: self.date_clicked(self.date_btn_7))
        self.date_btn_1.clicked.connect(lambda: self.date_clicked(self.date_btn_1))
        self.date_btn_2.clicked.connect(lambda: self.date_clicked(self.date_btn_2))
        self.date_btn_3.clicked.connect(lambda: self.date_clicked(self.date_btn_3))
        self.date_btn_4.clicked.connect(lambda: self.date_clicked(self.date_btn_4))
        self.date_btn_5.clicked.connect(lambda: self.date_clicked(self.date_btn_5))
        self.date_btn_6.clicked.connect(lambda: self.date_clicked(self.date_btn_6))
        self.setFixedHeight(88)
        self.setLayout(layout)

    def __change_date(self, sunday):
        """改变7个按钮的显示及date属性"""
        # 获得当周的每一天
        monday = sunday.addDays(1)
        tuesday = sunday.addDays(2)
        wednesday = sunday.addDays(3)
        thursday = sunday.addDays(4)
        friday = sunday.addDays(5)
        saturday = sunday.addDays(6)
        # 修改各按钮的相关属性及显示字样
        self.date_btn_7.date = sunday
        self.date_btn_7.setText(str(sunday.day()) + "\n周日")
        self.date_btn_1.date = monday
        self.date_btn_1.setText(str(monday.day()) + "\n周一")
        self.date_btn_2.date = tuesday
        self.date_btn_2.setText(str(tuesday.day()) + "\n周二")
        self.date_btn_3.date = wednesday
        self.date_btn_3.setText(str(wednesday.day()) + "\n周三")
        self.date_btn_4.date = thursday
        self.date_btn_4.setText(str(thursday.day()) + "\n周四")
        self.date_btn_5.date = friday
        self.date_btn_5.setText(str(friday.day()) + "\n周五")
        self.date_btn_6.date = saturday
        self.date_btn_6.setText(str(saturday.day()) + "\n周六")

    def __date_btn_style_changed(self, change_btn=None):
        for btn in self.__dateItems:
            if change_btn:
                if btn == change_btn:
                    btn.setStyleSheet("""
                    QPushButton{
                        border:none;
                        font-size:17px;
                        font-weight:bold;
                        color: rgb(255,255,255);
                        background-color: rgb(91,140,185);
                        border-radius: 25px;
                    }
                    QPushButton:hover{
                        font-size:16px;
                        color:rgb(66,111,153);
                        cursor:pointer;
                        font-weight:bold
                    }        
                    """)
                else:
                    btn.setStyleSheet("""
                    QPushButton{
                        border: none;
                        font-size: 14px;
                    }
                    QPushButton:hover{
                        font-size:16px;
                        color:rgb(66,111,153);
                        cursor:pointer;
                        font-weight:bold
                    }
                    """)
            else:
                btn.setStyleSheet("""
                QPushButton{
                    border: none;
                    font-size: 15px;
                }
                QPushButton:hover{
                    font-size:16px;
                    color:rgb(66,111,153);
                    cursor:pointer;
                    font-weight:bold
                }
                """)

    @staticmethod
    def __get_sunday(date):
        """获取参数date所在周的周日"""
        pre_days_count = -(date.dayOfWeek())
        if date.dayOfWeek() == 7:
            pre_days_count = 0
        return date.addDays(pre_days_count)

    def __today_style_change(self):
        """改变今日(当前时间)的显示样式"""
        today = QDate.currentDate()
        for btn in self.__dateItems:
            if btn.date == today:
                btn.setStyleSheet("""
                QPushButton{
                    border: none;
                    font-size: 17px;
                    font-weight:bold;
                    border-radius: 25px;
                    background-color:rgb(180,180,180)
                }
                QPushButton:hover{
                    font-size:16px;
                    color:rgb(66,111,153);
                    cursor:pointer;
                    font-weight:bold
                }
                """)
            else:
                btn.setStyleSheet("""
                QPushButton{
                    border: none;
                    font-size: 14px;
                }
                QPushButton:hover{
                    font-size:16px;
                    color:rgb(66,111,153);
                    cursor:pointer;
                    font-weight:bold
                }
                """)

    def back_today_clicked(self):
        """点击回到今日按钮"""
        # 获取今日日期
        self.date = QDate.currentDate()
        # 改变日期编辑框
        self.date_edit.setDate(self.date)
        # 得到今日所在周的周日
        sunday = self.__get_sunday(self.date)
        # 改变按钮date属性与显示
        self.__change_date(sunday)
        # 改变今日样式
        self.__today_style_change()
        self.click_date.emit(self.date)

    def date_clicked(self, date_btn):
        """点击的时间通过信号传出"""
        self.date = date_btn.date
        self.__date_btn_style_changed(date_btn)
        self.click_date.emit(date_btn.date)

    def date_edit_changed(self):
        """时间输入框的时间改变"""
        self.__date_btn_style_changed()
        # 获取改变后的时间
        edit_date = self.date_edit.date()
        # 改变后的时间所在周的周日
        sunday = self.__get_sunday(edit_date)
        # 改变按钮及date属性
        self.__change_date(sunday)
        # 改变今日(当前时间)样式
        self.__today_style_change()

    def last_week_clicked(self):
        """点击上周, 改变按钮的显示与date属性"""
        self.__date_btn_style_changed()
        # 获取当前的sunday
        cur_sunday = self.date_btn_7.date
        # 得到上周的sunday
        last_sunday = cur_sunday.addDays(-7)
        # 改变时间输入框
        self.date_edit.setDate(last_sunday)
        # 改变按钮的date属性和显示
        self.__change_date(last_sunday)

    def next_week_clicked(self):
        """点击下周, 改变按钮的显示与date属性"""
        self.__date_btn_style_changed()
        # 获取当前的sunday
        cur_sunday = self.date_btn_7.date
        # 得到下周的sunday
        next_sunday = cur_sunday.addDays(7)
        # 改变时间输入框
        self.date_edit.setDate(next_sunday)
        # 改变按钮的date属性与显示
        self.__change_date(next_sunday)

    def set_current_date(self, date):
        self.date_edit.setDate(date)


class ShowCommodity(QTableWidget):
    def __init__(self, *args):
        super(ShowCommodity, self).__init__(*args)
        # button to show request message and fail retry
        self.message_btn = QPushButton('刷新中...', self)
        self.message_btn.resize(100, 20)
        self.message_btn.move(100, 50)
        self.message_btn.setStyleSheet('text-align:center;border:none;background-color:rgb(210,210,210)')
        self.verticalHeader().setVisible(False)
        # get commodity 获取数据在其父窗口调用,传入url,方便按钮点击的逻辑

    def commodity_thread_back(self, content):
        print('piece.home.py {} 现货报表: '.format(str(sys._getframe().f_lineno)), content)
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
        self.horizontalHeader().setVisible(True)
        keys = [('serial_num', '序号'), ("variety", "品种"), ("area", "地区"), ('level', '等级'), ('price', '报价'), ('date', '日期'), ('note', '备注')]
        commodities = content['data']
        row = len(commodities)
        self.setRowCount(row)
        self.setColumnCount(len(keys))  # 列数
        labels = []
        set_keys = []
        for key_label in keys:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        self.setHorizontalHeaderLabels(labels)
        self.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
        self.verticalHeader().setSectionResizeMode(1)
        self.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if col == 0:
                    item = QTableWidgetItem(str(row+1))
                else:
                    item = QTableWidgetItem(str(commodities[row][set_keys[col]]))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, item)
        self.setMinimumHeight(30 + self.rowCount() * 25)


    def get_commodity(self, url):
        self.message_btn.setText('刷新中...')
        self.message_btn.show()
        self.message_btn.setEnabled(False)
        self.clear()
        self.setRowCount(0)
        self.horizontalHeader().setVisible(False)
        headers = {"User-Agent": "DAssistant-Client/" + config.VERSION}
        self.commodity_thread = RequestThread(
            url=url,
            method='get',
            headers=headers,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.commodity_thread.response_signal.connect(self.commodity_thread_back)
        self.commodity_thread.finished.connect(self.commodity_thread.deleteLater)
        self.commodity_thread.start()


class ShowFinance(QTableWidget):
    def __init__(self):
        super(ShowFinance, self).__init__()
        # button to show request message and fail retry
        self.message_btn = QPushButton('刷新中...', self)
        self.message_btn.resize(100, 20)
        self.message_btn.move(100, 50)
        self.message_btn.setStyleSheet('text-align:center;border:none;background-color:rgb(210,210,210)')
        self.verticalHeader().setVisible(False)
        # get finance 获取数据在其父窗口调用,传入url,方便时间选择的逻辑

    def finance_thread_back(self, content):
        print('piece.home.py {} 财经日历: '.format(str(sys._getframe().f_lineno)), content)
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
        self.horizontalHeader().setVisible(True)
        keys = [('serial_num', '序号'), ("date", "日期"), ("time", "时间"), ('country', '地区'), ('event', '事件描述'), ('expected', '预期值')]
        finance = content['data']
        row = len(finance)
        self.setRowCount(row)
        self.setColumnCount(len(keys))  # 列数
        labels = []
        set_keys = []
        for key_label in keys:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        # labels.append(' ')
        self.setHorizontalHeaderLabels(labels)
        self.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
        self.verticalHeader().setSectionResizeMode(1)
        self.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
        self.horizontalHeader().setSectionResizeMode(1, 3)  # 第1列随文字宽度
        self.horizontalHeader().setSectionResizeMode(2, 3)  # 第1列随文字宽度
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if col == 0:
                    item = QTableWidgetItem(str(row+1))
                else:
                    item = QTableWidgetItem(str(finance[row][set_keys[col]]))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, item)
        self.setMinimumHeight(30 + self.rowCount() * 25)


    def get_finance(self, url):
        self.message_btn.setText('刷新中...')
        self.message_btn.show()
        self.message_btn.setEnabled(False)
        self.clear()
        self.setRowCount(0)
        self.horizontalHeader().setVisible(False)
        headers = {"User-Agent": "DAssistant-Client/" + config.VERSION}
        self.finance_thread = RequestThread(
            url=url,
            method='get',
            headers=headers,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.finance_thread.response_signal.connect(self.finance_thread_back)
        self.finance_thread.finished.connect(self.finance_thread.deleteLater)
        self.finance_thread.start()
