# _*_ coding:utf-8 _*_
# __Author__： zizle
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget


# 显示用户的盒子
class UserTable(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(UserTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()

    def addUsers(self, json_list):
        rows = len(json_list)
        for user in json_list:
            print(user)
        self.setHorizontalHeaderLabels(['编号', ''])


