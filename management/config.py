# _*_ coding:utf-8 _*_
# Author: zizle  QQ:462894999

from PyQt5.QtCore import QSettings
SERVER_ADDR = "http://127.0.0.1:8000/"
# SERVER_ADDR = "http://192.168.2.181:8000/"
VERSION = '0.19.7'
ADMINISTRATOR = True
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# app设置
app_dawn = QSettings('dawn/initial.ini', QSettings.IniFormat)
# 静态文件根目录与服务器对应
MEDIA_ROOT = 'E:/mkDecision/'
