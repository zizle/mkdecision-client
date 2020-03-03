# _*_ coding:utf-8 _*_
"""
Create: 2019-08-23
Author: zizle
"""
import json
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QEnterEvent, QPainter, QColor, QPen, QIcon
from PyQt5.QtWebChannel import QWebChannel

from delivery import config
from delivery.widgets.web_view import WebView
from delivery.piece.base import TitleBar
from delivery.utils.channel import ChannelObj, NewsChannelObj
from delivery.utils.pdf import ShowServerPDF
import settings

# 枚举左上右下以及四个定点
Left, Top, Right, Bottom, LeftTop, RightTop, LeftBottom, RightBottom = range(8)


class Base(QWidget):
    # 四周边距
    Margins = 3

    def __init__(self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)
        self.resize(1024, 640)
        # windows centered(three step)
        myself = self.frameGeometry()  # 自身窗体信息(虚拟框架)
        myself.moveCenter(QDesktopWidget().availableGeometry().center())  # 框架中心移动到用户桌面中心
        self.move(myself.topLeft())  # 窗口左上角与虚拟框架左上角对齐
        self._pressed = False  # 按住鼠标标记
        self.Direction = None  # 方向标记
        # 背景透明
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # frame less
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        # 鼠标跟踪(否则与鼠标移动有关的都无法实现)
        self.setMouseTracking(True)
        # 布局
        layout = QVBoxLayout()
        # margins for resize window
        layout.setSpacing(0)
        layout.setContentsMargins(self.Margins, self.Margins, self.Margins, self.Margins)
        # window title
        # title_bar = TitleBar()
        # # signal slot
        # title_bar.windowMinimumed.connect(self.showMinimized)
        # title_bar.windowMaximumed.connect(self.showMaximized)
        # title_bar.windowNormaled.connect(self.showNormal)
        # title_bar.windowClosed.connect(self.close)
        # title_bar.windowMoved.connect(self.move)
        # self.windowTitleChanged.connect(title_bar.setTitle)
        # self.windowIconChanged.connect(title_bar.setIcon)
        # add tab container
        self.tab = QTabWidget()
        self.tab.setAutoFillBackground(True)  # 设置背景,否则由于受到父窗口的影响导致透明
        self.tab.tabCloseRequested.connect(self.close_tab)
        self.tab.tabBarClicked.connect(self.tab_changed)
        # self.tab.setTabBarAutoHide(True)
        self.tab.setTabsClosable(False)
        palette = self.tab.palette()
        palette.setColor(palette.Window, QColor(255, 255, 255))
        self.tab.setPalette(palette)
        self.tab.installEventFilter(self)  # 事件过滤
        # add widgets and layout to main layout
        # layout.addWidget(title_bar)
        layout.addWidget(self.tab)
        self.setLayout(layout)
        # set icon and title
        self.setWindowIcon(QIcon("images/delivery-logo.png"))
        self.setWindowTitle("交割通")
        # 主页
        self.web_show = WebView()
        # self.web_show.page().load(QUrl('file:///html/home.html'))
        # print(config.SERVER + 'media/html/home.html')
        # self.web_show.page().load(QUrl(config.SERVER + 'media/html/home.html'))  # 加载服务端html
        self.web_show.page().load(QUrl(settings.STATIC_PREFIX + 'delivery/html/home.html'))  # 加载服务端html
        # new page更多讨论交流的页面
        self.href = WebView()
        # 新闻公告显示列表页面
        self.nb_list_view = WebView()
        # 关于我们页面
        self.link_us = WebView()
        """js-主窗口交互通道"""
        self.channel_obj = ChannelObj()  # 交互信号对象
        self.channel_obj.serviceGuideSig.connect(self.show_service_guide) # 信号对象收到信息的槽函数连接
        self.channel_obj.moreCommunicationSig.connect(self.more_communication)
        self.channel_obj.newsBulletinShowSig.connect(self.news_bulletin_show)
        self.channel_obj.fileUrlSig.connect(self.get_file_show)
        self.channel_obj.userTokenSig.connect(self.set_user_token)
        web_channel = QWebChannel(self.web_show.page())  # 实例化信息通道
        self.web_show.page().setWebChannel(web_channel)  # 网页设置信息通道
        web_channel.registerObject("messageChannel", self.channel_obj)  # 注册信号对象(在网页中获取)
        """ 新闻公告页面js-与界面交互通道"""
        self.nb_channel_obj = NewsChannelObj()
        self.nb_channel_obj.newsBulletinContentSig.connect(self.news_bulletin_show)
        nb_channel = QWebChannel(self.nb_list_view.page())
        self.nb_list_view.page().setWebChannel(nb_channel)
        nb_channel.registerObject("newsChannel", self.nb_channel_obj)
        self.tab.addTab(self.web_show, '交割通')
        # 交流讨论页
        self.tab.addTab(self.href, '交流讨论')
        # self.href.page().load(QUrl('file:///html/communication.html'))
        self.href.page().load(QUrl(config.SERVER + 'media/html/communication.html'))
        # 关于我们
        self.link_us.page().load(QUrl(config.SERVER + 'media/html/linkus.html'))
        self.tab.addTab(self.link_us, '关于我们')
        # 数据维护页
        if config.CLIENT == 'management':
            from delivery.windows.maintain import DataMaintain
            maintain = DataMaintain()
            self.tab.addTab(maintain, '数据上传')
        # style
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

    def show_service_guide(self, msg):
        # print('展示服务指引', msg)
        # 信息库
        zh_lib = {
            'shfe': '上海期货交易所',
            'dce': '大连商品交易所',
            'czce': '郑州商品交易所',
            'register': '仓库仓单注册流程',
            'cancel': '仓库仓单注销流程',
            'delivery': '交割流程',
            'brand': '品牌名录',
            'hedging': '套保业务'
        }
        # 根据web页面传回的信息读取消息，实例化展示文档的页面，新开tab
        title = zh_lib[msg[0]] + zh_lib[msg[1]]
        file_url = config.SERVER + 'media/guide/' + title + '.pdf'
        content_show = ShowServerPDF(file_url=file_url, file_name=title + '.pdf')
        self.tab.addTab(content_show, title)
        self.tab.setCurrentWidget(content_show)
        self.tab_bar_close_handler()

    def more_communication(self, b):
        if b:
            # print('点击了更多讨论交流')
            # 新实例化一个webEngineView
            # self.href.page().load(QUrl('file:///html/communication.html'))
            # self.tab.addTab(self.href, '讨论交流')
            self.href.reload()
            # self.href.page().load(QUrl(config.SERVER + 'media/html/communication.html'))
            self.tab.setCurrentWidget(self.href)

    def news_bulletin_show(self, article):
        if article[0] == 'get_list':
            # print('显示列表')
            # self.nb_list_view.page().load(QUrl('file:///html/newsbulletin.html'))
            self.nb_list_view.page().load(QUrl(config.SERVER + 'media/html/newsbulletin.html'))
            self.tab.addTab(self.nb_list_view, '新闻/公告列表')
            self.tab.setCurrentWidget(self.nb_list_view)
            self.tab_bar_close_handler()  # 可关闭按钮显示处理
        else:
            # 请求本条新闻公告具体信息
            if not hasattr(self, 'news_bulletin'):
                self.news_bulletin = WebView()
            try:
                response = requests.get(
                    url=config.SERVER + article[0] + '/' + str(int(article[1])) + '/'
                )
                response_data = json.loads(response.content.decode('utf-8'))
            except Exception as e:
                response_data = {'content': ''}
            content = response_data['content']
            self.news_bulletin.setStyleSheet('font-size:18px')
            self.news_bulletin.setHtml(content)
            self.tab.addTab(self.news_bulletin, '新闻/公告')
            self.tab.setCurrentWidget(self.news_bulletin)
            self.tab_bar_close_handler()  # 可关闭按钮显示处理

    def get_file_show(self, file_url):
        try:
            name = file_url.rsplit('/', 1)[1]
        except Exception:
            return
        content_show = ShowServerPDF(file_url=file_url, file_name=name)
        content_show.setStyleSheet("border: none")
        self.tab.addTab(content_show, name)
        self.tab.setCurrentWidget(content_show)
        self.tab_bar_close_handler()  # 可关闭按钮显示处理

    def set_user_token(self, token):
        # 设置用户的token
        # print('保存用户token', token)
        config.APP_DAWN.setValue('token', token)

    def close(self):
        # 清除token
        config.APP_DAWN.remove('token')
        # 清除web缓存
        self.web_show.page().profile().clearHttpCache()
        self.href.page().profile().clearHttpCache()
        self.link_us.page().profile().clearHttpCache()
        if hasattr(self, 'news_bulletin'):
            self.news_bulletin.page().profile().clearHttpCache()
        super().close()
        qApp.closeAllWindows()

    def close_tab(self, index):
        self.tab.removeTab(index)
        self.tab.setCurrentIndex(0)

    def tab_changed(self, index):
        if index == 1:  # 讨论交流页面
            self.href.reload()
        elif index == 0:  # 交割通页面
            self.web_show.reload()
        elif index == 2:
            self.link_us.reload()

    def eventFilter(self, obj, event):
        """事件过滤器,用于解决鼠标进入其它控件后还原为标准鼠标样式"""
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)
        return super(Base, self).eventFilter(obj, event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        super(Base, self).mouseMoveEvent(event)
        pos = event.pos()
        xPos, yPos = pos.x(), pos.y()
        wm, hm = self.width() - self.Margins, self.height() - self.Margins
        if self.isMaximized() or self.isFullScreen():
            self.Direction = None
            self.setCursor(Qt.ArrowCursor)
            return
        if event.buttons() == Qt.LeftButton and self._pressed:
            self.resize_window(pos)
            return
        if xPos <= self.Margins and yPos <= self.Margins:
            # 左上角
            self.Direction = LeftTop
            self.setCursor(Qt.SizeFDiagCursor)
        elif wm <= xPos <= self.width() and hm <= yPos <= self.height():
            # 右下角
            self.Direction = RightBottom
            self.setCursor(Qt.SizeFDiagCursor)
        elif wm <= xPos and yPos <= self.Margins:
            # 右上角
            self.Direction = RightTop
            self.setCursor(Qt.SizeBDiagCursor)
        elif xPos <= self.Margins and hm <= yPos:
            # 左下角
            self.Direction = LeftBottom
            self.setCursor(Qt.SizeBDiagCursor)
        elif 0 <= xPos <= self.Margins and self.Margins <= yPos <= hm:
            # 左边
            self.Direction = Left
            self.setCursor(Qt.SizeHorCursor)
        elif wm <= xPos <= self.width() and self.Margins <= yPos <= hm:
            # 右边
            self.Direction = Right
            self.setCursor(Qt.SizeHorCursor)
        elif self.Margins <= xPos <= wm and 0 <= yPos <= self.Margins:
            # 上面
            self.Direction = Top
            self.setCursor(Qt.SizeVerCursor)
        elif self.Margins <= xPos <= wm and hm <= yPos <= self.height():
            # 下面
            self.Direction = Bottom
            self.setCursor(Qt.SizeVerCursor)

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        super(Base, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._mpos = event.pos()
            self._pressed = True

    def mouseReleaseEvent(self, event):
        """鼠标弹起事件"""
        super(Base, self).mouseReleaseEvent(event)
        self._pressed = False
        self.Direction = None

    def move(self, pos):
        if self.windowState() == Qt.WindowMaximized or self.windowState() == Qt.WindowFullScreen:
            # 最大化或者全屏则不允许移动
            return
        super(Base, self).move(pos)

    def paintEvent(self, event):
        """由于是全透明背景窗口,重绘事件中绘制透明度为1的难以发现的边框,用于调整窗口大小"""
        super(Base, self).paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 255, 255, 1), 2 * self.Margins))
        painter.drawRect(self.rect())

    def resize_window(self, pos):
        """调整窗口大小"""
        if self.Direction == None:
            return
        mpos = pos - self._mpos
        xPos, yPos = mpos.x(), mpos.y()
        geometry = self.geometry()
        x, y, w, h = geometry.x(), geometry.y(), geometry.width(), geometry.height()
        if self.Direction == LeftTop:  # 左上角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
        elif self.Direction == RightBottom:  # 右下角
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos = pos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos = pos
        elif self.Direction == RightTop:  # 右上角
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos.setX(pos.x())
        elif self.Direction == LeftBottom:  # 左下角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos.setY(pos.y())
        elif self.Direction == Left:  # 左边
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            else:
                return
        elif self.Direction == Right:  # 右边
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos = pos
            else:
                return
        elif self.Direction == Top:  # 上面
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            else:
                return
        elif self.Direction == Bottom:  # 下面
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos = pos
            else:
                return
        self.setGeometry(x, y, w, h)

    def showMaximized(self):
        """最大化,要去除上下左右边界,如果不去除则边框地方会有空隙"""
        super(Base, self).showMaximized()
        self.layout().setContentsMargins(0, 0, 0, 0)

    def showNormal(self):
        """还原,要保留上下左右边界,否则没有边框无法调整"""
        super(Base, self).showNormal()
        self.layout().setContentsMargins(self.Margins, self.Margins, self.Margins, self.Margins)

    def tab_bar_close_handler(self):
        self.tab.setTabsClosable(True)
        self.tab.tabBar().setTabButton(0, QTabBar.RightSide, None)
        self.tab.tabBar().setTabButton(1, QTabBar.RightSide, None)
        self.tab.tabBar().setTabButton(2, QTabBar.RightSide, None)
        if settings.ADMINISTRATOR is True:
            self.tab.tabBar().setTabButton(3, QTabBar.RightSide, None)
