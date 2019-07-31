# _*_ coding:utf-8 _*_
"""
small control in base window
Update: 2019-07-26
Author: zizle
"""
import fitz
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QTimer
from PyQt5.QtGui import QFont,  QColor, QCursor, QImage, QPixmap


class MenuBar(QWidget):
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
        button.clicked.connect(lambda :self.menu_btn_clicked.emit(button))
        self.layout().addWidget(button, alignment=Qt.AlignLeft)

    def addMenuButtons(self, buttons):
        if not isinstance(buttons, list):
            raise ValueError('buttons instance has no iterable')
        for name in buttons:
            self.addMenuButton(QPushButton(name))

    def addStretch(self):
        self.layout().addStretch()


class TitleBar(QWidget):
    # 窗口最小化信号
    windowMinimumed = pyqtSignal()
    # 窗口最大化信号
    windowMaximumed = pyqtSignal()
    # 窗口还原信号
    windowNormaled = pyqtSignal()
    # 窗口关闭信号
    windowClosed = pyqtSignal()
    # 窗口移动
    windowMoved = pyqtSignal(QPoint)

    def __init__(self, *args, **kwargs):
        super(TitleBar, self).__init__(*args, **kwargs)
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
#         self.iconLabel.setScaledContents(True)
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


class PDFReaderContent(QWidget):
    """显示PDF内容控件"""
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


class PermitBar(QWidget):
    def __init__(self, *args, **kwargs):
        super(PermitBar, self).__init__(*args, **kwargs)
        styleSheet = """
        PermitBar {
            background-color: rgb(85,88,91);
        }
        QPushButton {
            background-color: rgb(85,88,91);
            border:none;
            padding-left: 4px;
            padding-right: 4px;
            height:18px;
            color: #FFFFFF
        }
            QPushButton:hover {
            color: rgb(54,220,180);
        }
            QLabel {
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
        self.login_button = QPushButton('登录')
        self.register_button = QPushButton('注册')
        self.exit_button = QPushButton("退出")
        # signal connect slot
        self.login_button.clicked.connect(self.login_button_clicked)
        self.register_button.clicked.connect(self.register_button_clicked)
        self.exit_button.clicked.connect(self.exit_button_clicked)
        # widgets styles and actions
        self.login_message = QLabel("")
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

    def dynamic_user_info(self):
        # show username dynamic
        if self.timer_finished_count == len(self.username):
            self.login_message.setText(self.username)
            self.timer_finished_count = 0
        else:
            self.login_message.setText(self.username[self.timer_finished_count:] + " " + self.username[:self.timer_finished_count])
            self.timer_finished_count += 1

    def login_button_clicked(self):
        # dialog for user login
        from popup.base import Login  # import when required because import with file top will make a circle import
        def has_login(text):
            self.username = text
            self.timer_finished_count = 0
            self.login_button.hide()
            self.register_button.hide()
            self.exit_button.show()
            self.login_message.setText(self.username)
            self.timer = QTimer()  # timer would be bind to self
            self.timer.start(500)
            self.timer.timeout.connect(self.dynamic_user_info)
            # self.login_message.setText(message)
            # self.message = self.login_message.text()
            # # 动态展示登录信息
            # self.finish_count = 0
            # self.timer = QTimer()
            # self.timer.start(500)
            # self.timer.timeout.connect(self._time_record)

        popup = Login()
        popup.successful_login.connect(has_login)
        if not popup.exec():
            del popup

    def register_button_clicked(self):
        from popup.base import Register
        popup = Register()
        if not popup.exec():
            del popup

    def exit_button_clicked(self):
        pass
