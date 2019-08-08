# _*_ coding:utf-8 _*_
"""

Create: 2019-08-02
Author: zizle
"""
import sys
import json
import requests
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor

import config
from utils import get_desktop_path
from thread.request import RequestThread
from piece.maintain import TableCheckBox
from popup.maintain.pservice import CreateNewMenu
from piece.maintain.pservice import ArticleEditTools

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












