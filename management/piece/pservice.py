# _*_ coding:utf-8 _*_
"""
all pieces in produce service
Create: 2019-08-01
Author: zizle
"""
from PyQt5.QtWidgets import QWidget, QFrame, QVBoxLayout, QGridLayout,QLabel, QScrollArea, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

from widgets.pservice import LeaderLabel, MenuWidget, MenuButton

class MenuListWidget(QScrollArea):
    menu_clicked = pyqtSignal(QPushButton)

    def __init__(self, column,  *args):
        super(MenuListWidget, self).__init__(*args)
        self.setFixedWidth(280)
        self.column = column
        self.horizontalScrollBar().setVisible(False)
        # widget and layout
        self.menu_container = QWidget()  # main widget
        container_layout = QVBoxLayout()  # main layout
        # widgets add layout
        self.menu_container.setLayout(container_layout)
        self.draw_menu()
        self.setWidget(self.menu_container)  # main widget add scroll area (must be add after drawing)

    def draw_menu(self):
        menu_list = [
            {
                'name': '主菜单1',
                'subs': [
                    {'name': '菜单1'},
                    {'name': '菜单2'},
                    {'name': '菜单3'},
                    {'name': '菜单4'},
                    {'name': '菜单5'},
                ]
            }, {
                'name': '主菜单2',
                'subs': [
                    {'name': '菜单1'},
                    {'name': '菜单2'},
                    {'name': '菜单3'},
                ]
            }, {
                'name': '主菜单3',
                'subs': [
                    {'name': '菜单1'},
                    {'name': '菜单2'},
                    {'name': '菜单3'},
                    {'name': '菜单4'},
                    {'name': '菜单5'},
                    {'name': '菜单6'},
                    {'name': '菜单7'},
                ]
            }, {
                'name': '主菜单4',
                'subs': [
                    {'name': '菜单1'},
                    {'name': '菜单2'},
                    {'name': '菜单3'},
                    {'name': '菜单4'},
                    {'name': '菜单5'},
                    {'name': '菜单6'},
                    {'name': '菜单7'},
                    {'name': '菜单8'},
                    {'name': '菜单9'},
                ]
            }
        ]
        for data_index, menu_data in enumerate(menu_list):
            # a menu widget
            menu_widget = MenuWidget()  # a menu widget in piece.pservice.MenuWidget
            widget_layout = QVBoxLayout(spacing=0) # menu widget layout
            menu_widget.setLayout(widget_layout)  # add layout
            menu_label = LeaderLabel(menu_data['name'])
            menu_label.clicked.connect(self.menu_label_clicked)
            # a child widget
            menu_label.child_widget = QWidget()  # child of menu widget
            child_layout = QGridLayout()  # child layout
            child_layout.setContentsMargins(0,0,0,0)
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
            if data_index < len(menu_list) -1:
                # splitter line
                splitter_line = QFrame()
                splitter_line.setEnabled(True)
                splitter_line.setFrameShape(QFrame.HLine)
                splitter_line.setFrameShadow(QFrame.Sunken)
                self.menu_container.layout().addWidget(splitter_line)
        self.menu_container.layout().addStretch()

    def menu_label_clicked(self, menu_label):
        if menu_label.child_widget.isHidden():
            menu_label.child_widget.show()
        else:
            menu_label.child_widget.hide()

    def click_menu(self, button):
        self.menu_clicked.emit(button)

