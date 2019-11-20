# _*_ coding:utf-8 _*_
"""
small control in base window
Update: 2019-07-26
Author: zizle
"""
import fitz
import json
import requests
from PyQt5.QtWidgets import qApp, QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QLineEdit, QMessageBox, QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QTimer, QSize
from PyQt5.QtGui import QFont,  QColor, QCursor, QImage, QPixmap, QIcon
import config
from widgets.CAvatar import CAvatar


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
        layout.addWidget(self.buttonMinimum, alignment=Qt.AlignRight|Qt.AlignTop)
        # 最大化/还原按钮
        self.buttonMaximum = QPushButton(
            '1', parent=self, font=font, clicked=self.windowMaximized, objectName='buttonMaximum')
        layout.addWidget(self.buttonMaximum, alignment=Qt.AlignRight|Qt.AlignTop)
        # 关闭按钮
        self.buttonClose = QPushButton(
            'r', parent=self, font=font, clicked=self.windowClosed, objectName='buttonClose')
        layout.addWidget(self.buttonClose, alignment=Qt.AlignRight|Qt.AlignTop)
        # 属性、样式
        self._mouse_pos = None
        self.setObjectName('titleBar')
        self.setFixedHeight(self.HEIGHT)
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        self.window_icon.setMargin(2)
        self.window_icon.setFixedSize(self.HEIGHT-5, self.HEIGHT-5)
        self.window_title.setMargin(3)
        self.buttonMinimum.setFixedSize(self.HEIGHT-5, self.HEIGHT-5)
        self.buttonMaximum.setFixedSize(self.HEIGHT-5, self.HEIGHT-5)
        self.buttonClose.setFixedSize(self.HEIGHT-5, self.HEIGHT-5)
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


# 模块菜单栏
class ModuleBar(QWidget):
    def __init__(self, *args, **kwargs):
        super(ModuleBar, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0, spacing=0)
        layout.addWidget(QPushButton('菜单'))
        layout.addWidget(QPushButton('菜单'))
        layout.addWidget(QPushButton('菜单'))
        layout.addWidget(QPushButton('菜单'))
        self.setLayout(layout)
        # 样式设计
        print(self.parent().height())
        self.setStyleSheet("""
        QPushButton{
            background-color:rgb(85,88,91);
            color: rgb(255,20,150);
            border: 1px solid rgb(180,255,250);
            margin-left:3px;
            padding: 0px 4px;  /*上下，左右*/
            min-height:20px;
            max-height:20px;
            color: #FFFFFF
        }
        QPushButton:hover {
            background-color: #CD3333;
        }
        """)

    # 设置菜单按钮
    def setMenus(self, menu_data):
        # 清除所有的控件
        print('添加前模块菜单个数%d个 %s' % (self.layout().count(), 'piece.base.ModuleBar.setMenus'))
        count = self.layout().count()
        for i in range(count):
            widget = self.layout().itemAt(i).widget()
            widget.deleteLater()
            if i == count - 1:
                del widget  # 删除引用
        for button in menu_data:
            self.layout().addWidget(button)
        print('添加后模块菜单个数%d个 %s' % (self.layout().count(), 'piece.base.ModuleBar.setMenus'))

    # 添加菜单按钮
    def addMenu(self, menu):
        print('添加前模块菜单个数%d个 %s' % (self.layout().count(), 'piece.base.ModuleBar.addMenu'))
        self.layout().addWidget(menu)
        print('添加前模块菜单个数%d个 %s' % (self.layout().count(), 'piece.base.ModuleBar.addMenu'))


