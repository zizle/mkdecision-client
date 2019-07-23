# _*_ coding:utf-8 _*_
"""
windows in maintenance
Create: 2019-07-23
Update: 2019-07-23
Author: zizle
"""
import re
import json
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QRegExp
from PyQt5.QtGui import QCursor, QIntValidator, QRegExpValidator

import config
from threads import RequestThread
from utils import get_desktop_path

"""
中心窗口
"""

class HomePage(QWidget):
    """首页设置"""
    def __init__(self, *args, **kwargs):
        super(HomePage, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        set_bulletin = SetBulletinWidget()
        layout.addWidget(set_bulletin, 0, 0)
        layout.addWidget(QLabel("1行2列"), 0, 1)
        layout.addWidget(QLabel("2行1列"), 1, 0)
        layout.addWidget(QLabel("2行2列"), 1, 1)
        self.setLayout(layout)

class SystemPage(QWidget):
    """系统信息"""
    def __init__(self, *args, **kwargs):
        super(SystemPage, self).__init__(*args, **kwargs)
        self.client_info = ClientInfo()
        self.client_info.new_client_successful.connect(self.get_all_clients)
        layout = QGridLayout()
        layout.addWidget(self.client_info, 0, 0)
        self.setLayout(layout)
        # 请求所有客户端信息
        self.get_all_clients(tag=True)

    def fill_info_table(self, content):
        # 填充信息窗口
        if content['error']:
            return
        keys = [('serial_num', '序号'), ('update_time', '最近更新'), ("name", "名称"), ("machine_code", "机器码"),('bulletin_days', '公告(天)'), ('is_admin', "管理端"), ('is_active', "启用")]
        self.client_info.tab_0_show_content(content['data'], keys=keys)
        print(content)

    def get_all_clients(self, tag):
        if tag:
            self.clients_thread = RequestThread(
                url=config.SERVER_ADDR + 'user/clients/',
                method='get',
                headers=config.CLIENT_HEADERS,
                data=json.dumps({"machine_code": config.app_dawn.value('machine')}),
                cookies=config.app_dawn.value('cookies'),
            )
            self.clients_thread.finished.connect(self.clients_thread.deleteLater)
            self.clients_thread.response_signal.connect(self.fill_info_table)
            self.clients_thread.start()


"""
页面内控件
"""
class ClientTableCheckBox(QWidget):
    """ checkbox in client info table """
    check_change_signal = pyqtSignal(dict)

    def __init__(self, row, col, option_label, *args):
        super(ClientTableCheckBox, self).__init__(*args)
        v_layout = QVBoxLayout()
        layout = QHBoxLayout()
        self.check_box = QCheckBox()
        self.check_box.setMinimumHeight(15)
        self.rowIndex = row
        self.colIndex = col
        self.option_label = option_label
        layout.addWidget(self.check_box, alignment=Qt.AlignCenter)
        self.check_box.stateChanged.connect(self.check_state_changed)
        v_layout.addLayout(layout)
        self.setLayout(v_layout)

    def check_state_changed(self):
        self.check_change_signal.emit({'row': self.rowIndex, 'col': self.colIndex, 'flag': self.check_box.isChecked(), 'option_label': self.option_label})

    def setChecked(self, tag):
        self.check_box.setChecked(tag)

class ClientInfo(QWidget):
    # 客户端信息
    new_client_successful = pyqtSignal(bool)
    def __init__(self):
        super(ClientInfo, self).__init__()
        layout = QVBoxLayout(margin=0)
        # 添加一个tab
        tabs = QTabWidget()
        self.tab_0 = QWidget()
        self.tab_1 = QWidget()
        tabs.addTab(self.tab_0, "客户端")
        tabs.addTab(self.tab_1, "新增")
        # 初始化tab_0
        self.init_tab_0()
        self.init_tab_1()
        layout.addWidget(tabs)
        self.setLayout(layout)


    def init_tab_0(self):
        """ show all client information """
        layout = QVBoxLayout()
        self.tab_0_table = QTableWidget()
        layout.addLayout(layout)
        layout.addWidget(self.tab_0_table)
        self.tab_0.setLayout(layout)

    def init_tab_1(self):
        """ add a new client """
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignRight)
        self.tab_1_name_edit = QLineEdit()
        self.tab_1_name_edit.setPlaceholderText('为这个客户端起一个名字')
        self.tab_1_machine = QLineEdit()
        self.tab_1_machine.setPlaceholderText('输入机器码(小写字母与数字组合)')
        self.tab_1_bulletin_days = QLineEdit()
        self.tab_1_bulletin_days.setPlaceholderText("支持输入整数(默认为1)")
        self.tab_1_bulletin_days.setValidator(QIntValidator())
        self.tab_1_admin_check = QCheckBox()
        self.tab_1_active_check = QCheckBox()
        self.tab_1_active_check.setChecked(True)
        tab_1_submit = QPushButton("提交")
        tab_1_submit.clicked.connect(self.tab_1_new_client)
        layout.addRow('*客户端名称：', self.tab_1_name_edit)
        layout.addRow('*机器码：', self.tab_1_machine)
        layout.addRow('公告展示(天)：', self.tab_1_bulletin_days)
        layout.addRow('管理端：', self.tab_1_admin_check)
        layout.addRow('有效：', self.tab_1_active_check)
        layout.addRow('', tab_1_submit)
        self.tab_1.setLayout(layout)

    def tab_0_show_content(self, data, keys):
        """add data to table """
        row = len(data)
        self.tab_0_table.setRowCount(row)
        self.tab_0_table.setColumnCount(len(keys))  # 列数
        labels = []
        set_keys = []
        for key_label in keys:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        self.tab_0_table.setHorizontalHeaderLabels(labels)
        self.tab_0_setSectionResizeMode()  # 自适应大小
        for r in range(row):
            for c in range(self.tab_0_table.columnCount()):
                if c == 0:
                    item = QTableWidgetItem(str(r + 1))  # 序号
                else:
                    label_key = set_keys[c]
                    if label_key == 'is_admin' or label_key == 'is_active':  # 是否启用选择框展示
                        checkbox = ClientTableCheckBox(row=r, col=c, option_label=label_key)
                        checkbox.setChecked(int(data[r][label_key]))
                        checkbox.check_change_signal.connect(self.update_client_info)
                        self.tab_0_table.setCellWidget(r, c, checkbox)
                    item = QTableWidgetItem(str(data[r][label_key]))
                item.setTextAlignment(132)
                self.tab_0_table.setItem(r, c, item)

        # self.setFixedHeight(300)  # 修改大小

    def tab_0_setSectionResizeMode(self):
        self.tab_0_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 列自适应
        self.tab_0_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 第一列根据文字宽自适应
        # self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 行自适应
        self.tab_0_table.verticalHeader().setVisible(False)

    def tab_1_new_client(self):
        """ button signal for create a new client """
        # 收集客户端信息
        bulletin_day = self.tab_1_bulletin_days.text().strip(' ')
        data = dict()
        data['name'] = self.tab_1_name_edit.text().strip(' ')
        data['machine_code'] = self.tab_1_machine.text().strip(' ')
        data['bulletin_days'] = bulletin_day if bulletin_day else 1
        data['is_admin'] = self.tab_1_admin_check.isChecked()
        data['is_active'] = self.tab_1_active_check.isChecked()
        data['operation_code'] = config.app_dawn.value('machine')
        cookies = config.app_dawn.value('cookies')
        if not cookies:
            QMessageBox.information(self, '提示', "请先登录再进行操作~", QMessageBox.Yes)
            return
        if not re.match(r'^[0-9a-z]+$', data['machine_code']):
            QMessageBox.information(self, '提示', "机器码格式有误~", QMessageBox.Yes)
            return
        # 上传
        try:
            response = requests.post(
                url=config.SERVER_ADDR + 'user/clients/',
                headers=config.CLIENT_HEADERS,
                data=json.dumps(data),
                cookies=cookies
            )
        except Exception as error:
            QMessageBox.information(self, '提示', "发生了个错误!\n{}".format(error), QMessageBox.Yes)
            return
        response_data = json.loads(response.content.decode('utf-8'))
        if response.status_code != 201:
            QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
            return
        else:
            self.new_client_successful.emit(True)
            QMessageBox.information(self, '提示', "创建成功!返回查看.", QMessageBox.Yes)

    def update_client_info(self, signal):
        """ checkbox in table has changed """
        # 获取机器码
        table_item = self.tab_0_table.item(signal['row'], 3)
        machine_code = table_item.text()
        # 请求修改客户端信息
        print(machine_code)


