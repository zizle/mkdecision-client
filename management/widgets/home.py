# _*_ coding:utf-8 _*_
"""
Create: 2019-08-15
Author: zizle
"""
import sys
import json
import requests
import webbrowser
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QAbstractItemView, QLabel,\
    QPushButton, QStackedWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QPixmap

import config
from thread.request import RequestThread
from popup.base import ShowServerPDF, ShowHtmlContent


# 新闻公告条目
class NewsItem(QWidget):
    item_clicked = pyqtSignal(int)

    def __init__(self, title='', create_time='', item_id=None, *args, **kwargs):
        super(NewsItem, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0)
        title_btn = QPushButton(title)
        self.item_id = item_id
        title_btn.clicked.connect(lambda: self.item_clicked.emit(self.item_id))
        time = QLabel(create_time)
        layout.addWidget(title_btn, alignment=Qt.AlignLeft)
        layout.addWidget(time, alignment=Qt.AlignRight)
        self.setLayout(layout)
        # 样式
        title_btn.setCursor(Qt.PointingHandCursor)
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        self.setObjectName('newsItem')
        self.setStyleSheet("""
        #newsItem{
            border-bottom: 1px solid rgb(200,200,200);
            min-height:25px;
            max-height:25px;
        }
        QPushButton{
            border:none;
        }
        QPushButton:hover{
            color:rgb(100,20,240)
        }
        """)


# 轮播图控件
class ImageSlider(QStackedWidget):
    def __init__(self, *args, **kwargs):
        super(ImageSlider, self).__init__(*args, **kwargs)
        self.setObjectName('imageSlider')
        self.setStyleSheet("""
        #imageSlider{
            background-color: rgb(120,150,120)
        }
        """)

    # 添加图片
    def addImages(self, url_list):
        for img_path in url_list:
            pix_map = QPixmap(img_path)
            image_container = QLabel()
            image_container.setScaledContents(True)
            image_container.setPixmap(pix_map)
            self.addWidget(image_container)
        print(self.count())




# 轮播图控件
class ImageSlider1(QLabel):
    pixmap_list = list()

    def __init__(self, *args, **kwargs):
        super(ImageSlider1, self).__init__(*args, **kwargs)
        # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.change_carousel_pixmap)
        # initial property
        self.ad_name = None
        self.ad_file = None
        self.ad_content = None
        self.ad_redirect = None
        self.pixmap_flag = 0
        self.setScaledContents(True)
        # actions
        self.carousel_thread = None
        self.setObjectName('imageSlider')
        self.setStyleSheet("""
        #imageSlider{
            background-color: rgb(120,150,120)
        }
        """)

    def addImages(self, pixmap_list):
        self.pixmap_list = pixmap_list
        # for index, item in enumerate(pixmap_list):
            # rep = requests.get(config.SERVER_ADDR + item['image'])
            # pixmap = QPixmap()
            # pixmap.loadFromData(rep.content)
            # # add property
            # pixmap.index = index  # index in self.pixmap
            # pixmap.name = item['name']
            # pixmap.file = item['file']
            # pixmap.redirect = item['redirect']
            # pixmap.content = item['content']
            # append list
            # self.pixmap_list.append(pixmap)
        # set pixmap
        if len(self.pixmap_list)>0:
            initial_pixmap = self.pixmap_list[self.pixmap_flag]
            self.setPixmap(initial_pixmap)
            self.ad_name = initial_pixmap.name
            self.ad_file = initial_pixmap.file
            self.ad_content = initial_pixmap.content
            self.ad_redirect = initial_pixmap.redirect
            # start timer change pixmap
            if len(self.pixmap_list) > 1:
                self.timer.start(5000)

    # 轮播改变图片显示
    def change_carousel_pixmap(self):
        # self.animation.start()
        self.pixmap_flag += 1
        if self.pixmap_flag >= len(self.pixmap_list):
            self.pixmap_flag = 0
        pixmap = self.pixmap_list[self.pixmap_flag]
        # change self property
        self.ad_name = pixmap.name
        self.ad_file = pixmap.file
        self.ad_content = pixmap.content
        self.ad_redirect = pixmap.redirect
        self.setPixmap(self.pixmap_list[self.pixmap_flag])

    # 鼠标点击
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print('鼠标点击了广告轮播')
            return
            if self.ad_file:
                popup = ShowServerPDF(file_url=config.SERVER_ADDR + self.ad_file, file_name=self.ad_name)
                popup.deleteLater()
                popup.exec()
                del popup
            elif self.ad_content:
                popup = ShowHtmlContent(content=self.ad_content, title=self.ad_name)
                popup.deleteLater()
                popup.exec()
                del popup
            elif self.ad_redirect:
                webbrowser.open(self.ad_redirect)
                return
            else:
                return

