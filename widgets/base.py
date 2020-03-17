# _*_ coding:utf-8 _*_
# __Author__： zizle
import fitz
import chardet
import requests
from math import floor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QMenu, QPushButton, QCheckBox, QGridLayout, QScrollArea,\
    QVBoxLayout, QStackedWidget, QDialog, QTextBrowser
from PyQt5.QtGui import QPixmap, QFont, QIcon, QImage
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from widgets.CAvatar import CAvatar
import settings


__all__ = [
    'TitleBar',
    'NavigationBar',
    'LoadedPage',
    'ScrollFoldedBox',
    'TableCheckBox',
    'TableRowDeleteButton',
    'TableRowReadButton',
    'PDFContentPopup',
    'PDFContentShower',
    'TextContentPopup',
    'Paginator'
]  # 别的模块 import * 时控制可导入的类


""" 标题栏 """


# 标题栏
class TitleBar(QWidget):
    HEIGHT = settings.TITLE_BAR_HEIGHT

    def __init__(self, *args, **kwargs):
        super(TitleBar, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0, spacing=0)
        # 图标
        self.window_icon = QLabel(parent=self)
        pixmap = QPixmap('media/logo.png')
        self.window_icon.setScaledContents(True)
        self.window_icon.setPixmap(pixmap)
        # 标题
        self.window_title = QLabel(parent=self, objectName='titleName')
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
        self.window_title.setText('瑞达期货研究院分析决策系统管理端')
        self.setStyleSheet("""
        #titleBar{
            background-color: rgb(34,102,175);
        }
        #titleName{
            color: rgb(210,210,210);
            font-size:14px;
            font-weight: bold;
        }
        /*最小化最大化关闭按钮通用默认背景*/
        #buttonMinimum,#buttonMaximum,#buttonClose {
            border: none;
            background-color: rgb(34,102,175);
        }

        /*悬停*/
        #buttonMinimum:hover,#buttonMaximum:hover {
            background-color: rgb(33,165,229);
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
        # print('最小化窗口')
        self.parent().showMinimized()

    # 最大化
    def windowMaximized(self):
        # print('最大化窗口')
        if self.buttonMaximum.text() == '1':
            # 最大化
            self.buttonMaximum.setText('2')
            self.parent().showMaximized()
            # 修改配置中可用窗口显示区域的大小
            self.resize_access_frame_size()

        else:  # 还原
            self.buttonMaximum.setText('1')
            self.parent().showNormal()
            # 修改配置中可用窗口显示区域的大小
            self.resize_access_frame_size()

    # 调整可用显示区的大小
    def resize_access_frame_size(self):
        height = self.parent().height() - settings.TITLE_BAR_HEIGHT - settings.NAVIGATION_BAR_HEIGHT
        settings.app_dawn.setValue('SCREEN_WIDTH', self.parent().width() - 6)
        settings.app_dawn.setValue('SCREEN_HEIGHT', height)

    # 关闭
    def windowClosed(self):
        # print('关闭窗口')
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
class DropdownMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super(DropdownMenu, self).__init__(*args, **kwargs)
        self.setStyleSheet("""
        QMenu{
            background-color:rgb(34,102,175); /* sets background of the menu 设置整个菜单区域的背景色 */
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
        self.actions_menu = DropdownMenu()
        self.actions_menu.triggered.connect(self.module_action_selected)
        self.setLayout(layout)
        # 样式设计
        self.setObjectName('moduleBar')
        self.setStyleSheet("""
        #moduleBar{
            min-height:24px;
            max-height:24px;
        }
        QPushButton{
            background-color:rgb(34,102,175);
            color: rgb(235,20,150);
            border: 1px solid rgb(34,142,155);
            margin-left:3px;
            padding: 1px 6px;  /*上下，左右*/
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
    def setMenus(self, menu_obj_list):
        # print('添加前模块菜单个数%d个 %s' % (self.layout().count(), 'piece.base.ModuleBar.setMenus'))
        self.clearActionMenu()
        for menu_dict_item in menu_obj_list:
            menu = ModuleButton(mid=menu_dict_item['id'], text=menu_dict_item['name'])
            sub_module_items = menu_dict_item['subs']
            if sub_module_items:  # 有子菜单
                drop_down_menu = DropdownMenu()  # 创建下拉菜单
                drop_down_menu.triggered.connect(self.module_action_selected)  # 下拉菜单信号
                # 先加入原来的模块
                # drop_action = drop_down_menu.addAction(menu_dict_item['name'])
                # drop_action.aid = menu_dict_item['id']
                for sub_module in sub_module_items:
                    drop_action = drop_down_menu.addAction(sub_module['name'])
                    drop_action.aid = sub_module['id']
                menu.setMenu(drop_down_menu)
            else:  # 没有子菜单关联原菜单的点击事件
                menu.clicked_module.connect(self.module_menu_clicked)
            self.layout().addWidget(menu)
        # print('添加后模块菜单个数%d个 %s' % (self.layout().count(), 'piece.base.ModuleBar.setMenus'))

    # 设置管理菜单
    def setMenuActions(self, actions):
        # print('设置管理菜单')
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
        # self.system_manager_button.setText(action.text())
        self.menu_clicked.emit(action.aid, action.text())


# 登录信息栏
class PermitBar(QWidget):
    to_usercenter = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super(PermitBar, self).__init__(*args, **kwargs)
        self.user_id = None
        layout = QHBoxLayout(margin=0, spacing=0)
        # 用户头像
        self.avatar = CAvatar(self, shape=CAvatar.Circle, url='media/avatar.png', size=QSize(22, 22),
                              objectName='userAvatar')
        self.avatar.clicked.connect(self.to_user_center)
        layout.addWidget(self.avatar, alignment=Qt.AlignRight)
        # 用户名
        self.username_shown = QPushButton('用户名用户名', parent=self, objectName='usernameShown', clicked=self.to_user_center)
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
            border:none;
            padding: 0 2px;
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

    # 设置用户id
    def set_user_id(self, uid):
        self.user_id = uid

    # 前往用户中心
    def to_user_center(self):
        if not self.user_id:
            return
        self.to_usercenter.emit(self.user_id)

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

    # 设置头像
    def setAvatar(self, avatar_url):
        self.avatar.setUrl(avatar_url)

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
            # print('注销销毁定时器piece.base.PermitBar.user_logout()')
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
        self.setFixedHeight(settings.NAVIGATION_BAR_HEIGHT)
        self.setStyleSheet("""
        #navigationBar{
            background-color:rgb(34,102,185);
        }
        """)

    # 鼠标移动
    def mouseMoveEvent(self, event):
        # 接受事件不传递到父控件
        event.accept()


""" 承载具体窗口内容 """


# 承载模块内容的窗口
class LoadedPage(QStackedWidget):
    def __init__(self, *args, **kwargs):
        super(LoadedPage, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setMouseTracking(True)
        # self.setObjectName('pageContainer')
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)

    # 鼠标移动事件
    def mouseMoveEvent(self, event, *args, **kwargs):
        event.accept()  # 接受事件,不传递到父控件

    # 清除所有控件
    def clear(self):
        widget = None
        for i in range(self.count()):
            widget = self.widget(i)
            self.removeWidget(widget)
            if widget:
                widget.deleteLater()
        del widget


""" 菜单折叠窗 """


# 折叠盒子的按钮
class FoldedBodyButton(QPushButton):
    mouse_clicked = pyqtSignal(int, str)

    def __init__(self, text, bid, name_en=None, *args, **kwargs):
        super(FoldedBodyButton, self).__init__(*args, **kwargs)
        self.setText(text)
        self.bid = bid
        self.name_en=name_en
        self.clicked.connect(self.left_mouse_clicked)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName('button')

        self.setStyleSheet("""
        #button{
            border:none;
            padding: 5px 0;
            margin-top:3px;
            margin-bottom:3px;
            font-size: 14px;
            min-width: 60px;
            max-width: 60px;
        }
        #button:hover{
            color:rgb(200,120,200);
            background-color:rgb(200,200,200);
            border-radius:5px;
        }
        #button:pressed{
            background-color:rgb(150,150,180);
            color:rgb(250,250,250);
            border-radius:5px;
        }
        """)

    def left_mouse_clicked(self):
        # print(self.bid)
        name_en = self.name_en if self.name_en else ""
        self.mouse_clicked.emit(self.bid, name_en)



# FoldedHead(), FoldedBody()
# 折叠盒子的头
class FoldedHead(QWidget):
    def __init__(self, text, *args, **kwargs):
        super(FoldedHead, self).__init__(*args, **kwargs)
        self.head_text = text
        layout = QHBoxLayout(margin=0)
        self.head_label = QLabel(text, parent=self, objectName='headLabel')
        self.head_button = QPushButton('', parent=self, clicked=self.body_toggle, objectName='headButton', cursor=Qt.PointingHandCursor)
        self.head_button.setFixedSize(20,20)
        layout.addWidget(self.head_label, alignment=Qt.AlignLeft)
        layout.addWidget(self.head_button, alignment=Qt.AlignRight)
        self.setLayout(layout)
        # 样式
        self.body_hidden = False  # 显示与否
        self.body_height = 0  # 原始高度
        # 样式
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        # self.setStyleSheet("""
        # #headLabel{
        #     padding:8px 5px;
        #     font-weight: bold;
        #     font-size:12px;
        # }
        # """)
        self.moreButtonStyle()

    # 折叠的button样式
    def foldedButtonStyle(self):
        self.head_button.setStyleSheet("#headButton{border-image:url('media/folded.png')}")

    # 展开的button样式
    def moreButtonStyle(self):
        self.head_button.setStyleSheet("#headButton{border-image:url('media/more.png')}")

    # 设置身体控件(由于设置parent后用findChild没找到，用此法)
    def setBody(self, body):
        if not hasattr(self, 'bodyChild'):
            self.bodyChild = body

    def get_body(self):
        if hasattr(self, 'bodyChild'):
            return self.bodyChild
        return None

    # 窗体折叠展开动画
    def body_toggle(self):
        # print('头以下的身体折叠展开')
        body = self.get_body()
        if not body:
            return
        self.body_height = body.height()
        self.setMinimumWidth(self.width())
        if not self.body_hidden:
            body.hide()
            self.body_hidden = True
            self.foldedButtonStyle()
        else:
            body.show()
            self.body_hidden = False
            self.moreButtonStyle()


