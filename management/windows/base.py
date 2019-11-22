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
from popup.tips import InformationPopup
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
        login_popup.user_listed.connect(self.user_login_successfully)
        if not login_popup.exec_():
            login_popup.deleteLater()
            del login_popup

    # 启动自动登录
    def running_auto_login(self):
        machine_code = config.app_dawn.value('machine')
        token = config.app_dawn.value('AUTHORIZATION')
        print('启动客户端自动登录', token)
        if not machine_code or not token:
            print('windows.base.BaseWindows.running_auto_login 没有机器码或token,不用自动登录')
            return
        print('windows.base.BaseWindows.running_auto_login 有机器码或token,自动登录')
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'user/keep-online/?mc=' + machine_code,
                headers={'AUTHORIZATION': token}
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            return  # 自动登录失败
        else:
            # 用户名信息设置到登录信息栏
            user_data = response['data']
            sig_username = user_data['username']
            if not user_data['username']:
                phone = user_data['phone']
                sig_username = phone[0:3] + '****' + phone[8:11]
            # 登录成功
            data_dict = {
                'username': sig_username,
                'auth_data': response['data']
            }
            self.user_login_successfully(data_dict)

    # 用户登录成功
    def user_login_successfully(self, data_dict):
        print(data_dict)
        username = data_dict.get('username', '')
        auth_data = data_dict.get('auth_data', {})
        is_superuser = auth_data.get('is_superuser', False)
        is_maintainer = auth_data.get('is_maintainer', False)
        is_researcher = auth_data.get('is_researcher', False)
        client_is_manager = auth_data.get('ManagerClient', False)
        is_inner = False
        if is_superuser or is_maintainer or is_researcher:
            print('用户满足内部人员条件')
            is_inner = True
        # 改变用户名
        self.navigation_bar.permit_bar.show_username(username)
        if client_is_manager and is_inner:  # 用户满足条件且为管理端
            # 加入【管理维护-1】
            button = ModuleButton(mid=-1, text='数据管理')
            button.clicked_module.connect(self.module_clicked)
            self.navigation_bar.module_bar.addMenu(button)
            if is_superuser:  # 超管在管理端登录加入和【权限管理-9】
                button = ModuleButton(mid=-9, text='权限管理')
                button.clicked_module.connect(self.module_clicked)
                self.navigation_bar.module_bar.addMenu(button)
        else:  # 不是的话则尝试移除【管理维护-1】和【权限管理-9】
            self.navigation_bar.module_bar.removeMenu(mid=-1)
            self.navigation_bar.module_bar.removeMenu(mid=-9)

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
        # 如果有【数据管理-1】【权限管理-9】就移除
        self.navigation_bar.module_bar.removeMenu(mid=-1)
        self.navigation_bar.module_bar.removeMenu(mid=-9)
        # 移除token
        config.app_dawn.remove('AUTHORIZATION')
        self.navigation_bar.permit_bar.user_logout()  # 注销

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
            button = ModuleButton(mid=menu_item['id'], text=menu_item['name'])
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
            # 弹窗提示
            info_popup = InformationPopup(parent=self, message=str(e))
            if not info_popup.exec_():
                info_popup.deleteLater()
                del info_popup
            return
        else:
            if name == u'首页':
                tab = HomePage(parent=self.tab_loaded)
            elif name == u'数据管理':
                from windows.maintenance import MaintenanceHome
                tab = MaintenanceHome(parent=self.tab_loaded)
            elif name == u'权限管理':
                from windows.maintenance import AuthorityHome
                tab = AuthorityHome(parent=self.tab_loaded)
            else:
                tab = NoDataWindow(name=name)
            self.tab_loaded.clear()
            self.tab_loaded.addTab(tab, name)

