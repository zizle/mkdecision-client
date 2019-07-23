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
VERSION = '2019.1'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_HEADERS = {"User-Agent": "DAssistant-Client/" + VERSION}
# app设置
app_dawn = QSettings('dawn/initial.ini', QSettings.IniFormat)
# 首页中间Frame最小高度
HOME_PAGE_MIDDLE_WINDOW_MIN_HEIGHT = 200
# PDF展示框的尺寸
PDF_READER_DIALOG_WIDTH = 1000
PDF_READER_DIALOG_HEIGHT = 600
HOMEPAGE_REPORT_PAGE_COUNT = 5  # 常规报告一页显示条数

HOMEPAGE_NOTICE_PAGE_COUNT = 6  # 交易通知一页显示条数