# 折叠盒子的身体
class FoldedBody(QWidget):
    mouse_clicked = pyqtSignal(int, str, str)

    def __init__(self, *args, **kwargs):
        super(FoldedBody, self).__init__(*args, **kwargs)
        layout = QGridLayout(margin=0)
        self.button_list = list()
        self.setLayout(layout)
        # 样式
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)

    # 添加按钮
    def addButtons(self, button_list, horizontal_count=3):
        self.button_list.clear()

        for button_item in button_list:
            button = FoldedBodyButton(
                text=button_item['name'],
                bid=button_item['id'],
                name_en=button_item.get('name_en', None),
                parent=self
            )
            button.mouse_clicked.connect(self.body_button_clicked)
            self.button_list.append(button)

    # 按钮被点击
    def body_button_clicked(self, bid, name_en):
        # 获取body的parent
        head = self.get_head()
        self.mouse_clicked.emit(bid, head.head_text, name_en)

    # 设置身体控件(由于设置parent后用findChild没找到，用此法)
    def setHead(self, head):
        if not hasattr(self, 'myHead'):
            self.myHead = head

    def get_head(self):
        if hasattr(self, 'myHead'):
            return self.myHead
        return None

    def resetHorizationItemCount(self, body_width):
        # 得到控件的大小，计算一列能容下的数量，向下取整
        horizontal_count = floor(body_width / 65)  # 每个button的宽度是60 + 间距5
        # 设置填入buttons
        row_index = 0
        col_index = 0
        for index, button in enumerate(self.button_list):
            self.layout().addWidget(button, row_index, col_index)
            col_index += 1
            if col_index == horizontal_count:  # 因为col_index先+1,此处应相等
                row_index += 1
                col_index = 0


