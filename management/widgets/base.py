# _*_ coding:utf-8 _*_
"""
base widget in project
Create: 2019-08-07
Author: zizle
"""
import sys
import json
from PyQt5.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QWidget, QPushButton, QScrollArea, QVBoxLayout, QGridLayout
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QCursor

import config
from thread.request import RequestThread

class Loading(QLabel):
    clicked = pyqtSignal(bool)

    def __init__(self, *args):
        super(Loading, self).__init__()
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
        self.verticalHeader().setVisible(False)

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
        self.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
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

    def clear(self):
        super().clear()
        self.setRowCount(0)
        self.setColumnCount(0)


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


class MenuScrollContainer(QScrollArea):
    menu_clicked = pyqtSignal(QPushButton)

    def __init__(self, column, *args):
        super(MenuScrollContainer, self).__init__(*args)
        # self size style
        self.setFixedWidth(70 * column + (column + 1) * 10)
        self.column = column
        self.horizontalScrollBar().setVisible(False)
        # self.verticalScrollBar().setVisible(True)
        # widget and layout
        self.menu_container = QWidget()  # main widget
        self.menu_container.setFixedWidth(70 * column + (column + 1) * 10)
        container_layout = QVBoxLayout(spacing=0)  # main layout
        container_layout.setContentsMargins(0, 0, 0, 0)
        # widgets add layout
        self.menu_container.setLayout(container_layout)
        # self.setWidget(self.menu_container)  # main widget add scroll area (must be add after drawing)
        self.setStyleSheet("""
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

    def get_menu(self, url=None):
        if not url:
            return
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




