# _*_ coding:utf-8 _*_
"""

Create: 2019-08-23
Author: zizle
"""
from PyQt5.QtCore import QSettings
VERSION = '0.1.0'
# SERVER = "http://127.0.0.1:8000/"
SERVER = "http://210.13.218.130:9000/"
CLIENT = 'management'
# CLIENT = 'public'
APP_DAWN = QSettings('conf/initial.ini', QSettings.IniFormat)