# 滚动折叠盒子
class ScrollFoldedBox(QScrollArea):
    left_mouse_clicked = pyqtSignal(int, str, str)  # 当前id 与父级的text

    def __init__(self, *args, **kwargs):
        super(ScrollFoldedBox, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0, spacing=0)
        self.container = QWidget(parent=self)
        self.container.setLayout(layout)
        self.setWidgetResizable(True)
        self.setWidget(self.container)
        # 样式
        self.setObjectName('foldedBox')
        # 设置样式
        self.setMinimumWidth(240)
        self.head_list = list()

    def setFoldedStyleSheet(self, stylesheet):
        self.setStyleSheet(stylesheet)

    # 鼠标进入显示竖直滚动条
    def enterEvent(self, *args, **kwargs):
        super(ScrollFoldedBox, self).enterEvent(*args, **kwargs)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    # 鼠标离开不显示滚动条
    def leaveEvent(self, *args, **kwargs):
        super(ScrollFoldedBox, self).leaveEvent(*args, **kwargs)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    # 添加头部
    def addHead(self, text):
        head = FoldedHead(text, parent=self.container, objectName='foldedHead')
        self.container.layout().addWidget(head, alignment=Qt.AlignTop)
        self.head_list.append(head)
        return head

    # 添加头部的身体
    def addBody(self, head):
        body = FoldedBody(parent=self.container, objectName='foldedBody')
        head.setBody(body)
        # 找出head所在的位置
        for i in range(self.container.layout().count()):
            widget = self.container.layout().itemAt(i).widget()
            if isinstance(widget, FoldedHead) and widget == head:
                self.container.layout().insertWidget(i+1, body, alignment=Qt.AlignTop)
                break
        # 连接信号
        body.mouse_clicked.connect(self.left_mouse_clicked.emit)
        body.setHead(head)
        return body
    
    def setBodyHorizationItemCount(self):
        for head in self.head_list:
            body = head.get_body()
            if body:
                body.resetHorizationItemCount(self.width())