# 登录信息栏
class PermitBar(QWidget):
    def __init__(self, *args, **kwargs):
        super(PermitBar, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0, spacing=0)
        # 用户头像
        self.avatar = CAvatar(self, shape=CAvatar.Circle, url='media/avatar.jpg', size=QSize(24, 24), objectName='userAvatar')
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
        # 样式
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.logout_button.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
        #loginBtn,#registerBtn,#logoutBtn{
            border:none;
            padding-left: 2px;
            padding-right: 4px;
            color: #FFFFFF;
            min-height:24px;
            max-height:24px;
        }
        #logoutBtn{
            margin-right:5px;
        }
        #loginBtn:hover,#registerBtn:hover,#logoutBtn:hover {
            color: rgb(54,220,180);
            
        }
        #usernameShown{
            min-height:24px;
            max-height:24px;
            margin-right: 5px;
        }
        /*
        #userAvatar{
            background-color: rgb(100,255,120);
            min-height:24px;
            max-height:24px;
            min-width:24px;
            border-radius: 12px;
            margin-right: 2px;
        }
        */
        """)


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
            background-color:rgb(200,200,200);
            min-height: 24px;
            max-height: 24px;
        }
        
        """)

    # 鼠标移动
    def mouseMoveEvent(self, event):
        # 接受事件不传递到父控件
        event.accept()











# 主功能菜单栏
class MenuBar(QWidget):
    # 横向菜单栏
    menu_btn_clicked = pyqtSignal(QPushButton)

    def __init__(self, *args, **kwargs):
        super(MenuBar, self).__init__(*args, **kwargs)
        # 支持qss设置背景
        self.setAttribute(Qt.WA_StyledBackground, True)
        layout = QHBoxLayout(spacing=0)
        self.setLayout(layout)

    def setContentsMargins(self, *__args):
        self.layout().setContentsMargins(*__args)

    def addMenuButton(self, button):
        if not isinstance(button, QPushButton):
            raise ValueError('menu instance must be QPushButton QObject')
        button.clicked.connect(lambda: self.menu_btn_clicked.emit(button))
        self.layout().addWidget(button, alignment=Qt.AlignLeft)

    def addMenuButtons(self, buttons):
        if not isinstance(buttons, list):
            raise ValueError('buttons instance has no iterable')
        for name in buttons:
            self.addMenuButton(QPushButton(name))

    def addStretch(self):
        self.layout().addStretch()


