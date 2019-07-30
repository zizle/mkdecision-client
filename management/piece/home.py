# _*_ coding:utf-8 _*_
"""
all customer-widget in home page
Update: 2019-07-26
Author: zizle
"""
import sys
import json
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QColor, QBrush, QPixmap
from PyQt5.QtCore import QTimer, Qt, QPoint, QPropertyAnimation, QVariant, QEasingCurve

import config
from threads import RequestThread


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
            print(self.pixmap())


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
        self.clear()
        self.horizontalHeader().setVisible(False)
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
        self.clear()
        self.horizontalHeader().setVisible(False)
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




