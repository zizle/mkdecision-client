# _*_ coding:utf-8 _*_
# __Author__： zizle
import os
import re
import json
import time
import hashlib
import requests
import datetime
from PIL import Image
from pandas import read_excel
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QLabel, QPushButton, QLineEdit, \
    QTextEdit, QFileDialog, QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem, QDateEdit, QHeaderView, QListWidget,\
    QProgressBar,QMessageBox, QTimeEdit
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, QRegExp, QTimer, QTime
from PyQt5.QtGui import QBrush, QColor, QRegExpValidator
from widgets.base import FileLineEdit
import settings


# 新增新闻
class CreateNewsPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateNewsPopup, self).__init__(*args, **kwargs)
        self.setFixedSize(300, 150)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("新闻公告")
        layout = QGridLayout()
        layout.setParent(self)
        layout.addWidget(QLabel("标题:", self), 0, 0)
        self.bulletin_title = QLineEdit(self)
        layout.addWidget(self.bulletin_title, 0, 1)
        layout.addWidget(QLabel("文件:", self), 1, 0)
        self.file_path_edit = FileLineEdit()
        self.file_path_edit.setParent(self)
        layout.addWidget(self.file_path_edit, 1, 1)
        self.commit_button = QPushButton("提交", self)
        self.commit_button.clicked.connect(self.upload_news)
        layout.addWidget(self.commit_button, 2, 0, 1, 2)
        self.setLayout(layout)


        # layout = QVBoxLayout()
        # category_select_layout = QHBoxLayout()
        # category_select_layout.addWidget(QLabel('显示类型:'), alignment=Qt.AlignLeft)
        # self.category_combo = QComboBox(currentIndexChanged=self.category_combo_selected)
        # category_select_layout.addWidget(self.category_combo)
        # # 错误提示
        # self.error_message_label = QLabel()
        # category_select_layout.addWidget(self.error_message_label)
        # category_select_layout.addStretch()
        # layout.addLayout(category_select_layout)
        # # 公告名称
        # title_layout = QHBoxLayout()
        # title_layout.addWidget(QLabel('公告名称:'))
        # self.news_title_edit = QLineEdit()
        # title_layout.addWidget(self.news_title_edit)
        # layout.addLayout(title_layout)
        #
        # # 文件选择
        # self.file_widget = QWidget(parent=self)
        # file_widget_layout = QHBoxLayout(margin=0)
        # self.file_path_edit = QLineEdit()
        # self.file_path_edit.setEnabled(False)
        # file_widget_layout.addWidget(QLabel('文件:'), alignment=Qt.AlignLeft)
        # file_widget_layout.addWidget(self.file_path_edit)
        # file_widget_layout.addWidget(QPushButton('浏览', clicked=self.browser_file))
        # self.file_widget.setLayout(file_widget_layout)
        # layout.addWidget(self.file_widget)
        # # 文字输入
        # self.text_widget = QWidget(parent=self)
        # text_widget_layout = QHBoxLayout(margin=0)
        # self.text_edit = QTextEdit()
        # text_widget_layout.addWidget(QLabel('内容:'), alignment=Qt.AlignLeft)
        # text_widget_layout.addWidget(self.text_edit)
        # self.text_widget.setLayout(text_widget_layout)
        # layout.addWidget(self.text_widget)
        # # 提交按钮
        # self.commit_button = QPushButton('确认提交', clicked=self.commit_news_bulletin)
        # layout.addWidget(self.commit_button)
        # layout.addStretch()
        # self.setLayout(layout)
        # self.setWindowTitle('新增公告')
        # self._addCategoryCombo()

    # 类型选择的内容
    def _addCategoryCombo(self):
        for item in [(u'上传文件', 'file'), (u'上传内容', 'content')]:
            self.category_combo.addItem(item[0], item[1])

    # 确认上传新闻公告
    def commit_news_bulletin(self):
        self.commit_button.setEnabled(False)
        # 获取上传的类型
        category = self.category_combo.currentData()
        title = re.sub(r'\s+', '', self.news_title_edit.text())
        if not title:
            self.error_message_label.setText('请输入公告名称!')
            return
        data = dict()
        data['title'] = title  # 标题
        if category == 'file':  # 上传文件
            file_path = self.file_path_edit.text()
            if not file_path:
                self.error_message_label.setText('请选择文件!')
                return
            file_name = file_path.rsplit('/', 1)[1]
            file = open(file_path, "rb")   # 获取文件
            file_content = file.read()
            file.close()
            # 文件内容字段
            data["file"] = (file_name, file_content)
        else:
            data['content'] = self.text_edit.toPlainText()
        encode_data = encode_multipart_formdata(data)
        final_data = encode_data[0]
        self.upload_news(data=final_data, content_type=encode_data[1])

    # 选择了显示的样式
    def category_combo_selected(self):
        current_category = self.category_combo.currentData()
        self.news_title_edit.clear()
        if current_category == 'file':
            self.text_widget.hide()
            self.file_widget.show()
        else:
            self.text_widget.show()
            self.file_widget.hide()

    # 选择上传的文件
    def browser_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files(*.pdf)")
        self.file_path_edit.setText(file_path)

    # 公告上传的请求
    def upload_news(self):
        self.commit_button.setEnabled(False)
        title = re.sub(r'\s+', '', self.bulletin_title.text())
        if not title:
            QMessageBox.information(self, "错误", "标题不能为空!")
            return
        data = dict()
        data['bulletin_title'] = title  # 标题

        file_path = self.file_path_edit.text()
        if not file_path:
            QMessageBox.information(self, "错误", "请选择文件!")
            return
        file_name = file_path.rsplit('/', 1)[1]
        file = open(file_path, "rb")  # 获取文件
        file_content = file.read()
        file.close()
        data['utoken'] = settings.app_dawn.value('AUTHORIZATION')
        # 文件内容字段
        data["bulletin_file"] = (file_name, file_content)
        encode_data = encode_multipart_formdata(data)
        final_data = encode_data[0]
        try:
            # 发起上传请求
            r = requests.post(
                url=settings.SERVER_ADDR + 'bulletin/',
                headers={
                    'Content-Type': encode_data[1]
                },
                data=encode_data[0]
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, '错误', "上传数据错误!")
        else:
            QMessageBox.information(self, '错误', "上传成功!")
        finally:
            self.commit_button.setEnabled(True)
            self.close()


