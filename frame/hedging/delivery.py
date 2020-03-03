# _*_ coding: utf-8 _*_
# Author: zizle QQ: 462894999
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QUrl, QFile
import settings
from widgets.web_view import WebView

# 交割首页
class DeliveryPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(DeliveryPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0, spacing=0)
        self.tab = QTabWidget(parent=self)
        # self.tab.setAutoFillBackground(True)  # 设置背景,否则由于受到父窗口的影响导致透明
        self.tab.tabCloseRequested.connect(self.close_tab)
        self.tab.tabBarClicked.connect(self.tab_changed)
        # self.tab.setTabBarAutoHide(True)
        self.tab.setTabsClosable(False)
        palette = self.tab.palette()
        palette.setColor(palette.Window, QColor(255, 255, 255))
        self.tab.setPalette(palette)
        # layout.addWidget(title_bar)
        layout.addWidget(self.tab)
        # 主页面内容
        self.web_show = WebView()
        # .load(QUrl('file:///html/home.html')
        # html_path = QCoreApplication.applicationDirPath(se) /+ 'media/hedging/html/test.html'
        self.web_show.load(QUrl("file:///" + 'media/hedging/html/home.html'))  # 加载首页
        # 交流讨论页
        self.href = WebView()
        self.href.page().load(QUrl(settings.STATIC_PREFIX + 'delivery/html/communication.html'))
        # 关于我们的页面
        self.link_us = WebView()
        self.link_us.page().load(QUrl(settings.STATIC_PREFIX + 'delivery/html/linkus.html'))
        self.tab.addTab(self.web_show, "交割服务")
        self.tab.addTab(self.href, "交流讨论")
        self.tab.addTab(self.link_us, "关于我们")
        self.setLayout(layout)
        self.tab.setStyleSheet("""
        QTabBar::pane{
            border: 0.5px solid rgb(180,180,180);
        }
        QTabBar::tab{
            min-height: 25px
        }
        QTabBar::tab:selected {

        }
        QTabBar::tab:!selected {
            background-color:rgb(180,180,180)
        }
        QTabBar::tab:hover {
            color: rgb(20,100,230);
            background: rgb(220,220,220)
        }
        """)

    # 关闭tab
    def close_tab(self, index):
        self.tab.removeTab(index)
        self.tab.setCurrentIndex(0)

    # 页面切换
    def tab_changed(self, index):
        if index == 1:  # 讨论交流页面
            self.href.reload()
        elif index == 0:  # 交割通页面
            self.web_show.reload()
        elif index == 2:
            self.link_us.reload()








