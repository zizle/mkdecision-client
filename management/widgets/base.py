# _*_ coding:utf-8 _*_
"""
base widget in project
Create: 2019-08-07
Author: zizle
"""
import sys
import json
from PyQt5.QtWidgets import QTabWidget, QPushButton, QLabel, QTableWidget, QScrollArea, QWidget, QHBoxLayout,\
    QVBoxLayout, QGridLayout
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QPropertyAnimation, QSize
from PyQt5.QtGui import QCursor, QBrush, QColor

import config
from thread.request import RequestThread


# 自定义模块菜单的QPushButton
class ModuleButton(QPushButton):
    clicked_module = pyqtSignal(QPushButton)

    def __init__(self, mid, text, *args, **kwargs):
        super(ModuleButton, self).__init__(text, *args, **kwargs)
        self.mid = mid
        self.clicked.connect(lambda: self.clicked_module.emit(self))


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
            background-color: rgb(230, 230, 230)
        }
        """)

    # 鼠标移动事件
    def mouseMoveEvent(self, event, *args, **kwargs):
        event.accept()  # 接受事件,不传递到父控件


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
        # 折叠动画
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
    def addButtons(self, button_list, horizontal_count=3):
        if horizontal_count < 3:
            horizontal_count = 3
        row_index = 0
        col_index = 0
        for index, button in enumerate(button_list):
            self.layout().addWidget(button, row_index, col_index)
            col_index += 1
            if col_index == horizontal_count:  # 因为col_index先+1,此处应相等
                row_index += 1
                col_index = 0


# 折叠盒子
class FoldedBox(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(FoldedBox, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0, spacing=0)
        self.container = QWidget()
        self.container.setLayout(layout)
        self.setWidgetResizable(True)
        self.setWidget(self.container)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

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
        return body

    def addStretch(self):
        self.container.layout().addStretch()













class Loading(QLabel):
    clicked = pyqtSignal(bool)

    def __init__(self, *args):
        super(Loading, self).__init__(*args)
        self.click_able = False
        self.loading_text = '数据请求中···'
        self.setText(self.loading_text)
        self.setAlignment(Qt.AlignCenter)
        self.timer = QTimer()
        self.timeout_count = -1
        self.timer.timeout.connect(self.time_out)
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.hide_timer_out)
        self.count_hide = 5
        super().hide()

    def time_out(self):
        self.timeout_count += 1
        self.setText(self.loading_text[:5 + self.timeout_count])
        if self.timeout_count >= 3:
            self.timeout_count = -1

    def hide(self):
        self.timer.stop()
        super().hide()
        self.click_able = False

    def show(self):
        self.setText(self.loading_text)
        self.timer.start(500)
        super().show()
        self.click_able = False

    def no_data(self):
        self.timer.stop()
        self.setText('没有数据.{}秒后可新增'.format(self.count_hide))
        self.hide_timer.start(1000)
        self.click_able = False

    def hide_timer_out(self):
        self.count_hide -= 1
        self.setText('没有数据.{}秒后可新增'.format(self.count_hide))
        if self.count_hide <= 0:
            self.hide_timer.stop()
            self.hide()
            self.count_hide = 5

    def retry(self):
        self.timer.stop()
        self.setText('请求失败.请重试!')
        self.click_able = True

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.click_able:
            self.clicked.emit(True)


class TableShow(QTableWidget):
    def __init__(self, *args):
        super(TableShow, self).__init__(*args)
        # style
        self.horizontalHeader().setSectionResizeMode(1)  # 横向随控件大小
        self.verticalHeader().setVisible(False)  # 纵向随控件大小
        self.setFocusPolicy(0)  # 选中后边框虚线-无
        self.setMouseTracking(True)  # 跟踪鼠标-滑过整行颜色改变
        self.setSelectionMode(QAbstractItemView.NoSelection)  # 选中后的前景色-无
        # self.verticalHeader().setSectionResizeMode(1)

    def show_content(self, contents, header_couple, show='file'):
        if show not in ['file', 'content']:
            raise ValueError('table can not show this content.')
        if not isinstance(contents, list):
            raise ValueError('content must be a list.')
        row = len(contents)
        self.setRowCount(row)
        self.setColumnCount(len(header_couple))  # 列数
        labels = []
        set_keys = []
        for key_label in header_couple:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        self.setHorizontalHeaderLabels(labels)
        self.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
        self.horizontalHeader().setSectionResizeMode(self.columnCount()-1, 3)  # 最后1列随文字宽度
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if col == 0:
                    item = QTableWidgetItem(str(row + 1))
                else:
                    label_key = set_keys[col]
                    if label_key == 'to_look':
                        item = QTableWidgetItem('查看')
                        item.title = contents[row]['title']
                        if show == 'file':
                            item.file = contents[row]['file']
                        elif show == 'content':
                            item.content = contents[row]['content']
                        else:
                            pass
                    else:
                        item = QTableWidgetItem(str(contents[row][label_key]))
                item.setTextAlignment(Qt.AlignCenter)
                item.content_id = contents[row]['id']
                self.setItem(row, col, item)
        self.setMinimumHeight(35 + row * 30.5)

    def clear(self):
        super().clear()
        self.setRowCount(0)
        self.setColumnCount(0)

    def leaveEvent(self, *args, **kwargs):
        """鼠标离开控件"""
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                # self.item(row, col).setForeground(QBrush(QColor(0, 0, 0)))  # 改变了其他的item字体色
                self.item(row, col).setBackground(QBrush(QColor(255, 255, 255)))

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        # 获取当前这个item
        current_item = self.itemAt(event.pos())
        if current_item:
            row = current_item.row()
            for item in [self.item(row, col) for col in range(self.columnCount())]:
                # item.setForeground(QBrush(QColor(255, 10, 20)))  # 改变了当前的item字体色
                item.setBackground(QBrush(QColor(220,220,220)))
            for other_row in range(self.rowCount()):
                if other_row == row:
                    continue
                for other_item in [self.item(other_row, col) for col in range(self.columnCount())]:
                    # other_item.setForeground(QBrush(QColor(0, 0, 0)))  # 改变了其他的item字体色
                    other_item.setBackground(QBrush(QColor(255,255,255)))


class MenuScrollContainer(QScrollArea):
    menu_clicked = pyqtSignal(QPushButton)

    def __init__(self, column, *args):
        super(MenuScrollContainer, self).__init__(*args)
        # self size style
        self.setFixedWidth(70 * column + (column + 1) * 10)
        self.column = column
        self.horizontalScrollBar().setVisible(False)
        # widget and layout
        self.menu_container = QWidget()  # main widget
        self.menu_container.setFixedWidth(70 * column + (column + 1) * 10)
        container_layout = QVBoxLayout(spacing=0)  # main layout
        container_layout.setContentsMargins(0, 0, 0, 0)
        # widgets add layout
        self.menu_container.setLayout(container_layout)
        # self.setWidget(self.menu_container)  # main widget add scroll area (must be add after drawing)
        self.setStyleSheet("""
        MenuScrollContainer{
            background-color: rgb(255,255,255);
        }
        QPushButton{
            color: rgb(50,50,50);
            border: none;
            padding:2px 4px;
            margin-left:5px;
            height:18px;
            font-size:13px;
        }
        QPushButton:hover {
            background-color: rgb(224,255,255);
            border: 0.5px solid rgb(170,170,170);
        }
        QLabel{
            font-weight:bold;
            font-size:14px;
        }
        MenuWidget{
            background-color: rgb(255,255,255);
            border-bottom: 1px solid rgb(170,170,170);
        }
        MenuWidget:hover{
            background-color: rgb(210,210,210);
            border-bottom: 1px solid rgb(0,0,0)
        }
        QScrollBar:vertical
        {
            width:8px;
            background:rgba(0,0,0,0%);
            margin:0px,0px,0px,0px;
            /*留出8px给上面和下面的箭头*/
            padding-top:8px;
            padding-bottom:8px;
        }
        QScrollBar::handle:vertical
        {
            width:4px;
            background:rgba(0,0,0,8%);
            /*滚动条两端变成椭圆*/
            border-radius:4px;

        }
        QScrollBar::handle:vertical:hover
        {
            width:8px;
            /*鼠标放到滚动条上的时候，颜色变深*/
            background:rgba(0,0,0,40%);
            border-radius:4px;
            min-height:20;
        }
        QScrollBar::add-line:vertical
        {
            height:9px;width:8px;
            /*设置下箭头*/
            border-image:url(media/scroll/3.png);
            subcontrol-position:bottom;
        }
        QScrollBar::sub-line:vertical 
        {
            height:9px;width:8px;
            /*设置上箭头*/
            border-image:url(media/scroll/1.png);
            subcontrol-position:top;
        }
        QScrollBar::add-line:vertical:hover
        /*当鼠标放到下箭头上的时候*/
        {
            height:9px;width:8px;
            border-image:url(media/scroll/4.png);
            subcontrol-position:bottom;
        }
        QScrollBar::sub-line:vertical:hover
        /*当鼠标放到下箭头上的时候*/
        {
            height:9px;
            width:8px;
            border-image:url(media/scroll/2.png);
            subcontrol-position:top;
        }
        """)
        # initial data
        self.menu_thread = None

    def get_menu(self, url=None):
        if not url:
            return
        if self.menu_thread:
            del self.menu_thread
        self.menu_thread = RequestThread(
            url=url,
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.menu_thread.response_signal.connect(self.menu_thread_back)
        self.menu_thread.finished.connect(self.menu_thread.deleteLater)
        self.menu_thread.start()

    def menu_thread_back(self, content):
        print('widgets.base.py {} 请求到左侧菜单: '.format(str(sys._getframe().f_lineno)), content)
        if content['error']:
            return
        for data_index, menu_data in enumerate(content['data']):
            # a menu widget
            menu_widget = MenuWidget()  # a menu widget in piece.pservice.MenuWidget
            widget_layout = QVBoxLayout(spacing=0)  # menu widget layout
            widget_layout.setContentsMargins(0, 0, 0, 0)  # 设置菜单字是否贴边margin(left, top, right, bottom)
            menu_widget.setLayout(widget_layout)  # add layout
            menu_label = LeaderLabel(menu_data['name'])
            menu_label.clicked.connect(self.menu_label_clicked)
            # a child widget
            menu_label.child_widget = QWidget()  # child of menu widget
            child_layout = QGridLayout(spacing=5)  # child layout
            child_layout.setContentsMargins(0, 0, 5, 10)
            menu_label.child_widget.setLayout(child_layout)
            row_index = 0  # control rows
            column_index = 0  # control columns
            for child in menu_data['subs']:
                # a child widget
                button = MenuButton(child['name'])
                # add property
                button.parent = menu_data['name']
                button.parent_en = menu_data['name_en']
                button.name_en = child['name_en']
                button.mouse_clicked.connect(self.click_menu)
                child_layout.addWidget(button, row_index, column_index)
                column_index += 1
                if column_index >= self.column:
                    row_index += 1
                    column_index = 0
            widget_layout.addWidget(menu_label, alignment=Qt.AlignTop)
            widget_layout.addWidget(menu_label.child_widget)
            self.menu_container.layout().addWidget(menu_widget)
        self.menu_container.layout().addStretch()
        self.setWidget(self.menu_container)  # main widget add scroll area (must be add after drawing)

    def menu_label_clicked(self, menu_label):
        if menu_label.child_widget.isHidden():
            menu_label.child_widget.show()
        else:
            menu_label.child_widget.hide()

    def click_menu(self, button):
        self.menu_clicked.emit(button)


class NormalTable(QTableWidget):
    def __init__(self, *args):
        super(NormalTable, self).__init__(*args)
        # style
        self.horizontalHeader().setSectionResizeMode(1)  # 横向随控件大小
        self.verticalHeader().setVisible(False)  # 纵向随控件大小
        self.verticalHeader().setSectionResizeMode(1)

    def show_content(self, contents, header_couple):
        if not isinstance(contents, list):
            raise ValueError('content must be a list.')
        row = len(contents)
        self.setRowCount(row)
        self.setColumnCount(len(header_couple))  # 列数
        labels = []
        set_keys = []
        for key_label in header_couple:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        self.setHorizontalHeaderLabels(labels)
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if col == 0:
                    item = QTableWidgetItem(str(row + 1))
                else:
                    label_key = set_keys[col]
                    item = QTableWidgetItem(str(contents[row][label_key]))
                item.setTextAlignment(Qt.AlignCenter)
                item.content_id = contents[row]['id']
                self.setItem(row, col, item)
        # 设定固定高度
        self.setMinimumHeight(35 + row * 30)

    def clear(self):
        super().clear()
        self.setRowCount(0)
        self.setColumnCount(0)


"""本模块内部自引用控件"""

# /* 菜单栏内部控件 */

class LeaderLabel(QLabel):
    # 菜单的展开与关闭label
    clicked = pyqtSignal(QLabel)
    def __init__(self, *args):
        super(LeaderLabel, self).__init__(*args)
        self.setStyleSheet('padding:8px 0; border:none')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self)


class MenuButton(QPushButton):
    # 菜单
    mouse_clicked = pyqtSignal(QPushButton)

    def __init__(self, *args, **kwargs):
        super(MenuButton, self).__init__(*args)
        self.clicked.connect(self.btn_clicked)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def btn_clicked(self):
        self.mouse_clicked.emit(self)


class MenuWidget(QWidget):
    # 每个菜单块容器
    def __init__(self, *args, **kwargs):
        super(MenuWidget, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)

# /* 菜单栏内部控件 */




