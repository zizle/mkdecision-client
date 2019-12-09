# _*_ coding:utf-8 _*_
# __Author__： zizle
import sys
import time
import json
import requests
import chardet
from PyQt5.QtWidgets import QSplashScreen, QWidget, QDesktopWidget, QVBoxLayout, QHBoxLayout, QLabel, QMenu, QAction,\
    QPushButton, QTabWidget, QScrollArea, QGridLayout
from PyQt5.QtGui import QPixmap, QFont, QIcon, QEnterEvent, QPen, QPainter, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize

import settings
from utils.machine import get_machine_code
from widgets.CAvatar import CAvatar
from popup.tips import InformationPopup

""" 折叠菜单盒子相关 """


# 折叠盒子的按钮
class FoldedBodyButton(QPushButton):
    mouse_clicked = pyqtSignal(dict)

    def __init__(self, text, group_text, gid, bid, *args, **kwargs):
        super(FoldedBodyButton, self).__init__(*args, **kwargs)
        self.setText(text)
        self.group_text = group_text
        self.gid = gid
        self.bid = bid
        self.clicked.connect(self.left_mouse_clicked)

    def left_mouse_clicked(self):
        self.mouse_clicked.emit({
            'group_id': self.gid,
            'group_text': self.group_text,
            'category_id': self.bid,
        })


# FoldedHead(), FoldedBody()
# 折叠盒子的头
class FoldedHead(QWidget):
    def __init__(self, text, *args, **kwargs):
        super(FoldedHead, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0)
        self.head_label = QLabel(text, parent=self)
        self.head_button = QPushButton('折叠', parent=self, clicked=self.body_toggle)
        layout.addWidget(self.head_label, alignment=Qt.AlignLeft)
        layout.addWidget(self.head_button, alignment=Qt.AlignRight)
        self.setLayout(layout)
        # 样式
        self.body_hidden = False  # 显示与否
        self.body_height = 0  # 原始高度
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        self.setObjectName('foldedHead')
        self.setStyleSheet("""
        #foldedHead{
            background-color: rgb(20,120,200);
            border-bottom: 1px solid rgb(200,200,200)
        }
        """)

    # 设置身体控件(由于设置parent后用findChild没找到，用此法)
    def setChildBody(self, body):
        if not hasattr(self, 'bodyChild'):
            self.bodyChild = body

    def get_body(self):
        if hasattr(self, 'bodyChild'):
            return self.bodyChild

    # 窗体折叠展开动画
    def body_toggle(self):
        print('头以下的身体折叠展开')
        body = self.get_body()
        if not body:
            return
        self.body_height = body.height()
        self.setMinimumWidth(self.width())
        if not self.body_hidden:
            body.hide()
            self.body_hidden = True
        else:
            body.show()
            self.body_hidden = False


# 折叠盒子的身体
class FoldedBody(QWidget):
    mouse_clicked = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(FoldedBody, self).__init__(*args, **kwargs)
        layout = QGridLayout(margin=0)
        self.setLayout(layout)
        # 样式
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        self.setObjectName('foldedBody')
        self.setStyleSheet("""
        #foldedBody{
            background-color: rgb(20,120,100)
        }
        """)

    # 添加按钮
    def addButtons(self, group_text, button_list, horizontal_count=3):
        if horizontal_count < 3:
            horizontal_count = 3
        row_index = 0
        col_index = 0
        for index, button_item in enumerate(button_list):
            button = FoldedBodyButton(
                text=button_item['name'],
                group_text=group_text,
                gid=button_item['group'],
                bid=button_item['id'],
                parent=self
            )
            button.mouse_clicked.connect(self.left_mouse_clicked)
            self.layout().addWidget(button, row_index, col_index)
            col_index += 1
            if col_index == horizontal_count:  # 因为col_index先+1,此处应相等
                row_index += 1
                col_index = 0

    # 踢皮球，将信号直接传出
    def left_mouse_clicked(self, signal):
        self.mouse_clicked.emit(signal)


