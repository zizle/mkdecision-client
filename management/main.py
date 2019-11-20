# _*_ coding:utf-8 _*_
"""
client for management
Create: 2019-07-22
Author: zizle
"""
import sys
from PyQt5.QtWidgets import QApplication

from piece import StartScreen
from windows.base import BaseWindow, Base
from utils.client import check_client_existed


app = QApplication(sys.argv)
splash = StartScreen()  # welcome
splash.show()
app.processEvents()  # non-blocking
base_window = BaseWindow()  # main page
# base_window = Base()  # main page
check_client_existed()  # 启动检测当前客户端是否存在
base_window.get_module_menus()  # 获取模块菜单信息
# base_window.permit_bar.check_keep_online()
base_window.show()
splash.finish(base_window)  # close welcome when main page loaded
sys.exit(app.exec_())
