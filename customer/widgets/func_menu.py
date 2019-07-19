# _*_ coding:utf-8 _*_
# company: RuiDa Futures
# author: zizle
from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt


class FuncMenu(QWidget):
    func_signal = pyqtSignal(str)

    def __init__(self):
        super(FuncMenu, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        style = """
        FuncMenu {
            background-color: rgb(160,150,200)
        }
        """
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持设置背景色
        self.menus = []
        self.layout = QHBoxLayout(spacing=0, margin=0)
        self.setLayout(self.layout)
        self.setStyleSheet(style)

    def addMenus(self, menus):
        """添加按钮"""
        for menu in menus:
            menu_button = MenuButton(menu)
            self.menus.append(menu_button)
            menu_button.menu_click_signal.connect(self.menu_clicked)
            self.layout.addWidget(menu_button)
            if menu == "全部":
                menu_button.style_changed()  # 默认选择

    def addSpacer(self):
        """添加伸缩条"""
        # self.layout.addSpacerItem(QSpacerItem(
        #     40, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.layout.addStretch()

    def menu_clicked(self, click_menu):
        """按钮点击传出信号"""
        for menu in self.menus:
            if menu == click_menu:
                menu.style_changed()
            else:
                menu.init_style()
        self.func_signal.emit(click_menu.text())


class MenuButton(QPushButton):
    menu_click_signal = pyqtSignal(QPushButton)

    def __init__(self, *args):
        super(MenuButton, self).__init__(*args)
        self.clicked.connect(self.menu_clicked)
        self.__init_ui()

    def __init_ui(self):
        self.setFixedHeight(26)
        self.init_style()

    def init_style(self):
        self.setStyleSheet("""
        QPushButton {
            border:none;
            border-bottom: 1px solid rgb(160,150,200);
            padding: 2px 12px;
            height: 22px;
            font-size:14px;
        }
        QPushButton:hover{
            background-color: rgb(200, 200, 200);
            border-bottom: 1px solid rgb(54,157,180);
        }    
        """)

    def menu_clicked(self):
        """按钮点击传出按钮文字信号"""
        self.menu_click_signal.emit(self)

    def style_changed(self):
        self.setStyleSheet("""
        QPushButton {
            border:none;
            padding: 2px 12px;
            height: 22px;
            font-size:14px;
            font-weight: bold;
            border-bottom: 1px solid red;
            font-weight: bold;
        }
        QPushButton:hover{
            background-color: rgb(200, 200, 200)
        }    
        """)