# 上传常规报告线程
class UploadReportThread(QThread):
    response_signal = pyqtSignal(int, bool)

    def __init__(self, file_list, machine_code, token, *args, **kwargs):
        super(UploadReportThread, self).__init__(*args, **kwargs)
        self.file_list = file_list
        self.machine_code = machine_code
        self.token = token

    def run(self):
        for file_item in self.file_list:
            # 读取文件
            try:
                data_file = dict()
                # 增加其他字段
                data_file['name'] = file_item['file_name']
                data_file['date'] = file_item['file_date']
                data_file['category_id'] = file_item['category_id']
                data_file['variety_ids'] = str(file_item['variety_ids'])
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
                    url=settings.SERVER_ADDR + 'home/normal-report/?mc=' + self.machine_code,
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
                with open('debug/normal_report.log', 'w') as f:
                    f.write(str(e) + '\n')
                self.response_signal.emit(file_item['row_index'], False)
            else:
                self.response_signal.emit(file_item['row_index'], True)


# 新增常规报告
class CreateReportPopup(QDialog):
    def __init__(self, variety_info, *args, **kwargs):
        super(CreateReportPopup, self).__init__(*args, **kwargs)
        self.setWindowTitle("新建报告")
        self.variety_info = variety_info
        # 总布局-左右
        layout = QHBoxLayout()
        # 左侧上下布局
        llayout = QVBoxLayout()
        # 左侧是品种树
        self.left_tree = QTreeWidget(clicked=self.variety_tree_clicked)
        self.left_tree.header().hide()
        self.left_tree.setMaximumWidth(160)
        llayout.addWidget(self.left_tree)
        layout.addLayout(llayout)
        # 右侧上下布局
        rlayout = QVBoxLayout(spacing=10)
        # 所属品种
        attach_varieties_layout = QHBoxLayout()
        attach_varieties_layout.addWidget(QLabel('所属品种:'))
        self.attach_varieties = QLabel()
        self.attach_varieties.variety_ids = list()  # id字符串
        attach_varieties_layout.addWidget(self.attach_varieties)
        attach_varieties_layout.addStretch()
        attach_varieties_layout.addWidget(QPushButton('清空', objectName='deleteBtn', cursor=Qt.PointingHandCursor,
                                                      clicked=self.clear_attach_varieties), alignment=Qt.AlignRight)
        rlayout.addLayout(attach_varieties_layout)
        # 所属分类
        attach_category_layout = QHBoxLayout()
        attach_category_layout.addWidget(QLabel('所属分类:'))
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(400)
        attach_category_layout.addWidget(self.category_combo)
        attach_category_layout.addStretch()
        rlayout.addLayout(attach_category_layout)
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("报告日期:", self))
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        rlayout.addLayout(date_layout)
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel('报告标题:', self))
        self.title_edit = QLineEdit(self)
        title_layout.addWidget(self.title_edit)
        rlayout.addLayout(title_layout)
        # 选择报告
        select_report_layout = QHBoxLayout()
        select_report_layout.addWidget(QLabel('报告文件:', self))
        self.report_file_edit = FileLineEdit()
        self.report_file_edit.setParent(self)
        select_report_layout.addWidget(self.report_file_edit)
        rlayout.addLayout(select_report_layout)
        # 提交按钮
        self.commit_button = QPushButton('提交', clicked=self.commit_upload_report)
        rlayout.addWidget(self.commit_button, alignment=Qt.AlignRight)
        rlayout.addStretch()
        layout.addLayout(rlayout)
        self.setLayout(layout)
        self.setFixedSize(800, 500)
        self.setStyleSheet("""
        #deleteBtn{
            border: none;
            color:rgb(200,100,80)
        }
        #newCategoryBtn{
            border:none;
            color:rgb(80,100,200)
        }
        """)
        self.geTreeVarieties()
        for category_item in [("日报", 1), ("周报", 2), ("月报", 3), ("年报", 4), ("专题报告", 5), ("其他", 0)]:
            self.category_combo.addItem(category_item[0], category_item[1])

    def geTreeVarieties(self):
        # 填充品种树
        for group_item in self.variety_info:
            group = QTreeWidgetItem(self.left_tree)
            group.setText(0, group_item['name'])
            group.gid = group_item['id']
            # 添加子节点
            for variety_item in group_item['subs']:
                child = QTreeWidgetItem()
                child.setText(0, variety_item['name'])
                child.vid = variety_item['id']
                group.addChild(child)
        self.left_tree.expandAll()  # 展开所有

    # 清空所属品种
    def clear_attach_varieties(self):
        self.attach_varieties.setText('')
        self.attach_varieties.variety_ids.clear()  # id列表

    def commit_upload_report(self):
        data = dict()
        title = self.title_edit.text()
        file_path = self.report_file_edit.text()
        if not all([title, file_path]):
            QMessageBox.information(self, "错误", "请填写完整信息")
            return
        data['utoken'] = settings.app_dawn.value('AUTHORIZATION')
        data['title'] = title
        data['link_varieties'] = ','.join(map(str, self.attach_varieties.variety_ids))
        data["custom_time"] = self.date_edit.text()
        data['category'] = self.category_combo.currentData()
        # 读取文件
        file = open(file_path, "rb")
        file_content = file.read()
        file.close()
        filename = file_path.rsplit('/', 1)[1]
        # 文件内容字段
        data["report_file"] = (filename,file_content)
        encode_data = encode_multipart_formdata(data)
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'report/',
                headers={"Content-Type": encode_data[1]},
                data=encode_data[0]
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, "错误", str(e))
        else:
            QMessageBox.information(self, "成功", "添加报告成功")
            self.close()




    # 点击左侧品种树
    def variety_tree_clicked(self):
        item = self.left_tree.currentItem()
        if item.childCount():  # has children open the root
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        text = item.text(0)
        if item.parent() and item.vid not in self.attach_varieties.variety_ids:  # 所属品种中增加当前品种
            self.attach_varieties.setText(self.attach_varieties.text() + text + '、')
            self.attach_varieties.variety_ids.append(item.vid)

