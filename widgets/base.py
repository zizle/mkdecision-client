# _*_ coding:utf-8 _*_
# __Author__： zizle
import chardet
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QMenu, QPushButton, QTabWidget, QGridLayout, QScrollArea,\
    QVBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from widgets.CAvatar import CAvatar


__all__ = ['TitleBar', 'NavigationBar', 'LoadedTab', 'ScrollFoldedBox']  # 别的模块 import * 时控制可导入的类


""" 标题栏 """


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


""" 菜单折叠窗 """


# 折叠盒子的按钮
class FoldedBodyButton(QPushButton):
    mouse_clicked = pyqtSignal(dict)

    def __init__(self, text, *args, **kwargs):
        super(FoldedBodyButton, self).__init__(*args, **kwargs)
        self.setText(text)
        # self.group_text = group_text
        # self.gid = gid
        # self.bid = bid
        self.clicked.connect(self.left_mouse_clicked)

    def left_mouse_clicked(self):
        self.mouse_clicked.emit({
            'group_text': self.text(),
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
        # 样式
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)

    # 设置身体控件(由于设置parent后用findChild没找到，用此法)
    def setBody(self, body):
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

    # 添加按钮
    def addButtons(self, group_text, button_list, horizontal_count=3):
        if horizontal_count < 3:
            horizontal_count = 3
        row_index = 0
        col_index = 0
        for index, button_item in enumerate(button_list):
            button = FoldedBodyButton(
                text=button_item.text(),
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
        self.container = QWidget(parent=self)
        self.container.setLayout(layout)
        self.setWidgetResizable(True)
        self.setWidget(self.container)
        # 样式
        self.setObjectName('foldedBox')
        # 设置样式
        self.setMinimumWidth(220)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("""
        #foldedHead{
            background-color: rgb(20,120,200);
            border-bottom: 1px solid rgb(200,200,200)
        }
        #foldedBody{
            background-color: rgb(20,120,100)
        }
        """)

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
        body.mouse_clicked.connect(self.body_button_clicked)
        return body

    # 获取折叠窗的数据
    def getFoldedBoxMenu(self):
        head1 = self.addHead('第1个品种分组')
        head2 = self.addHead('第2个品种分组')
        head3 = self.addHead('第3个品种分组')
        body2 = self.addBody(head=head2)
        buttons = [QPushButton('品种' + str(i)) for i in range(40)]
        body2.addButtons('二组', buttons, horizontal_count=2)

        buttons = [QPushButton('品种' + str(i)) for i in range(55)]
        body1 = self.addBody(head=head1)
        body1.addButtons('一组', buttons, horizontal_count=2)
        self.container.layout().addStretch()

    def body_button_clicked(self, signal):
        pass