# 登录注销栏
class PermitBar1(QWidget):
    user_logout = pyqtSignal(bool)
    is_superman = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        super(PermitBar1, self).__init__(*args, **kwargs)
        styleSheet = """
        PermitBar {
            background-color: rgb(85,88,91);
        }
        #loginBtn,#registerBtn,#exitBtn {
            background-color: rgb(85,88,91);
            border:none;
            padding-left: 4px;
            padding-right: 4px;
            height:18px;
            color: #FFFFFF
        }
        #loginBtn:hover,#registerBtn:hover,#exitBtn:hover {
            color: rgb(54,220,180);
        }
        #loginMessage{
            background-color: rgb(85,88,91);
            height:18px;
            color: rgb(210, 200, 205)
        }
        """
        # 支持qss设置背景
        self.setAttribute(Qt.WA_StyledBackground, True)
        # 设置背景颜色,否则由于受到父窗口的影响导致透明
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(palette.Window, QColor(255,255,255))
        self.setPalette(palette)
        layout = QHBoxLayout(spacing=0)
        layout.setContentsMargins(0,0,0,0)
        # widgets
        self.login_button = QPushButton('登录', objectName='loginBtn', clicked=self.login_button_clicked)
        self.register_button = QPushButton('注册', objectName='registerBtn', clicked=self.register_button_clicked)
        self.exit_button = QPushButton("退出", objectName='exitBtn', clicked=self.logout)
        # widgets styles and actions
        self.login_message = QLabel(objectName='loginMessage')
        self.login_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.register_button.setCursor(QCursor(Qt.PointingHandCursor))
        # hide message and exit button
        self.login_message.hide()
        self.exit_button.hide()
        self.setStyleSheet(styleSheet)
        self.exit_button.setStyleSheet("""
        QPushButton {
            background-color: rgb(85,88,91);
            border:none;
            padding-left: 10px;
            padding-right: 8px;
            height:18px;
            font-size:11px;
            color: rgb(210,210,210)
        }
        QPushButton:hover {
            color: rgb(230,0,5);
        }
        """)
        # add to layout
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)
        layout.addWidget(self.login_message)
        layout.addWidget(self.exit_button)
        self.setLayout(layout)

    # 自动登录
    def check_keep_online(self):
        machine_code = config.app_dawn.value('machine')
        token = config.app_dawn.value('AUTHORIZATION')
        if not machine_code or not token:
            print('piece.base.PermitBar.check_keep_online 没有机器码或token,不用自动登录')
            return
        print('piece.base.PermitBar.check_keep_online 有机器码或token,自动登录')
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'user/keep-online/?mc=' + machine_code,
                headers={'AUTHORIZATION': token}
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            return
        # 用户名信息设置到登录信息栏
        user_data = response['data']
        sig_username = user_data['username']
        if not user_data['username']:
            phone = user_data['phone']
            sig_username = phone[0:3] + '****' + phone[8:11]
        # 判断是否是超级管理员登录
        print('piece.base.PermitBar.check_keep_online:', user_data)
        self.has_login(sig_username)  # 设置到信息栏
        if user_data['superman']:
            print('自动登录-超级管理员发出信号1')
            self.is_superman.emit(True)
            print('自动登录-超级管理员发出信号2')

    # 点击登录
    def login_button_clicked(self):
        from popup.base import LoginPopup
        popup = LoginPopup(parent=self)
        popup.user_listed.connect(self.has_login)
        popup.deleteLater()
        if not popup.exec_():
            del popup

    # 已登录改变显示状态
    def has_login(self, text):
        self.username = text
        # 定时器用于动态展示用户名
        if hasattr(self, 'timer'):
            del self.timer
        self.timer = QTimer()
        self.timer_finished_count = 0
        self.login_button.hide()
        self.register_button.hide()
        self.exit_button.show()
        self.login_message.setText(self.username)
        self.login_message.show()
        self.timer.start(500)
        self.timer.timeout.connect(self._dynamic_user_info)

    # 动态滚动展示用户信息
    def _dynamic_user_info(self):
        if self.timer_finished_count == len(self.username):
            self.login_message.setText(self.username)
            self.timer_finished_count = 0
        else:
            self.login_message.setText(
                self.username[self.timer_finished_count:] + " " + self.username[:self.timer_finished_count])
            self.timer_finished_count += 1

    # 注销退出
    def logout(self):
        # 移除信息
        config.app_dawn.remove('AUTHORIZATION')
        self.login_button.show()
        self.register_button.show()
        self.exit_button.hide()
        self.login_message.setText('')
        self.login_message.hide()
        # 停止定时器
        if hasattr(self, 'timer'):
            self.timer.stop()
        # 传出信号
        self.user_logout.emit(True)

    # 点击注册
    def register_button_clicked(self):
        from popup.base import RegisterPopup
        popup = RegisterPopup(parent=self)
        popup.user_registered.connect(self.has_login)  # 注册即登录
        popup.deleteLater()
        if not popup.exec_():
            del popup











class PDFReaderContent(QWidget):
    # 显示PDF内容控件
    def __init__(self):
        super(PDFReaderContent, self).__init__()
        self.page_layout = QVBoxLayout()  # 每一页内容展示在一个竖向布局中
        self.setLayout(self.page_layout)

    def add_page(self, page):
        """添加页码"""
        page_label = QLabel()
        page_label.setMinimumSize(self.width()+180, self.height())  # 设置label大小
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
        self.page_layout.addWidget(page_label, alignment=Qt.AlignRight)