# 新增常规报告
class CreateReportPopup1(QDialog):
    def __init__(self, variety_info, *args, **kwargs):
        super(CreateReportPopup, self).__init__(*args, **kwargs)
        self.variety_info = variety_info
        # 总布局-左右
        layout = QHBoxLayout()
        # 左侧上下布局
        llayout = QVBoxLayout()
        # 左侧是品种树
        self.left_tree = QTreeWidget(clicked=self.variety_tree_clicked)
        self.left_tree.header().hide()
        self.left_tree.setMaximumWidth(160)
        llayout.addWidget(self.left_tree)
        layout.addLayout(llayout)
        # 右侧上下布局
        rlayout = QVBoxLayout()
        # 所属品种
        attach_varieties_layout = QHBoxLayout()
        attach_varieties_layout.addWidget(QLabel('所属品种:'))
        self.attach_varieties = QLabel()
        self.attach_varieties.variety_ids = list()  # id字符串
        attach_varieties_layout.addWidget(self.attach_varieties)
        attach_varieties_layout.addStretch()
        attach_varieties_layout.addWidget(QPushButton('清空', objectName='deleteBtn', cursor=Qt.PointingHandCursor, clicked=self.clear_attach_varieties), alignment=Qt.AlignRight)
        rlayout.addLayout(attach_varieties_layout)
        rlayout.addWidget(QLabel(parent=self, objectName='varietyError'))
        # 所属分类
        attach_category_layout = QHBoxLayout()
        attach_category_layout.addWidget(QLabel('所属分类:'))
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(400)
        attach_category_layout.addWidget(self.category_combo)
        attach_category_layout.addStretch()
        # attach_category_layout.addWidget(QPushButton('新分类?', objectName='newCategoryBtn', cursor=Qt.PointingHandCursor, clicked=self.add_new_category), alignment=Qt.AlignRight)
        rlayout.addLayout(attach_category_layout)
        rlayout.addWidget(QLabel(parent=self, objectName='categoryError'))
        # 选择报告
        rlayout.addWidget(QPushButton('选择报告', clicked=self.select_reports), alignment=Qt.AlignLeft)
        # 预览表格
        self.review_table = QTableWidget()
        self.review_table.verticalHeader().hide()
        rlayout.addWidget(self.review_table)
        # 提交按钮
        self.commit_button = QPushButton('提交', clicked=self.commit_upload_report)
        rlayout.addWidget(self.commit_button, alignment=Qt.AlignRight)
        layout.addLayout(rlayout)
        self.setLayout(layout)
        self.setMinimumWidth(800)
        self.setStyleSheet("""
        #deleteBtn{
            border: none;
            color:rgb(200,100,80)
        }
        #newCategoryBtn{
            border:none;
            color:rgb(80,100,200)
        }
        """)
        self.geTreeVarieties()
        for category_item in [("日报", 1),("周报", 2),("月报", 3),("年报", 4),("专题报告", 5),("其他", 0)]:
            self.category_combo.addItem(category_item[0], category_item[1])

    # 获取分类选框内容
    def getCategoryCombo(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/data-category/normal_report/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            self.category_combo.clear()
            for category_item in response['data']:
                self.category_combo.addItem(category_item['name'], category_item['id'])
            # 加入其它
            self.category_combo.addItem('其它', 0)

    # 清空所属品种
    def clear_attach_varieties(self):
        self.attach_varieties.setText('')
        self.attach_varieties.variety_ids.clear()  # id列表

    # 新增报告分类
    # def add_new_category(self):
    #     popup = QDialog(parent=self)
    #     def commit_new_category():
    #         print('提交新建分类')
    #         name = re.sub(r'\s+', '', popup.category_name_edit.text())
    #         if not name:
    #             popup.name_error_label.setText('请输入正确的分类名称!')
    #             return
    #         # 提交常规报告分类
    #         try:
    #             r = requests.post(
    #                 url=settings.SERVER_ADDR + 'home/data-category/normal_report/?mc=' + settings.app_dawn.value('machine'),
    #                 headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
    #                 data=json.dumps({'name': name})
    #             )
    #             response = json.loads(r.content.decode('utf-8'))
    #             if r.status_code != 201:
    #                 raise ValueError(response['message'])
    #         except Exception as e:
    #             popup.name_error_label.setText(str(e))
    #         else:
    #             # 重新获取填充分类选框
    #             self.getCategoryCombo()
    #             popup.close()
    #
    #     popup.setWindowTitle('新建分类')
    #     new_layout = QGridLayout()
    #     new_layout.addWidget(QLabel('名称:'), 0, 0)
    #     popup.category_name_edit = QLineEdit()
    #     new_layout.addWidget(popup.category_name_edit, 0, 1)
    #     popup.name_error_label = QLabel()
    #     new_layout.addWidget(popup.name_error_label, 1, 0, 1, 2)
    #     new_layout.addWidget(QPushButton('确定', clicked=commit_new_category), 2, 1)
    #     popup.setLayout(new_layout)
    #     if not popup.exec_():
    #         popup.deleteLater()
    #         del popup

    # 获取左侧品种树的品种内容
    def geTreeVarieties(self):
        # 填充品种树
        for group_item in self.variety_info:
            group = QTreeWidgetItem(self.left_tree)
            group.setText(0, group_item['name'])
            group.gid = group_item['id']
            # 添加子节点
            for variety_item in group_item['subs']:
                child = QTreeWidgetItem()
                child.setText(0, variety_item['name'])
                child.vid = variety_item['id']
                group.addChild(child)
        self.left_tree.expandAll()  # 展开所有


    # 点击左侧品种树
    def variety_tree_clicked(self):
        item = self.left_tree.currentItem()
        if item.childCount():  # has children open the root
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        text = item.text(0)
        if item.parent() and item.vid not in self.attach_varieties.variety_ids:  # 所属品种中增加当前品种
            self.attach_varieties.setText(self.attach_varieties.text() + text + '、')
            self.attach_varieties.variety_ids.append(item.vid)

    # 选择报告文件
    def select_reports(self):
        path_list, _ = QFileDialog.getOpenFileNames(self, '打开文件', '', "PDF files(*.pdf)")
        # 遍历报告文件填充预览表格与设置状态
        self.review_table.setRowCount(len(path_list))
        self.review_table.setColumnCount(4)
        self.review_table.setHorizontalHeaderLabels(['序号', '报告名', '报告日期', '状态'])
        self.review_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.review_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, file_path in enumerate(path_list):
            item_1 = QTableWidgetItem(str(row + 1))
            item_1.file_path = file_path
            item_1.setTextAlignment(Qt.AlignCenter)
            self.review_table.setItem(row, 0, item_1)
            file_name = file_path.rsplit('/', 1)[1]
            item_2 = QTableWidgetItem(file_name)
            item_2.setTextAlignment(Qt.AlignCenter)
            self.review_table.setItem(row, 1, item_2)
            # 日期控件
            date_edit = QDateEdit(QDate.currentDate())
            date_edit.setCalendarPopup(True)
            date_edit.setDisplayFormat('yyyy-MM-dd')
            self.review_table.setCellWidget(row, 2, date_edit)
            # 装态
            item_4 = QTableWidgetItem('等待上传')
            item_4.setTextAlignment(Qt.AlignCenter)
            self.review_table.setItem(row, 3, item_4)

    # 确认上传报告
    def commit_upload_report(self):
        self.commit_button.setEnabled(False)
        # 获取所属品种列表id
        attach_variety_ids = self.attach_varieties.variety_ids
        if not attach_variety_ids:
            self.findChild(QLabel, 'varietyError').setText('请选择所属品种(支持多选)')
            return
        # 获取所属分类
        attach_category = self.category_combo.currentData()
        # 遍历表格打包文件信息(上传线程处理，每上传一个发个信号过来修改上传状态)
        file_message_list = list()
        for row in range(self.review_table.rowCount()):
            message_item = self.review_table.item(row, 3)  # 设置上传状态
            message_item.setText('正在上传...')
            message_item.setForeground(QBrush(QColor(20, 50, 200)))
            # 设置颜色
            file_message_list.append({
                'file_name': self.review_table.item(row, 1).text(),
                'file_path': self.review_table.item(row, 0).file_path,
                'category_id': attach_category,
                'variety_ids': attach_variety_ids,
                'file_date': self.review_table.cellWidget(row, 2).text(),
                'row_index': row
            })
        # 开启线程
        if hasattr(self, 'uploading_thread'):
            del self.uploading_thread
        self.uploading_thread = UploadReportThread(
            file_list=file_message_list,
            machine_code=settings.app_dawn.value('machine'),
            token=settings.app_dawn.value('AUTHORIZATION'),
        )
        self.uploading_thread.finished.connect(self.uploading_thread.deleteLater)
        self.uploading_thread.response_signal.connect(self.change_loading_state)
        self.uploading_thread.start()

    # 上传的线程返回消息
    def change_loading_state(self, row, succeed):
        item = self.review_table.item(row, 3)
        if succeed:
            item.setText('上传成功!')
            item.setForeground(QBrush(QColor(20, 200, 50)))
        else:
            item.setText('上传失败...')
            item.setForeground(QBrush(QColor(200, 20, 50)))
        if row == self.review_table.rowCount() - 1:
            self.commit_button.setEnabled(True)


# 上传交易通知线程
class UploadTransactionNoticeThread(QThread):
    response_signal = pyqtSignal(int, bool)

    def __init__(self, file_list, machine_code, token, *args, **kwargs):
        super(UploadTransactionNoticeThread, self).__init__(*args, **kwargs)
        self.file_list = file_list
        self.machine_code = machine_code
        self.token = token

    def run(self):
        for file_item in self.file_list:
            # 读取文件
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
                    url=settings.SERVER_ADDR + 'home/transaction_notice/?mc=' + self.machine_code,
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
                with open('debug/home_notice.log', 'w') as f:
                    f.write(str(e) + '\n')
                self.response_signal.emit(file_item['row_index'], False)
            else:
                self.response_signal.emit(file_item['row_index'], True)


# 新增交易通知
class CreateTransactionNoticePopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateTransactionNoticePopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFixedSize(400, 150)
        self.setWindowTitle("新增通知")
        layout = QVBoxLayout(self)
        title_layout = QHBoxLayout(self)
        title_layout.addWidget(QLabel("通知标题:", self))
        self.title_edit = QLineEdit(self)
        title_layout.addWidget(self.title_edit)
        layout.addLayout(title_layout)
        category_layout = QHBoxLayout(self)
        category_layout.addWidget(QLabel("所属分类:", self))
        self.category_combobox = QComboBox(self)
        for category_item in [(1,"交易所"), (2,"公司"), (3, "系统"), (0, "其他")]:
            self.category_combobox.addItem(category_item[1], category_item[0])
        category_layout.addWidget(self.category_combobox)
        self.category_combobox.setMinimumWidth(200)
        category_layout.addStretch()
        layout.addLayout(category_layout)
        file_layout = QHBoxLayout(self)
        self.file_edit = FileLineEdit()
        self.file_edit.setParent(self)
        file_layout.addWidget(QLabel('通知文件:'))
        file_layout.addWidget(self.file_edit)
        layout.addLayout(file_layout)
        self.commit_button = QPushButton("提交", self)
        self.commit_button.clicked.connect(self.commit_new_notice)
        layout.addWidget(self.commit_button, alignment=Qt.AlignRight)
        self.setLayout(layout)

    def commit_new_notice(self):
        data = dict()
        title = self.title_edit.text().strip()
        file_path = self.file_edit.text()
        if not all([title, file_path]):
            QMessageBox.information(self, "错误", "请填写完整信息")
            return
        data['utoken'] = settings.app_dawn.value('AUTHORIZATION')
        data['title'] = title
        data['category'] = self.category_combobox.currentData()
        # 读取文件
        file = open(file_path, "rb")
        file_content = file.read()
        file.close()
        filename = file_path.rsplit('/', 1)[1]
        # 文件内容字段
        data["notice_file"] = (filename, file_content)
        encode_data = encode_multipart_formdata(data)
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'exnotice/',
                headers={"Content-Type": encode_data[1]},
                data=encode_data[0]
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, "错误", str(e))
        else:
            QMessageBox.information(self, "成功", "添加通知成功")
            self.close()


