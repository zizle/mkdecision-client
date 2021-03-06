# _*_ coding:utf-8 _*_
# Author: zizle  QQ:462894999
import os
from PyQt5.QtCore import QSettings
#SERVER_ADDR = "http://127.0.0.1:5000/"
# SERVER_ADDR = "http://210.13.218.130:9002/"
SERVER_ADDR = "http://192.168.0.113:5000/"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ADMINISTRATOR = True
# app设置
app_dawn = QSettings('dawn/initial.ini', QSettings.IniFormat)
# 数据管理功能块一行数量
COLLECTOR_BLOCK_ROWCOUNT = 4
# 与后端对应的静态文件路径
STATIC_PREFIX = SERVER_ADDR + 'ads/'
# 首页广告变化速率，单位毫秒
IMAGE_SLIDER_RATE = 3000
# 标题栏高度
TITLE_BAR_HEIGHT = 32
# 菜单栏高度
NAVIGATION_BAR_HEIGHT = 24
