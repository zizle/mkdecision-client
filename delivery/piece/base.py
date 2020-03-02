# _*_ coding:utf-8 _*_
"""
small control in base window
Update: 2019-07-26
Author: zizle
"""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QFont,  QColor


class TitleBar(QWidget):
    windowMinimumed = pyqtSignal()  # 窗口最小化信号
    windowMaximumed = pyqtSignal()  # 窗口最大化信号
    windowNormaled = pyqtSignal()  # 窗口还原信号
    windowClosed = pyqtSignal()  # 窗口关闭信号
    windowMoved = pyqtSignal(QPoint)  # 窗口移动

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
