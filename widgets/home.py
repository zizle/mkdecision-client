# _*_ coding:utf-8 _*_
# Author: zizle QQ:462894999

import os
import json
import requests
import chardet
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTabWidget, QScrollArea, QPushButton, \
    QStackedWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
import settings
from widgets.base import ScrollFoldedBox
# from widgets.base import ScrollFoldedBox
# from widgets.home import NewsItem, ImageSlider
# from piece.home import NewsBox
# from frame.home import HomeNormalReport, HomeTransactionNotice

""" 首页相关控件 """


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





# 首页可滚动窗口
class HomePage(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(HomePage, self).__init__(*args, **kwargs)
        container = QWidget(parent=self)
        layout = QVBoxLayout(margin=2)
        news_layout = QHBoxLayout()  # 新闻-轮播布局
        # 新闻公告栏
        news_box = NewsBox(parent=self)
        news_box.addItems([NewsItem(title=str(i) + ' 新闻新闻新闻新闻新闻新闻新闻新闻标题', create_time='2019-11-22',
                                    item_id=i, parent=news_box) for i in range(8)])
        news_more_button = news_box.setMoreNewsButton()  # 设置更多按钮
        news_more_button.clicked.connect(self.read_more_news)  # 更多按钮点击事件
        # 图片轮播栏
        image_slider = ImageSlider(parent=self)
        image_slider.addImages(['media/slider/' + path for path in os.listdir('media/slider')])
        # 新闻-轮播加入布局
        news_layout.addWidget(news_box, alignment=Qt.AlignLeft)
        news_layout.addWidget(image_slider)

        self.setMinimumHeight(self.parent().height())  # 必须在大小控制之前设置
        self.setMinimumWidth(self.parent().width() - 20)  # 减掉一部分避免布局的padding/margin等影响，出现横向滚动条
        # 新闻-轮播大小控制
        news_box.setMinimumWidth(self.width() * 0.3)
        news_box.setMinimumHeight(self.height() * 0.35)
        news_box.setMaximumHeight(self.height() * 0.45)
        image_slider.setMaximumHeight(self.height() * 0.45)

        # 菜单-显示窗布局
        box_frame_layout = QHBoxLayout()

        # 菜单滚动折叠窗
        self.folded_box = ScrollFoldedBox(parent=self)
        self.folded_box.left_mouse_clicked.connect(self.folded_box_clicked)
        self.folded_box.setMinimumWidth(230)
        # head1 = self.variety_box.addHead('第1个品种分组')
        # head2 = self.variety_box.addHead('第2个品种分组')
        # head3 = self.variety_box.addHead('第3个品种分组')
        # body2 = self.variety_box.addBody(head=head2)
        # buttons = [QPushButton('品种' + str(i)) for i in range(40)]
        # body2.addButtons(buttons, horizontal_count=2)
        #
        # buttons = [QPushButton('品种' + str(i)) for i in range(55)]
        # body1 = self.variety_box.addBody(head=head1)
        # body1.addButtons(buttons, horizontal_count=2)
        # self.variety_box.addStretch()
        self.getModuleMenu()
        # 显示窗
        self.tab_frame = QTabWidget(parent=self)
        self.tab_frame.setDocumentMode(True)
        self.tab_frame.tabBar().hide()
        # 菜单-显示窗加入布局
        box_frame_layout.addWidget(self.folded_box, alignment=Qt.AlignLeft)
        box_frame_layout.addWidget(self.tab_frame)

        # 总布局加入布局或控件
        layout.addLayout(news_layout)
        layout.addLayout(box_frame_layout)
        # 内部控件加入布局
        container.setLayout(layout)
        # 滚动区设置内部控件
        self.setWidget(container)
        self.setWidgetResizable(True)  # 内部控件可随窗口调整大小
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # 始终显示右侧滚动条
        # 设置滚动条样式
        with open("media/ScrollBar.qss", "rb") as fp:
            content = fp.read()
            encoding = chardet.detect(content) or {}
            content = content.decode(encoding.get("encoding") or "utf-8")
        self.setStyleSheet(content)

    # 点更多新闻按钮
    def read_more_news(self):
        print('点击了新闻【更多>>】')

    # 点击做下角菜单
    def folded_box_clicked(self, signal):
        print('点击了分组%s-组id%d-菜单%d' % (signal['group_text'], signal['group_id'], signal['category_id']))
        # 根据group_text实例化窗口显示
        if signal['group_text'] == u'常规报告':
            frame_show = HomeNormalReport(group_id=signal['group_id'], category_id=signal['category_id'])
            frame_show.getVarieties()
        elif signal['group_text'] == u'交易通知':
            frame_show = HomeTransactionNotice(group_id=signal['group_id'], category_id=signal['category_id'])
            frame_show.getNotices()
        else:
            frame_show = QLabel('该模块正在加紧开放中.\n感谢您的支持...', alignment=Qt.AlignCenter)
        self.tab_frame.clear()
        self.tab_frame.addTab(frame_show, '')

    # 获取左下角菜单数据
    def getModuleMenu(self):
        try:
            r = requests.get(
                url=settings.SERVER + 'home/groups-categories/?mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            return
        for head_item in response['data']:
            if head_item['name'] in [u'新闻公告', u'广告展示']:  # 去除【新闻公告】和【广告展示】
                continue
            head = self.folded_box.addHead(head_item['name'])
            body = self.folded_box.addBody(head=head)
            if head_item['name'] in [u'常规报告', u'交易通知']:  # 常规报告和交易通知加入一个全部和一个其他, 【全部】的id为0【其他】的id为-1
                head_item['categories'].insert(0, {'id': 0, 'name': '全部', 'group': head_item['id']})
                head_item['categories'].append({'id': -1, 'name': '其他', 'group': head_item['id']})
            body.addButtons(group_text=head_item['name'], button_list=head_item['categories'])
        self.folded_box.addStretch()  # 添加底部伸缩

