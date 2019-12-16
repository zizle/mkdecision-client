# _*_ coding:utf-8 _*_
# Author: zizle  QQ:462894999

from PyQt5.QtCore import QSettings
# SERVER_ADDR = "http://127.0.0.1:8000/"
SERVER_ADDR = "http://192.168.2.181:8000/"
ADMINISTRATOR = True
# app设置
app_dawn = QSettings('dawn/initial.ini', QSettings.IniFormat)
# 数据管理功能块一行数量
COLLECTOR_BLOCK_ROWCOUNT = 4