class EditSpotMessageWidget(QWidget):
    commit_successful = pyqtSignal()
    def __init__(self, *args, **kwargs):
        super(EditSpotMessageWidget, self).__init__(*args,**kwargs)
        layout = QVBoxLayout(self)
        date_layout = QHBoxLayout(self)
        date_layout.addWidget(QLabel("日期:", self))
        self.custom_time_edit = QDateEdit(QDate.currentDate(),parent=self)
        self.custom_time_edit.setCalendarPopup(True)
        self.custom_time_edit.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(self.custom_time_edit)
        date_layout.addStretch()
        layout.addLayout(date_layout)
        name_layout= QHBoxLayout(self)
        name_layout.addWidget(QLabel("名称:", self))
        self.name_edit = QLineEdit(self)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        area_layout = QHBoxLayout(self)
        area_layout.addWidget(QLabel("地区:", self))
        self.area_edit = QLineEdit(self)
        area_layout.addWidget(self.area_edit)
        layout.addLayout(area_layout)
        level_layout = QHBoxLayout(self)
        level_layout.addWidget(QLabel("等级:", self))
        self.level_edit = QLineEdit(self)
        level_layout.addWidget(self.level_edit)
        layout.addLayout(level_layout)
        price_layout = QHBoxLayout(self)
        price_layout.addWidget(QLabel("价格:", self))
        self.price_edit = QLineEdit(self)
        decimal_validator = QRegExpValidator(QRegExp(r"[-]{0,1}[0-9]+[.]{1}[0-9]+"))
        self.price_edit.setValidator(decimal_validator)
        price_layout.addWidget(self.price_edit)
        layout.addLayout(price_layout)
        increase_layout = QHBoxLayout(self)
        increase_layout.addWidget(QLabel("增减:", self))
        self.increase_edit = QLineEdit(self)
        self.increase_edit.setValidator(decimal_validator)
        increase_layout.addWidget(self.increase_edit)
        layout.addLayout(increase_layout)
        self.commit_button = QPushButton("确认提交", self)
        self.commit_button.clicked.connect(self.commit_spot)
        layout.addWidget(self.commit_button, alignment=Qt.AlignRight)
        self.setLayout(layout)

    def commit_spot(self):
        date = self.custom_time_edit.text()
        name = self.name_edit.text().strip()
        area = self.area_edit.text().strip()
        level = self.level_edit.text().strip()
        price = self.price_edit.text().strip()
        increase = self.increase_edit.text().strip()
        if not all([name,level,price]):
            QMessageBox.information(self, "错误", "请填写完整信息")
            return
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'spot/',
                headers={"Content-Type":"application/json;charset=utf8"},
                data=json.dumps({
                    'utoken': settings.app_dawn.value('AUTHORIZATION'),
                    'custom_time': date,
                    'name':name,
                    'area':area,
                    'level':level,
                    'price':price,
                    'increase':increase
                })
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 201:
                raise ValueError(response['message'])

        except Exception as e:
            QMessageBox.information(self,'错误', str(e))
        else:

            QMessageBox.information(self, "成功",response['message'])
            self.commit_successful.emit()