class PageController(QWidget):
    # 页码控制器
    clicked = pyqtSignal(int)
    def __init__(self, *args, **kwargs):
        super(PageController, self).__init__(*args, **kwargs)
        # total page
        self.total_page = 1
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        homePage = QPushButton("首页")
        prePage = QPushButton("<上一页")
        self.curPage = QLabel("1")
        nextPage = QPushButton("下一页>")
        finalPage = QPushButton("尾页")
        self.totalPage = QLabel("共1页")
        skipLabel_0 = QLabel("跳到")
        self.skipPage = QLineEdit()
        skipLabel_1 = QLabel("页")
        confirmSkip = QPushButton("确定")
        # signal
        homePage.clicked.connect(self.click_home_page)
        prePage.clicked.connect(self.click_pre_page)
        nextPage.clicked.connect(self.click_next_page)
        finalPage.clicked.connect(self.click_final_page)
        confirmSkip.clicked.connect(self.click_confirm_skip)
        layout.addWidget(homePage)
        layout.addWidget(prePage)
        layout.addWidget(self.curPage)
        layout.addWidget(nextPage)
        layout.addWidget(finalPage)
        layout.addWidget(self.totalPage)
        layout.addWidget(skipLabel_0)
        layout.addWidget(self.skipPage)
        layout.addWidget(skipLabel_1)
        layout.addWidget(confirmSkip)
        self.setStyleSheet("""     
        QLineEdit{
            max-width:25px;
            min-width:25px;
        }
        QPushButton{
            border: 1px solid rgb(180,180,180);
            font-size:11px;
            padding: 2px 4px
        }
        QPushButton:hover{
            color: rgb(50,50,230);
        }
        """)
        self.setLayout(layout)

    def set_total_page(self, total):
        try:
            self.total_page = int(total)
        except Exception:
            return
        self.totalPage.setText("共" + str(total) + "页")

    def click_home_page(self):
        # get current page number
        try:
            current_page = int(self.curPage.text())
        except Exception:
            return
        if current_page == 1:
            QMessageBox.information(self, '错误', '已经是首页', QMessageBox.Yes)
            return
        self.curPage.setText(str(1))
        # emit signal
        self.clicked.emit(1)

    def click_pre_page(self):
        # get current page number
        try:
            current_page = int(self.curPage.text())
        except Exception:
            return
        if current_page <= 1:
            QMessageBox.information(self, '错误', '当前是第一页', QMessageBox.Yes)
            return
        request_page = current_page - 1
        self.curPage.setText(str(request_page))
        # emit signal
        self.clicked.emit(request_page)

    def click_next_page(self):
        # get current page number and total page
        try:
            current_page = int(self.curPage.text())
        except Exception:
            return
        if current_page == self.total_page:
            QMessageBox.information(self, '错误', '当前是最后一页', QMessageBox.Yes)
            return
        request_page = current_page + 1
        self.curPage.setText(str(request_page))
        # emit signal
        self.clicked.emit(request_page)

    def click_final_page(self):
        # get current page number and total page
        try:
            current_page = int(self.curPage.text())
        except Exception:
            return
        if current_page == self.total_page:
            QMessageBox.information(self, '错误', '已经是尾页', QMessageBox.Yes)
            return
        self.curPage.setText(str(self.total_page))
        # emit signal
        self.clicked.emit(self.total_page)

    def click_confirm_skip(self):
        # get skip page number
        try:
            skip_page = int(self.skipPage.text().strip(' '))
        except Exception as error:
            QMessageBox.warning(self, '错误', '请输入正确的页码.', QMessageBox.Yes)
            return
        if skip_page < 1 or skip_page > self.total_page:
            QMessageBox.warning(self, '错误', '超出范围.', QMessageBox.Yes)
            return
        self.curPage.setText(str(skip_page))
        self.clicked.emit(skip_page)


class TableCheckBox(QWidget):
    """ checkbox in client info table """
    clicked_changed = pyqtSignal(dict)

    def __init__(self, row, col, option_label, *args):
        super(TableCheckBox, self).__init__(*args)
        v_layout = QVBoxLayout()
        layout = QHBoxLayout()
        self.check_box = QCheckBox()
        self.check_box.setMinimumHeight(15)
        self.rowIndex = row
        self.colIndex = col
        self.option_label = option_label
        layout.addWidget(self.check_box, alignment=Qt.AlignCenter)
        self.check_box.stateChanged.connect(self.check_state_changed)
        v_layout.addLayout(layout)
        self.setLayout(v_layout)

    def check_state_changed(self):
        # self.check_change_signal.emit({'row': self.rowIndex, 'col': self.colIndex, 'checked': self.check_box.isChecked(), 'option_label': self.option_label})
        self.clicked_changed.emit({'row': self.rowIndex, 'col': self.colIndex, 'checked': self.check_box.isChecked(), 'option_label': self.option_label})

    def setChecked(self, tag):
        self.check_box.setChecked(tag)


