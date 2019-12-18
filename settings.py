# _*_ coding:utf-8 _*_
# Author: zizle  QQ:462894999

from PyQt5.QtCore import QSettings
# SERVER_ADDR = "http://127.0.0.1:8000/"
SERVER_ADDR = "http://192.168.191.2:8000/"
ADMINISTRATOR = True
# app设置
app_dawn = QSettings('dawn/initial.ini', QSettings.IniFormat)
# 数据管理功能块一行数量
COLLECTOR_BLOCK_ROWCOUNT = 4
# 与后端对应的静态文件路径
STATIC_PREFIX = SERVER_ADDR + 'mkDecision/'
# 首页广告变化速率，单位毫秒
IMAGE_SLIDER_RATE = 3000
