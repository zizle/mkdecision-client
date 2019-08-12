# _*_ coding:utf-8 _*_
"""

Create: 2019-08-02
Author: zizle
"""
import json
import requests
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox, QTextEdit, QFileDialog
from PyQt5.QtCore import pyqtSignal, Qt

import config
from utils import text_content_handler, get_desktop_path

class CreateNewMenu(QDialog):
    new_data_signal = pyqtSignal(dict)
    def __init__(self, *args):
        super(CreateNewMenu, self).__init__(*args)
        layout = QGridLayout()
        # labels
        name_label = QLabel('名称：')
        parent_label = QLabel('父级：')
        # edit
        self.name_edit = QLineEdit()
        # combo
        self.parent_combo = QComboBox()
        self.parent_combo.addItem('')
        # submit
        submit_btn = QPushButton('提交')
        # signal
        submit_btn.clicked.connect(self.submit_menu)
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(self.name_edit, 0, 1)
        layout.addWidget(parent_label, 1, 0)
        layout.addWidget(self.parent_combo, 1, 1)
        layout.addWidget(submit_btn, 2, 1)
        self.setLayout(layout)
        # get parent module name
        self.get_parent_module()
        # show message
        self.message = QLabel('正在创建...', self)
        self.message.setStyleSheet('background-color:rgb(200,200,200)')
        self.message.setAlignment(Qt.AlignCenter)
        self.message.move(50, 5)
        self.message.hide()

    def get_parent_module(self):
        try:
            response = requests.get(
                url=config.SERVER_ADDR + 'pservice/module/',  # query param parent=None
                headers=config.CLIENT_HEADERS,
                data=json.dumps({'machine_code':config.app_dawn.value('machine')}),
                cookies=config.app_dawn.value('cookies')
            )
        except Exception as error:
            QMessageBox(self, "错误", str(error))
            return
        response_data = json.loads(response.content.decode('utf-8'))
        for item in response_data['data']:
            self.parent_combo.addItem(item['name'])


    def submit_menu(self):
        data = dict()
        name = self.name_edit.text().strip(' ')
        if not name:
            QMessageBox.information(self, "错误", "请填写名称.", QMessageBox.Yes)
            return
        data['name'] = name
        data['parent'] = self.parent_combo.currentText()
        self.message.show()
        self.new_data_signal.emit(data)


class CreateMessage(QDialog):
    new_data_signal = pyqtSignal(list)
    message_id = None
    def __init__(self, content=None, *args):
        super(CreateMessage, self).__init__(*args)
        self.content = content
        layout = QGridLayout()
        # labels
        title_label = QLabel('标题')
        author_label = QLabel('作者')
        content_label = QLabel('内容')
        # edits
        self.title_edit = QLineEdit()
        self.author_edit = QLineEdit()
        self.content_edit = QTextEdit()
        # submit
        submit_btn = QPushButton('提交')
        # signal
        submit_btn.clicked.connect(self.submit_message)
        # add layout
        layout.addWidget(title_label, 0, 0)
        layout.addWidget(self.title_edit, 0, 1)
        layout.addWidget(author_label, 1, 0)
        layout.addWidget(self.author_edit, 1, 1)
        layout.addWidget(content_label, 2, 0)
        layout.addWidget(self.content_edit, 2,1)
        layout.addWidget(submit_btn, 3, 1)
        self.setLayout(layout)

    def submit_message(self):
        # collection message content
        data = dict()
        data['title']= self.title_edit.text().strip(' ')
        data['author']= self.author_edit.text().strip(' ')
        data['content']= text_content_handler(self.content_edit.toPlainText())
        data['machine_code'] = config.app_dawn.value('machine')
        if self.message_id is not None:
            # update message, put method
            data['message_id'] = self.message_id
            self.new_data_signal.emit(['put', data])
        else:
            # create a new message, post method
            self.new_data_signal.emit(['post', data])

    def modify(self, title, author, content):
        self.title_edit.setText(title)
        self.author_edit.setText(author)
        self.content_edit.setText(content)


class CreateMLSFile(QDialog):
    new_data_signal = pyqtSignal(dict)
    def __init__(self, content=None, *args):
        super(CreateMLSFile, self).__init__(*args)
        self.content = content
        layout = QGridLayout()
        # labels
        title_label = QLabel('标题')
        file_label = QLabel('文件')
        # edits
        self.title_edit = QLineEdit()
        self.file_edit = QLineEdit()
        # button
        select_btn = QPushButton('浏览')
        submit_btn = QPushButton('提交')
        # signal
        select_btn.clicked.connect(self.file_selected)
        submit_btn.clicked.connect(self.submit)
        # style sheet
        self.title_edit.setPlaceholderText('展示标题(默认文件名)')
        select_btn.setFixedWidth(30)
        self.setMaximumWidth(400)
        layout.addWidget(title_label, 0, 0)
        layout.addWidget(self.title_edit, 0, 1, 1, 2)
        layout.addWidget(file_label, 1, 0)
        layout.addWidget(self.file_edit, 1, 1)
        layout.addWidget(select_btn, 1, 2)
        layout.addWidget(submit_btn, 2, 1, 1,2)
        self.setLayout(layout)

    def file_selected(self):
        # select file
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        self.file_edit.setText(file_path)
        title = self.title_edit.text().strip(' ')
        if not title:
            file_name_list = file_path.rsplit('/', 1)
            file_raw_name = file_name_list[1].rsplit('.', 1)[0]
            self.title_edit.setText(file_raw_name)

    def submit(self):
        data = dict()
        data['title'] = self.title_edit.text().strip(' ')
        data['file_path'] = self.file_edit.text()
        if not all([data['title'], data['file_path']]):
            return
        self.new_data_signal.emit(data)


class CreateTPSFile(CreateMLSFile):
    pass

class CreateRSRFile(CreateMLSFile):
    pass






