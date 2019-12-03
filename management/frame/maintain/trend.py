# _*_ coding:utf-8 _*_
# __Author__： zizle
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QPushButton, \
    QTabWidget
from PyQt5.QtCore import Qt, pyqtSignal
from popup.maintain.trend import NewTrendTablePopup


# 数据分析管理页
class TrendMaintain(QWidget):
    network_result = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(TrendMaintain, self).__init__(*args, **kwargs)
        self.create_button = QPushButton('新数据表', clicked=self.create_data_table)
        layout = QHBoxLayout(margin=0)
        # 左侧功能列表
        self.option_list = QListWidget(parent=self)
        # 右侧显示tab
        self.frame_tab = QTabWidget(parent=self)
        layout.addWidget(self.option_list, alignment=Qt.AlignLeft)
        layout.addWidget(self.frame_tab)
        self.setLayout(layout)

    # 新增数据表
    def create_data_table(self):
        popup = NewTrendTablePopup(parent=self)
        popup.getVarietyTableGroups()  # 获取左侧目录树的数据
        popup.deleteLater()
        if not popup.exec_():
            del popup
