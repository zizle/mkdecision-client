# _*_ coding:utf-8 _*_
"""
the base window of project
Update: 2019-07-25
Author: zizle
"""
import os
import sys
import json
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QEnterEvent, QPainter, QColor, QPen, QIcon


import config
from windows.maintenance import Maintenance
from popup.base import TipShow
from piece.base import TitleBar, MenuBar, PermitBar
from frame.base import NoDataWindow, RegisterClient
from .home import HomePage
from .pservice import PService
# 枚举左上右下以及四个定点
Left, Top, Right, Bottom, LeftTop, RightTop, LeftBottom, RightBottom = range(8)


class Base(QWidget):
    # 四周边距
    Margins = 3

    def __init__(self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)
        self.resize(1280, 768)
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
        # menu bar and permit bar layout
        mp_layout = QHBoxLayout(spacing=0)
        mp_layout.setContentsMargins(0,0,0,0)
        # window title
        title_bar = TitleBar()
        # signal slot
        title_bar.windowMinimumed.connect(self.showMinimized)
        title_bar.windowMaximumed.connect(self.showMaximized)
        title_bar.windowNormaled.connect(self.showNormal)
        title_bar.windowClosed.connect(self.close)
        title_bar.windowMoved.connect(self.move)
        self.windowTitleChanged.connect(title_bar.setTitle)
        self.windowIconChanged.connect(title_bar.setIcon)
        # menu bar
        self.menu_bar = MenuBar()
        self.menu_bar.installEventFilter(self)
        # 设置背景颜色,否则由于受到父窗口的影响导致透明
        self.menu_bar.setAutoFillBackground(True)
        palette = self.menu_bar.palette()
        palette.setColor(palette.Window, QColor(255,255,255))
        self.menu_bar.setPalette(palette)
        self.menu_bar.setContentsMargins(10, 0, 0, 4)
        self.menu_bar.setStyleSheet("""
        MenuBar{
            background-color:rgb(85,88,91);
        }
        QPushButton{
            background-color:rgb(85,88,91);
            color: rgb(192,192,192);
            border: 0.5px solid rgb(170,170,170);
            padding:0 7px;
            margin-left:5px;
            height:18px;
            color: #FFFFFF
        }
        QPushButton:hover {
            background-color: #CD3333;
        }
        MenuWidget{
        
        }
        """)
        self.menu_bar.menu_btn_clicked.connect(self.menu_clicked)
        # permit bar
        permit_bar = PermitBar()
        # add tab container
        self.tab = QTabWidget()
        self.tab.setAutoFillBackground(True)  # 设置背景,否则由于受到父窗口的影响导致透明
        self.tab.setTabBarAutoHide(True)
        palette = self.tab.palette()
        palette.setColor(palette.Window, QColor(255,255,255))
        self.tab.setPalette(palette)
        self.tab.installEventFilter(self) # 事件过滤
        # add widget to menu and permit layout
        mp_layout.addWidget(self.menu_bar)
        mp_layout.addWidget(permit_bar)
        # add widgets and layout to main layout
        layout.addWidget(title_bar)
        layout.addLayout(mp_layout)
        layout.addWidget(self.tab)
        self.setLayout(layout)
        # set icon and title
        self.setWindowIcon(QIcon("media/logo.png"))
        self.setWindowTitle("瑞达期货研究院分析决策系统-管理端 " + config.VERSION)
        # get menus in server
        self.get_menus()

    def close(self):
        # 注销
        try:
            response = requests.post(
                url=config.SERVER_ADDR + "user/passport/?option=logout",
                headers=config.CLIENT_HEADERS,
                cookies=config.app_dawn.value('cookies')
            )
        except Exception:
            pass
        # 移除cookie和权限
        config.app_dawn.remove('cookies')
        config.app_dawn.remove('access_main_module')
        super().close()

    def eventFilter(self, obj, event):
        """事件过滤器,用于解决鼠标进入其它控件后还原为标准鼠标样式"""
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)
        return super(Base, self).eventFilter(obj, event)

    def get_menus(self):
        try:
            # 请求主菜单数据
            response = requests.get(
                url=config.SERVER_ADDR + "basic/module/",
                headers=config.CLIENT_HEADERS,
                data=json.dumps({"machine_code": config.app_dawn.value('machine')})
            )
        except Exception as e:
            QMessageBox.information(self, "获取数据错误", "请检查网络设置.\n{}".format(e), QMessageBox.Yes)
            sys.exit()  # catch exception sys exit
        response_content = json.loads(response.content.decode("utf-8"))
        if response.status_code != 200:
            QMessageBox.information(self, "获取数据错误", response_content['message'], QMessageBox.Yes)
            sys.exit()
        for item in response_content["data"]:
            menu_btn = QPushButton(item['name'])
            menu_btn.unum = item['id']
            menu_btn.name_en = item['name_en']
            self.menu_bar.addMenuButton(menu_btn)
        self.menu_bar.addStretch()

    def menu_clicked(self, menu):
        name_en = menu.name_en
        name = menu.text()
        access_modules = config.app_dawn.value('access_main_module')
        if not access_modules:
            access_modules = []
        if name_en not in ['machine_code','home_page', 'maintenance'] + access_modules:
            popup = TipShow()
            popup.confirm_btn.clicked.connect(popup.close)
            popup.information(title='无权限', message='您不能查看此功能，\n如已登录请联系管理员开放！')
            if not popup.exec():
                del popup
            return
        if name_en == 'machine_code':
            tab = RegisterClient()
        elif name_en == 'home_page':
            tab = HomePage()
        elif name_en == 'product_service':
            tab = PService()
        elif name_en == 'maintenance':
            tab = Maintenance()
        else:
            tab = NoDataWindow(name=name)
        self.tab.clear()
        self.tab.addTab(tab, name)

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