# 滚动折叠盒子
class ScrollFoldedBox(QScrollArea):
    left_mouse_clicked = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(ScrollFoldedBox, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0, spacing=0)
        self.container = QWidget()
        self.container.setLayout(layout)
        self.setWidgetResizable(True)
        self.setWidget(self.container)

        # 样式
        self.setObjectName('foldedBox')
        with open("media/ScrollBar.qss", "rb") as fp:
            content = fp.read()
            encoding = chardet.detect(content) or {}
            content = content.decode(encoding.get("encoding") or "utf-8")
        # 设置样式
        self.setStyleSheet(content)

    def addHead(self, text):
        head = FoldedHead(text, parent=self)
        self.container.layout().addWidget(head, alignment=Qt.AlignTop)
        return head

    def addBody(self, head):
        body = FoldedBody()
        head.setChildBody(body)
        # 找出head所在的位置
        for i in range(self.container.layout().count()):
            widget = self.container.layout().itemAt(i).widget()
            if isinstance(widget, FoldedHead) and widget == head:
                self.container.layout().insertWidget(i+1, body, alignment=Qt.AlignTop)
                break
        # 连接信号
        body.mouse_clicked.connect(self.body_button_clicked)
        return body

    def addStretch(self):
        self.container.layout().addStretch()

    # 设置竖直滚动条一直显示
    def setVerticalScrollBarAlwayOn(self):
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    # 踢皮球，直接将信号传出
    def body_button_clicked(self, signal):
        self.left_mouse_clicked.emit(signal)


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
                url=settings.SERVER + 'basic/client/',
                data=json.dumps({
                    'machine_code': machine_code,
                    'is_manager': settings.ADMINISTRATOR
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            settings.app_dawn.remove('machine')
            self.showMessage("欢迎使用分析决策系统\n程序启动失败...\n" + str(e), Qt.AlignCenter, Qt.red)
            time.sleep(3)
            sys.exit()
        else:
            # 写入配置
            print('utils.client.make_client_existed写入配置')
            settings.app_dawn.setValue('machine', response['data']['machine_code'])


""" 标题栏相关 """


# 标题栏
class TitleBar(QWidget):
    HEIGHT = 35

    def __init__(self, *args, **kwargs):
        super(TitleBar, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0, spacing=0)
        # 图标
        self.window_icon = QLabel(parent=self)
        pixmap = QPixmap('media/logo.png')
        self.window_icon.setScaledContents(True)
        self.window_icon.setPixmap(pixmap)
        # 标题
        self.window_title = QLabel(parent=self)
        layout.addWidget(self.window_icon, Qt.AlignLeft)
        layout.addWidget(self.window_title, Qt.AlignLeft)
        # 中间伸缩
        # layout.addStretch()
        # 右侧控制大小
        # 利用Webdings字体来显示图标
        font = QFont()
        font.setFamily('Webdings')
        # 最小化按钮
        self.buttonMinimum = QPushButton(
            '0', parent=self, font=font, clicked=self.windowMinimumed, objectName='buttonMinimum')
        layout.addWidget(self.buttonMinimum, alignment=Qt.AlignRight | Qt.AlignTop)
        # 最大化/还原按钮
        self.buttonMaximum = QPushButton(
            '1', parent=self, font=font, clicked=self.windowMaximized, objectName='buttonMaximum')
        layout.addWidget(self.buttonMaximum, alignment=Qt.AlignRight | Qt.AlignTop)
        # 关闭按钮
        self.buttonClose = QPushButton(
            'r', parent=self, font=font, clicked=self.windowClosed, objectName='buttonClose')
        layout.addWidget(self.buttonClose, alignment=Qt.AlignRight | Qt.AlignTop)
        # 属性、样式
        self._mouse_pos = None
        self.setObjectName('titleBar')
        self.setFixedHeight(self.HEIGHT)
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        self.window_icon.setMargin(2)
        self.window_icon.setFixedSize(self.HEIGHT - 5, self.HEIGHT - 5)
        self.window_title.setMargin(3)
        self.buttonMinimum.setFixedSize(self.HEIGHT - 5, self.HEIGHT - 5)
        self.buttonMaximum.setFixedSize(self.HEIGHT - 5, self.HEIGHT - 5)
        self.buttonClose.setFixedSize(self.HEIGHT - 5, self.HEIGHT - 5)
        self.window_title.setText('瑞达期货研究院分析决策系统_管理端_0101911')
        self.setStyleSheet("""
        #titleBar{
            background-color: rgb(85,88,91);
        }
        /*最小化最大化关闭按钮通用默认背景*/
        #buttonMinimum,#buttonMaximum,#buttonClose {
            border: none;
            background-color: rgb(85,88,91);
        }

        /*悬停*/
        #buttonMinimum:hover,#buttonMaximum:hover {
            background-color: rgb(72,75,78);
        }
        #buttonClose:hover {
            color: white;
            background-color: rgb(200,49,61);
        }

        /*鼠标按下不放*/
        #buttonMinimum:pressed,#buttonMaximum:pressed {
            background-color: rgb(37,39,41);
        }
        #buttonClose:pressed {
            color: white;
            background-color: rgb(161, 73, 92);
        }

        """)

        # 布局
        self.setLayout(layout)

    # 最小化
    def windowMinimumed(self):
        print('最小化窗口')
        self.parent().showMinimized()

    # 最大化
    def windowMaximized(self):
        print('最大化窗口')
        if self.buttonMaximum.text() == '1':
            # 最大化
            self.buttonMaximum.setText('2')
            self.parent().showMaximized()
        else:  # 还原
            self.buttonMaximum.setText('1')
            self.parent().showNormal()

    # 关闭
    def windowClosed(self):
        print('关闭窗口')
        self.parent().close()

    # 鼠标双击
    def mouseDoubleClickEvent(self, event):
        self.windowMaximized()

    # 鼠标移动
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._mouse_pos:
            self.parent().move(self.mapToGlobal(event.pos() - self._mouse_pos))
        event.accept()  # 接受事件,不传递到父控件

    # 鼠标点击
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self._mouse_pos = event.pos()
        event.accept()  # 接受事件,不传递到父控件

    # 鼠标弹起
    def mouseReleaseEvent(self, event):
        """鼠标弹起事件"""
        self._mouse_pos = None
        event.accept()  # 接受事件,不传递到父控件


""" 导航栏相关 """


# 自定义模块菜单的QPushButton
class ModuleButton(QPushButton):
    clicked_module = pyqtSignal(QPushButton)

    def __init__(self, mid, text, *args, **kwargs):
        super(ModuleButton, self).__init__(text, *args, **kwargs)
        self.mid = mid
        self.clicked.connect(lambda: self.clicked_module.emit(self))


# 管理菜单按钮
class ManagerMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super(ManagerMenu, self).__init__(*args, **kwargs)
        self.setStyleSheet("""
        QMenu{
            background-color:rgb(85,88,91); /* sets background of the menu 设置整个菜单区域的背景色 */
            border: 1px solid rgb(250,255,250);/*整个菜单区域的边框粗细、样式、颜色*/
         }
        QMenu::item {
            /* sets background of menu item. set this to something non-transparent
                if you want menu color and menu item color to be different */
            background-color: transparent;
            padding:2px 16px;/*设置菜单项文字上下和左右的内边距，效果就是菜单中的条目左右上下有了间隔*/
            margin:0px 2px;/*设置菜单项的外边距*/
            border-bottom:1px solid rgb(180,255,250);/*为菜单项之间添加横线间隔*/
            color: rgb(255,255,255)
        }

        QMenu::item:selected { /* when user selects item using mouse or keyboard */
            background-color: #2dabf9;/*这一句是设置菜单项鼠标经过选中的样式*/
        }
        """)


# 模块菜单栏
class ModuleBar(QWidget):
    menu_clicked = pyqtSignal(int, str)

    def __init__(self, *args, **kwargs):
        super(ModuleBar, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0, spacing=0)
        self.system_manager_button = QPushButton('系统管理')
        self.actions_menu = ManagerMenu()
        self.actions_menu.triggered.connect(self.module_action_selected)
        self.setLayout(layout)
        # 样式设计
        self.setObjectName('moduleBar')
        self.setStyleSheet("""
        #moduleBar{
            min-height:20px;
            max-height:20px;
        }
        QPushButton{
            background-color:rgb(85,88,91);
            color: rgb(255,20,150);
            border: 1px solid rgb(180,255,250);
            margin-left:3px;
            padding: 0px 6px;  /*上下，左右*/
            min-height:16px;
            max-height:16px;
            color: #FFFFFF
        }
        QPushButton:hover {
            background-color: #CD3333;
        }
        """)

    # 清除系统之外的即管理菜单菜单
    def clearActionMenu(self):
        self.actions_menu.clear()
        self.system_manager_button.hide()
        self.system_manager_button.setText('系统管理')

    # 设置菜单按钮
    def setMenus(self, menu_data):
        print('添加前模块菜单个数%d个 %s' % (self.layout().count(), 'piece.base.ModuleBar.setMenus'))
        self.clearActionMenu()
        for menu_item in menu_data:
            menu = ModuleButton(mid=menu_item['id'], text=menu_item['name'])
            menu.clicked_module.connect(self.module_menu_clicked)
            self.layout().addWidget(menu)
        print('添加后模块菜单个数%d个 %s' % (self.layout().count(), 'piece.base.ModuleBar.setMenus'))

    # 添加菜单按钮
    def addMenu(self, mid, text):
        print('添加前模块菜单个数%d个 %s' % (self.layout().count(), 'piece.base.ModuleBar.addMenu'))
        menu = ModuleButton(mid=mid, text=text)
        menu.clicked_module.connect(self.module_menu_clicked)
        self.layout().addWidget(menu)
        print('添加前模块菜单个数%d个 %s' % (self.layout().count(), 'piece.base.ModuleBar.addMenu'))

    # 设置管理菜单
    def setMenuActions(self, actions):
        print('设置管理菜单')
        if not actions:
            return
        self.actions_menu.clear()
        self.system_manager_button.setText('系统管理')
        for action_item in actions:
            action = self.actions_menu.addAction(action_item['name'])
            action.aid = action_item['id']
        self.system_manager_button.setMenu(self.actions_menu)
        self.layout().addWidget(self.system_manager_button)
        self.system_manager_button.show()

    # 菜单被点击了
    def module_menu_clicked(self, button):
        self.menu_clicked.emit(button.mid, button.text())

    # 管理菜单选择了
    def module_action_selected(self, action):
        self.system_manager_button.setText(action.text())
        self.menu_clicked.emit(action.aid, action.text())


# 登录信息栏
class PermitBar(QWidget):
    def __init__(self, *args, **kwargs):
        super(PermitBar, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0, spacing=0)
        # 用户头像
        self.avatar = CAvatar(self, shape=CAvatar.Circle, url='media/avatar.jpg', size=QSize(22, 22),
                              objectName='userAvatar')
        layout.addWidget(self.avatar, alignment=Qt.AlignRight)
        # 用户名
        self.username_shown = QLabel('用户名用户名', parent=self, objectName='usernameShown')
        layout.addWidget(self.username_shown, alignment=Qt.AlignRight)
        # 按钮
        self.login_button = QPushButton('登录', parent=self, objectName='loginBtn')
        layout.addWidget(self.login_button, alignment=Qt.AlignRight)
        self.register_button = QPushButton('注册', parent=self, objectName='registerBtn')
        layout.addWidget(self.register_button, alignment=Qt.AlignRight)
        self.logout_button = QPushButton('注销', parent=self, objectName='logoutBtn')
        layout.addWidget(self.logout_button, alignment=Qt.AlignRight)
        self.setLayout(layout)
        # 样式、属性
        self.username = ''
        self.timer_finished_count = 0
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.logout_button.setCursor(Qt.PointingHandCursor)
        self.initial_show()  # 初始显示的控件
        self.setObjectName('permitBar')
        self.setStyleSheet("""
        #permitBar{
            min-height:22px;
            max-height:22px;
        }
        #loginBtn,#registerBtn,#logoutBtn{
            border:none;
            padding-left: 2px;
            padding-right: 4px;
            color: #FFFFFF;
        }
        #logoutBtn{
            margin-right:5px;
        }
        #loginBtn:hover,#registerBtn:hover,#logoutBtn:hover {
            color: rgb(54,220,180);

        }
        #usernameShown{
            margin-left: 3px;
        }
        /*
        #userAvatar{
            background-color: rgb(100,255,120);
            min-width:22px;
            border-radius: 12px;
            margin-right: 2px;
        }
        */
        """)

    def initial_show(self):
        self.avatar.hide()
        self.username_shown.hide()
        self.logout_button.hide()

    # 显示用户名
    def show_username(self, username):
        self.avatar.show()
        self.username_shown.setText(username + " ")  # 加空格防止初始动态化的时候跳动
        self.username = username
        self.username_shown.show()
        self.login_button.hide()
        self.register_button.hide()
        self.logout_button.show()
        if hasattr(self, 'timer'):
            self.timer.deleteLater()
            del self.timer
        self.timer = QTimer()
        self.timer.start(500)
        self.timer.timeout.connect(self._dynamic_username)

    # 用户注销
    def user_logout(self):
        self.username_shown.setText('')
        self.username = ''
        self.username_shown.hide()
        self.logout_button.hide()
        self.avatar.hide()
        self.login_button.show()
        self.register_button.show()
        if hasattr(self, 'timer'):
            print('注销销毁定时器piece.base.PermitBar.user_logout()')
            self.timer.stop()
            self.timer.deleteLater()
            del self.timer

    # 设置用户名滚动显示
    def _dynamic_username(self):
        if self.timer_finished_count == len(self.username):
            self.username_shown.setText(self.username + " ")
            self.timer_finished_count = 0
        else:
            text = self.username[self.timer_finished_count:] + " " + self.username[:self.timer_finished_count]
            self.username_shown.setText(text)
            self.timer_finished_count += 1


# 导航栏
class NavigationBar(QWidget):
    clicked_login_button = pyqtSignal()
    clicked_register_button = pyqtSignal()
    clicked_logout_button = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(NavigationBar, self).__init__(*args, **kwargs)
        # 模块菜单栏
        self.module_bar = ModuleBar(parent=self, objectName='moduleBar')
        # 登录信息栏
        self.permit_bar = PermitBar(parent=self, objectName='permitBar')
        # 信号连接
        self.permit_bar.login_button.clicked.connect(self.clicked_login_button.emit)
        self.permit_bar.register_button.clicked.connect(self.clicked_register_button.emit)
        self.permit_bar.logout_button.clicked.connect(self.clicked_logout_button.emit)
        # 布局
        layout = QHBoxLayout(margin=0)
        layout.addWidget(self.module_bar, alignment=Qt.AlignLeft)
        layout.addWidget(self.permit_bar, alignment=Qt.AlignRight)
        self.setLayout(layout)
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setObjectName('navigationBar')
        self.setMouseTracking(True)
        self.setStyleSheet("""
        #navigationBar{
            background-color:rgb(100, 100, 100);
            min-height: 24px;
            max-height: 24px;
        }
        """)

    # 鼠标移动
    def mouseMoveEvent(self, event):
        # 接受事件不传递到父控件
        event.accept()


""" 承载具体窗口内容 """


# 承载模块内容的窗口
class LoadedTab(QTabWidget):
    def __init__(self, *args, **kwargs):
        super(LoadedTab, self).__init__(*args, **kwargs)
        self.setDocumentMode(True)  # 去掉边框
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setTabBarAutoHide(True)
        self.setMouseTracking(True)
        self.setObjectName('loadedTab')
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        self.setStyleSheet("""
        #loadedTab{
            background-color: rgb(230, 235, 230)
        }
        """)

    # 鼠标移动事件
    def mouseMoveEvent(self, event, *args, **kwargs):
        event.accept()  # 接受事件,不传递到父控件


""" 主窗口 """


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
        self.setWindowTitle("瑞达期货研究院分析决策系统_管理端_0101911")
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
        # 加入首页菜单
        self._add_homepage_menu()

    # 加入【首页】
    def _add_homepage_menu(self):
        self.navigation_bar.module_bar.addMenu(mid=0, text='首页')

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
        machine_code = settings.app_dawn.value('machine')
        token = settings.app_dawn.value('AUTHORIZATION')
        print('启动客户端自动登录', token)
        if not machine_code or not token:
            print('windows.base.BaseWindows.running_auto_login 没有机器码或token,不用自动登录')
            return
        print('windows.base.BaseWindows.running_auto_login 有机器码或token,自动登录')
        try:
            r = requests.get(
                url=settings.SERVER + 'user/keep-online/?mc=' + machine_code,
                headers={'AUTHORIZATION': token}
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            settings.app_dawn.remove('AUTHORIZATION')  # 状态保持失败移除token
            return  # 自动登录失败
        else:
            if response['data']:
                self.user_login_successfully(response['data'])

    # 用户登录成功(注册成功)
    def user_login_successfully(self, response_data):
        print(response_data)
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
        # 设置模块名称
        self.navigation_bar.module_bar.setMenus(response_data['modules'])
        # 设置管理角色的菜单
        self.navigation_bar.module_bar.setMenuActions(response_data['actions'])

    # 用户点击【注册】
    def user_to_register(self):
        print('用户点击注册按钮')
        from popup.base import RegisterPopup
        register_popup = RegisterPopup(parent=self)
        register_popup.user_registered.connect(self.user_login_successfully)
        if not register_popup.exec_():
            register_popup.deleteLater()
            del register_popup

    # 用户点击【注销】
    def user_to_logout(self):
        print('用户点击注销按钮')
        # 清除菜单
        self.navigation_bar.module_bar.clearActionMenu()
        # 移除token
        settings.app_dawn.remove('AUTHORIZATION')
        self.navigation_bar.permit_bar.user_logout()  # 注销
        # 返回首页
        self.module_clicked(module_id=0, module_text='首页')

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

    # 点击模块菜单事件(接受到模块的id和模块名称)
    def module_clicked(self, module_id, module_text):
        print(module_id, module_text)
        # 查询权限
        machine_code = settings.app_dawn.value('machine')
        if machine_code:
            url = settings.SERVER + 'limit/access-module/' + str(module_id) + '/?mc=' + machine_code
        else:
            url = settings.SERVER + 'limit/access-module/' + str(module_id) + '/'
        try:
            r = requests.get(
                url=url,
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
        else:
            try:
                if module_text == u'首页':
                    from widgets.home import HomePage
                    tab = HomePage(parent=self.tab_loaded)
                elif module_text == u'运营管理':
                    from widgets.operation import OperationMaintain
                    tab = OperationMaintain()
                    tab.addListItem()  # 加入管理项目
            # elif module_text == u'数据管理':
            #     from windows.maintenance import MaintenanceHome
            #     tab = MaintenanceHome(parent=self.tab_loaded)
            # elif module_text == u'权限管理':
            #     from windows.maintenance import AuthorityHome
            #     tab = AuthorityHome(parent=self.tab_loaded)
            #     tab.addComboItem()  # 添加选择当前角色，并由此出发请求相应用户列表
                else:
                    tab = QLabel(parent=self.tab_loaded,
                                 styleSheet='font-size:16px;font-weight:bold;color:rgb(230,50,50)',
                                 alignment=Qt.AlignCenter)
                    tab.setText("「" + module_text + "」暂未开放\n敬请期待,感谢支持~.")
            except Exception as e:
                import traceback
                traceback.print_exc()

            self.tab_loaded.clear()
            self.tab_loaded.addTab(tab, module_text)