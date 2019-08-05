# _*_ coding:utf-8 _*_
"""
management client config
Create: 2019-07-22
Update: 2019-07-22
Author: zizle
"""
import os
from PyQt5.QtCore import QSettings
SERVER_ADDR = "http://127.0.0.1:8008/"
VERSION = '0.19.7'
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_HEADERS = {"User-Agent": "DAssistant-Client/" + VERSION}
# app设置
app_dawn = QSettings('dawn/initial.ini', QSettings.IniFormat)
# page size
HOMEPAGE_REPORT_PAGESIZE = 20
HOMEPAGE_NOTICE_PAGESIZE = 20
