# _*_ coding:utf-8 _*_
"""
all dialog of data-maintenance module, in the home page
Update: 2019-07-25
Author: zizle
"""
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon


class CreateNewBulletin(QDialog):
    def __init__(self):
        super(CreateNewBulletin, self).__init__()
        self.setWindowTitle('设置')
        self.setWindowIcon(QIcon("media/bulletin.png"))
        layout = QVBoxLayout()
        # 添加一个tab
        tabs = QTabWidget()
        self.tab_0 = QWidget()
        self.tab_1 = QWidget()
        tabs.addTab(self.tab_0, "添加公告")
        tabs.addTab(self.tab_1, "显示天数")
        # 初始化tab_0
        self.init_tab_0()
        self.init_tab_1()
        layout.addWidget(tabs)
        self.setLayout(layout)

    def init_tab_0(self):
        grid_layout_0 = QGridLayout()
        tab_0_label_0 = QLabel("名称：")
        tab_0_label_1 = QLabel("展示：")
        self.tab_0_label_2 = QLabel('文件：')
        self.tab_0_label_3 = QLabel('内容：')
        tab_0_edit_0 = QLineEdit()  # 名称
        self.tab_0_edit_1 = QLineEdit()  # 文件路径
        tab_0_edit_0.setPlaceholderText("输入条目展示的名称(默认文件名)")
        tab_0_combo = QComboBox()
        tab_0_combo.addItems(['文件展示', '显示文字'])
        tab_0_combo.currentTextChanged.connect(self.tab_0_show_type_changed)
        self.tab_0_btn_0  = QPushButton('浏览')
        tab_0_btn_1 = QPushButton('提交')
        self.tab_0_edit_2 = QTextEdit()  # 内容
        # initial hide the content edit
        self.tab_0_label_3.hide()
        self.tab_0_edit_2.hide()
        grid_layout_0.addWidget(tab_0_label_0, 0, 0)
        grid_layout_0.addWidget(tab_0_edit_0, 0, 1, 1, 2)
        grid_layout_0.addWidget(tab_0_label_1, 1, 0)
        grid_layout_0.addWidget(tab_0_combo, 1, 1, 1, 2)
        grid_layout_0.addWidget(self.tab_0_label_2, 2, 0)
        grid_layout_0.addWidget(self.tab_0_edit_1, 2, 1)
        grid_layout_0.addWidget(self.tab_0_btn_0, 2, 2)
        grid_layout_0.addWidget(self.tab_0_label_3, 3, 0)
        grid_layout_0.addWidget(self.tab_0_edit_2, 3, 1, 1, 2)
        grid_layout_0.addWidget(tab_0_btn_1, 4, 1, 1,2)
        self.tab_0.setLayout(grid_layout_0)

    def init_tab_1(self):
        grid_layout_1 = QGridLayout()
        tip_label = QLabel("* 设置公告栏展示距今日几天前的内容")
        tip_label.setStyleSheet("color: rgb(84,182,230);font-size:12px;")
        tab_1_label_0 = QLabel("设置天数：")
        self.tab_1_edit_0 = QLineEdit()
        self.tab_1_edit_0.setFixedHeight(28)
        self.tab_1_edit_0.setPlaceholderText("请输入正整数.")
        tab_1_btn_0 = QPushButton("提交")
        grid_layout_1.addWidget(tip_label, 0, 0, 1, 2)
        grid_layout_1.addWidget(tab_1_label_0, 1, 0)
        grid_layout_1.addWidget(self.tab_1_edit_0, 1, 1, 1, 2)
        grid_layout_1.addWidget(tab_1_btn_0, 2, 1, 1, 2)
        self.tab_1.setLayout(grid_layout_1)

    def tab_0_show_type_changed(self, text):
        if text == '文件展示':
            self.resize(318, 214)
            self.tab_0_label_2.show()
            self.tab_0_edit_1.show()
            self.tab_0_btn_0.show()
            self.tab_0_label_3.hide()
            self.tab_0_edit_2.hide()
        elif text == '显示文字':
            self.resize(318, 300)
            self.tab_0_label_2.hide()
            self.tab_0_edit_1.hide()
            self.tab_0_btn_0.hide()
            self.tab_0_label_3.show()
            self.tab_0_edit_2.show()