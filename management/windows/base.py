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
from windows.maintenance import Maintenance, MaintenanceHome
from popup.base import TipShow
from piece.base import TitleBar, MenuBar, NavigationBar, PermitBar1, TitleBar1
from frame.base import NoDataWindow, RegisterClient
from widgets.base import ModuleButton, LoadedTab
from .home import HomePage
from .pservice import PService
from .danalysis import DAnalysis
from utils.machine import get_machine_code
# 枚举左上右下以及四个定点
Left, Top, Right, Bottom, LeftTop, RightTop, LeftBottom, RightBottom = range(8)


# 主窗体
class BaseWindow(QWidget):
    Left, Top, Right, Bottom, LeftTop, RightTop, LeftBottom, RightBottom = range(8)
    MARGIN = 3

    def __init__(self, *args, **kwargs):
        super(BaseWindow, self).__init__(*args, **kwargs)
        # self.mousePressed = False
        # 设置窗体的图标和名称
        self.setWindowIcon(QIcon("media/logo.png"))
        self.setWindowTitle("瑞达期货研究院分析决策系统_管理端_0101911")
        # 标题栏
        self.title_bar = TitleBar(parent=self)
        # 导航栏
        self.navigation_bar = NavigationBar(parent=self)
        # 导航栏的信号
        self.navigation_bar.clicked_login_button.connect(self.user_to_login)
        self.navigation_bar.clicked_register_button.connect(self.user_to_register)
        self.navigation_bar.clicked_logout_button.connect(self.user_to_logout)
        # 窗口承载体
        self.tab_loaded = LoadedTab(parent=self)
        # 属性、样式
        user_desktop = QDesktopWidget().availableGeometry()  # 用户的桌面信息,来改变自身窗体大小
        max_width = user_desktop.width()
        max_height = user_desktop.height()
        self.resize(max_width * 0.8, max_height * 0.8)
        self.setMaximumSize(max_width, max_height)  # 最大为用户桌面大小
        self.setMinimumSize(max_width * 0.5, max_height * 0.5)  # 最小为用户桌面大小的一半
        my_frame = self.frameGeometry()  # 1 (三步法放置桌面中心)自身窗体信息(虚拟框架)
        my_frame.moveCenter(user_desktop.center())  # 2 框架中心移动到用户桌面中心
        self.move(my_frame.topLeft())  # 3 窗口左上角与虚拟框架左上角对齐
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 背景全透明(影响子窗口)
        self._pressed = False
        self._direction = None
        self._mouse_pos = None
        self.setMouseTracking(True)  # 鼠标不点下移动依然有效(针对本窗口, 子控件无效)
        self.title_bar.installEventFilter(self)  # 子控件安装事件事件过滤
        self.navigation_bar.installEventFilter(self)
        self.tab_loaded.installEventFilter(self)
        # 布局
        layout = QVBoxLayout(margin=self.MARGIN, spacing=0)
        layout.addWidget(self.title_bar)
        layout.addWidget(self.navigation_bar)
        layout.addWidget(self.tab_loaded)
        self.setLayout(layout)

    # 用户点击【登录】
    def user_to_login(self):
        print('用户点击登录按钮')
        from popup.base import LoginPopup
        login_popup = LoginPopup(parent=self)
        if not login_popup.exec_():
            login_popup.deleteLater()
            del login_popup

    # 用户点击【注册】
    def user_to_register(self):
        print('用户点击注册按钮')
        from popup.base import RegisterPopup
        register_popup = RegisterPopup(parent=self)
        if not register_popup.exec_():
            register_popup.deleteLater()
            del register_popup


    # 用户点击【注销】
    def user_to_logout(self):
        print('用户点击注销按钮')

    # 获取模块菜单
    def get_module_menus(self):
        try:
            # 请求主菜单数据
            machine_code = config.app_dawn.value('machine')
            if machine_code:
                url = config.SERVER_ADDR + 'basic/modules/?mc=' + machine_code
            else:
                url = config.SERVER_ADDR + 'basic/modules/'
            r = requests.get(
                url=url,
                headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({"machine_code": config.app_dawn.value('machine')})
            )
            response = json.loads(r.content.decode("utf-8"))
        except Exception:
            sys.exit()  # catch exception sys exit
        # 模块菜单填充到相应的控件中
        menus = list()
        for menu_item in response['data']:
            button = ModuleButton(mid=menu_item['id'], text=menu_item['name'] )
            button.clicked_module.connect(self.module_clicked)  # 绑定模块菜单点击信号
            menus.append(button)
        self.navigation_bar.module_bar.setMenus(menus)

    # 点击模块菜单事件
    def module_clicked(self, menu):
        name = menu.text()
        # 查询权限
        machine_code = config.app_dawn.value('machine')
        if machine_code:
            url = config.SERVER_ADDR + 'limit/access-module/' + str(menu.mid) + '/?mc=' + machine_code
        else:
            url = config.SERVER_ADDR + 'limit/access-module/' + str(menu.mid) + '/'
        try:
            r = requests.get(
                url=url,
                headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')}
            )
            response = json.loads(r.content.decode('utf-8'))
            if not response['data']['permission']:
                raise ValueError(response['message'])
        except Exception as e:
            print(e)
            # 提示错误结果
            return
        else:
            # 有权限
            if name == u'客户端注册':
                tab = RegisterClient()
            elif name == u'管理维护':
                tab = MaintenanceHome(parent=self.tab)
            else:
                tab = NoDataWindow(name=name)
            self.tab_loaded.clear()
            self.tab_loaded.addTab(tab, name)

    # 事件过滤器, 用于解决鼠标进入其它控件后还原为标准鼠标样式
    def eventFilter(self, obj, event):
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)
            self._direction = None  # 去除方向
            self._pressed = None  # 去除按下标记
        return super(BaseWindow, self).eventFilter(obj, event)

    # 鼠标按下事件
    def mousePressEvent(self, event):
        super(BaseWindow, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._mouse_pos = event.pos()
            self._pressed = True

    # 鼠标弹起事件
    def mouseReleaseEvent(self, event):
        super(BaseWindow, self).mouseReleaseEvent(event)
        self._pressed = False
        self._direction = None

    # 鼠标移动事件(只有边框MARGIN大小范围有效果,因为其他的是其子控件)(会捕获子控件的鼠标按住移动的事件)
    def mouseMoveEvent(self, event):
        super(BaseWindow, self).mouseMoveEvent(event)
        pos = event.pos()
        pos_x, pos_y = pos.x(), pos.y()
        print(pos_x, pos_y)
        wm, hm = self.width() - self.MARGIN, self.height() - self.MARGIN
        print(wm, hm)
        # 窗口最大无需事件
        if self.isMaximized() or self.isFullScreen():
            self._direction = None
            self.setCursor(Qt.ArrowCursor)
            return
        if event.buttons() == Qt.LeftButton and self._pressed:
            self.resize_window(pos)
            print('调整窗口大小')
            # return
        if pos_x <= self.MARGIN and pos_y <= self.MARGIN:
            # 左上角
            print('鼠标在左上角')
            self._direction = self.LeftTop
            self.setCursor(Qt.SizeFDiagCursor)
        elif wm <= pos_x <= self.width() and hm <= pos_y <= self.height():
            # 右下角
            print('鼠标在右下角')
            self._direction = self.RightBottom
            self.setCursor(Qt.SizeFDiagCursor)
        elif wm <= pos_x and pos_y <= self.MARGIN:
            # 右上角
            print('鼠标在右上角')
            self._direction = self.RightTop
            self.setCursor(Qt.SizeBDiagCursor)
        elif pos_x <= self.MARGIN and hm <= pos_y:
            # 左下角
            self._direction = self.LeftBottom
            self.setCursor(Qt.SizeBDiagCursor)
        elif 0 <= pos_x <= self.MARGIN <= pos_y <= hm:
            # 左边

            self._direction = self.Left
            self.setCursor(Qt.SizeHorCursor)
        elif wm <= pos_x <= self.width() and self.MARGIN <= pos_y <= hm:
            # 右边
            self._direction = self.Right
            self.setCursor(Qt.SizeHorCursor)
        elif wm >= pos_x >= self.MARGIN >= pos_y >= 0:
            # 上面
            self._direction = self.Top
            self.setCursor(Qt.SizeVerCursor)
        elif self.MARGIN <= pos_x <= wm and hm <= pos_y <= self.height():
            # 下面
            self._direction = self.Bottom
            self.setCursor(Qt.SizeVerCursor)

    # 由于是全透明背景窗口,重绘事件中绘制透明度为1的难以发现的边框,用于调整窗口大小
    def paintEvent(self, event):
        super(BaseWindow, self).paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 255, 255, 1), 2 * self.MARGIN))
        painter.drawRect(self.rect())

    # 调整窗口大小
    def resize_window(self, pos):
        if self._direction is None:
            return
        mpos = pos - self._mouse_pos
        xPos, yPos = mpos.x(), mpos.y()
        geometry = self.geometry()
        x, y, w, h = geometry.x(), geometry.y(), geometry.width(), geometry.height()
        if self._direction == LeftTop:  # 左上角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
        elif self._direction == RightBottom:  # 右下角
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mouse_pos = pos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mouse_pos = pos
        elif self._direction == RightTop:  # 右上角
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mouse_pos.setX(pos.x())
        elif self._direction == LeftBottom:  # 左下角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mouse_pos.setY(pos.y())
        elif self._direction == Left:  # 左边
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            else:
                return
        elif self._direction == Right:  # 右边
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mouse_pos = pos
            else:
                return
        elif self._direction == Top:  # 上面
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            else:
                return
        elif self._direction == Bottom:  # 下面
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mouse_pos = pos
            else:
                return
        self.setGeometry(x, y, w, h)
        
    # 窗口最大化去除边界MARGIN
    def showMaximized(self):
        super(BaseWindow, self).showMaximized()
        self.layout().setContentsMargins(0, 0, 0, 0)

    # 还原保留调整大小的边界
    def showNormal(self):
        super(BaseWindow, self).showNormal()
        self.layout().setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)


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
        title_bar = TitleBar1()
        # signal slot
        # title_bar.windowMinimumed.connect(self.showMinimized)
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
        self.permit_bar = PermitBar1()

        self.permit_bar.is_superman.connect(self.superman_login_event)  # 超级管理员登录需有【权限管理】模块
        self.permit_bar.user_logout.connect(self.user_logout_event)  # 用户退出就回到【首页】
        # add tab container
        self.tab = QTabWidget()
        self.tab.setAutoFillBackground(True)  # 设置背景,否则由于受到父窗口的影响导致透明
        self.tab.setTabBarAutoHide(True)
        palette = self.tab.palette()
        palette.setColor(palette.Window, QColor(255,255,255))
        self.tab.setPalette(palette)
        self.tab.installEventFilter(self)  # 事件过滤
        # style
        self.setStyleSheet("""
        QTabWidget::pane{
            border:none;
        }
        """)
        # add widget to menu and permit layout
        mp_layout.addWidget(self.menu_bar)
        mp_layout.addWidget(self.permit_bar)
        # add widgets and layout to main layout
        layout.addWidget(title_bar)
        layout.addLayout(mp_layout)
        layout.addWidget(self.tab)
        self.setLayout(layout)
        # set icon and title
        self.setWindowIcon(QIcon("media/logo.png"))
        self.setWindowTitle("瑞达期货研究院分析决策系统_管理端_0101911")

        # 在获取功能模块前先获取客户端是否已经存在
        self.check_client_existed()
        # 获取功能模块名
        self.get_menus()

    # 启动检查客户端是否存在
    def check_client_existed(self):
        exist_mc = config.app_dawn.value('machine')
        if exist_mc:  # 原来就存在则不发起请求
            print('windows.base.Base.check_client_existed 客户端没卸载')
            return
        # 获取机器码
        print('windows.base.Base.check_client_existed 客户端已卸载重装,鉴定是否已注册过的')
        machine_code = get_machine_code()
        # 查询机器是否存在
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'basic/client-existed/?mc=' + machine_code
            )
            response = json.loads(r.content.decode('utf-8'))
        except Exception:
            return
        if response['data']['existed']:
            # 存在,写入配置
            print('注册过的客户端,写入配置')
            config.app_dawn.setValue('machine', machine_code)

    # 获取模块功能按钮
    def get_menus(self):
        try:
            # 请求主菜单数据
            machine_code = config.app_dawn.value('machine')
            if machine_code:
                url = config.SERVER_ADDR + 'basic/modules/?mc=' + machine_code
            else:
                url = config.SERVER_ADDR + 'basic/modules/'
            r = requests.get(
                url=url,
                headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({"machine_code": config.app_dawn.value('machine')})
            )
            response = json.loads(r.content.decode("utf-8"))
        except Exception as e:
            QMessageBox.information(self, "获取数据错误", "请检查网络设置.\n{}".format(e), QMessageBox.Yes)
            sys.exit()  # catch exception sys exit
        for item in response["data"]:
            menu_btn = QPushButton(item['name'])
            menu_btn.mid = item['id']
            self.menu_bar.addMenuButton(menu_btn)
        self.menu_bar.addStretch()

    def menu_clicked(self, menu):
        name = menu.text()
        # 查询权限
        machine_code = config.app_dawn.value('machine')
        if machine_code:
            url = config.SERVER_ADDR + 'limit/access-module/'+str(menu.mid)+'/?mc=' + machine_code
        else:
            url = config.SERVER_ADDR + 'limit/access-module/'+str(menu.mid) + '/'
        try:
            r = requests.get(
                url=url,
                headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')}
            )
            response = json.loads(r.content.decode('utf-8'))
        except Exception as e:
            return
        if not response['data']['permission']:
            popup = TipShow(parent=self)
            popup.confirm_btn.clicked.connect(popup.close)
            popup.information(title='无权限', message=response['message'])
            if not popup.exec():
                del popup
            return
        # 有权限
        if name == u'客户端注册':
            tab = RegisterClient()
        elif name == u'管理维护':
            tab = MaintenanceHome(parent=self.tab)
        else:
            tab = NoDataWindow(name=name)
        self.tab.clear()
        self.tab.addTab(tab, name)

    # 用户退出事件,回到【首页】
    def user_logout_event(self):
        menu = QPushButton(u'首页')
        menu.mid = 0
        self.menu_clicked(menu)

    # 超级管理员登录增加权限管理模块
    def superman_login_event(self, flag):
        print('超级管理员登录了，增加【权限管理】 windows.base.Base.superman_login_event')
        menu = QPushButton('权限管理')
        menu.mid = -99
        self.menu_bar.addMenuButton(menu)
        self.menu_bar.addStretch()

    def eventFilter(self, obj, event):
        """事件过滤器,用于解决鼠标进入其它控件后还原为标准鼠标样式"""
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)
        return super(Base, self).eventFilter(obj, event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        try:
            super(Base, self).mouseMoveEvent(event)
            pos = event.pos()
            xPos, yPos = pos.x(), pos.y()
            print(xPos, yPos)
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
        except Exception as e:
            print(e)

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