""" 表格控件 """


# 复选框
class TableCheckBox(QWidget):
    check_activated = pyqtSignal(QWidget)

    def __init__(self, checked=False, *args, **kwargs):
        super(TableCheckBox, self).__init__(*args, **kwargs)
        self.check_box = QCheckBox(checked=checked)
        self.check_box.setMinimumHeight(14)
        layout = QVBoxLayout()
        layout.addWidget(self.check_box, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        self.check_box.stateChanged.connect(lambda: self.check_activated.emit(self))


# 删除一条记录
class TableRowDeleteButton(QPushButton):
    button_clicked = pyqtSignal(QPushButton)

    def __init__(self, *args, **kwargs):
        super(TableRowDeleteButton, self).__init__(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(lambda: self.button_clicked.emit(self))
        self.setObjectName('tableDelete')
        self.setStyleSheet("""
            #tableDelete{
                border: none;
                padding: 1px 8px;
                color: rgb(200,100,100);
            }
            #tableDelete:hover{
                color: rgb(240,100,100)
            }
            """)


# 阅读一条记录
class TableRowReadButton(QPushButton):
    button_clicked = pyqtSignal(QPushButton)

    def __init__(self, *args, **kwargs):
        super(TableRowReadButton, self).__init__(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(lambda: self.button_clicked.emit(self))
        self.setObjectName('tableDelete')
        self.setStyleSheet("""
        #tableDelete{
            border: none;
            padding: 1px 8px;
            color: rgb(100,150,180);
        }
        #tableDelete:hover{
            color: rgb(120,130,230)
        }
        """)


""" 阅读内容相关 """


# PDF文件内容直显
class PDFContentShower(QScrollArea):
    def __init__(self, file, *args, **kwargs):
        super(PDFContentShower, self).__init__(*args, **kwargs)
        self.file = file
        # auth doc type
        # scroll
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # 设置滚动条样式
        with open("media/ScrollBar.qss", "rb") as fp:
            content = fp.read()
            encoding = chardet.detect(content) or {}
            content = content.decode(encoding.get("encoding") or "utf-8")
        self.setStyleSheet(content)
        # content
        self.page_container = QWidget()
        self.page_container.setLayout(QVBoxLayout())
        # initial data
        self.add_pages()
        # add to show
        self.setWidget(self.page_container)

    def add_pages(self):
        # 请求文件
        if not self.file:
            message_label = QLabel('没有文件.')
            self.page_container.layout().addWidget(message_label)
            return
        try:
            response = requests.get(self.file)
            doc = fitz.Document(filename='a', stream=response.content)
        except Exception as e:
            message_label = QLabel('获取文件内容失败.\n{}'.format(e))
            self.page_container.layout().addWidget(message_label)
            return
        for page_index in range(doc.pageCount):
            page = doc.loadPage(page_index)
            page_label = QLabel()
            # page_label.setMinimumSize(self.width() - 20, self.height())  # 设置label大小
            # show PDF content
            zoom_matrix = fitz.Matrix(1.5, 1.5)  # 图像缩放比例
            pagePixmap = page.getPixmap(
                matrix=zoom_matrix,
                alpha=False)
            imageFormat = QImage.Format_RGB888  # get image format
            pageQImage = QImage(
                pagePixmap.samples,
                pagePixmap.width,
                pagePixmap.height,
                pagePixmap.stride,
                imageFormat)  # init QImage
            page_map = QPixmap()
            page_map.convertFromImage(pageQImage)
            page_label.setPixmap(page_map)
            page_label.setScaledContents(True)  # pixmap resize with label
            self.page_container.layout().addWidget(page_label)


# PDF文件内容弹窗
class PDFContentPopup(QDialog):
    def __init__(self, title, file, *args, **kwargs):
        super(PDFContentPopup, self).__init__(*args, **kwargs)
        self.file = file
        self.file_name = title
        # auth doc type
        self.setWindowTitle(title)
        self.setMinimumSize(1010, 600)
        self.download = QPushButton("下载PDF")
        self.download.setIcon(QIcon('media/download-file.png'))
        self.setWindowIcon(QIcon("media/reader.png"))
        # scroll
        scroll_area = QScrollArea()
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # 设置滚动条样式
        with open("media/ScrollBar.qss", "rb") as fp:
            content = fp.read()
            encoding = chardet.detect(content) or {}
            content = content.decode(encoding.get("encoding") or "utf-8")
        scroll_area.setStyleSheet(content)
        # content
        self.page_container = QWidget()
        self.page_container.setLayout(QVBoxLayout())
        layout = QVBoxLayout(margin=0)
        # initial data
        self.add_pages()
        # add to show
        scroll_area.setWidget(self.page_container)
        # add layout
        # layout.addWidget(self.download, alignment=Qt.AlignLeft)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def add_pages(self):
        # 请求文件
        if not self.file:
            message_label = QLabel('没有文件.')
            self.page_container.layout().addWidget(message_label)
            return
        try:
            response = requests.get(self.file)
            doc = fitz.Document(filename=self.file_name, stream=response.content)
        except Exception as e:
            message_label = QLabel('获取文件内容失败.\n{}'.format(e))
            self.page_container.layout().addWidget(message_label)
            return
        for page_index in range(doc.pageCount):
            page = doc.loadPage(page_index)
            page_label = QLabel()
            page_label.setMinimumSize(self.width() - 25, self.height())  # 设置label大小
            # show PDF content
            zoom_matrix = fitz.Matrix(1.58, 1.5)  # 图像缩放比例
            pagePixmap = page.getPixmap(
                matrix=zoom_matrix,
                alpha=False)
            imageFormat = QImage.Format_RGB888  # get image format
            pageQImage = QImage(
                pagePixmap.samples,
                pagePixmap.width,
                pagePixmap.height,
                pagePixmap.stride,
                imageFormat)  # init QImage
            page_map = QPixmap()
            page_map.convertFromImage(pageQImage)
            page_label.setPixmap(page_map)
            page_label.setScaledContents(True)  # pixmap resize with label
            self.page_container.layout().addWidget(page_label)


# 纯文字内容弹窗
class TextContentPopup(QDialog):
    def __init__(self, title, content, *args, **kwargs):
        super(TextContentPopup, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        text_browser = QTextBrowser()
        text_browser.setText(content)
        layout.addWidget(text_browser)
        self.setWindowTitle(title)
        self.setLayout(layout)


""" 分页 """


# 页码控制区
class Paginator(QWidget):
    clicked = pyqtSignal(int)

    def __init__(self, total_pages=1, *args, **kwargs):
        super(Paginator, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0)
        self.total_pages = total_pages
        self.current_page = 1
        self.home_button = QPushButton('首页', objectName='pageButton', cursor=Qt.PointingHandCursor, clicked=self.go_home_page)
        self.pre_button = QPushButton('上一页', objectName='pageButton', cursor=Qt.PointingHandCursor, clicked=self.go_pre_page)
        self.current_label = QLabel(objectName='pageLabel')
        self.current_label.setText(str(self.current_page) + '/' + str(self.total_pages))
        self.next_button = QPushButton('下一页', objectName='pageButton', cursor=Qt.PointingHandCursor, clicked=self.go_next_page)
        self.final_button = QPushButton('尾页', objectName='pageButton', cursor=Qt.PointingHandCursor, clicked=self.go_final_page)
        layout.addWidget(self.home_button)
        layout.addWidget(self.pre_button)
        layout.addWidget(self.current_label)
        layout.addWidget(self.next_button)
        layout.addWidget(self.final_button)
        self.setLayout(layout)
        self.setStyleSheet("""
        #pageButton{
            border:none;
            color:rgb(100,100,100);
            font-size:12px;
        }
        #pageButton:hover{
            border-bottom:1px solid rgb(95,95,95);
        }
        #pageLabel{
            color:rgb(100,100,100);
        }
        """)

    # 设置外边距
    def setMargins(self, a, b, c, d):
        self.layout().setContentsMargins(a, b, c, d)

    # 清空页码
    def clearPages(self):
        self.current_page = self.total_pages = 1
        self.current_label.setText('1/1')

    # 设置总页数
    def setTotalPages(self, total_pages):
        self.total_pages = total_pages
        self.current_page = self.current_page
        self.setCurrentPageLable()

    # 设置当前页
    def setCurrentPageLable(self):
        self.current_label.setText(str(self.current_page) + '/' + str(self.total_pages))

    # 点击首页
    def go_home_page(self):
        if self.current_page == 1:
            return
        self.current_page = 1
        self.setCurrentPageLable()
        self.clicked.emit(self.current_page)

    # 点击尾页
    def go_final_page(self):
        if self.current_page == self.total_pages:
            return
        self.current_page = self.total_pages
        self.setCurrentPageLable()
        self.clicked.emit(self.current_page)

    # 点击上一页
    def go_pre_page(self):
        if self.current_page == 1:
            return
        self.current_page -= 1
        self.setCurrentPageLable()
        self.clicked.emit(self.current_page)

    # 点击下一页
    def go_next_page(self):
        if self.current_page == self.total_pages:
            return
        self.current_page += 1
        # print('下一页里',self.current_page)
        self.setCurrentPageLable()
        self.clicked.emit(self.current_page)