# 新增现货报表
class CreateNewSpotTablePopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateNewSpotTablePopup, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(self)
        self.setFixedSize(300, 280)
        self.setWindowTitle("现货数据")
        self.setAttribute(Qt.WA_DeleteOnClose)
        title_layout = QHBoxLayout(self)
        title_layout.addStretch()
        title_layout.addWidget(QPushButton("模板下载", self, objectName='downloadModel', clicked=self.download_model_file))
        title_layout.addWidget(QPushButton("批量上传", self, objectName='uploadfile', clicked=self.upload_file))
        layout.addLayout(title_layout)
        self.edit_widget = EditSpotMessageWidget()
        self.edit_widget.setParent(self)
        self.edit_widget.commit_successful.connect(self.close)
        layout.addWidget(self.edit_widget)
        self.setLayout(layout)
        self.setStyleSheet("""
        #downloadModel{
            border: none;
            color:rgb(20,150,200)
        }
        #downloadModel:pressed{
            color: red;
        }
        #downloadModel:hover{
            color: rgb(20, 180, 200)
        }
        """)

    def upload_file(self):
        self.edit_widget.commit_button.setEnabled(False)
        self.edit_widget.commit_button.setText("处理文件")
        upload_file_path, _ = QFileDialog.getOpenFileName(self, '打开表格', '', "Excel file(*.xls *xlsx)")
        if upload_file_path:
            data = dict()
            data['utoken'] = settings.app_dawn.value('AUTHORIZATION')
            f = open(upload_file_path,'rb')
            file_content = f.read()
            f.close()
            filename = upload_file_path.rsplit('/',1)[1]
            data['spot_file'] = (filename, file_content)
            encode_data = encode_multipart_formdata(data)
            try:
                r = requests.post(
                    url=settings.SERVER_ADDR + 'spot/',
                    headers={"Content-Type": encode_data[1]},
                    data=encode_data[0]
                )
                response = json.loads(r.content.decode('utf8'))
                if r.status_code != 201:
                    raise ValueError(response['message'])
            except Exception as e:
                QMessageBox.information(self, "错误", str(e))
                self.edit_widget.commit_button.setEnabled(True)
                self.edit_widget.commit_button.setText("确认提交")
            else:
                QMessageBox.information(self, "成功", "上传数据成功")
                self.edit_widget.commit_button.setEnabled(True)
                self.edit_widget.commit_button.setText("确认提交")
                self.close()

    # 下载数据模板
    def download_model_file(self):
        directory = QFileDialog.getExistingDirectory(None, '保存到', os.getcwd())
        # 请求模板文件信息，保存
        try:
            r = requests.get(url=settings.SERVER_ADDR + 'model_files/?filename=spot_file_model.xlsx')
            save_path = os.path.join(directory, '现货报表模板.xlsx')
            if r.status_code != 200:
                raise ValueError('下载模板错误.')
            with open(save_path, 'wb') as f:
                f.write(r.content)
        except Exception as e:
            pass


