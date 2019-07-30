# _*_ coding:utf-8 _*_
"""
all customer-widget in home page
Create: 2019-07-25
Author: zizle
"""
import sys
import json
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QColor, QBrush, QPixmap, QCursor
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QDate, QRect

import config
from threads import RequestThread

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


class Carousel(QLabel):
    pixmap_list = list()

    def __init__(self):
        super(Carousel, self).__init__()
        self.message_btn = QPushButton('刷新中...', self)
        self.message_btn.resize(100, 20)
        self.message_btn.move(80, 50)
        self.message_btn.setStyleSheet('text-align:center;border:none;background-color:rgb(210,210,210)')
        self.message_btn.clicked.connect(self.get_carousel)
        self.message_btn.hide()
        self.pixmap_flag = 0
        self.setMaximumHeight(350)
        self.setScaledContents(True)
        self.get_carousel()

    def carousel_thread_back(self, content):
        # set advertisement carousel
        print('piece.home.py {} 轮播数据: '.format(str(sys._getframe().f_lineno)), content)
        if content['error']:
            self.message_btn.setText('失败,请重试!')
            self.message_btn.setEnabled(True)
        else:
            if not content['data']:
                self.message_btn.setText('完成,无数据.')
                return  # function finished
            else:
                self.message_btn.setText('刷新完成!')
                self.message_btn.hide()
        # create advertisements carousel
        for index, item in enumerate(content['data']):
            rep = requests.get(config.SERVER_ADDR + item['image'])
            pixmap = QPixmap()
            pixmap.loadFromData(rep.content)
            self.pixmap_list.append(pixmap)
        # set pixmap
        self.setPixmap(self.pixmap_list[self.pixmap_flag])
        # change pixmap
        self.timer = QTimer()
        self.timer.timeout.connect(self.change_carousel_pixmap)
        self.timer.start(5000)

    def change_carousel_pixmap(self):
        # self.animation.start()
        self.pixmap_flag += 1
        if self.pixmap_flag >= len(self.pixmap_list):
            self.pixmap_flag=0
        self.setPixmap(self.pixmap_list[self.pixmap_flag])

    def get_carousel(self):
        # get advertisement carousel data
        self.message_btn.setText('刷新中...')
        self.message_btn.show()
        self.message_btn.setEnabled(False)
        self.carousel_thread = RequestThread(
            url=config.SERVER_ADDR + 'homepage/carousel/',
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.carousel_thread.finished.connect(self.carousel_thread.deleteLater)
        self.carousel_thread.response_signal.connect(self.carousel_thread_back)
        self.carousel_thread.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print('piece.home.py {} 广告图:'.format(str(sys._getframe().f_lineno)), self.pixmap())


class MenuTree(QTreeWidget):
    def __init__(self, menu_parent, *args, **kwargs):
        super(MenuTree, self).__init__(*args, **kwargs)
        self.menu_parent = menu_parent  # parent menu id
        # button to show request message and fail retry
        self.message_btn = QPushButton('刷新中...', self)
        self.message_btn.resize(100, 20)
        self.message_btn.move(80, 50)
        self.message_btn.setStyleSheet('text-align:center;border:none;background-color:rgb(210,210,210)')
        self.message_btn.clicked.connect(self.get_menus)
        self.message_btn.hide()
        # menu tree style
        self.setMaximumWidth(300)
        self.setExpandsOnDoubleClick(False)
        self.setRootIsDecorated(False)  # remove root icon
        self.setHeaderHidden(True)
        self.get_menus()

    def get_menus(self):
        self.message_btn.setText('刷新中...')
        self.message_btn.show()
        self.message_btn.setEnabled(False)
        headers = config.CLIENT_HEADERS
        self.menu_thread = RequestThread(
            url=config.SERVER_ADDR + "basic/module/?parent={}".format(self.menu_parent),
            method='get',
            headers=headers,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.menu_thread.response_signal.connect(self.menu_thread_back)
        self.menu_thread.finished.connect(self.menu_thread.deleteLater)
        self.menu_thread.start()

    def menu_thread_back(self, content):
        print('piece.home.py {} 主页左菜单：'.format(str(sys._getframe().f_lineno)), content)
        if content['error']:
            self.message_btn.setText('失败,请重试!')
            self.message_btn.setEnabled(True)
        else:
            if not content['data']:
                self.message_btn.setText('完成,无数据.')
                return  # function finished
            else:
                self.message_btn.setText('刷新完成!')
                self.message_btn.hide()
        # fill tree menu
        for menu in content['data']:
            menu_item = QTreeWidgetItem(self)
            menu_item.setText(0, menu['name'])
            # menu.setTextAlignment(0, Qt.AlignCenter)
            menu_item.id = menu['id']


class ShowBulletin(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(ShowBulletin, self).__init__(*args)
        # button to show request message and fail retry
        self.message_btn = QPushButton('刷新中...', self)
        self.message_btn.resize(100, 20)
        self.message_btn.move(100, 50)
        self.message_btn.setStyleSheet('text-align:center;border:none;background-color:rgb(210,210,210)')
        self.message_btn.clicked.connect(self.get_bulletin)
        self.message_btn.hide()
        # table style
        self.setFixedSize(300,350)
        self.setMouseTracking(True)
        self.setShowGrid(False)  # no grid
        self.setFocusPolicy(0)  # No empty box appears in the selection
        self.setSelectionMode(QAbstractItemView.NoSelection)  # hold the style(exp:font color)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # no edit
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setStyleSheet("""
        QTableWidget{
            background-color:rgb(255,255,255);
            border: 1px solid rgb(220,220,220);
        }
        QTableWidget::item{
            border-bottom: 1px solid rgb(200,200,200);
            cursor:hand;
        }
        QScrollBar:vertical
        {
            width:8px;
            background:rgba(0,0,0,0%);
            margin:0px,0px,0px,0px;
            /*留出8px给上面和下面的箭头*/
            padding-top:8px;
            padding-bottom:8px;
        }
        QScrollBar::handle:vertical
        {
            width:8px;
            background:rgba(0,0,0,8%);
            /*滚动条两端变成椭圆*/
            border-radius:4px;

        }
        QScrollBar::handle:vertical:hover
        {
            width:8px;
            /*鼠标放到滚动条上的时候，颜色变深*/
            background:rgba(0,0,0,40%);
            border-radius:4px;
            min-height:20;
        }
        QScrollBar::add-line:vertical
        {
            height:9px;width:8px;
            /*设置下箭头*/
            border-image:url(media/scroll/3.png);
            subcontrol-position:bottom;
        }
        QScrollBar::sub-line:vertical 
        {
            height:9px;width:8px;
            /*设置上箭头*/
            border-image:url(media/scroll/1.png);
            subcontrol-position:top;
        }
        QScrollBar::add-line:vertical:hover
        /*当鼠标放到下箭头上的时候*/
        {
            height:9px;width:8px;
            border-image:url(media/scroll/4.png);
            subcontrol-position:bottom;
        }
        QScrollBar::sub-line:vertical:hover
        /*当鼠标放到下箭头上的时候*/
        {
            height:9px;
            width:8px;
            border-image:url(media/scroll/2.png);
            subcontrol-position:top;
        }
        """)
        self.cellClicked.connect(self.cell_clicked)
        self.get_bulletin()  # threading

    def get_bulletin(self):
        self.message_btn.setText('刷新中...')
        self.message_btn.show()
        self.message_btn.setEnabled(False)
        headers = {"User-Agent": "DAssistant-Client/" + config.VERSION}
        self.ble_thread = RequestThread(
            url=config.SERVER_ADDR + "homepage/bulletin/",
            method='get',
            headers=headers,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.ble_thread.response_signal.connect(self.ble_thread_back)
        self.ble_thread.finished.connect(self.ble_thread.deleteLater)
        self.ble_thread.start()

    def ble_thread_back(self, content):
        print('piece.home.py {} 公告: '.format(str(sys._getframe().f_lineno)), content)
        if content['error']:
            self.message_btn.setText('失败,请重试!')
            self.message_btn.setEnabled(True)
        else:
            if not content['data']:
                self.message_btn.setText('完成,无数据.')
                return  # function finished
            else:
                self.message_btn.setText('刷新完成!')
                self.message_btn.hide()
        # fill table
        keys = ["name", "file", "create_time"]
        bulletins = content['data']
        self.setRowCount(len(bulletins))
        self.setColumnCount(len(keys))
        self.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
        self.horizontalHeader().setSectionResizeMode(1, 3)  # 第1列随文字宽度
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 第1列随文字宽度
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if col == 1:
                    item = QTableWidgetItem("查看")
                    item.file = bulletins[row]["file"]
                    item.content = bulletins[row]["content"]
                else:
                    item = QTableWidgetItem(str(bulletins[row][keys[col]]))
                    font = QFont()
                    if col == self.columnCount() - 1:
                        size = 8
                        item.setFont(QFont(font))
                    else:
                        size = 10
                    font.setPointSize(size)
                    item.setFont(QFont(font))
                self.setItem(row, col, item)

    def cell_clicked(self, row, col):
        print('piece.home.py {} 点击公告:'.format(str(sys._getframe().f_lineno)), row, col)
        if col == 1:
            item = self.item(row, col)
            name_item = self.item(row, 0)
            if item.file:
                from utils import get_server_file
                get_server_file(url=config.SERVER_ADDR + item.file, file=item.file, title=name_item.text())
            elif item.content:
                from widgets.dialog import ContentReadDialog
                read_dialog = ContentReadDialog(content=item.content, title=name_item.text())
                if not read_dialog.exec():
                    del read_dialog  # 弹窗生命周期未结束,手动删除
            else:
                pass

    def leaveEvent(self, *args, **kwargs):
        """鼠标离开控件"""
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                self.item(row, col).setForeground(QBrush(QColor(0, 0, 0)))  # 改变了其他的item字体色

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        # 获取当前这个item
        current_item = self.itemAt(event.pos())
        if current_item:
            row = current_item.row()
            for item in [self.item(row, col) for col in range(self.columnCount())]:
                # item.setBackground(QBrush(QColor(200, 200, 200)))  # 改变了当前的item背景色
                item.setForeground(QBrush(QColor(255, 10, 20)))  # 改变了当前的item字体色
            for other_row in range(self.rowCount()):
                if other_row == row:
                    continue
                for other_item in [self.item(other_row, col) for col in range(self.columnCount())]:
                    # other_item.setBackground(QBrush(QColor(240, 240, 240)))  # 改变了其他的item背景色
                    other_item.setForeground(QBrush(QColor(0, 0, 0)))  # 改变了其他的item字体色


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
        self.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = QTableWidgetItem(str(commodities[row][set_keys[col]]))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, item)


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
        labels.append(' ')
        self.setHorizontalHeaderLabels(labels)
        self.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
        self.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
        self.horizontalHeader().setSectionResizeMode(1, 3)  # 第1列随文字宽度
        self.horizontalHeader().setSectionResizeMode(2, 3)  # 第1列随文字宽度
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = QTableWidgetItem(str(finance[row][set_keys[col]]))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, item)

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


class ShowNotice(QTableWidget):
    def __init__(self, *args):
        super(ShowNotice, self).__init__(*args)
        # button to show request message and fail retry
        self.message_btn = QPushButton('刷新中...', self)
        self.message_btn.resize(100, 20)
        self.message_btn.move(100, 50)
        self.message_btn.setStyleSheet('text-align:center;border:none;background-color:rgb(210,210,210)')
        self.verticalHeader().setVisible(False)
        # get notice 获取数据在其父窗口调用,传入url,方便按钮点击的逻辑

    def get_notice(self, url):
        self.message_btn.setText('刷新中...')
        self.message_btn.show()
        self.message_btn.setEnabled(False)
        self.clear()
        self.setRowCount(0)
        self.horizontalHeader().setVisible(False)
        headers = {"User-Agent": "DAssistant-Client/" + config.VERSION}
        self.notice_thread = RequestThread(
            url=url,
            method='get',
            headers=headers,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.notice_thread.response_signal.connect(self.notice_thread_back)
        self.notice_thread.finished.connect(self.notice_thread.deleteLater)
        self.notice_thread.start()

    def notice_thread_back(self, content):
        print('piece.home.py {} 交易通知: '.format(str(sys._getframe().f_lineno)), content)
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
        keys = [('serial_num', '序号'), ("name", "标题"), ("type_zh", "类型"),('create_time', '时间')]
        reports = content['data']
        row = len(reports)
        self.setRowCount(row)
        self.setColumnCount(len(keys) + 1)  # 列数
        labels = []
        set_keys = []
        for key_label in keys:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        labels.append(' ')
        self.setHorizontalHeaderLabels(labels)
        self.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
        self.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
        self.horizontalHeader().setSectionResizeMode(self.columnCount()-1, QHeaderView.ResizeToContents)  # 第2列随文字宽度
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if col == self.columnCount() - 1:
                    item = QTableWidgetItem('查看')
                else:
                    item = QTableWidgetItem(str(reports[row][set_keys[col]]))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, item)


class ShowReport(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(ShowReport, self).__init__(*args)
        # button to show request message and fail retry
        self.message_btn = QPushButton('刷新中...', self)
        self.message_btn.resize(100, 20)
        self.message_btn.move(100, 50)
        self.message_btn.setStyleSheet('text-align:center;border:none;background-color:rgb(210,210,210)')
        self.message_btn.clicked.connect(self.get_report)
        self.verticalHeader().setVisible(False)
        # get report 获取数据在其父窗口调用,传入url,方便按钮点击的逻辑

    def get_report(self, url):
        self.message_btn.setText('刷新中...')
        self.message_btn.show()
        self.message_btn.setEnabled(False)
        self.clear()
        self.setRowCount(0)
        self.horizontalHeader().setVisible(False)
        headers = {"User-Agent": "DAssistant-Client/" + config.VERSION}
        self.report_thread = RequestThread(
            url=url,
            method='get',
            headers=headers,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.report_thread.response_signal.connect(self.report_thread_back)
        self.report_thread.finished.connect(self.report_thread.deleteLater)
        self.report_thread.start()

    def report_thread_back(self, content):
        print('piece.home.py {} 常规报告: '.format(str(sys._getframe().f_lineno)), content)
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
        keys = [('serial_num', '序号'), ("name", "标题"), ("type_zh", "类型"),('create_time', '时间')]
        reports = content['data']
        row = len(reports)
        self.setRowCount(row)
        self.setColumnCount(len(keys) + 1)  # 列数
        labels = []
        set_keys = []
        for key_label in keys:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        labels.append(' ')
        self.setHorizontalHeaderLabels(labels)
        self.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
        self.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
        self.horizontalHeader().setSectionResizeMode(self.columnCount()-1, QHeaderView.ResizeToContents)  # 第2列随文字宽度
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if col == self.columnCount() - 1:
                    item = QTableWidgetItem('查看')
                else:
                    item = QTableWidgetItem(str(reports[row][set_keys[col]]))
                # font = QFont()
                # if col == self.columnCount() - 1:
                #     size = 8
                    # item.setFont(QFont(font))
                # else:
                #     size = 10
                # font.setPointSize(size)
                # item.setFont(QFont(font))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, item)




