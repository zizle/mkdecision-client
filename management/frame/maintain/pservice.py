# _*_ coding:utf-8 _*_
"""

Create: 2019-08-02
Author: zizle
"""
import sys
import json
import requests
from fitz.fitz import Document
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor

import config
from utils import get_desktop_path
from thread.request import RequestThread
from piece.base import PageController
from piece.maintain import TableCheckBox
from popup.maintain.base import UploadFile
from popup.maintain.pservice import CreateMessage, CreateMLSFile, CreateTPSFile, CreateRSRFile
from piece.maintain.pservice import ArticleEditTools
from widgets.maintain.base import ContentShowTable, TableShow
from widgets.base import Loading

class MessageCommMaintain(QWidget):
    def __init__(self):
        super(MessageCommMaintain, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        # widgets
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        self.table = QTableWidget()
        # signal
        create_btn.clicked.connect(self.create_new_msg_comm)
        # style
        self.table.verticalHeader().setVisible(False)
        # add to layout
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def create_new_msg_comm(self):
        def create_message(signal):
            try:
                response = requests.post(
                    url=config.SERVER_ADDR + 'pservice/consult/msg/',
                    data=json.dumps(signal[1]),
                    cookies=config.app_dawn.value('cookies')
                )
                response_data = json.loads(response.content.decode('utf-8'))
            except Exception as error:
                QMessageBox.information(popup, '错误', '创建失败.\n{}'.format(error), QMessageBox.Yes)
                return
            if response.status_code != 201:
                QMessageBox.information(popup, '错误', response_data['message'], QMessageBox.Yes)
                return
            QMessageBox.information(popup, '成功', '创建成功.赶紧刷新看看吧。', QMessageBox.Yes)
            popup.close()
        popup = CreateMessage()
        popup.new_data_signal.connect(create_message)
        if not popup.exec():
            del popup


class MarketAnalysisMaintain(QWidget):
    def __init__(self):
        super(MarketAnalysisMaintain, self).__init__()
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        # widgets
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        self.table = QTableWidget()
        # signal
        create_btn.clicked.connect(self.create_new_mks)
        # style
        self.table.verticalHeader().setVisible(False)
        # add to layout
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def create_new_mks(self):
        popup = UploadFile(url=config.SERVER_ADDR + 'pservice/consult/mks/')
        if not popup.exec():
            del popup










class MarketAnalysis(QScrollArea):
    def __init__(self):
        super(MarketAnalysis, self).__init__()
        self.popup = None
        self.setWidgetResizable(True)
        loading_layout = QHBoxLayout(self)
        self.loading = Loading()
        loading_layout.addWidget(self.loading)
        self.container = QWidget()
        layout = QVBoxLayout()
        option_layout = QHBoxLayout()
        create_btn = QPushButton('新增')
        refresh_btn = QPushButton('刷新')
        # show table
        self.show_table = TableShow()
        # paginator
        page_controller = PageController()
        option_layout.addWidget(create_btn)
        option_layout.addWidget(refresh_btn)
        option_layout.addStretch()
        # signal
        self.loading.clicked.connect(self.get_content_to_show)
        create_btn.clicked.connect(self.create_new_mls)
        refresh_btn.clicked.connect(self.get_content_to_show)
        self.show_table.cellClicked.connect(self.show_table_clicked)
        layout.addLayout(option_layout)
        layout.addWidget(self.show_table)
        layout.addWidget(page_controller, alignment=Qt.AlignCenter)
        self.container.setLayout(layout)
        self.get_content_to_show()

    def get_content_to_show(self):
        self.loading.show()
        self.show_table.clear()
        self.mls_thread = RequestThread(
            url=config.SERVER_ADDR + 'pservice/consult/file/?mark=mls',
            method='get',
            data=json.dumps({'machine_code': config.app_dawn.value('machine'), 'maintain': True}),
            cookies=config.app_dawn.value('cookies')
        )
        self.mls_thread.response_signal.connect(self.mls_thread_back)
        self.mls_thread.finished.connect(self.mls_thread.deleteLater)
        self.mls_thread.start()

    def mls_thread_back(self, content):
        print('frame.pservice.py {} 市场分析文件: '.format(sys._getframe().f_lineno), content)
        if content['error']:
            self.loading.retry()
            return
        if not content['data']:
            self.loading.no_data()
            return
        self.loading.hide()
        # fill show table
        header_couple = [
            ('serial_num', '序号'),
            ('create_time', '上传时间'),
            ('title', '标题'),
            ('is_active', '显示'),
            ('to_look', ' ')
        ]
        self.show_table.show_content(contents=content['data'], header_couple=header_couple)
        self.setWidget(self.container)

    def create_new_mls(self):
        self.popup = CreateMLSFile()
        self.popup.new_data_signal.connect(self.create_a_mls)
        if not self.popup.exec():
            self.popup = None

    def create_a_mls(self, signal):
        if not self.popup:
            return
        data = dict()
        # get file upload
        data['title'] = signal['title']
        data['mark'] = 'mls'
        data['machine_code'] = config.app_dawn.value('machine')
        file_raw_name = signal["file_path"].rsplit("/", 1)
        file = open(signal["file_path"], "rb")
        file_content = file.read()
        file.close()
        data["file"] = (file_raw_name[1], file_content)
        encode_data = encode_multipart_formdata(data)
        data = encode_data[0]
        headers = config.CLIENT_HEADERS
        headers['Content-Type'] = encode_data[1]
        try:
            response = requests.post(
                url=config.SERVER_ADDR + "pservice/consult/file/",
                headers=headers,
                data=data,
                cookies=config.app_dawn.value('cookies')
            )
            response_data = json.loads(response.content.decode('utf-8'))
        except Exception as error:
            QMessageBox.information(self, '提示', "发生了个错误!\n{}".format(error), QMessageBox.Yes)
            return
        if response.status_code != 201:
            QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
            return
        else:
            QMessageBox.information(self, '成功', '创建成功, 赶紧刷新看看吧.', QMessageBox.Yes)
            self.popup.close()  # close the dialog

    def show_table_clicked(self, row, col):
        print('piece.home.py {} 点击市场分析:'.format(str(sys._getframe().f_lineno)), row, col)
        if col == 4:
            item = self.show_table.item(row, col)
            try:
                response = requests.get(url=config.SERVER_ADDR + item.file, headers=config.CLIENT_HEADERS)
                doc = Document(filename=item.title, stream=response.content)
                popup = PDFReader(doc=doc, title=item.title)
            except Exception as error:
                QMessageBox.information(self, "错误", '查看文件失败.\n{}'.format(error), QMessageBox.Yes)
                return
            if not popup.exec():
                del popup


class MSGCommunication(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(MSGCommunication, self).__init__(*args, **kwargs)
        self.popup = None
        self.setWidgetResizable(True)
        # show loading data
        loading_layout = QHBoxLayout(self)
        self.loading = Loading()
        loading_layout.addWidget(self.loading)
        # content widget
        self.container = QWidget()
        layout = QVBoxLayout()
        option_layout = QHBoxLayout()
        create_btn = QPushButton('新增')
        refresh_btn = QPushButton('刷新')
        option_layout.addWidget(create_btn)
        option_layout.addWidget(refresh_btn)
        option_layout.addStretch()
        # a table to show message content
        self.show_table = ContentShowTable()
        # signal
        create_btn.clicked.connect(self.create_new_message)
        refresh_btn.clicked.connect(self.get_all_message)
        self.show_table.cellClicked.connect(self.show_table_clicked)
        layout.addLayout(option_layout)
        layout.addWidget(self.show_table)
        self.container.setLayout(layout)
        self.get_all_message()

    def create_new_message(self):
        self.popup = CreateMessage()
        self.popup.new_data_signal.connect(self.create_message)
        if not self.popup.exec():
            self.popup = None

    def create_message(self, signal):
        if not self.popup:
            return
        if signal[0] == 'put':
            try:
                response = requests.put(
                    url=config.SERVER_ADDR + 'pservice/consult/msg/',
                    data=json.dumps(signal[1]),
                    cookies=config.app_dawn.value('cookies')
                )
                response_data = json.loads(response.content.decode('utf-8'))
            except Exception as error:
                QMessageBox.information(self.popup, '错误', '更新失败.\n{}'.format(error), QMessageBox.Yes)
                return
            if response.status_code != 205:
                QMessageBox.information(self.popup, '错误', response_data['message'], QMessageBox.Yes)
                return
            QMessageBox.information(self.popup, '成功', '修改成功.', QMessageBox.Yes)
            self.popup.close()
        if signal[0] == 'post':
            try:
                response = requests.post(
                    url=config.SERVER_ADDR + 'pservice/consult/msg/',
                    data=json.dumps(signal[1]),
                    cookies=config.app_dawn.value('cookies')
                )
                response_data = json.loads(response.content.decode('utf-8'))
            except Exception as error:
                QMessageBox.information(self.popup, '错误', '创建失败.\n{}'.format(error), QMessageBox.Yes)
                return
            if response.status_code != 201:
                QMessageBox.information(self.popup, '错误', response_data['message'], QMessageBox.Yes)
                return
            QMessageBox.information(self.popup, '成功', '创建成功.', QMessageBox.Yes)
            self.popup.close()

    def get_all_message(self):
        self.loading.show()
        self.show_table.clear()
        self.msg_thread = RequestThread(
            url=config.SERVER_ADDR + 'pservice/consult/msg/',
            method='get',
            data=json.dumps({'machine_code': config.app_dawn.value('machine'), 'maintain': True}),
            cookies=config.app_dawn.value('cookies')
        )
        self.msg_thread.response_signal.connect(self.msg_thread_back)
        self.msg_thread.finished.connect(self.msg_thread.deleteLater)
        self.msg_thread.start()

    def msg_thread_back(self, content):
        print('frame.pservice.py {} 短信通数据: '.format(sys._getframe().f_lineno), content)
        if content['error']:
            self.loading.retry()
            return
        if not content['data']:
            self.loading.no_data()
            return
        self.loading.hide()
        # fill show table
        header_couple = [
            ('serial_num', '序号'),
            ('create_time', '上传时间'),
            ('title', '名称'),
            ('author', '作者'),
            ('is_active', '显示'),
            ('to_look', ' ')
        ]
        self.show_table.set_contents(contents=content['data'], header_couple=header_couple)
        self.setWidget(self.container)

    def show_table_clicked(self, row, col):
        if col == 5:
            item = self.show_table.item(row, col)
            title_item = self.show_table.item(row, 2)
            author_item = self.show_table.item(row, 3)
            self.popup = CreateMessage()
            self.popup.message_id = item.content_id
            self.popup.modify(title=title_item.text(), author=author_item.text(), content=item.content)
            self.popup.new_data_signal.connect(self.create_message)
            if not self.popup.exec():
                self.popup = None


class PServiceMenuInfo(QWidget):
    def __init__(self, *args, **kwargs):
        super(PServiceMenuInfo, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        action_layout = QHBoxLayout()
        create_btn = QPushButton("+新增")
        refresh_btn = QPushButton('刷新')
        create_btn.clicked.connect(self.create_new_menu)
        self.show_table = QTableWidget()
        # mount widget to show request message
        self.message_btn = QPushButton('刷新中...', self.show_table)
        self.message_btn.resize(100, 20)
        self.message_btn.move(100, 100)
        self.message_btn.setStyleSheet('text-align:center;border:none;background-color:rgb(210,210,210)')
        # style
        self.show_table.verticalHeader().setVisible(False)
        action_layout.addWidget(create_btn)
        action_layout.addWidget(refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.show_table)
        self.setLayout(layout)
        # get all menu
        self.get_all_menu()

    def create_new_menu(self):
        def upload_menu(signal):
            print('frame.maintain.home.py {} 新菜单:'.format(str(sys._getframe().f_lineno)), signal)
            data = dict()
            data['machine_code'] = config.app_dawn.value('machine')
            data['name'] = signal['name']
            data['parent'] = signal['parent']
            try:
                response = requests.post(
                    url=config.SERVER_ADDR + "pservice/module/",
                    headers=config.CLIENT_HEADERS,
                    data=json.dumps(data),
                    cookies=config.app_dawn.value('cookies')
                )
            except Exception as error:
                QMessageBox.information(self, '提示', "发生了个错误!\n{}".format(error), QMessageBox.Yes)
                popup.message.hide()
                return
            response_data = json.loads(response.content.decode('utf-8'))
            if response.status_code != 201:
                QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
                popup.message.hide()
                return
            else:
                QMessageBox.information(self, '成功', '添加成功, 赶紧刷新看看吧.', QMessageBox.Yes)
                popup.message.close()
                popup.close()  # close the dialog
        popup = CreateNewMenu()
        popup.new_data_signal.connect(upload_menu)
        if not popup.exec():
            del popup

    def get_all_menu(self):
        self.message_btn.setText('刷新中...')
        self.message_btn.show()
        self.message_btn.setEnabled(False)
        self.show_table.clear()
        self.show_table.setRowCount(0)
        self.show_table.horizontalHeader().setVisible(False)
        self.menu_thread = RequestThread(
            url=config.SERVER_ADDR + 'pservice/module/',
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"machine_code": config.app_dawn.value('machine'), "maintain": True}),
            cookies=config.app_dawn.value('cookies'),
        )
        self.menu_thread.finished.connect(self.menu_thread.deleteLater)
        self.menu_thread.response_signal.connect(self.menu_thread_back)
        self.menu_thread.start()

    def menu_thread_back(self, content):
        # fill show table
        print('frame.maintain.home.py {} 产品服务菜单: '.format(str(sys._getframe().f_lineno)), content)
        if content['error']:
            self.message_btn.setText('失败,请重试!')
            self.message_btn.setEnabled(True)
            return
        else:
            if not content['data']:
                self.message_btn.setText('完成,无数据.')
                return  # function finished
            else:
                self.message_btn.setText('刷新完成!')
                self.message_btn.hide()
        # fill table
        self.show_table.horizontalHeader().setVisible(True)
        try:
            keys = [
                ('serial_num', '序号'),
                ('create_time', '创建时间'),
                ('name', '名称'),
                ('parent', '父级'),
                ('is_active', '展示')
            ]
            notices = content['data']
            row = len(notices)
            self.show_table.setRowCount(row)
            self.show_table.setColumnCount(len(keys))  # 列数
            labels = []
            set_keys = []
            for key_label in keys:
                set_keys.append(key_label[0])
                labels.append(key_label[1])
            self.show_table.setHorizontalHeaderLabels(labels)
            self.show_table.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
            self.show_table.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
            for row in range(self.show_table.rowCount()):
                for col in range(self.show_table.columnCount()):
                    if col == 0:
                        item = QTableWidgetItem(str(row + 1))
                    else:
                        label_key = set_keys[col]
                        if label_key == 'is_active':
                            checkbox = TableCheckBox(row=row, col=col, option_label=label_key)
                            checkbox.setChecked(int(notices[row][label_key]))
                            checkbox.clicked_changed.connect(self.update_menu_info)
                            self.show_table.setCellWidget(row, col, checkbox)
                        item = QTableWidgetItem(str(notices[row][set_keys[col]]))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.menu_id = notices[row]['id']
                    self.show_table.setItem(row, col, item)
        except Exception as e:
            print(e)

    def update_menu_info(self, signal):
        item = self.show_table.item(signal['row'], signal['col'])
        show = '显示' if signal['checked'] else '不显示'
        print('frame.maintain.base.py {} 修改服务菜单：'.format(sys._getframe().f_lineno), item.menu_id, show)


class PersonTrain(QScrollArea):
    def __init__(self):
        super(PersonTrain, self).__init__()
        self.setWidgetResizable(True)
        container = QWidget()
        layout = QGridLayout()
        title_label = QLabel('标题')
        content_label = QLabel('内容')
        self.title_edit = QLineEdit()  # title
        tools = ArticleEditTools()
        self.content_edit = QTextEdit()
        self.submit_btn = QPushButton('提交')
        # signal
        tools.tool_clicked.connect(self.clicked_tools)
        self.submit_btn.clicked.connect(self.submit)
        layout.addWidget(title_label, 0, 0)
        layout.addWidget(self.title_edit, 0, 1)
        layout.addWidget(content_label, 1, 0)
        layout.addWidget(tools, 1, 1)
        layout.addWidget(self.content_edit, 2,1)
        layout.addWidget(self.submit_btn, 3, 1)
        container.setLayout(layout)
        self.setWidget(container)

    def clicked_tools(self, name):
        if name == 'image':
            # select image and upload server return image address
            desktop_path = get_desktop_path()
            file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "Image files (*.png)")
            if not file_path:
                return
            try:  # read image content and upload
                data = dict()
                image_raw_name = file_path.rsplit("/", 1)
                image = open(file_path, 'rb')
                image_content = image.read()
                image.close()
                data['file'] = (image_raw_name[1], image_content)
                data['machine_code'] = config.app_dawn.value('machine')
                data['file_type'] = 'image'
                print(data)
                encode_data = encode_multipart_formdata(data)
                data = encode_data[0]
                # print(data)
                headers = config.CLIENT_HEADERS
                headers['Content-Type'] = encode_data[1]
                response = requests.post(
                    url=config.SERVER_ADDR + "multimedia/",
                    headers=headers,
                    data=data,
                    cookies=config.app_dawn.value('cookies')
                )
            except Exception as error:
                QMessageBox.information('失败', '添加图片失败.{}'.format(error), QMessageBox.Yes)
                return
            response_data = json.loads(response.content.decode('utf-8'))
            if response.status_code != 201:
                QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
                return
            else:
                QMessageBox.information(self, '成功', '上传成功.', QMessageBox.Yes)
            # 读取图片路径
            image_addr = response_data['path']
            print(image_addr)
            image_element = '<image src='+ image_addr +'></image>'
            # 光标下移一行添加标签，再下移一行
            self.content_edit.moveCursor(QTextCursor.Down)
            self.content_edit.append(image_element)
            self.content_edit.moveCursor(QTextCursor.Down)
            self.content_edit.append('')
        else:
            return

    def submit(self):
        self.submit_btn.setEnabled(False)
        data = dict()
        title = self.title_edit.text().strip(' ')
        if not title:
            QMessageBox.information(self, '错误', '请起一个标题名', QMessageBox.Yes)
            return
        # handler content
        content_list = self.content_edit.toPlainText().strip(' ').split('\n')  # 去除前后空格和分出换行
        # 处理文本内容
        text_content = ""
        for line in content_list:
            if line.startswith('<image') and line.endswith('</image>'):
                text_content += line
            else:
                text_content += "<p>" + line + "</p>"
        data['title'] = title
        data['content'] = text_content
        data['machine_code'] = config.app_dawn.value('machine')
        data['mark'] = 'person_train'
        # upload
        try:
            response = requests.post(
                url=config.SERVER_ADDR + "pservice/adviser/pst/",  # person train
                headers=config.CLIENT_HEADERS,
                data=json.dumps(data),
                cookies=config.app_dawn.value('cookies')
            )
        except Exception as error:
            QMessageBox.information('失败', '提交失败.{}'.format(error), QMessageBox.Yes)
            self.submit_btn.setEnabled(True)
            return
        response_data = json.loads(response.content.decode('utf-8'))
        if response.status_code != 201:
            QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
            self.submit_btn.setEnabled(True)
            return
        else:
            QMessageBox.information(self, '成功', '新建文章成功.', QMessageBox.Yes)
            self.submit_btn.setEnabled(True)


