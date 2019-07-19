import sys
import asyncio
from PyQt5.QtWidgets import QApplication

from windows.master import MasterWindow
from widgets import StartScreen
from utils import auto_login

app = QApplication(sys.argv)
splash = StartScreen()  # 软件启动页
splash.show()
app.processEvents()  # 主进程非阻塞
w = MasterWindow()  # 主页面
w.show()
splash.finish(w)  # 加载完成关闭启动欢迎
auto_login(mount_window=w)  # 启动登录
sys.exit(app.exec_())