class TitleBar1(QWidget):
    windowMinimumed = pyqtSignal()  # 窗口最小化信号
    windowMaximumed = pyqtSignal()  # 窗口最大化信号
    windowNormaled = pyqtSignal()  # 窗口还原信号
    windowClosed = pyqtSignal()  # 窗口关闭信号
    windowMoved = pyqtSignal(QPoint)  # 窗口移动
    def __init__(self, *args, **kwargs):
        super(TitleBar1, self).__init__(*args, **kwargs)
        # 样式
        StyleSheet = """
        /*标题栏*/
        TitleBar {
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
        QLabel{
            color:rgb(210,210,210)
        }
        """
        self.setStyleSheet(StyleSheet)
        # 支持qss设置背景
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.mPos = None
        self.iconSize = 25  # 图标的默认大小
        # 设置默认背景颜色,否则由于受到父窗口的影响导致透明
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(palette.Window, QColor(240, 240, 240))
        self.setPalette(palette)
        # 布局
        layout = QHBoxLayout(spacing=0)
        layout.setContentsMargins(0, 0, 0, 0)
        # 窗口图标
        self.iconLabel = QLabel(self)
        self.iconLabel.setContentsMargins(8, 0, 3, 0)
        # self.iconLabel.setScaledContents(True)
        layout.addWidget(self.iconLabel)
        # 窗口标题
        self.titleLabel = QLabel(self)
        self.titleLabel.setMargin(2)
        layout.addWidget(self.titleLabel)
        # 中间伸缩条
        layout.addStretch()
        # 利用Webdings字体来显示图标
        font = QFont()
        font.setFamily('Webdings')
        # 最小化按钮
        self.buttonMinimum = QPushButton(
            '0', self, clicked=self.windowMinimumed.emit, font=font, objectName='buttonMinimum')
        layout.addWidget(self.buttonMinimum, alignment=Qt.AlignTop)
        # 最大化/还原按钮
        self.buttonMaximum = QPushButton(
            '1', self, clicked=self.showMaximized, font=font, objectName='buttonMaximum')
        layout.addWidget(self.buttonMaximum, alignment=Qt.AlignTop)
        # 关闭按钮
        self.buttonClose = QPushButton(
            'r', self, clicked=self.windowClosed.emit, font=font, objectName='buttonClose')
        layout.addWidget(self.buttonClose, alignment=Qt.AlignTop)
        self.buttonMinimum.setMinimumSize(30,30)
        self.buttonMinimum.setMaximumSize(30,30)
        self.buttonMaximum.setMinimumSize(30,30)
        self.buttonMaximum.setMaximumSize(30,30)
        self.buttonClose.setMinimumSize(30,30)
        self.buttonClose.setMaximumSize(30,30)
        # 初始高度
        self.setMinimumHeight(38)
        self.setMaximumHeight(38)
        self.setLayout(layout)

    def enterEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super(TitleBar, self).enterEvent(event)

    def mouseDoubleClickEvent(self, event):
        super(TitleBar, self).mouseDoubleClickEvent(event)
        self.showMaximized()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.mPos:
            self.windowMoved.emit(self.mapToGlobal(event.pos() - self.mPos))
        event.accept()

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.mPos = event.pos()
        event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标弹起事件"""
        self.mPos = None
        event.accept()

    def setIcon(self, icon):
        """设置图标"""
        self.iconLabel.setPixmap(icon.pixmap(self.iconSize, self.iconSize))

    def setIconSize(self, size):
        """设置图标大小"""
        self.iconSize = size

    def setTitle(self, title):
        """设置标题"""
        self.titleLabel.setText(title)

    def showMaximized(self):
        if self.buttonMaximum.text() == '1':
            # 最大化
            self.buttonMaximum.setText('2')
            self.windowMaximumed.emit()
        else:  # 还原
            self.buttonMaximum.setText('1')
            self.windowNormaled.emit()
