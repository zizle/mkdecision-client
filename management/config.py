# _*_ coding:utf-8 _*_
"""
management client config
Create: 2019-07-22
Update: 2019-07-22
Author: zizle
"""
from PyQt5.QtCore import QSettings
VERSION = '2019.1'
CLIENT_HEADERS = {"User-Agent": "DAssistant-Client/" + VERSION}
# app设置
app_dawn = QSettings('dawn/initial.ini', QSettings.IniFormat)