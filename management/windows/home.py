# _*_ coding:utf-8 _*_
"""
首页窗口
Update: 2019-11-22
Author: zizle
"""
import os
import chardet
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTabWidget, QScrollArea
from PyQt5.QtCore import Qt

from widgets.base import FoldedBox
from widgets.home import NewsItem, ImageSlider
from piece.home import NewsBox


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

        # 品种非滚动折叠窗
        self.variety_box = FoldedBox(parent=self)
        head1 = self.variety_box.addHead('第1个品种分组')
        head2 = self.variety_box.addHead('第2个品种分组')
        head3 = self.variety_box.addHead('第3个品种分组')
        body2 = self.variety_box.addBody(head=head2)
        buttons = [QPushButton('品种' + str(i)) for i in range(40)]
        body2.addButtons(buttons, horizontal_count=2)

        buttons = [QPushButton('品种' + str(i)) for i in range(55)]
        body1 = self.variety_box.addBody(head=head1)
        body1.addButtons(buttons, horizontal_count=2)
        self.variety_box.addStretch()
        # 显示窗
        self.tab_frame = QTabWidget(parent=self)
        # self.tab_frame.setDocumentMode(True)
        # 菜单-显示窗加入布局
        box_frame_layout.addWidget(self.variety_box, alignment=Qt.AlignLeft)
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

