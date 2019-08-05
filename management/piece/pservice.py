# _*_ coding:utf-8 _*_
"""
all pieces in produce service
Create: 2019-08-01
Author: zizle
"""
import sys
import json
from PyQt5.QtWidgets import QWidget, QFrame, QVBoxLayout, QGridLayout, QScrollArea, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QLine

import config
from widgets.pservice import LeaderLabel, MenuWidget, MenuButton
from thread.request import RequestThread

class MenuListWidget(QScrollArea):
    menu_clicked = pyqtSignal(QPushButton)

    def __init__(self, column,  *args):
        super(MenuListWidget, self).__init__(*args)
        # button to show request message and fail retry
        self.message_btn = QPushButton('刷新中...', self)
        self.message_btn.resize(100, 20)
        self.message_btn.move(100, 50)
        self.message_btn.setStyleSheet('text-align:center;border:none;background-color:rgb(210,210,210)')
        self.message_btn.clicked.connect(self.get_menu)
        self.message_btn.hide()
        # self size style
        self.setFixedWidth(70 * column + (column+1)*10)
        self.column = column
        self.horizontalScrollBar().setVisible(False)
        # self.verticalScrollBar().setVisible(True)
        # widget and layout
        self.menu_container = QWidget()  # main widget
        self.menu_container.setFixedWidth(70 * column + (column + 1) * 10)
        container_layout = QVBoxLayout(spacing=0)  # main layout
        container_layout.setContentsMargins(0,0,0,0)
        # widgets add layout
        self.menu_container.setLayout(container_layout)
        self.get_menu()
        # self.setWidget(self.menu_container)  # main widget add scroll area (must be add after drawing)
        self.setStyleSheet("""
        QPushButton{
            color: rgb(50,50,50);
            border: none;
            padding:0 4px;
            margin-left:5px;
            height:18px;
        }
        QPushButton:hover {
            background-color: rgb(224,255,255);
            border: 0.5px solid rgb(170,170,170);
        }
        QLabel{
            font-weight:bold;
            font-size:13px;
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

    def get_menu(self):
        self.message_btn.setText('刷新中...')
        self.message_btn.show()
        self.message_btn.setEnabled(False)
        headers = {"User-Agent": "DAssistant-Client/" + config.VERSION}
        self.menu_thread = RequestThread(
            url=config.SERVER_ADDR + "pservice/module/",
            method='get',
            headers=headers,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.menu_thread.response_signal.connect(self.menu_thread_back)
        self.menu_thread.finished.connect(self.menu_thread.deleteLater)
        self.menu_thread.start()

    def menu_thread_back(self, content):
        print('piece.home.py {} 产品服务菜单: '.format(str(sys._getframe().f_lineno)), content)
        if content['error']:
            self.message_btn.setText('失败,请重试!')
            self.message_btn.setEnabled(True)
        else:
            if not content['data']:
                self.message_btn.setText('完成,无数据.')
                return  # function finished
            else:
                self.message_btn.setText('刷新完成!')
                self.message_btn.hide()
        # fill table

        # menu_list = [
        #     {
        #         'name': '主菜单1',
        #         'subs': [
        #             {'name': '菜单1'},
        #             {'name': '菜单2'},
        #             {'name': '菜单3'},
        #             {'name': '菜单4'},
        #             {'name': '菜单5'},
        #         ]
        #     }, {
        #         'name': '主菜单2',
        #         'subs': [
        #             {'name': '菜单1'},
        #             {'name': '菜单2'},
        #             {'name': '菜单3'},
        #         ]
        #     }, {
        #         'name': '主菜单3',
        #         'subs': [
        #             {'name': '菜单1'},
        #             {'name': '菜单2'},
        #             {'name': '菜单3'},
        #             {'name': '菜单4'},
        #             {'name': '菜单5'},
        #             {'name': '菜单6'},
        #             {'name': '菜单7'},
        #         ]
        #     }, {
        #         'name': '主菜单4',
        #         'subs': [
        #             {'name': '菜单1'},
        #             {'name': '菜单2'},
        #             {'name': '菜单3'},
        #             {'name': '菜单4'},
        #             {'name': '菜单5'},
        #             {'name': '菜单6'},
        #             {'name': '菜单7'},
        #             {'name': '菜单8'},
        #             {'name': '菜单9'},
        #         ]
        #     }
        # ]
        for data_index, menu_data in enumerate(content['data']):
            # a menu widget
            menu_widget = MenuWidget()  # a menu widget in piece.pservice.MenuWidget
            widget_layout = QVBoxLayout(spacing=0) # menu widget layout
            widget_layout.setContentsMargins(0,0,0,0)  # 设置菜单字是否贴边margin(left, top, right, bottom)
            menu_widget.setLayout(widget_layout)  # add layout
            menu_label = LeaderLabel(menu_data['name'])
            menu_label.clicked.connect(self.menu_label_clicked)
            # a child widget
            menu_label.child_widget = QWidget()  # child of menu widget
            child_layout = QGridLayout(spacing=5)  # child layout
            child_layout.setContentsMargins(0,0,5,10)
            menu_label.child_widget.setLayout(child_layout)
            row_index = 0  # control rows
            column_index = 0  # control columns



            for child in menu_data['subs']:
                # a child widget
                button = MenuButton(child['name'])
                # add property
                button.parent_name = menu_data['name']
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

