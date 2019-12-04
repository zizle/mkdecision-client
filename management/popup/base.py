# _*_ coding:utf-8 _*_
# Author: zizle  QQ:462894999

import re
import fitz
import json
import requests
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QTextBrowser, QScrollArea, QVBoxLayout,\
    QWidget, QGridLayout
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

import config


# 登录弹窗
class LoginPopup(QDialog):
    user_listed = pyqtSignal(dict)  # 登录成功发出信号

    def __init__(self, *args, **kwargs):
        super(LoginPopup, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        # 手机
        phone_label = QLabel()
        phone_label.setPixmap(QPixmap('media/passport_icon/phone.png'))
        layout.addWidget(phone_label, 0, 0)
        # 填写手机
        self.phone_edit = QLineEdit()
        layout.addWidget(self.phone_edit, 0, 1)
        # 手机号错误提示框
        self.phone_error = QLabel()
        layout.addWidget(self.phone_error, 1, 0, 1, 2)
        # 密码
        password_label = QLabel()
        password_label.setPixmap(QPixmap('media/passport_icon/password.png'))
        layout.addWidget(password_label, 2, 0)
        # 填写密码
        self.password_edit = QLineEdit()
        layout.addWidget(self.password_edit, 2, 1)
        # 密码错误提示框
        self.password_error = QLabel()
        layout.addWidget(self.password_error, 3, 0, 1, 2)
        # 确认登录
        login_button = QPushButton('登录', clicked=self.commit_login)
        layout.addWidget(login_button, 4, 0, 1, 2)
        # 登录错误框
        self.login_error = QLabel()
        layout.addWidget(self.login_error, 5, 0, 1, 2)
        # 样式
        self.setWindowTitle('登录')
        phone_label.setFixedSize(36, 35)
        phone_label.setScaledContents(True)
        self.phone_edit.setFixedHeight(35)
        password_label.setScaledContents(True)
        password_label.setFixedSize(36, 35)
        self.password_edit.setFixedHeight(35)
        # 布局
        self.setLayout(layout)

    # 获取手机号和密码提交登录
    def commit_login(self):
        # 获取手机
        phone = self.phone_edit.text()
        phone = re.match(r'^[1][3-9][0-9]{9}$', phone)
        if not phone:
            self.phone_error.setText('请输入正确的手机号')
            return
        phone = phone.group()
        # 获取密码
        password = self.password_edit.text()
        password = re.sub(r'\s+', '', password)
        if not password:
            self.password_error.setText('请输入密码')
            return
        # 登录成功
        if self._login_post(phone, password):
            self.close()

    # 提交登录
    def _login_post(self, phone, password):
        try:
            r = requests.post(
                url=config.SERVER_ADDR + 'user/login/?mc=' + config.app_dawn.value('machine'),
                headers={
                    "AUTHORIZATION": config.app_dawn.value('AUTHORIZATION'),
                },
                data=json.dumps({
                    "phone": phone,
                    "password": password,
                }),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.login_error.setText(str(e))
            # 移除token
            config.app_dawn.remove('AUTHORIZATION')
            return False
        else:
            if response['data']:
                self.user_listed.emit(response['data'])
                return True
            else:
                return False


# 注册弹窗
class RegisterPopup(QDialog):
    user_registered = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(RegisterPopup, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        # 手机号
        phone_label = QLabel()
        phone_label.setPixmap(QPixmap('media/passport_icon/phone.png'))
        layout.addWidget(phone_label, 0, 0)
        # 填写手机
        self.phone_edit = QLineEdit()
        layout.addWidget(self.phone_edit, 0, 1)
        # 手机号错误提示框
        self.phone_error = QLabel()
        layout.addWidget(self.phone_error, 1, 0, 1, 2)
        # 用户名
        username_label = QLabel()
        username_label.setPixmap(QPixmap('media/passport_icon/username.png'))
        layout.addWidget(username_label, 2, 0)
        # 填写用户名
        self.username_edit = QLineEdit()
        layout.addWidget(self.username_edit, 2, 1)
        self.username_error = QLabel()
        layout.addWidget(self.username_error, 3, 0, 1, 2)
        # 密码
        password_label = QLabel()
        password_label.setPixmap(QPixmap('media/passport_icon/password.png'))
        layout.addWidget(password_label, 4, 0)
        # 填写密码
        self.password_edit = QLineEdit()
        layout.addWidget(self.password_edit, 4, 1)
        # 密码错误提示框
        self.password_error = QLabel()
        layout.addWidget(self.password_error, 5, 0, 1, 2)
        # 确认密码
        re_password_label = QLabel()
        re_password_label.setPixmap(QPixmap('media/passport_icon/password.png'))
        layout.addWidget(re_password_label, 6, 0)
        # 填写确认密码
        self.re_password_edit = QLineEdit()
        layout.addWidget(self.re_password_edit, 6, 1)
        # 确认密码错误提示框
        self.re_password_error = QLabel()
        layout.addWidget(self.re_password_error, 7, 0, 1, 2)
        # 注册
        register_button = QPushButton('立即注册', clicked=self.commit_register)
        layout.addWidget(register_button, 8, 0, 1, 2)
        # 注册错误框
        self.register_error = QLabel()
        layout.addWidget(self.register_error, 9, 0, 1, 2)
        # 样式
        self.setWindowTitle('注册')
        phone_label.setFixedSize(36, 35)
        phone_label.setScaledContents(True)
        self.phone_edit.setFixedHeight(35)
        username_label.setFixedSize(36, 35)
        self.username_edit.setFixedHeight(35)
        password_label.setScaledContents(True)
        password_label.setFixedSize(36, 35)
        self.password_edit.setFixedHeight(35)
        re_password_label.setScaledContents(True)
        re_password_label.setFixedSize(36, 35)
        self.re_password_edit.setFixedHeight(35)
        # 布局
        self.setLayout(layout)

    # 获取信息提交注册
    def commit_register(self):
        print('提交注册')
        # 获取手机
        phone = self.phone_edit.text()
        phone = re.match(r'^[1][3-9][0-9]{9}$', phone)
        if not phone:
            self.phone_error.setText('请输入正确的手机号')
            return
        phone = phone.group()
        # 用户名
        username = self.username_edit.text().strip()
        if username:
            username = re.match(r'^[\u4e00-\u9fa5_0-9a-z]{2,20}', username)
            if not username:
                self.username_error.setText('用户名需由中文、数字、字母及下划线组成,2-20个字符')
                return
            username = username.group()
        # 获取密码
        password = self.password_edit.text()
        password = re.sub(r'\s+', '', password)
        if not password or len(password) < 6:
            self.password_error.setText('密码至少为6位.')
            return
        # 确认密码
        re_password = self.re_password_edit.text()
        re_password = re.sub(r'\s+', '', re_password)
        if re_password != password:
            self.re_password_error.setText('两次输入密码不一致')
            return
        print('用户名:', username)
        print('手机:', phone)
        print('密码:', password)
        print('确认密码:', re_password)
        # 提交注册
        response_data = self._register_post(phone=phone, username=username, password=password)
        if response_data:
            # 注册成功
            self.user_registered.emit(response_data)
            self.close()

    # 提交注册
    def _register_post(self, phone, username, password):
        try:
            r = requests.post(
                url=config.SERVER_ADDR + 'user/register/?mc=' + config.app_dawn.value('machine'),
                data=json.dumps({
                    "phone": phone,
                    "username": username,
                    "password": password,
                }),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            self.register_error.setText(str(e))
            # 移除token
            return {}
        else:  # 注册成功
            return response['data']











class ShowHtmlContent(QDialog):
    def __init__(self, content="<p>没有内容</p>", title="内容"):
        super(ShowHtmlContent, self).__init__()
        layout = QVBoxLayout()
        text_browser = QTextBrowser()
        text_browser.setStyleSheet("font-size:14px;")
        text_browser.setHtml(content)
        layout.addWidget(text_browser)
        self.setWindowTitle(title)
        self.setLayout(layout)


class ShowServerPDF(QDialog):
    def __init__(self, file_url=None, file_name="查看PDF", *args):
        super(ShowServerPDF, self).__init__(*args)
        self.file = file_url
        self.file_name = file_name
        # auth doc type
        self.setWindowTitle(file_name)
        self.setMinimumSize(1000, 600)
        self.download = QPushButton("下载PDF")
        self.download.setIcon(QIcon('media/download-file.png'))
        self.setWindowIcon(QIcon("media/reader.png"))
        # scroll
        scroll_area = QScrollArea()
        scroll_area.horizontalScrollBar().setVisible(False)
        # content
        self.page_container = QWidget()
        self.page_container.setLayout(QVBoxLayout())
        layout = QVBoxLayout()
        # initial data
        self.add_pages()
        # add to show
        scroll_area.setWidget(self.page_container)
        # add layout
        layout.addWidget(self.download, alignment=Qt.AlignLeft)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def add_pages(self):
        # 请求文件
        if not self.file:
            message_label = QLabel('没有文件.')
            self.page_container.layout().addWidget(message_label)
            return
        try:
            response = requests.get(self.file)
            doc = fitz.Document(filename=self.file_name, stream=response.content)
        except Exception as e:
            message_label = QLabel('获取文件内容失败.\n{}'.format(e))
            self.page_container.layout().addWidget(message_label)
            return
        for page_index in range(doc.pageCount):
            page = doc.loadPage(page_index)
            page_label = QLabel()
            page_label.setMinimumSize(self.width() - 20, self.height())  # 设置label大小
            # show PDF content
            zoom_matrix = fitz.Matrix(1.58, 1.5)  # 图像缩放比例
            pagePixmap = page.getPixmap(
                matrix=zoom_matrix,
                alpha=False)
            imageFormat = QImage.Format_RGB888  # get image format
            pageQImage = QImage(
                pagePixmap.samples,
                pagePixmap.width,
                pagePixmap.height,
                pagePixmap.stride,
                imageFormat)  # init QImage
            page_map = QPixmap()
            page_map.convertFromImage(pageQImage)
            page_label.setPixmap(page_map)
            page_label.setScaledContents(True)  # pixmap resize with label
            self.page_container.layout().addWidget(page_label)

