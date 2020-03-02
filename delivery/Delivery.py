# _*_ coding:utf-8 _*_
"""
交割软件
Create: 2019-08-23
Author: zizle
"""

import sys
from PyQt5.QtWidgets import QApplication

from piece import StartScreen
from windows.base import Base


app = QApplication(sys.argv)
splash = StartScreen()  # welcome
splash.show()
app.processEvents()  # non-blocking
base_window = Base()  # main page
base_window.show()
splash.finish(base_window)  # close welcome when main page loaded
sys.exit(app.exec_())
