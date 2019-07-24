# _*_ coding:utf-8 _*_
"""
dialog in data-maintenance module
Update: 2019-07-24
Author: zizle
"""
import re
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator, QIcon

import config

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


class CreateNewClient(QDialog):
    new_data_signal = pyqtSignal(dict)
    def __init__(self, *args):
        super(CreateNewClient, self).__init__(*args)
        self.setMinimumWidth(360)
        self.setWindowTitle('新建')
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignRight)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('为这个客户端起一个名字')
        self.machine = QLineEdit()
        self.machine.setPlaceholderText('输入机器码(小写字母与数字组合)')
        self.bulletin_days = QLineEdit()
        self.bulletin_days.setPlaceholderText("支持输入整数(默认为1)")
        self.bulletin_days.setValidator(QIntValidator())
        self.admin_check = QCheckBox()
        self.active_check = QCheckBox()
        self.active_check.setChecked(True)
        submit_btn = QPushButton("提交")
        submit_btn.clicked.connect(self.new_client_signal)
        layout.addRow('*客户端名称：', self.name_edit)
        layout.addRow('*机器码：', self.machine)
        layout.addRow('公告展示(天)：', self.bulletin_days)
        layout.addRow('管理端：', self.admin_check)
        layout.addRow('有效：', self.active_check)
        layout.addRow('', submit_btn)
        self.setLayout(layout)

    def new_client_signal(self):
        # 收集客户端信息
        bulletin_day = self.bulletin_days.text().strip(' ')
        data = dict()
        data['name'] = self.name_edit.text().strip(' ')
        data['machine_code'] = self.machine.text().strip(' ')
        data['bulletin_days'] = bulletin_day if bulletin_day else 1
        data['is_admin'] = self.admin_check.isChecked()
        data['is_active'] = self.active_check.isChecked()
        data['operation_code'] = config.app_dawn.value('machine')
        if not config.app_dawn.value('cookies'):
            QMessageBox.information(self, '提示', "请先登录再进行操作~", QMessageBox.Yes)
            return
        if not data['name']:
            QMessageBox.information(self, '提示', "请为这个客户端取个名字~", QMessageBox.Yes)
            return
        if not re.match(r'^[0-9a-z]+$', data['machine_code']):
            QMessageBox.information(self, '提示', "机器码格式有误~", QMessageBox.Yes)
            return
        # emit signal
        self.new_data_signal.emit(data)