class EditFinanceCalendarWidget(QWidget):
    def __init__(self):
        super(EditFinanceCalendarWidget, self).__init__()
        layout = QVBoxLayout(margin=0)
        layout.setParent(self)
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("日期:", self))
        self.date_edit = QDateEdit(QDate.currentDate(), self)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        layout.addLayout(date_layout)
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("时间:", self))
        self.time_edit = QTimeEdit(QTime.currentTime(),self)
        self.time_edit.setDisplayFormat('hh:mm:ss')
        time_layout.addWidget(self.time_edit)
        time_layout.addStretch()
        layout.addLayout(time_layout)
        area_layout = QHBoxLayout()
        area_layout.addWidget(QLabel('地区:', self))
        self.area_edit = QLineEdit(self)
        area_layout.addWidget(self.area_edit)
        layout.addLayout(area_layout)
        event_layout = QHBoxLayout()
        event_layout.addWidget(QLabel('事件:', self), alignment=Qt.AlignTop)
        self.event_edit = QTextEdit(self)
        self.event_edit.setFixedHeight(100)
        event_layout.addWidget(self.event_edit)
        layout.addLayout(event_layout)
        expected_layout = QHBoxLayout()
        expected_layout.addWidget(QLabel('预期值:', self))
        self.expected_edit = QLineEdit(self)
        expected_layout.addWidget(self.expected_edit)
        layout.addLayout(expected_layout)
        self.commit_button = QPushButton("提交", self)
        self.commit_button.clicked.connect(self.commit_financial_calendar)
        layout.addWidget(self.commit_button, alignment=Qt.AlignRight)
        self.setLayout(layout)

    def commit_financial_calendar(self):
        date = self.date_edit.text().strip()
        time = self.time_edit.text().strip()
        area = self.area_edit.text().strip()
        event = self.event_edit.toPlainText()
        expected = self.expected_edit.text().strip()

        if not all([date,time,area,event]):
            QMessageBox.information(self, "错误", "请填写完整信息")
            return
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'fecalendar/',
                headers={"Content-Type":"application/json;charset=utf8"},
                data=json.dumps({
                    'utoken': settings.app_dawn.value('AUTHORIZATION'),
                    'date': date,
                    'time':time,
                    'country':area,
                    'event':event,
                    'expected':expected,
                })
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self,'错误', str(e))
        else:

            QMessageBox.information(self, "成功",response['message'])

