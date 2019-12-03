# _*_ coding:utf-8 _*_
# Author: zizle QQ:462894999
import re
import sys
import json
import xlrd
import datetime
import requests
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import QWidget, QDialog, QHBoxLayout, QVBoxLayout, QPushButton, QTreeWidget, QGridLayout,\
    QLineEdit, QLabel, QTreeWidgetItem, QTabWidget, QTableWidget, QTableWidgetItem, QFileDialog, QComboBox, QCompleter,\
    QHeaderView, QDateEdit

from PyQt5.QtCore import pyqtSignal, Qt, QThread, QDate
from PyQt5.QtGui import QIcon, QFont

import config
from utils import get_desktop_path

""" 常规报告 """


# 上传【常规报告文件】的线程
class UploadReportThread(QThread):
    response_signal = pyqtSignal(list)
    
    def __init__(self, file_list, machine_code, token, *args, **kwargs):
        super(UploadReportThread, self).__init__(*args, **kwargs)
        self.file_list = file_list
        self.machine_code = machine_code
        self.token = token

    def run(self):
        for file_item in self.file_list:
            # 读取文件
            print('上传常规报告文件', file_item['file_path'])
            try:
                data_file = dict()
                # 增加其他字段
                data_file['name'] = file_item['file_name']
                data_file['date'] = file_item['file_date']
                data_file['category_id'] = file_item['category_id']
                data_file['variety_id'] = file_item['variety_id']
                # 读取文件
                file = open(file_item['file_path'], "rb")
                file_content = file.read()
                file.close()
                # 文件内容字段
                data_file["file"] = (file_item['file_name'], file_content)
                encode_data = encode_multipart_formdata(data_file)
                data_file = encode_data[0]
                # 发起上传请求
                r = requests.post(
                    url=config.SERVER_ADDR + 'home/normal-report/?mc=' + self.machine_code,
                    headers={
                        'AUTHORIZATION': self.token,
                        'Content-Type': encode_data[1]
                    },
                    data=data_file
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 201:
                    raise ValueError(response['message'])
            except Exception as e:
                self.response_signal.emit([file_item['row_index'], str(e)])
            else:
                self.response_signal.emit([file_item['row_index'], response['message']])


# 维护【常规报告】的Tab Frame
class NormalReportMaintain(QWidget):
    network_result = pyqtSignal(bool)
    group_error = pyqtSignal(str)

    def __init__(self, group_id, category_id, category_text, *args, **kwargs):
        super(NormalReportMaintain, self).__init__(*args, **kwargs)
        self.group_id = group_id
        self.category_id = category_id
        layout = QVBoxLayout(margin=0)
        # 所属分类布局（含新建）
        attach_category_layout = QHBoxLayout()
        attach_category_label = QLabel('所属分类:', parent=self)
        self.attach_category = QLabel(category_text, parent=self)
        self.attach_category_tips = QLabel('不选则归类为【其他】。' if not category_id else '', objectName='categoryError')
        self.new_category_label = QLabel('当前没有的分类?')
        self.new_category_edit = QLineEdit()
        self.new_category_edit.hide()  # 隐藏编辑框
        self.new_category_button = QPushButton('新建', parent=self, clicked=self.add_new_category,
                                               objectName='newCategoryBtn', cursor=Qt.PointingHandCursor)
        attach_category_layout.addWidget(attach_category_label, alignment=Qt.AlignLeft)
        attach_category_layout.addWidget(self.attach_category)
        attach_category_layout.addStretch()  # 中间伸缩
        attach_category_layout.addWidget(self.attach_category_tips)
        attach_category_layout.addWidget(self.new_category_label)
        attach_category_layout.addWidget(self.new_category_edit)
        attach_category_layout.addWidget(self.new_category_button)
        # 选择品种导入报告和信息提示布局
        self.variety_combo = QComboBox(parent=self)
        self.variety_combo.setEditable(True)
        button_message_layout = QHBoxLayout()
        self.select_report_button = QPushButton('添加', parent=self, clicked=self.select_report_files)
        self.show_tips_label = QLabel(parent=self)
        button_message_layout.addWidget(QLabel('所属品种:'))
        button_message_layout.addWidget(self.variety_combo)
        button_message_layout.addWidget(self.select_report_button)
        button_message_layout.addStretch()
        button_message_layout.addWidget(self.show_tips_label)
        # 显示带操作表格
        self.report_table_show = QTableWidget()
        self.report_table_show.verticalHeader().hide()
        layout.addLayout(attach_category_layout)
        layout.addLayout(button_message_layout)
        layout.addWidget(self.report_table_show)
        self.commit_button = QPushButton('确认上传',parent=self, clicked=self.upload_reports)
        layout.addWidget(self.commit_button, alignment=Qt.AlignRight)
        self.setLayout(layout)
        self.setStyleSheet("""
        #categoryError{
            color: rgb(220,20,10)
        }
        #newCategoryBtn{
            min-width:35px;
            max-width:35px;
            border:none;
            color: rgb(100,50,200)
        }
        #newCategoryBtn:hover{
            color:rgb(240,120,120)
        }
        #dateEdit{
            border:none;
        }
        """)
        # 初始化，获取所有品种数据
        self.get_varieties()

    # 请求获取所有品种数据
    def get_varieties(self):
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'basic/variety/?mc=' + config.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
        except Exception as e:
            self.show_tips_label.setText(str(e))
            return
        else:
            name_en_list = list()
            for variety_item in response['data']:
                name_en_list.append(variety_item['name_en'])
                self.variety_combo.addItem(variety_item['name'], variety_item['id'])
                name_en_list.append(variety_item['name'])
            self.variety_combo.setCompleter(QCompleter(name_en_list))

    # 选择常规报告文件
    def select_report_files(self):
        # 获取当前品种名称和报告类型
        report_category = self.attach_category.text() if self.attach_category.text() else '其他'
        current_variety_text = self.variety_combo.currentText() + '(' + report_category + ')'
        file_path_list, _ = QFileDialog.getOpenFileNames(self, '选择文件', '', 'PDF files (*.pdf)')
        if not file_path_list:
            return
        print('数量', len(file_path_list))
        # 数据在表格中展示
        self.report_table_show.setColumnCount(5)
        self.report_table_show.setRowCount(len(file_path_list))
        self.report_table_show.setHorizontalHeaderLabels(['序号', '文件名', '品种(报告类型)', '报告日期', '状态'])
        self.report_table_show.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.report_table_show.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.report_table_show.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        for row, file_path in enumerate(file_path_list):
            item_0 = QTableWidgetItem(str(row + 1))
            item_0.setTextAlignment(Qt.AlignCenter)
            # 处理文件名
            item_1 = QTableWidgetItem(file_path.rsplit('/', 1)[1])
            item_1.file_abspath = file_path  # 保存好绝对路径
            item_1.setTextAlignment(Qt.AlignCenter)
            item_2 = QTableWidgetItem(current_variety_text)
            item_2.setTextAlignment(Qt.AlignCenter)
            item_3 = QDateEdit(QDate.currentDate(), objectName='dateEdit')
            item_3.setCalendarPopup(True)
            item_3.setDisplayFormat('yyyy-MM-dd')
            item_3.setAlignment(Qt.AlignCenter)
            item_4 = QTableWidgetItem('等待上传')
            item_4.setTextAlignment(Qt.AlignCenter)
            self.report_table_show.setItem(row, 0, item_0)
            self.report_table_show.setItem(row, 1, item_1)
            self.report_table_show.setItem(row, 2, item_2)
            self.report_table_show.setCellWidget(row, 3, item_3)
            self.report_table_show.setItem(row, 4, item_4)
        self.commit_button.setEnabled(True)

    # 确认上传常规报告文件
    def upload_reports(self):
        # 获取当前品种id
        current_variety_id = self.variety_combo.currentData()
        if not current_variety_id:
            self.show_tips_label.setText('您还未选择品种')
            return
        # 遍历表格打包文件信息(上传线程处理，每上传一个发个信号过来修改上传状态)
        file_message_list = list()
        for row in range(self.report_table_show.rowCount()):
            message_item = self.report_table_show.item(row, 4)  # 设置上传状态
            message_item.setText('正在上传...')
            file_message_list.append({
                'file_name': self.report_table_show.item(row, 1).text(),
                'file_path': self.report_table_show.item(row, 1).file_abspath,
                'category_id': self.category_id,
                'variety_id': current_variety_id,
                'file_date': self.report_table_show.cellWidget(row, 3).text(),
                'row_index': row
            })
        # 开启线程
        if hasattr(self, 'uploading_thread'):
            del self.uploading_thread
        self.uploading_thread = UploadReportThread(
            file_list=file_message_list,
            machine_code=config.app_dawn.value('machine'),
            token=config.app_dawn.value('AUTHORIZATION'),
        )
        self.uploading_thread.finished.connect(self.uploading_thread.deleteLater)
        self.uploading_thread.response_signal.connect(self.change_loading_state)
        self.uploading_thread.start()
        self.commit_button.setEnabled(False)

    # 改变上传状态
    def change_loading_state(self, row_message):
        self.report_table_show.item(row_message[0], 4).setText(row_message[1])

    # 新建数据组别下的分类
    def add_new_category(self):
        # 获取分组id
        if not self.group_id:
            self.group_error.emit('请先选择所属模块再创建分类.')
            return
        print('在组id为%d下创建分类' % self.group_id)
        # 显示编辑框
        if self.new_category_edit.isHidden():
            self.new_category_label.hide()
            self.new_category_edit.show()
            self.new_category_button.setText('确定')
        else:
            print('发起新建分类的请求。')
            if self._commit_new_category():
                self.new_category_edit.hide()
                self.new_category_label.show()
                self.new_category_button.setText('新建')

    # 新建分类的请求
    def _commit_new_category(self):
        # 获取name,去除空格
        name = re.sub(r'\s+', '', self.new_category_edit.text())
        if not name:
            self.attach_category_tips.setText('请输入分类名称')
            return
        try:
            r = requests.post(
                url=config.SERVER_ADDR + 'home/group-categories/' + str(self.group_id) + '/?mc=' + config.app_dawn.value('machine'),
                headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'name': name
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            self.attach_category_tips.setText(str(e))
            return False
        else:
            # 重新获取左侧列表
            self.network_result.emit(True)
            # 根据返回的数据，写入选择的分类
            self.category_id = response['data']['id']
            self.attach_category.setText(response['data']['name'])
            self.attach_category_tips.setText('')
            return True


""" 交易通知 """


# 上传【交易通知文件】的线程
class UploadNoticeThread(QThread):
    response_signal = pyqtSignal(list)

    def __init__(self, file_list, machine_code, token, *args, **kwargs):
        super(UploadNoticeThread, self).__init__(*args, **kwargs)
        self.file_list = file_list
        self.machine_code = machine_code
        self.token = token

    def run(self):
        for file_item in self.file_list:
            # 读取文件
            print('上传交易通知文件', file_item)
            try:
                data_file = dict()
                # 增加其他字段
                data_file['name'] = file_item['file_name']
                data_file['date'] = file_item['file_date']
                data_file['category_id'] = file_item['category_id']
                # 读取文件
                file = open(file_item['file_path'], "rb")
                file_content = file.read()
                file.close()
                # 文件内容字段
                data_file["file"] = (file_item['file_name'], file_content)
                encode_data = encode_multipart_formdata(data_file)
                data_file = encode_data[0]
                # 发起上传请求
                r = requests.post(
                    url=config.SERVER_ADDR + 'home/transaction-notice/?mc=' + self.machine_code,
                    headers={
                        'AUTHORIZATION': self.token,
                        'Content-Type': encode_data[1]
                    },
                    data=data_file
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 201:
                    raise ValueError(response['message'])
            except Exception as e:
                self.response_signal.emit([file_item['row_index'], str(e)])
            else:
                self.response_signal.emit([file_item['row_index'], response['message']])


# 维护【交易通知】的Tab Frame
class TransactionNoticeMaintain(QWidget):
    network_result = pyqtSignal(bool)

    def __init__(self, group_id, category_id, category_text, *args, **kwargs):
        super(TransactionNoticeMaintain, self).__init__(*args, **kwargs)
        self.group_id = group_id
        self.category_id = category_id
        layout = QVBoxLayout(margin=0)
        # 所属分类布局（含新建）
        attach_category_layout = QHBoxLayout()
        attach_category_label = QLabel('所属分类:', parent=self)
        self.attach_category = QLabel(category_text, parent=self)
        self.attach_category_tips = QLabel('不选则归类为【其他】。' if not category_id else '', objectName='categoryError')
        self.new_category_label = QLabel('当前没有的分类?')
        self.new_category_edit = QLineEdit()
        self.new_category_edit.hide()  # 隐藏编辑框
        self.new_category_button = QPushButton('新建', parent=self, clicked=self.add_new_category,
                                               objectName='newCategoryBtn', cursor=Qt.PointingHandCursor)
        attach_category_layout.addWidget(attach_category_label, alignment=Qt.AlignLeft)
        attach_category_layout.addWidget(self.attach_category)
        attach_category_layout.addStretch()  # 中间伸缩
        attach_category_layout.addWidget(self.attach_category_tips)
        attach_category_layout.addWidget(self.new_category_label)
        attach_category_layout.addWidget(self.new_category_edit)
        attach_category_layout.addWidget(self.new_category_button)
        # 导入通知和信息提示布局
        button_message_layout = QHBoxLayout()
        self.select_notice_button = QPushButton('新增通知', parent=self, clicked=self.select_notice_files)
        self.show_tips_label = QLabel(parent=self)
        button_message_layout.addWidget(self.select_notice_button)
        button_message_layout.addWidget(self.show_tips_label)
        button_message_layout.addStretch()  # 伸缩
        # 显示带操作表格
        self.notice_table_show = QTableWidget()
        self.notice_table_show.verticalHeader().hide()
        layout.addLayout(attach_category_layout)
        layout.addLayout(button_message_layout)
        layout.addWidget(self.notice_table_show)
        self.commit_button = QPushButton('确认上传', parent=self, clicked=self.upload_notices)
        layout.addWidget(self.commit_button, alignment=Qt.AlignRight)
        self.setLayout(layout)
        self.setStyleSheet("""
        #categoryError{
            color: rgb(220,20,10)
        }
        #newCategoryBtn{
            min-width:35px;
            max-width:35px;
            border:none;
            color: rgb(100,50,200)
        }
        #newCategoryBtn:hover{
            color:rgb(240,120,120)
        }
        #dateEdit{
            border:none;
        }
        """)
        # 初始化，获取所有品种数据

    # 选择交易通知文件
    def select_notice_files(self):
        # 获取当前品种名称和报告类型
        notice_category = self.attach_category.text() if self.attach_category.text() else '其他'
        file_path_list, _ = QFileDialog.getOpenFileNames(self, '选择文件', '', 'PDF files (*.pdf)')
        if not file_path_list:
            return
        # 数据在表格中展示
        self.notice_table_show.setColumnCount(5)
        self.notice_table_show.setRowCount(len(file_path_list))
        self.notice_table_show.setHorizontalHeaderLabels(['序号', '文件名', '所属类别', '发布日期', '状态'])
        self.notice_table_show.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.notice_table_show.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.notice_table_show.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        for row, file_path in enumerate(file_path_list):
            item_0 = QTableWidgetItem(str(row + 1))
            item_0.setTextAlignment(Qt.AlignCenter)
            self.notice_table_show.setItem(row, 0, item_0)
            # 处理文件名
            item_1 = QTableWidgetItem(file_path.rsplit('/', 1)[1])
            item_1.file_abspath = file_path  # 保存好绝对路径
            item_1.setTextAlignment(Qt.AlignCenter)
            self.notice_table_show.setItem(row, 1, item_1)
            # 所属类别
            item_2 = QTableWidgetItem(notice_category)
            item_2.setTextAlignment(Qt.AlignCenter)
            self.notice_table_show.setItem(row, 2, item_2)
            # 通知日期
            item_3 = QDateEdit(QDate.currentDate(), objectName='dateEdit')
            item_3.setCalendarPopup(True)
            item_3.setDisplayFormat('yyyy-MM-dd')
            item_3.setAlignment(Qt.AlignCenter)
            self.notice_table_show.setCellWidget(row, 3, item_3)
            # 状态
            item_4 = QTableWidgetItem('等待上传')
            item_4.setTextAlignment(Qt.AlignCenter)
            self.notice_table_show.setItem(row, 4, item_4)
        self.commit_button.setEnabled(True)

    # 上传交易通知文件
    def upload_notices(self):
        # 遍历表格打包文件信息(上传线程处理，每上传一个发个信号过来修改上传状态)
        file_message_list = list()
        for row in range(self.notice_table_show.rowCount()):
            message_item = self.notice_table_show.item(row, 4)  # 设置上传状态
            message_item.setText('正在上传...')
            file_message_list.append({
                'file_name': self.notice_table_show.item(row, 1).text(),
                'file_path': self.notice_table_show.item(row, 1).file_abspath,  # 文件的绝对路径保存在item_1中
                'category_id': self.category_id,
                'file_date': self.notice_table_show.cellWidget(row, 3).text(),
                'row_index': row
            })
        # 开启线程
        if hasattr(self, 'uploading_thread'):
            del self.uploading_thread
        self.uploading_thread = UploadNoticeThread(
            file_list=file_message_list,
            machine_code=config.app_dawn.value('machine'),
            token=config.app_dawn.value('AUTHORIZATION'),
        )
        self.uploading_thread.finished.connect(self.uploading_thread.deleteLater)
        self.uploading_thread.response_signal.connect(self.change_loading_state)
        self.uploading_thread.start()
        self.commit_button.setEnabled(False)

    # 改变上传状态
    def change_loading_state(self, row_message):
        self.notice_table_show.item(row_message[0], 4).setText(row_message[1])

    # 新增数据类别
    def add_new_category(self):
        # 获取分组id
        if not self.group_id:
            self.group_error.emit('请先选择所属模块再创建分类.')
            return
        print('在组id为%d下创建分类' % self.group_id)
        # 显示编辑框
        if self.new_category_edit.isHidden():
            self.new_category_label.hide()
            self.new_category_edit.show()
            self.new_category_button.setText('确定')
        else:
            print('发起新建分类的请求。')
            if self._commit_new_category():
                self.new_category_edit.hide()
                self.new_category_label.show()
                self.new_category_button.setText('新建')

    # 新建分类的请求
    def _commit_new_category(self):
        # 获取name,去除空格
        name = re.sub(r'\s+', '', self.new_category_edit.text())
        if not name:
            self.attach_category_tips.setText('请输入分类名称')
            return
        try:
            r = requests.post(
                url=config.SERVER_ADDR + 'home/group-categories/' + str(
                    self.group_id) + '/?mc=' + config.app_dawn.value('machine'),
                headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'name': name
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            self.attach_category_tips.setText(str(e))
            return False
        else:
            # 重新获取左侧列表
            self.network_result.emit(True)
            # 根据返回的数据，写入选择的分类
            self.category_id = response['data']['id']
            self.attach_category.setText(response['data']['name'])
            self.attach_category_tips.setText('')
            return True


# 新增分组数据弹窗
class NewHomeDataPopup(QDialog):
    network_result = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(NewHomeDataPopup, self).__init__(*args, **kwargs)
        self.setWindowTitle('新增数据')
        # 总左右布局
        layout = QHBoxLayout()
        # 左侧上下布局
        llayout = QVBoxLayout()
        # 左侧分类树
        self.left_tree = QTreeWidget(parent=self)
        self.left_tree.header().hide()
        self.left_tree.clicked.connect(self.left_tree_clicked)
        self.add_group_button = QPushButton('新增模块', parent=self, clicked=self.add_new_group)
        llayout.addWidget(self.left_tree, alignment=Qt.AlignLeft)
        llayout.addWidget(self.add_group_button, alignment=Qt.AlignLeft)
        # 右侧上下布局
        rlayout = QVBoxLayout()
        # 右侧所属模块布局
        attach_group_layout = QHBoxLayout()
        attach_group_label = QLabel('维护模块:', parent=self)
        self.attach_group = QLabel(parent=self)
        self.attach_group.gid = None
        attach_group_layout.addWidget(attach_group_label, alignment=Qt.AlignLeft)
        attach_group_layout.addWidget(self.attach_group)
        attach_group_layout.addStretch()  # 右侧伸缩使显示靠左
        # 维护模块错误提示
        self.attach_group_error = QLabel(parent=self, objectName='groupError')
        attach_group_layout.addWidget(self.attach_group_error)
        rlayout.addLayout(attach_group_layout)

        # 右侧显示维护数据frame的控件
        self.right_tab = QTabWidget(parent=self)
        self.right_tab.tabBar().hide()
        self.right_tab.setDocumentMode(True)
        # 控件布局
        rlayout.addWidget(self.right_tab)
        # 加入总布局显示
        layout.addLayout(llayout)
        layout.addLayout(rlayout)
        self.setFixedSize(1000, 500)
        self.setLayout(layout)
        self.setStyleSheet("""
        #groupError{
            color: rgb(220,20,10)
        }
        """)
        # 初始化数据分类
        self.get_groups_categories()

    # 获取数据分组(含分组内的类别)
    def get_groups_categories(self):
        self.left_tree.clear()
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'home/groups-categories/?mc=' + config.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
            return
        else:
            # 填充分组树
            for group_item in response['data']:
                group = QTreeWidgetItem(self.left_tree)
                group.setText(0, group_item['name'])
                group.gid = group_item['id']
                # 添加子节点
                for category_item in group_item['categories']:
                    child = QTreeWidgetItem()
                    child.setText(0, category_item['name'])
                    child.cid = category_item['id']
                    group.addChild(child)
            self.left_tree.expandAll()
            self.network_result.emit('')

    # 新增数据大分组
    def add_new_group(self):
        new_popup = QDialog(parent=self)
        # 提交新建大组
        def commit_new_group():
            print('提交新建大组')
            name = re.sub(r'\s+', '', new_popup.name_edit.text())
            if not name:
                new_popup.name_error.setText('请输入名称')
                return
            try:
                r = requests.post(
                    url=config.SERVER_ADDR + 'home/data-groups/?mc=' + config.app_dawn.value('machine'),
                    headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')},
                    data=json.dumps({
                        'name': name
                    })
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 201:
                    raise ValueError(response['message'])
            except Exception as e:
                new_popup.name_error.setText(str(e))
            else:
                new_popup.close()
                self.get_groups_categories()  # 重新请求分组数据
                self.network_result.emit('hasNewGroup')

        new_popup.setWindowTitle('新增大组')
        nglayout = QGridLayout()
        # 加入编辑名称
        new_popup.name_edit = QLineEdit(parent=new_popup)
        new_popup.name_error = QLabel(parent=new_popup, objectName='nameError')
        nglayout.addWidget(QLabel('名称:', parent=new_popup), 0, 0)
        nglayout.addWidget(new_popup.name_edit, 0, 1)
        nglayout.addWidget(new_popup.name_error, 1, 0, 1, 2)
        abtlayout = QHBoxLayout()
        abtlayout.addWidget(QPushButton('确定提交', parent=new_popup, objectName='addNdgbtn',
                                        clicked=commit_new_group), alignment=Qt.AlignRight)
        nglayout.addLayout(abtlayout, 1, 1)
        new_popup.setLayout(nglayout)
        new_popup.setFixedSize(250, 110)

        if not new_popup.exec_():
            new_popup.deleteLater()
            del new_popup

    # 显示子控件中组错误的信息
    def show_group_error_message(self, message):
        self.attach_group_error.setText(message)

    # 点击左侧分组树
    def left_tree_clicked(self):
        self.attach_group_error.setText('')  # 清空组错误
        current_item = self.left_tree.currentItem()
        parent = current_item.parent()
        if parent:
            self.attach_group.gid = parent.gid
            group_text = parent.text(0)
            category_id = current_item.cid  # 有父类的是cid，详见函数self.get_groups_categories
            category_text = current_item.text(0)
        else:
            self.attach_group.gid = current_item.gid
            group_text = current_item.text(0)
            category_id = 0
            category_text = ''
        # 改变所属分组的显示
        self.attach_group.setText(group_text)
        # 没有父级时改变tab内的显示
        if group_text == u'常规报告':
            maintain_tab = NormalReportMaintain(parent=self, group_id=self.attach_group.gid, category_id=category_id, category_text=category_text)
            maintain_tab.network_result.connect(self.get_groups_categories)
            maintain_tab.group_error.connect(self.show_group_error_message)
        elif group_text == u'交易通知':
            maintain_tab = TransactionNoticeMaintain(parent=self, group_id=self.attach_group.gid, category_id=category_id, category_text=category_text)
            maintain_tab.network_result.connect(self.get_groups_categories)
        else:
            maintain_tab = QLabel('该模块还不支持新增数据。', alignment=Qt.AlignCenter)
        self.right_tab.clear()
        self.right_tab.addTab(maintain_tab, '')



















class CreateNewBulletin(QDialog):
    new_data_signal = pyqtSignal(dict)
    def __init__(self):
        super(CreateNewBulletin, self).__init__()
        layout = QGridLayout()
        # labels
        title_label = QLabel('标题：')
        style_label = QLabel('展示方式：')
        self.file_label = QLabel('文件：')
        self.content_label = QLabel('内容：')
        self.content_label.hide()
        # edits
        self.title_edit = QLineEdit()
        self.file_edit = QLineEdit()
        self.content_edit = QTextEdit()
        self.content_edit.hide()
        # combos
        self.show_combo = QComboBox()
        self.show_combo.addItems(['文件展示', '显示内容'])
        self.show_combo.currentTextChanged.connect(self.change_show_style)
        # buttons
        self.select_file_btn = QPushButton('选择')
        submit_btn = QPushButton('提交')
        self.select_file_btn.setMaximumWidth(30)
        # select button signal
        self.select_file_btn.clicked.connect(self.select_file_clicked)
        submit_btn.clicked.connect(self.submit_carousel)
        # add layout
        # named
        layout.addWidget(title_label, 0, 0)
        layout.addWidget(self.title_edit, 0, 1, 1, 2)
        # show style
        layout.addWidget(style_label, 1, 0)
        layout.addWidget(self.show_combo, 1, 1, 1, 2)
        # select file
        layout.addWidget(self.file_label, 2, 0)
        layout.addWidget(self.file_edit, 2, 1)
        layout.addWidget(self.select_file_btn, 2, 2)
        # edit content
        layout.addWidget(self.content_label, 3, 0)
        layout.addWidget(self.content_edit, 3, 1, 1, 2)
        # submit
        layout.addWidget(submit_btn, 6, 1, 1, 2)
        self.setLayout(layout)

    def change_show_style(self, text):
        if text == '文件展示':
            # hide content
            self.content_label.hide()
            self.content_edit.clear()
            self.content_edit.hide()
            # show file
            self.file_label.show()
            self.file_edit.show()
            self.select_file_btn.show()
        elif text == '显示内容':
            # hide file
            self.file_label.hide()
            self.file_edit.clear()
            self.file_edit.hide()
            self.select_file_btn.hide()
            # show content
            self.content_label.show()
            self.content_edit.show()
        else:
            pass

    def select_file_clicked(self):
        # select file
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        file_name_list = file_path.rsplit('/', 1)
        if not self.title_edit.text().strip(' '):
            self.title_edit.setText((file_name_list[1].rsplit('.', 1))[0])
        self.file_edit.setText(file_path)

    def select_img_clicked(self):
        # select image
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "Image files (*.png *.jpg)")
        if not file_path:
            return
        self.file_edit.setText(file_path)

    def submit_carousel(self):
        # submit carousel data
        data = dict()
        show_dict = {
            "文件展示": "show_file",
            "显示内容": "show_text",
        }
        title = self.title_edit.text().strip(' ')
        if not title:
            QMessageBox.warning(self, "错误", "请起一个名字!", QMessageBox.Yes)
            return
        show_style = show_dict.get(self.show_combo.currentText(), None)
        if not show_style:
            QMessageBox.warning(self, "错误", "没有选择展示方式!", QMessageBox.Yes)
            return
        if show_style == "show_file" and not self.file_edit.text():
            QMessageBox.warning(self, "错误", "要显示文件需上传pdf文件!", QMessageBox.Yes)
            return
        if show_style == 'show_text' and not self.content_edit.toPlainText().strip(' '):
            QMessageBox.warning(self, '错误', '显示内容需填写内容.')
            return
        file_path = self.file_edit.text()
        content_list = self.content_edit.toPlainText().split('\n')
        # 处理文本内容
        text_content = ""
        if content_list[0]:
            for p in content_list:
                text_content += "<p style='margin:0;'><span>&nbsp;&nbsp;</span>" + p + "</p>"
        data["name"] = title
        data["file"] = file_path
        data["content"] = text_content
        data['show_type'] = show_style
        # signal upload
        self.new_data_signal.emit(data)












    #
    # new_data_signal = pyqtSignal(dict)
    #
    # def __init__(self):
    #     super(CreateNewBulletin, self).__init__()
    #     self.setWindowTitle('设置')
    #     self.setWindowIcon(QIcon("media/bulletin.png"))
    #     layout = QVBoxLayout()
    #     # 添加一个tab
    #     tabs = QTabWidget()
    #     self.tab_0 = QWidget()
    #     self.tab_1 = QWidget()
    #     tabs.addTab(self.tab_0, "添加公告")
    #     # tabs.addTab(self.tab_1, "显示天数")
    #     # 初始化tab_0
    #     self.init_tab_0()
    #     self.init_tab_1()
    #     layout.addWidget(tabs)
    #     self.setLayout(layout)
    #
    # def init_tab_0(self):
    #     grid_layout_0 = QGridLayout()
    #     tab_0_label_0 = QLabel("名称：")
    #     tab_0_label_1 = QLabel("展示：")
    #     self.tab_0_label_2 = QLabel('文件：')
    #     self.tab_0_label_3 = QLabel('内容：')
    #     self.tab_0_edit_0 = QLineEdit()  # 名称
    #     self.tab_0_edit_1 = QLineEdit()  # 文件路径
    #     self.tab_0_edit_0.setPlaceholderText("输入条目展示的名称(默认文件名)")
    #     self.tab_0_combo = QComboBox()
    #     self.tab_0_combo.addItems(['文件展示', '显示文字'])
    #     self.tab_0_combo.currentTextChanged.connect(self.tab_0_show_type_changed)
    #     self.tab_0_btn_0  = QPushButton('浏览')
    #     self.tab_0_btn_0.setMaximumWidth(30)
    #     tab_0_btn_1 = QPushButton('提交')
    #     self.tab_0_btn_0.clicked.connect(self.select_file)
    #     tab_0_btn_1.clicked.connect(self.submit_bulletin)
    #     self.tab_0_edit_2 = QTextEdit()  # 内容
    #     # initial hide the content edit
    #     self.tab_0_label_3.hide()
    #     self.tab_0_edit_2.hide()
    #     grid_layout_0.addWidget(tab_0_label_0, 0, 0)
    #     grid_layout_0.addWidget(self.tab_0_edit_0, 0, 1, 1, 2)
    #     grid_layout_0.addWidget(tab_0_label_1, 1, 0)
    #     grid_layout_0.addWidget(self.tab_0_combo, 1, 1, 1, 2)
    #     grid_layout_0.addWidget(self.tab_0_label_2, 2, 0)
    #     grid_layout_0.addWidget(self.tab_0_edit_1, 2, 1)
    #     grid_layout_0.addWidget(self.tab_0_btn_0, 2, 2)
    #     grid_layout_0.addWidget(self.tab_0_label_3, 3, 0)
    #     grid_layout_0.addWidget(self.tab_0_edit_2, 3, 1, 1, 2)
    #     grid_layout_0.addWidget(tab_0_btn_1, 4, 1, 1,2)
    #     self.tab_0.setLayout(grid_layout_0)
    #
    # def init_tab_1(self):
    #     grid_layout_1 = QGridLayout()
    #     tip_label = QLabel("* 设置公告栏展示距今日几天前的内容")
    #     tip_label.setStyleSheet("color: rgb(84,182,230);font-size:12px;")
    #     tab_1_label_0 = QLabel("设置天数：")
    #     self.tab_1_edit_0 = QLineEdit()
    #     self.tab_1_edit_0.setFixedHeight(28)
    #     self.tab_1_edit_0.setPlaceholderText("请输入正整数.")
    #     tab_1_btn_0 = QPushButton("提交")
    #     grid_layout_1.addWidget(tip_label, 0, 0, 1, 2)
    #     grid_layout_1.addWidget(tab_1_label_0, 1, 0)
    #     grid_layout_1.addWidget(self.tab_1_edit_0, 1, 1, 1, 2)
    #     grid_layout_1.addWidget(tab_1_btn_0, 2, 1, 1, 2)
    #     self.tab_1.setLayout(grid_layout_1)
    #
    # def tab_0_show_type_changed(self, text):
    #     if text == '文件展示':
    #         self.resize(318, 214)
    #         self.tab_0_label_2.show()
    #         self.tab_0_edit_1.show()
    #         self.tab_0_btn_0.show()
    #         self.tab_0_label_3.hide()
    #         self.tab_0_edit_2.hide()
    #     elif text == '显示文字':
    #         self.resize(318, 300)
    #         self.tab_0_label_2.hide()
    #         self.tab_0_edit_1.hide()
    #         self.tab_0_btn_0.hide()
    #         self.tab_0_label_3.show()
    #         self.tab_0_edit_2.show()
    #
    # def select_file(self):
    #     """ select file when show type is file """
    #     # 弹窗
    #     desktop_path = get_desktop_path()
    #     file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
    #     if not file_path:
    #         return
    #     if not self.tab_0_edit_0.text().strip(' '):  # set bulletin name
    #         file_raw_name = file_path.rsplit("/", 1)
    #         file_name_list = file_raw_name[1].rsplit(".", 1)
    #         self.tab_0_edit_0.setText(file_name_list[0])
    #     self.tab_0_edit_1.setText(file_path)  # set file path
    #
    # def submit_bulletin(self):
    #     """ create new bulletin in server """
    #     # collect data
    #     data = dict()
    #     show_dict = {
    #         "文件展示": "show_file",
    #         "显示文字": "show_text",
    #     }
    #     show_type = show_dict.get(self.tab_0_combo.currentText(), None)
    #     file_path = self.tab_0_edit_1.text()
    #     if not show_type:
    #         QMessageBox.warning(self, "错误", "未选择展示方式!", QMessageBox.Yes)
    #         return
    #     if show_type == "show_file" and not file_path:
    #         QMessageBox.warning(self, "错误", "请选择文件!", QMessageBox.Yes)
    #         return
    #     if show_type == "show_file" and not self.tab_0_edit_0.text().strip(' '):
    #         # doesn't names for this bulletin when show type is file
    #         file_raw_name = file_path.rsplit("/", 1)
    #         file_name_list = file_raw_name.rsplit(".", 1)
    #         self.tab_0_edit_0.setText(file_name_list[0])
    #     if show_type == "show_text" and not self.tab_0_edit_0.text().strip(' '):
    #         # doesn't names for this bulletin when show type is text
    #         QMessageBox.warning(self, "错误", "展示文本时需输入条目名称!", QMessageBox.Yes)
    #         return
    #     content_list = self.tab_0_edit_2.toPlainText().strip(' ').split('\n') # 去除前后空格和分出换行
    #     if show_type == "show_text" and not content_list[0]:
    #         QMessageBox.warning(self, "错误", "请输入展示文本的内容!", QMessageBox.Yes)
    #         return
    #     # 处理文本内容
    #     text_content = ""
    #     if show_type == "show_text":
    #         for p in content_list:
    #             text_content += "<p style='margin:0;'><span>&nbsp;&nbsp;</span>" + p + "</p>"
    #     data["title"] = self.tab_0_edit_0.text().strip(' ')
    #     data["show_type"] = show_type
    #     data["file"] = file_path
    #     data["content"] = text_content
    #     data["set_option"] = "new_bulletin"
    #     print('popup.maintain.home.py {} : '.format(str(sys._getframe().f_lineno)), "上传公告:", data)
    #     self.new_data_signal.emit(data)


class CreateNewCarousel(QDialog):
    new_data_signal = pyqtSignal(dict)

    def __init__(self):
        super(CreateNewCarousel, self).__init__()
        self.setFixedSize(430, 220)
        layout = QGridLayout()
        # labels
        name_label = QLabel('名称：')
        image_label = QLabel('图片：')
        style_label = QLabel('广告方式：')
        self.file_label = QLabel('文件：')
        self.content_label = QLabel('内容：')
        self.url_label = QLabel('网址：')
        self.content_label.hide()
        self.url_label.hide()
        # edits
        self.name_edit = QLineEdit()
        self.image_edit = QLineEdit()
        self.file_edit = QLineEdit()
        self.url_edit = QLineEdit()
        self.content_edit = QTextEdit()
        self.content_edit.hide()
        self.url_edit.hide()
        # combos
        self.show_combo = QComboBox()
        self.show_combo.addItems(['文件展示', '显示内容', '链接网址'])
        self.show_combo.currentTextChanged.connect(self.change_show_style)
        # buttons
        self.select_file_btn = QPushButton('选择')
        select_img_btn = QPushButton('图片')
        submit_btn = QPushButton('提交')
        self.select_file_btn.setMaximumWidth(30)
        select_img_btn.setMaximumWidth(30)
        # select button signal
        self.select_file_btn.clicked.connect(self.select_file_clicked)
        select_img_btn.clicked.connect(self.select_img_clicked)
        submit_btn.clicked.connect(self.submit_carousel)
        # add layout
        # named
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(self.name_edit, 0, 1, 1, 2)
        # select image
        layout.addWidget(image_label, 1, 0)
        layout.addWidget(self.image_edit, 1, 1)
        layout.addWidget(select_img_btn, 1, 2)
        # show style
        layout.addWidget(style_label, 2, 0)
        layout.addWidget(self.show_combo, 2, 1, 1, 2)
        # select file
        layout.addWidget(self.file_label, 3, 0)
        layout.addWidget(self.file_edit, 3, 1)
        layout.addWidget(self.select_file_btn, 3, 2)
        # edit content
        layout.addWidget(self.content_label, 4, 0)
        layout.addWidget(self.content_edit, 4, 1, 1, 2)
        # edit url address
        layout.addWidget(self.url_label, 5, 0)
        layout.addWidget(self.url_edit, 5, 1, 1,2)
        # submit
        layout.addWidget(submit_btn, 6, 1, 1, 2)
        self.setLayout(layout)

    def change_show_style(self, text):
        if text == '文件展示':
            # hide content
            self.content_label.hide()
            self.content_edit.clear()
            self.content_edit.hide()
            # hide url
            self.url_label.hide()
            self.url_edit.clear()
            self.url_edit.hide()
            # show file
            self.file_label.show()
            self.file_edit.show()
            self.select_file_btn.show()
        elif text == '显示内容':
            # hide file
            self.file_label.hide()
            self.file_edit.clear()
            self.file_edit.hide()
            self.select_file_btn.hide()
            # hide url link
            self.url_label.hide()
            self.url_edit.clear()
            self.url_edit.hide()
            # show content
            self.content_label.show()
            self.content_edit.show()
        elif text == '链接网址':
            # hide file
            self.file_label.hide()
            self.file_edit.clear()
            self.file_edit.hide()
            self.select_file_btn.hide()
            # hide content
            self.content_label.hide()
            self.content_edit.clear()
            self.content_edit.hide()
            # show url link
            self.url_label.show()
            self.url_edit.show()
        else:
            pass

    def select_file_clicked(self):
        # select file
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        self.file_edit.setText(file_path)

    def select_img_clicked(self):
        # select image
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "Image files (*.png *.jpg)")
        if not file_path:
            return
        self.image_edit.setText(file_path)

    def submit_carousel(self):
        # submit carousel data
        data = dict()
        show_dict = {
            "文件展示": "show_file",
            "显示内容": "show_text",
            "链接网址": "redirect"
        }
        name = self.name_edit.text().strip(' ')
        if not name:
            QMessageBox.warning(self, "错误", "请起一个名字!", QMessageBox.Yes)
            return
        image_path = self.image_edit.text()
        if not image_path:
            QMessageBox.warning(self, "错误", "请上传展示的图片!", QMessageBox.Yes)
            return
        show_style = show_dict.get(self.show_combo.currentText(), None)
        if not show_style:
            QMessageBox.warning(self, "错误", "没有选择展示方式!", QMessageBox.Yes)
            return
        if show_style == "show_file" and not self.file_edit.text():
            QMessageBox.warning(self, "错误", "要显示文件需上传pdf文件!", QMessageBox.Yes)
            return
        if show_style == "redirect" and not self.url_edit.text().strip(' '):
            QMessageBox.warning(self, "错误", "跳转网址需填写网址.", QMessageBox.Yes)
            return
        if show_style == 'show_text' and not self.content_edit.toPlainText().strip(' '):
            QMessageBox.warning(self, '错误', '显示内容需填写内容.')
            return
        file_path = self.file_edit.text()
        content_list = self.content_edit.toPlainText().split('\n')
        # 处理文本内容
        text_content = ""
        if content_list[0]:
            for p in content_list:
                text_content += "<p style='margin:0;'><span>&nbsp;&nbsp;</span>" + p + "</p>"
        redirect_url = self.url_edit.text().strip(' ')
        data["name"] = name
        data["image"] = image_path
        data["file"] = file_path
        data["content"] = text_content
        data["redirect"] = redirect_url
        # signal upload
        print('popup.maintain.home.py {} : 上传轮播：'.format(str(sys._getframe().f_lineno)), data )
        self.new_data_signal.emit(data)


class CreateNewCommodity(QDialog):
    new_data_signal = pyqtSignal(list)
    def __init__(self):
        super(CreateNewCommodity, self).__init__()
        self.resize(850,550)
        layout = QVBoxLayout()
        load_file_btn = QPushButton('+数据')
        self.review_table = QTableWidget()
        tip_label = QLabel('*请检查无误上传,提交后将不可更改.')
        submit_btn = QPushButton("提交")
        # widget style
        tip_label.setStyleSheet('font-size:12px; color:rgb(255,10,10)')
        self.review_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.review_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # button signal
        load_file_btn.clicked.connect(self.read_new_commodity)
        submit_btn.clicked.connect(self.submit_commodity)
        # add layout
        layout.addWidget(load_file_btn, alignment=Qt.AlignLeft)
        layout.addWidget(self.review_table)
        layout.addWidget(tip_label)
        layout.addWidget(submit_btn, alignment=Qt.AlignRight)
        self.setLayout(layout)

    def read_new_commodity(self):
        # upload data to review table
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.xlsx *.xls)")
        if not file_path:
            return
        rf = xlrd.open_workbook(filename=file_path)
        sheet1 = rf.sheet_by_index(0)
        row_header = sheet1.row_values(0)
        # excel file header match
        header_labels = ["品种", "地区", "等级", "报价", "日期", "备注"]
        if row_header != header_labels:
            return
        # table initial
        self.review_table.setRowCount(sheet1.nrows - 1)
        self.review_table.setColumnCount(len(header_labels))
        self.review_table.setHorizontalHeaderLabels(header_labels)
        for row in range(1, sheet1.nrows):  # skip header
            row_content = sheet1.row_values(row)
            row_content[4] = datetime.datetime.strftime(xlrd.xldate_as_datetime(row_content[4], rf.datemode), "%Y-%m-%d")
            # data to review table
            for col, col_data in enumerate(row_content):
                item = QTableWidgetItem(str(col_data))
                item.setTextAlignment(132)
                self.review_table.setItem(row - 1, col, item)

    def submit_commodity(self):
        # submit commodity
        data = []
        header_labels = ["variety", "area", "level", "price", "date", "note"]
        for row in range(self.review_table.rowCount()):
            item = dict()
            for col in range(len(header_labels)):
                col_item = self.review_table.item(row, col)
                if not col_item or not col_item.text():
                    continue
                item[header_labels[col]] = col_item.text()
            # 验证信息
            for key in header_labels:
                if key == "note":
                    continue
                if len(item) > 1 and not item.get(key):
                    QMessageBox.warning(self, "错误", "请将信息填写完整!", QMessageBox.Yes)
                    return
            if len(item) >= 5:
                data.append(item)
        if not data:
            QMessageBox.warning(self, "错误", "您未填写任何信息!", QMessageBox.Yes)
            return
        self.review_table.clear()
        self.review_table.setRowCount(0)
        self.review_table.setHorizontalHeaderLabels(["品种", "地区", "等级", "报价", "时间", "备注"])
        self.new_data_signal.emit(data)


class CreateNewFinance(QDialog):
    new_data_signal = pyqtSignal(list)
    def __init__(self):
        super(CreateNewFinance, self).__init__()
        self.resize(850, 550)
        layout = QVBoxLayout()
        load_file_btn = QPushButton('+数据')
        self.review_table = QTableWidget()
        tip_label = QLabel('*请检查无误上传,提交后将不可更改.')
        submit_btn = QPushButton("提交")
        # widget style
        tip_label.setStyleSheet('font-size:12px; color:rgb(255,10,10)')
        self.review_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.review_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # button signal
        load_file_btn.clicked.connect(self.read_new_finance)
        submit_btn.clicked.connect(self.submit_finance)
        # add layout
        layout.addWidget(load_file_btn, alignment=Qt.AlignLeft)
        layout.addWidget(self.review_table)
        layout.addWidget(tip_label)
        layout.addWidget(submit_btn, alignment=Qt.AlignRight)
        self.setLayout(layout)

    def read_new_finance(self):
        # upload data to review table
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.xlsx *.xls)")
        if not file_path:
            return
        rf = xlrd.open_workbook(filename=file_path)
        sheet1 = rf.sheet_by_index(0)
        row_header = sheet1.row_values(0)
        # excel file header match
        header_labels = ["日期", "时间", "地区", "事件描述", "预期值"]
        if row_header != header_labels:
            return
        # table initial
        self.review_table.setRowCount(sheet1.nrows - 1)
        self.review_table.setColumnCount(len(header_labels))
        self.review_table.setHorizontalHeaderLabels(header_labels)
        for row in range(1, sheet1.nrows):  # skip header
            row_content = sheet1.row_values(row)
            row_content[0] = datetime.datetime.strftime(xlrd.xldate_as_datetime(row_content[0], rf.datemode), "%Y-%m-%d")
            row_content[1] = datetime.datetime.strftime(xlrd.xldate_as_datetime(row_content[1], rf.datemode), "%H:%M")
            # data to review table
            for col, col_data in enumerate(row_content):
                item = QTableWidgetItem(str(col_data))
                item.setTextAlignment(132)
                self.review_table.setItem(row - 1, col, item)

    def submit_finance(self):
        # submit commodity
        data = []
        header_labels = ["date", "time", "country", "event", "expected"]
        for row in range(self.review_table.rowCount()):
            item = dict()
            for col in range(len(header_labels)):
                col_item = self.review_table.item(row, col)
                if not col_item or not col_item.text():
                    continue
                item[header_labels[col]] = col_item.text()
            # 验证信息
            for key in header_labels:
                if len(item) > 1 and not item.get(key):
                    QMessageBox.warning(self, "错误", "请将信息填写完整!", QMessageBox.Yes)
                    return
            if len(item) >= 5:
                data.append(item)
        if not data:
            QMessageBox.warning(self, "错误", "您未填写任何信息!", QMessageBox.Yes)
            return
        self.review_table.clear()
        self.review_table.setRowCount(0)
        self.review_table.setHorizontalHeaderLabels(["品种", "地区", "等级", "报价", "时间", "备注"])
        self.new_data_signal.emit(data)


class CreateNewNotice(QDialog):
    new_data_signal = pyqtSignal(dict)
    def __init__(self):
        super(CreateNewNotice, self).__init__()
        layout = QGridLayout()
        # labels
        name_label = QLabel("名称：")
        type_label = QLabel("类型：")
        file_label = QLabel("文件：")
        # edits
        self.name_edit = QLineEdit()
        self.file_edit = QLineEdit()
        # combo
        self.type_combo = QComboBox()
        self.type_combo.addItems(["交易所", "公司", "系统", "其他"])
        # buttons
        select_file_btn = QPushButton('选择')
        submit_btn = QPushButton('提交')
        # styles
        select_file_btn.setMaximumWidth(30)
        # signal
        select_file_btn.clicked.connect(self.select_file_clicked)
        submit_btn.clicked.connect(self.submit_notice)
        # add layout
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(self.name_edit, 0, 1, 1, 2)
        layout.addWidget(type_label, 1, 0)
        layout.addWidget(self.type_combo, 1, 1, 1, 2)
        layout.addWidget(file_label, 2, 0)
        layout.addWidget(self.file_edit, 2, 1)
        layout.addWidget(select_file_btn, 2, 2)
        layout.addWidget(submit_btn, 3, 1, 1, 2)
        self.setLayout(layout)

    def select_file_clicked(self):
        # select file
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        file_name_list = file_path.rsplit('/', 1)
        if not self.name_edit.text().strip(' '):
            self.name_edit.setText((file_name_list[1].rsplit('.', 1))[0])
        self.file_edit.setText(file_path)

    def submit_notice(self):
        type_dict = {
            "公司": "company",
            "交易所": "changelib",
            "系统": "system",
            "其他":"others"
        }
        # collect data
        title = self.name_edit.text().strip(' ')
        type_text = self.type_combo.currentText()
        file_path = self.file_edit.text()
        if not title:
            QMessageBox.warning(self, "错误", "请起一个名字!", QMessageBox.Yes)
            return
        if not type_text:
            QMessageBox.warning(self, "错误", "请选择报告类型!", QMessageBox.Yes)
            return
        if not file_path:
            QMessageBox.warning(self, "错误", "请选择报告文件!", QMessageBox.Yes)
            return
        self.new_data_signal.emit({
            'title': title,
            'type_zh': type_text,
            'type_en': type_dict.get(type_text, None),
            'file_path': file_path
        })


class CreateNewReport(QDialog):
    new_data_signal = pyqtSignal(dict)

    def __init__(self):
        super(CreateNewReport, self).__init__()
        layout = QGridLayout()
        # labels
        title_label = QLabel("名称：")
        type_label = QLabel("类型：")
        file_label = QLabel("文件：")
        # edits
        self.name_edit = QLineEdit()
        self.file_edit = QLineEdit()
        # combo
        self.type_combo = QComboBox()
        self.type_combo.addItems(["日报", "周报", "月报", "年报", "专题", "投资报告", "其他"])
        # buttons
        select_file_btn = QPushButton('选择')
        submit_btn = QPushButton('提交')
        # styles
        select_file_btn.setMaximumWidth(30)
        # signal
        select_file_btn.clicked.connect(self.select_file_clicked)
        submit_btn.clicked.connect(self.submit_report)
        # add layout
        layout.addWidget(title_label, 0, 0)
        layout.addWidget(self.name_edit, 0, 1, 1,2)
        layout.addWidget(type_label, 1, 0)
        layout.addWidget(self.type_combo, 1, 1, 1,2)
        layout.addWidget(file_label, 2, 0)
        layout.addWidget(self.file_edit, 2, 1)
        layout.addWidget(select_file_btn, 2,2)
        layout.addWidget(submit_btn, 3, 1, 1,2)
        self.setLayout(layout)

    def select_file_clicked(self):
        # select file
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        file_name_list = file_path.rsplit('/', 1)
        if not self.name_edit.text().strip(' '):
            self.name_edit.setText((file_name_list[1].rsplit('.', 1))[0])
        self.file_edit.setText(file_path)

    def submit_report(self):
        type_dict = {
            "日报": "daily",
            "周报": "weekly",
            "月报": "monthly",
            "年报": "annual",
            "专题": "special",
            "投资报告": "invest",
            "其他": "others"
        }
        # collect data
        title = self.name_edit.text().strip(' ')
        type_text = self.type_combo.currentText()
        file_path = self.file_edit.text()
        if not title:
            QMessageBox.warning(self, "错误", "请起一个名字!", QMessageBox.Yes)
            return
        if not type_text:
            QMessageBox.warning(self, "错误", "请选择报告类型!", QMessageBox.Yes)
            return
        if not file_path:
            QMessageBox.warning(self, "错误", "请选择报告文件!", QMessageBox.Yes)
            return
        self.new_data_signal.emit({
            'title': title,
            'type_zh': type_text,
            'type_en': type_dict.get(type_text, None),
            'file_path': file_path
        })


