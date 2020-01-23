# _*_ coding:utf-8 _*_
# __Author__： zizle
import os
import json
import time
import requests
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QVBoxLayout, QLabel, QSplashScreen
from PyQt5.QtGui import QIcon, QEnterEvent, QPen, QPainter, QColor, QPixmap, QFont
from PyQt5.QtCore import Qt

import settings
from widgets.base import TitleBar, NavigationBar, LoadedPage
from utils.machine import get_machine_code
from popup.tips import InformationPopup

""" 欢迎页 """


# 欢迎页
class WelcomePage(QSplashScreen):
    def __init__(self, *args, **kwargs):
        super(WelcomePage, self).__init__(*args, *kwargs)
        self.setPixmap(QPixmap('media/start.png'))
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.setFont(font)
        self.showMessage("欢迎使用分析决策系统\n程序正在启动中...", Qt.AlignCenter, Qt.blue)

    # 启动使客户端存在
    def make_client_existed(self):
        machine_code = get_machine_code()  # 获取机器码
        # 查询机器是否存在
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'client/',
                data=json.dumps({
                    'machine_code': machine_code,
                    'is_manager': settings.ADMINISTRATOR
                }),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            settings.app_dawn.remove('machine')
            self.showMessage("欢迎使用分析决策系统\n获取数据失败...\n" + str(e), Qt.AlignCenter, Qt.red)
            time.sleep(1.5)
        else:
            # 写入配置
            settings.app_dawn.setValue('machine', response['data']['machine_code'])

    # 启动访问广告图片文件并保存至本地
    def getCurrentAdvertisements(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/advertise/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            # 清空slider文件夹
            for path in ['media/slider/' + path for path in os.listdir('media/slider')]:
                os.remove(path)
            # 遍历请求每一个图片
            for ad_item in response['data']:
                image_name = ad_item['image'].rsplit('/', 1)[1]
                time.sleep(0.0001)
                r = requests.get(url=settings.STATIC_PREFIX + ad_item['image'])
                with open('media/slider/' + image_name, 'wb') as img:
                    img.write(r.content)


# 主窗口(无边框)
class BaseWindow(QWidget):
    # 枚举左上右下以及四个定点
    Left, Top, Right, Bottom, LeftTop, RightTop, LeftBottom, RightBottom = range(8)
    MARGIN = 3  # 边缘宽度小用于调整窗口大小

    def __init__(self, *args, **kwargs):
        super(BaseWindow, self).__init__(*args, **kwargs)
        # self.mousePressed = False
        # 设置窗体的图标和名称
        self.setWindowIcon(QIcon("media/logo.png"))
        self.setWindowTitle("瑞达期货研究院分析决策系统管理端0102001")
        # 标题栏
        self.title_bar = TitleBar(parent=self)
        # 导航栏
        self.navigation_bar = NavigationBar(parent=self)
        # 导航栏的信号
        self.navigation_bar.clicked_login_button.connect(self.user_to_login)
        self.navigation_bar.clicked_register_button.connect(self.user_to_register)
        self.navigation_bar.clicked_logout_button.connect(self.user_to_logout)
        self.navigation_bar.module_bar.menu_clicked.connect(self.module_clicked)  # 选择了某个模块的
        # 窗口承载体
        self.page_container = LoadedPage(parent=self)
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
        self.page_container.installEventFilter(self)
        # 布局
        layout = QVBoxLayout(margin=self.MARGIN, spacing=0)
        layout.addWidget(self.title_bar)
        layout.addWidget(self.navigation_bar)
        layout.addWidget(self.page_container)
        self.setLayout(layout)

    # 用户点击【登录】
    def user_to_login(self):
        from popup.base import LoginPopup
        login_popup = LoginPopup(parent=self)
        login_popup.user_listed.connect(self.user_login_successfully)
        if not login_popup.exec_():
            login_popup.deleteLater()
            del login_popup

    # 启动自动登录
    def running_auto_login(self):
        if settings.app_dawn.value('auto') == '1':  # 自动登录
            machine_code = settings.app_dawn.value('machine')
            token = settings.app_dawn.value('AUTHORIZATION')
            if not machine_code or not token:
                self.user_to_login()
                return
            try:
                r = requests.get(
                    url=settings.SERVER_ADDR + 'user/keep-online/?mc=' + machine_code,
                    headers={'AUTHORIZATION': token}
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 200:
                    raise ValueError(response['message'])
            except Exception:
                settings.app_dawn.remove('AUTHORIZATION')  # 状态保持失败移除token
                self.user_to_login()
                return  # 自动登录失败
            else:
                if response['data']:
                    self.user_login_successfully(response['data'])
        else:
            # 删除token
            settings.app_dawn.remove('AUTHORIZATION')

    # 用户登录成功(注册成功)
    def user_login_successfully(self, response_data):
        # 保存token
        token = response_data['Authorization']
        settings.app_dawn.setValue('AUTHORIZATION', token)
        # 组织滚动显示用户名
        dynamic_username = response_data['username']
        if not response_data['username']:
            phone = response_data['phone']
            dynamic_username = phone[0:3] + '****' + phone[7:11]
        # 改变显示用户名
        self.navigation_bar.permit_bar.show_username(dynamic_username)
        # 设置管理角色的菜单
        self.navigation_bar.module_bar.setMenuActions(response_data['actions'])

    # 用户点击【注册】
    def user_to_register(self):
        # print('用户点击注册按钮')
        from popup.base import RegisterPopup
        register_popup = RegisterPopup(parent=self)
        register_popup.user_registered.connect(self.user_login_successfully)
        if not register_popup.exec_():
            register_popup.deleteLater()
            del register_popup

    # 用户点击【注销】
    def user_to_logout(self):
        if self.navigation_bar.permit_bar.username_shown.isHidden():
            return
        # print('用户点击注销按钮生效')
        # 清除菜单
        self.navigation_bar.module_bar.clearActionMenu()
        # 移除token
        settings.app_dawn.remove('AUTHORIZATION')
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
        wm, hm = self.width() - self.MARGIN, self.height() - self.MARGIN
        # print(wm, hm)
        # 窗口最大无需事件
        if self.isMaximized() or self.isFullScreen():
            self._direction = None
            self.setCursor(Qt.ArrowCursor)
            return
        if event.buttons() == Qt.LeftButton and self._pressed:
            self.resize_window(pos)
        if pos_x <= self.MARGIN and pos_y <= self.MARGIN:
            # 左上角
            self._direction = self.LeftTop
            self.setCursor(Qt.SizeFDiagCursor)
        elif wm <= pos_x <= self.width() and hm <= pos_y <= self.height():
            # 右下角
            self._direction = self.RightBottom
            self.setCursor(Qt.SizeFDiagCursor)
        elif wm <= pos_x and pos_y <= self.MARGIN:
            # 右上角
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
        if self._direction == self.LeftTop:  # 左上角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
        elif self._direction == self.RightBottom:  # 右下角
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mouse_pos = pos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mouse_pos = pos
        elif self._direction == self.RightTop:  # 右上角
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mouse_pos.setX(pos.x())
        elif self._direction == self.LeftBottom:  # 左下角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mouse_pos.setY(pos.y())
        elif self._direction == self.Left:  # 左边
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            else:
                return
        elif self._direction == self.Right:  # 右边
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mouse_pos = pos
            else:
                return
        elif self._direction == self.Top:  # 上面
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            else:
                return
        elif self._direction == self.Bottom:  # 下面
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

    # 获取系统的普通模块
    def getSystemStartModules(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'module/start/?mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            modules = {}
        else:
            modules = response['data']
        # 设置模块菜单
        self.navigation_bar.module_bar.setMenus(modules)

    # 点击模块菜单事件(接受到模块的id和模块名称)
    def module_clicked(self, module_id, module_text):
        # print(module_id, module_text)
        # 查询权限
        machine_code = settings.app_dawn.value('machine')
        machine_code = machine_code if machine_code else ''
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'limit/access-module/' + str(module_id) + '/?mc=' + machine_code,
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')}
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
        else:  # 模块权限验证通过
            if module_text == u'首页':
                from frame.home import HomePage
                page = HomePage(parent=self.page_container)
                page.getCurrentNews()
                page.getCurrentSliderAdvertisement()
                page.getFoldedBoxContent()
                page.folded_box_clicked(category_id=1, head_text='常规报告') # 默认点击常规报告分类id=1
            elif module_text == u'产品服务':
                from frame.infoService import InfoServicePage
                page = InfoServicePage(parent=self.page_container)

            elif module_text == '数据分析':
                from frame.trend import TrendPage
                page = TrendPage(parent=self.page_container)
                page.getGroupVarieties()
                page.getTrendPageCharts()
            elif module_text == '数据管理':
                from frame.collector import CollectorMaintain
                page = CollectorMaintain(parent=self.page_container)

            elif module_text == u'运营管理':
                from frame.operator import OperatorMaintain
                page = OperatorMaintain(parent=self.page_container)
                page.addListItem()  # 加入管理项目
            elif module_text == u'权限管理':
                from frame.authority import AuthorityMaintain
                page = AuthorityMaintain(parent=self.page_container)
                page.getCurrentUsers()
            # elif module_text == u'数据管理':
            #     from windows.maintenance import MaintenanceHome
            #     tab = MaintenanceHome(parent=self.tab_loaded)
            # elif module_text == u'权限管理':
            #     from windows.maintenance import AuthorityHome
            #     tab = AuthorityHome(parent=self.tab_loaded)
            #     tab.addComboItem()  # 添加选择当前角色，并由此出发请求相应用户列表
            else:
                page = QLabel(parent=self.page_container,
                              styleSheet='font-size:16px;font-weight:bold;color:rgb(230,50,50)',
                              alignment=Qt.AlignCenter)
                page.setText("「" + module_text + "」暂未开放\n敬请期待,感谢支持~.")

            self.page_container.clear()
            # print('当前窗体个数：', self.page_container.count())
            self.page_container.addWidget(page)
            # self.page_container.removeWidget(self.page_container.widget(0))
            # print('当前窗体个数：', self.page_container.count())


            # self.tab_loaded.clear()