# 新增财经日历
class CreateNewFinanceCalendarPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateNewFinanceCalendarPopup, self).__init__(*args, **kwargs)
        self.setFixedSize(300, 280)
        self.setWindowTitle("财经日历")
        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QVBoxLayout()
        option_layout = QHBoxLayout()
        option_layout.addStretch()
        self.download_model_button = QPushButton("模板下载", self, objectName='downloadModel', clicked=self.download_model_file)
        option_layout.addWidget(self.download_model_button)
        self.option_button = QPushButton("批量上传", self, clicked=self.upload_file)
        option_layout.addWidget(self.option_button)
        layout.addLayout(option_layout)
        self.edit_widget = EditFinanceCalendarWidget()
        self.edit_widget.setParent(self)
        layout.addWidget(self.edit_widget)
        self.setLayout(layout)
        self.setStyleSheet("""
        #downloadModel{
            border: none;
            color:rgb(20,150,200)
        }
        #downloadModel:pressed{
            color: red;
        }
        #downloadModel:hover{
            color: rgb(20, 180, 200)
        }
        """)

    def upload_file(self):
        self.edit_widget.commit_button.setEnabled(False)
        self.edit_widget.commit_button.setText("处理文件")
        upload_file_path, _ = QFileDialog.getOpenFileName(self, '打开表格', '', "Excel file(*.xls *xlsx)")
        if upload_file_path:
            data = dict()
            data['utoken'] = settings.app_dawn.value('AUTHORIZATION')
            f = open(upload_file_path, 'rb')
            file_content = f.read()
            f.close()
            filename = upload_file_path.rsplit('/', 1)[1]
            data['fecalendar_file'] = (filename, file_content)
            encode_data = encode_multipart_formdata(data)
            try:
                r = requests.post(
                    url=settings.SERVER_ADDR + 'fecalendar/',
                    headers={"Content-Type": encode_data[1]},
                    data=encode_data[0]
                )
                response = json.loads(r.content.decode('utf8'))
                if r.status_code != 201:
                    raise ValueError(response['message'])
            except Exception as e:
                QMessageBox.information(self, "错误", str(e))
                self.edit_widget.commit_button.setEnabled(True)
                self.edit_widget.commit_button.setText("确认提交")
            else:
                QMessageBox.information(self, "成功", "上传数据成功")
                self.edit_widget.commit_button.setEnabled(True)
                self.edit_widget.commit_button.setText("确认提交")
                self.close()

    # 下载数据模板
    def download_model_file(self):
        directory = QFileDialog.getExistingDirectory(None, '保存到', os.getcwd())
        # 请求模板文件信息，保存
        try:
            r = requests.get(url=settings.SERVER_ADDR + 'model_files/?filename=finance_calendar_model.xlsx')
            save_path = os.path.join(directory, '财经日历模板.xlsx')
            if r.status_code != 200:
                raise ValueError('下载模板错误.')
            with open(save_path, 'wb') as f:
                f.write(r.content)
        except Exception as e:
            pass
