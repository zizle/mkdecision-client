# _*_ coding:utf-8 _*_
# __Author__： zizle
import os
import json
import requests
import chardet
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QStackedWidget, QScrollArea, QPushButton, \
    QTabWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from widgets.base import ScrollFoldedBox

""" 【更多新闻】页面"""


class MoreNewsPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(MoreNewsPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.addWidget(QLabel('暂无更多新闻，关注其他资讯...', styleSheet='font-size:18px;color:rgb(200,120,130)')
                         , alignment=Qt.AlignCenter)
        self.setLayout(layout)


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
        }
        #createTime{
            padding:0 5px;
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
        }
        #createTime{
            padding:0 5px;
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


# 新闻公告板块
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

    # 设置更多按钮
    def setMoreNewsButton(self):
        count = self.layout().count()
        self.layout().insertWidget(count, self.more_button, alignment=Qt.AlignRight)
        return self.more_button


""" 图片广告轮播相关 """


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
            image_container = QLabel(parent=self, objectName='imageContainer')
            image_container.setScaledContents(True)
            image_container.setPixmap(pix_map)
            self.addWidget(image_container)
        print(self.count())


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
        news_slider_layout.addWidget(self.image_slider)
        layout.addLayout(news_slider_layout)
        # 左下角菜单折叠窗
        # 菜单-显示窗布局
        box_frame_layout = QHBoxLayout()
        # 菜单滚动折叠窗
        self.folded_box = ScrollFoldedBox(parent=self)
        self.folded_box.getFoldedBoxMenu()  # 初始化获取它的内容再加入布局
        box_frame_layout.addWidget(self.folded_box, alignment=Qt.AlignLeft)
        # 显示窗
        self.frame_window = QTabWidget(parent=self)
        box_frame_layout.addWidget(self.frame_window)
        layout.addLayout(box_frame_layout)
        container.setLayout(layout)
        self.setWidget(container)
        self.setWidgetResizable(True)  # 内部控件可随窗口调整大小
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 始终不显示右侧滚动条
        # 设置滚动条样式(包含子控件)
        with open("media/ScrollBar.qss", "rb") as fp:
            content = fp.read()
            encoding = chardet.detect(content) or {}
            content = content.decode(encoding.get("encoding") or "utf-8")
        self.setStyleSheet(content)

    # 阅读更多新闻
    def read_more_news(self):
        print('阅读更多新闻')
        self.more_news_signal.emit(True)

    # 阅读一条新闻
    def read_news_item(self, news_id):
        print('阅读一条新闻', news_id)

    # 根据当前需求显示获取新闻公告数据
    def getCurrentNews(self):
        news_list = [NewsItem(title=str(i) + ' 新闻新闻新闻新闻新闻新闻新闻新闻标题', create_time='2019-11-22',
                              item_id=i, parent=self) for i in range(11)]
        self.news_box.addItems(news_list)
        more_button = self.news_box.setMoreNewsButton()
        more_button.clicked.connect(self.read_more_news)  # 阅读更多新闻

    # 获取当前广告轮播数据
    def getCurrentSliderAdvertisement(self):
        print('获取当前广告轮播的数据')
        self.image_slider.addImages(['media/slider/' + path for path in os.listdir('media/slider')])