class SetBulletinWidget(QWidget):
    # 设置首页公告
    def __init__(self):
        super(SetBulletinWidget, self).__init__()
        self.setFixedSize(340, 300)
        self.title = QLabel("公告栏")
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
        layout.addWidget(self.title)
        layout.addWidget(tabs)
        self.setLayout(layout)


    def init_tab_0(self):
        self.show_type_list = ["文件展示", "显示文字"]
        layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.form_layout.setLabelAlignment(Qt.AlignRight)
        self.tab_0_edit_0 = QLineEdit()
        self.tab_0_edit_0.setPlaceholderText("输入条目展示的名称(默认文件名)")
        self.tab_0_edit_1 = QComboBox()
        self.tab_0_edit_1.addItems(self.show_type_list)
        self.tab_0_edit_1.currentTextChanged.connect(self.tab_0_show_type_changed)
        self.tab_0_edit_2 = QLineEdit()
        self.tab_0_edit_2.setEnabled(False)
        select_file_button = QPushButton("…")
        select_file_button.setFixedSize(30, 25)
        select_file_button.clicked.connect(self.tab_0_file_selected)
        show_type_layout = QHBoxLayout()
        show_type_layout.addWidget(self.tab_0_edit_2)
        show_type_layout.addWidget(select_file_button)
        # 固定大小
        self.tab_0_edit_0.setFixedSize(220, 25)
        self.tab_0_edit_1.setFixedSize(220, 25)
        self.tab_0_edit_2.setFixedSize(220, 25)
        # 填写文字的框
        self.text_edit = QTextEdit()
        self.text_edit.hide()
        self.form_layout.addRow("展示方式：", self.tab_0_edit_1)
        self.form_layout.addRow("公告名称：", self.tab_0_edit_0)
        self.form_layout.addRow("选择文件：", show_type_layout)
        # 上传按钮
        upload_button = QPushButton("确认")
        upload_button.setStyleSheet('border:none; background-color:rgb(100,182,220);height:30px; width:80px')
        upload_button.setCursor(QCursor(Qt.PointingHandCursor))
        upload_button.clicked.connect(self.tab_0_upload_data)
        upload_button_layout = QHBoxLayout()
        upload_button_layout.addWidget(upload_button, alignment=Qt.AlignRight)
        layout.addLayout(self.form_layout)
        layout.addLayout(upload_button_layout)
        layout.addStretch()
        self.tab_0.setLayout(layout)

    def init_tab_1(self):
        """初始化显示天数tab"""
        layout = QVBoxLayout()
        tip_label = QLabel("* 设置公告栏展示距今日几天前的内容")
        tip_label.setStyleSheet("color: rgb(84,182,230);font-size:12px;")
        form_layout = QFormLayout()
        self.tab_1_edit_1 = QLineEdit()
        self.tab_1_edit_1.setFixedHeight(28)
        self.tab_1_edit_1.setPlaceholderText("请输入正整数.")
        form_layout.addRow("设置天数：", self.tab_1_edit_1)
        self.set_button = QPushButton("确认设置")
        self.set_button.clicked.connect(self.tab_1_upload_data)
        self.set_button.setStyleSheet('border:none; background-color:rgb(100,182,220);height:30px; width:80px')
        self.set_button.setCursor(QCursor(Qt.PointingHandCursor))
        form_layout.addRow('', self.set_button)
        layout.addWidget(tip_label)
        layout.addLayout(form_layout)
        layout.addStretch()
        self.tab_1.setLayout(layout)

    def tab_0_show_type_changed(self, signal):
        """添加公告展示方式改变"""
        self.tab_0_edit_0.clear()
        self.text_edit.clear()
        self.tab_0_edit_2.clear()
        show_type_layout = QHBoxLayout()
        self.tab_0_edit_2 = QLineEdit()
        self.tab_0_edit_2.setFixedSize(220, 25)
        self.tab_0_edit_2.setEnabled(False)
        select_file_button = QPushButton("…")
        select_file_button.setFixedSize(30, 25)
        show_type_layout.addWidget(self.tab_0_edit_2)
        show_type_layout.addWidget(select_file_button)
        # 文字展示所需
        self.text_edit = QTextEdit()
        self.text_edit.setFixedSize(220, 100)
        self.form_layout.removeRow(self.form_layout.rowCount() - 1)
        if signal == self.show_type_list[0]:
            self.tab_0_edit_0.setPlaceholderText("输入条目展示的名称(默认文件名)")
            self.form_layout.addRow("选择文件：", show_type_layout)
        elif signal == self.show_type_list[1]:
            self.tab_0_edit_0.setPlaceholderText("输入条目展示的名称(必填)")
            self.form_layout.addRow("内容：", self.text_edit)
        else:
            pass

    def tab_0_file_selected(self):
        """选择文件"""
        # 弹窗
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        if not self.tab_0_edit_0.text().strip(' '):
            file_raw_name = file_path.rsplit("/", 1)
            file_name_list = file_raw_name[1].rsplit(".", 1)
            self.tab_0_edit_0.setText(file_name_list[0])
        self.tab_0_edit_2.setText(file_path)

    def tab_0_upload_data(self):
        """设置公告上传"""
        data = dict()
        show_dict = {
            "文件展示": "show_file",
            "显示文字": "show_text",
        }
        show_type = show_dict.get(self.tab_0_edit_1.currentText(), None)
        file_path = self.tab_0_edit_2.text()
        if not show_type:
            QMessageBox.warning(self, "错误", "未选择展示方式!", QMessageBox.Yes)
            return
        if show_type == "show_file" and not file_path:
            QMessageBox.warning(self, "错误", "请选择文件!", QMessageBox.Yes)
            return
        if show_type == "show_file" and not self.tab_0_edit_0.text().strip(' '):
            # 处理文件名称
            file_raw_name = file_path.rsplit("/", 1)
            file_name_list = file_raw_name.rsplit(".", 1)
            self.tab_0_edit_0.setText(file_name_list[0])
        if show_type == "show_text" and not self.tab_0_edit_0.text().strip(' '):
            QMessageBox.warning(self, "错误", "展示内容需输入条目名称!", QMessageBox.Yes)
            return
        content_list = self.text_edit.toPlainText().strip(' ').split('\n') # 去除前后空格和分出换行
        if show_type == "show_text" and not content_list[0]:
            QMessageBox.warning(self, "错误", "展示内容请填写文本内容!", QMessageBox.Yes)
            return
        # 处理文本内容
        text_content = ""
        if show_type == "show_text":
            for p in content_list:
                text_content += "<p style='margin:0;'><span>&nbsp;&nbsp;</span>" + p + "</p>"
        data["name"] = self.tab_0_edit_0.text().strip(' ')
        data["show_type"] = show_type
        data["file"] = file_path
        data["content"] = text_content
        data["set_option"] = "new_bulletin"
        self.set_bulletin_signal.emit(data)
        self.tab_0_edit_0.clear()
        self.tab_0_edit_2.clear()
        self.text_edit.clear()

    def tab_1_upload_data(self):
        try:
            days = int(self.tab_1_edit_1.text())
        except Exception as e:
            QMessageBox.warning(self, "错误", "请输入一个正整数!\n{}".format(e), QMessageBox.Yes)
            return
        if days <= 0:
            QMessageBox.warning(self, "错误", "请输入大于0的正整数!", QMessageBox.Yes)
            return
        data = dict()
        data["set_option"] = "days"
        data["days"] = days
        self.set_bulletin_signal.emit(data)
        self.tab_1_edit_1.clear()




