# _*_ coding:utf-8 _*_
# Author: zizle  QQ:462894999

import sys
from PyQt5.QtWidgets import QApplication
from frame.base import WelcomePage, BaseWindow

app = QApplication(sys.argv)
splash = WelcomePage()  # welcome
splash.show()
app.processEvents()  # non-blocking
splash.make_client_existed()  # 启动使当前客户端存在（发送请求,不存在就注册）
splash.getCurrentAdvertisements()
base_window = BaseWindow()  # main window
base_window.getSystemStartModules()  # 获取系统模块
base_window.show()
base_window.running_auto_login()  # 自动登录
base_window.module_clicked(module_id=1, module_text=u'首页')  # 启动后显示首页
splash.finish(base_window)  # close welcome when main page loaded  # 执行到这句话才会消失欢迎页
sys.exit(app.exec_())