class ResearchReport(MarketAnalysis):
    def get_content_to_show(self):
        self.loading.show()
        self.show_table.clear()
        self.rsr_thread = RequestThread(
            url=config.SERVER_ADDR + 'pservice/consult/file/?mark=rsr',
            method='get',
            data=json.dumps({'machine_code': config.app_dawn.value('machine'), 'maintain': True}),
            cookies=config.app_dawn.value('cookies')
        )
        self.rsr_thread.response_signal.connect(self.rsr_thread_back)
        self.rsr_thread.finished.connect(self.rsr_thread.deleteLater)
        self.rsr_thread.start()

    def rsr_thread_back(self, content):
        print('frame.pservice.py {} 调研报告文件: '.format(sys._getframe().f_lineno), content)
        if content['error']:
            self.loading.retry()
            return
        if not content['data']:
            self.loading.no_data()
            self.setWidget(self.container)
            return
        self.loading.hide()
        # fill show table
        header_couple = [
            ('serial_num', '序号'),
            ('create_time', '上传时间'),
            ('title', '标题'),
            ('is_active', '显示'),
            ('to_look', ' ')
        ]
        self.show_table.show_content(contents=content['data'], header_couple=header_couple)
        self.setWidget(self.container)

    def create_new_rsr(self):
        self.popup = CreateRSRFile()
        self.popup.new_data_signal.connect(self.create_a_rsr)
        if not self.popup.exec():
            self.popup = None

    def create_a_rsr(self, signal):
        if not self.popup:
            return
        data = dict()
        # get file upload
        data['title'] = signal['title']
        data['mark'] = 'rsr'
        data['machine_code'] = config.app_dawn.value('machine')
        file_raw_name = signal["file_path"].rsplit("/", 1)
        file = open(signal["file_path"], "rb")
        file_content = file.read()
        file.close()
        data["file"] = (file_raw_name[1], file_content)
        encode_data = encode_multipart_formdata(data)
        data = encode_data[0]
        headers = config.CLIENT_HEADERS
        headers['Content-Type'] = encode_data[1]
        try:
            response = requests.post(
                url=config.SERVER_ADDR + "pservice/consult/file/",
                headers=headers,
                data=data,
                cookies=config.app_dawn.value('cookies')
            )
            response_data = json.loads(response.content.decode('utf-8'))
        except Exception as error:
            QMessageBox.information(self, '提示', "发生了个错误!\n{}".format(error), QMessageBox.Yes)
            return
        if response.status_code != 201:
            QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
            return
        else:
            QMessageBox.information(self, '成功', '创建成功, 赶紧刷新看看吧.', QMessageBox.Yes)
            self.popup.close()  # close the dialog


