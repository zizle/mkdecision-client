# _*_ coding:utf-8 _*_
"""
client for management
Create: 2019-07-22
Update: 2019-07-22
Author: zizle
"""
import sys
from PyQt5.QtWidgets import QApplication

from windows.master import MasterWindow
from widgets import StartScreen
from utils import auto_login

# app = QApplication(sys.argv)
# splash = StartScreen()  # 软件启动页
# splash.show()
# app.processEvents()  # 主进程非阻塞
# w = MasterWindow()  # 主页面
# w.show()
# splash.finish(w)  # 加载完成关闭启动欢迎
# auto_login(mount_window=w)  # 启动登录
# sys.exit(app.exec_())

from windows.base import Base
app = QApplication(sys.argv)
splash = StartScreen()  # 软件启动页
splash.show()
app.processEvents()  # 主进程非阻塞
base_window = Base()  # 主页面
base_window.show()
splash.finish(base_window)  # 加载完成关闭启动欢迎
# auto_login(mount_window=w)  # 启动登录
sys.exit(app.exec_())