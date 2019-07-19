# _*_ coding:utf-8 _*_
"""
config file
date: 2019-07-19
author: zizle
"""
import os
from PyQt5.QtCore import QSettings
VERSION = "2019.1"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_ADDR = "http://127.0.0.1:8008/"
CLIENT_HEADERS = {"User-Agent": "DAssistant-Client/" + VERSION}
# 首页中间Frame最小高度
HOME_PAGE_MIDDLE_WINDOW_MIN_HEIGHT = 200
# PDF展示框的尺寸
PDF_READER_DIALOG_WIDTH = 1000
PDF_READER_DIALOG_HEIGHT = 600
# app设置
app_dawn = QSettings('dawn/initial.ini', QSettings.IniFormat)
HOMEPAGE_REPORT_PAGE_COUNT = 5  # 常规报告一页显示条数

HOMEPAGE_NOTICE_PAGE_COUNT = 6  # 交易通知一页显示条数