class TopicalStudy(MarketAnalysis):

    def get_content_to_show(self):
        self.loading.show()
        self.show_table.clear()
        self.tps_thread = RequestThread(
            url=config.SERVER_ADDR + 'pservice/consult/file/?mark=tps',
            method='get',
            data=json.dumps({'machine_code': config.app_dawn.value('machine'), 'maintain': True}),
            cookies=config.app_dawn.value('cookies')
        )
        self.tps_thread.response_signal.connect(self.tps_thread_back)
        self.tps_thread.finished.connect(self.tps_thread.deleteLater)
        self.tps_thread.start()

    def tps_thread_back(self, content):
        print('frame.pservice.py {} 市场分析文件: '.format(sys._getframe().f_lineno), content)
        if content['error']:
            self.loading.retry()
            return
        if not content['data']:
            self.loading.no_data()
            self.setWidget(self.container)
            return
        self.loading.hide()
        # fill show table
        header_couple = [
            ('serial_num', '序号'),
            ('create_time', '上传时间'),
            ('title', '标题'),
            ('is_active', '显示'),
            ('to_look', ' ')
        ]
        self.show_table.show_content(contents=content['data'], header_couple=header_couple)
        self.setWidget(self.container)

    def create_new_tps(self):
        self.popup = CreateTPSFile()
        self.popup.new_data_signal.connect(self.create_a_tps)
        if not self.popup.exec():
            self.popup = None

    def create_a_tps(self, signal):
        if not self.popup:
            return
        data = dict()
        # get file upload
        data['title'] = signal['title']
        data['mark'] = 'tps'
        data['machine_code'] = config.app_dawn.value('machine')
        file_raw_name = signal["file_path"].rsplit("/", 1)
        file = open(signal["file_path"], "rb")
        file_content = file.read()
        file.close()
        data["file"] = (file_raw_name[1], file_content)
        encode_data = encode_multipart_formdata(data)
        data = encode_data[0]
        headers = config.CLIENT_HEADERS
        headers['Content-Type'] = encode_data[1]
        try:
            response = requests.post(
                url=config.SERVER_ADDR + "pservice/consult/file/",
                headers=headers,
                data=data,
                cookies=config.app_dawn.value('cookies')
            )
            response_data = json.loads(response.content.decode('utf-8'))
        except Exception as error:
            QMessageBox.information(self, '提示', "发生了个错误!\n{}".format(error), QMessageBox.Yes)
            return
        if response.status_code != 201:
            QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
            return
        else:
            QMessageBox.information(self, '成功', '创建成功, 赶紧刷新看看吧.', QMessageBox.Yes)
            self.popup.close()  # close the dialog












