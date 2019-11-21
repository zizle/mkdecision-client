# _*_ coding:utf-8 _*_
"""
client for management
Create: 2019-07-22
Author: zizle
"""
import sys
from PyQt5.QtWidgets import QApplication

from piece.welcome import WelcomePage
from windows.base import BaseWindow

app = QApplication(sys.argv)
splash = WelcomePage()  # welcome
splash.show()
app.processEvents()  # non-blocking
splash.make_client_existed()  # 启动使当前客户端存在
base_window = BaseWindow()  # main window
base_window.get_module_menus()  # 获取模块菜单信息
base_window.running_auto_login()  # 自动登录
base_window.show()
splash.finish(base_window)  # close welcome when main page loaded  # 执行到这句话才会消失欢迎页
sys.exit(app.exec_())
