# _*_ coding:utf-8 _*_
"""
public popups in project
Create: 2019-07-25
Author: zizle
"""
import re
import fitz
import json
import requests
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QCheckBox, QTextBrowser, QScrollArea, QVBoxLayout,\
    QWidget, QHBoxLayout, QGridLayout
from PyQt5.QtGui import QCursor, QIcon, QImage, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

import config
from piece.base import TitleBar


# 登录弹窗
class LoginPopup(QDialog):
    user_listed = pyqtSignal(str)

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
            # 保存token
            user_data = response['data']
            token = user_data['Authorization']
            config.app_dawn.setValue('AUTHORIZATION', token)
            # 发出信号
            sig_username = user_data['username']
            if not user_data['username']:
                phone = user_data['phone']
                sig_username = phone[0:3] + '****' + phone[7:11]
            self.user_listed.emit(sig_username)
            return True


# 注册弹窗
class RegisterPopup(QDialog):
    user_registered = pyqtSignal(str)

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
            if not re.match(r'^[\u4e00-\u9fa5_0-9a-z]{6,20}', username):
                self.username_error.setText('用户名需由中文、数字、字母及下划线组成,6-20个字符')
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
        user_data = self._register_post(phone=phone, username=username, password=password)
        print(user_data)
        try:
            if user_data:
                # 注册成功
                # 保存token
                token = user_data['Authorization']
                config.app_dawn.setValue('AUTHORIZATION', token)
                # 发出信号
                sig_username = user_data['username']
                if not user_data['username']:
                    phone = user_data['phone']
                    sig_username = phone[0:3] + '****' + phone[7:11]
                self.user_registered.emit(sig_username)
                self.close()
        except Exception as e:
            print(e)

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
        else:  # 登录成功
            return response['data']





class Register(QDialog):
    """注册弹窗"""
    button_click_signal = pyqtSignal(str)
    login_signal = pyqtSignal(str)

    def __init__(self):
        super(Register, self).__init__()
        self.resize(490, 400)
        # 设置无边框
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 添加个head
        title_bar = TitleBar(self)
        self.setWindowTitle("注册")
        title_bar.setTitle("注册账号")
        title_bar.setGeometry(0, 0, 490, 50)
        # 按钮处理
        title_bar.buttonMinimum.hide()
        title_bar.buttonMaximum.hide()
        title_bar.buttonClose.setCursor(QCursor(Qt.PointingHandCursor))
        title_bar.windowClosed.connect(self.close)
        title_bar.windowMoved.connect(self.move)
        self.windowIconChanged.connect(title_bar.setIcon)
        self.setWindowIcon(QIcon("media/logo.png"))
        # 手机号
        account_label = QLabel("手机：", self)
        account_label.setGeometry(75, 100, 60, 36)
        account_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        self.account_edit = QLineEdit(self)
        self.account_edit.setPlaceholderText("请输入手机号")
        self.account_edit.setCursor(QCursor(Qt.PointingHandCursor))
        self.account_edit.setGeometry(145, 100, 220, 35)
        # 昵称
        nick_label = QLabel("昵称：", self)
        nick_label.setGeometry(75, 150, 60, 35)
        nick_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        self.nick_edit = QLineEdit(self)
        self.nick_edit.setPlaceholderText("请输入昵称,不填为空")
        self.nick_edit.setCursor(QCursor(Qt.PointingHandCursor))
        self.nick_edit.setGeometry(145, 150, 220, 35)
        # 密码
        password_label = QLabel("密码：", self)
        password_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        password_label.setGeometry(75, 200, 60, 35)
        self.password_edit = QLineEdit(self)
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setCursor(QCursor(Qt.PointingHandCursor))
        self.password_edit.setGeometry(145, 200, 220, 35)
        # 确认密码
        confirm_password = QLabel("确认密码：", self)
        confirm_password.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        confirm_password.setGeometry(75, 250, 60, 35)
        self.confirm_edit = QLineEdit(self)
        self.confirm_edit.setPlaceholderText("请再次输入密码")
        self.confirm_edit.setCursor(QCursor(Qt.PointingHandCursor))
        self.confirm_edit.setGeometry(145, 250, 220, 35)
        # 协议
        self.agreement = QCheckBox("我已阅读并同意", self)
        self.agreement.setStyleSheet("font-size:11px;color:rgb(100,100,100)")
        self.agreement.setChecked(True)
        self.agreement.setGeometry(145, 295, 110, 25)
        self.agreement.stateChanged.connect(self.agreement_state_changed)
        agreement_button = QPushButton("《决策分析系统最终用户许可协议》", self)
        agreement_button.setStyleSheet("font-size:11px;border:none; color:rgb(0,0,255)")
        agreement_button.setCursor(QCursor(Qt.PointingHandCursor))
        agreement_button.setGeometry(240, 295, 165, 25)
        # agreement_button.clicked.connect(lambda: self.button_clicked("agreement"))
        # 注册
        self.register_button = QPushButton("注册", self)
        self.register_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.register_button.setStyleSheet("color:#FFFFFF;font-size:15px;background-color:rgb(30,50,190);")
        self.register_button.setGeometry(145, 330, 220, 35)
        self.register_button.clicked.connect(self.register_account)
        # # 已有账号
        # has_account = QLabel("已有账号?", self)
        # has_account.setStyleSheet("font-size:11px;")
        # has_account.setGeometry(145, 370, 60, 20)
        # # 登录
        # self.login_button = QPushButton("登录", self)
        # self.login_button.setStyleSheet("font-size:11px;border:none;color:rgb(30,50,190)")
        # self.login_button.setGeometry(195, 370, 30, 20)
        # self.login_button.setCursor(QCursor(Qt.PointingHandCursor))
        # self.login_button.clicked.connect(self.to_login)
        self.setStyleSheet("RegisterDialog {border:1px solid rgb(54, 157, 180)}")

    def agreement_state_changed(self):
        """同意协议状态发生改变"""
        if not self.agreement.isChecked():
            self.register_button.setEnabled(False)
            self.register_button.setStyleSheet("color:#FFFFFF;font-size:15px;background-color:rgb(200,200,200);")
        else:
            self.register_button.setStyleSheet("color:#FFFFFF;font-size:15px;background-color:rgb(30,50,190);")
            self.register_button.setEnabled(True)

    def to_login(self):
        # close self and to show login dialog widget
        def emit_login_successful(message):
            # 重新实例化的登录窗口，要再次传出信号才能改变登录栏的显示状态
            popup.successful_login.emit(message)
        self.close()
        popup = Login()
        popup.successful_login.connect(emit_login_successful)
        popup.deleteLater()
        popup.exec()
        del popup

    def register_account(self):
        # 上传信息,注册账号
        phone = self.account_edit.text().strip(' ')
        nick_name = self.nick_edit.text().strip(' ')
        password = self.password_edit.text().strip(' ')
        confirm_psd = self.confirm_edit.text().strip(' ')
        if password != confirm_psd:
            popup = TipShow()
            popup.information('错误', '两次密码输入不一致.')
            popup.deleteLater()
            popup.exec()
            del popup
            return
        # 验证手机号
        if not re.match(r'^[1]([3-9])[0-9]{9}$', phone):
            popup = TipShow()
            popup.information('错误', '请输入正确的手机号.')
            popup.deleteLater()
            popup.exec()
            del popup
            return
        # 注册
        try:
            response = requests.post(
                url=config.SERVER_ADDR + 'user/register/',
                data=json.dumps({
                    'phone':phone,
                    'nick_name': nick_name,
                    'password': password,
                    'machine_code': config.app_dawn.value('machine'),
                    'is_admin': True
                })
            )
            response_data = json.loads(response.content.decode('utf-8'))
        except Exception as error:
            popup = TipShow()
            popup.information('错误', '注册失败.\n{}'.format(error))
            popup.confirm_btn.clicked.connect(popup.close)
            popup.deleteLater()
            popup.exec()
            del popup
            return
        if response.status_code != 201:
            popup = TipShow()
            popup.information('错误', response_data['message'])
            popup.confirm_btn.clicked.connect(popup.close)
            popup.deleteLater()
            popup.exec()
            del popup
            return
        popup = TipShow()
        popup.information('成功', '恭喜!注册成功.返回登录.')
        popup.confirm_btn.clicked.connect(popup.close)
        popup.deleteLater()
        popup.exec()
        del popup
        self.to_login()


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


class TipShow(QDialog):
    def __init__(self, *args, **kwargs):
        super(TipShow, self).__init__(*args, **kwargs)
        self.setMinimumSize(300,200)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        layout = QVBoxLayout(spacing=12)
        action_layout = QHBoxLayout()
        # widgets
        title_bar = TitleBar()
        self.tips_label = QLabel()
        self.cancel_btn = QPushButton('取消')
        self.confirm_btn = QPushButton('确定')
        # signal
        self.windowIconChanged.connect(title_bar.setIcon)
        self.windowTitleChanged.connect(title_bar.setTitle)
        title_bar.windowClosed.connect(self.close)  # close dialog
        # style
        layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setContentsMargins(0,0,0,0)
        title_bar.setMaximumHeight(30)
        title_bar.setMinimumHeight(30)
        title_bar.buttonMinimum.hide()
        title_bar.buttonMaximum.hide()
        title_bar.setIconSize(20)
        self.tips_label.setAlignment(Qt.AlignCenter)
        self.setWindowIcon(QIcon('media/logo.png'))
        self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.confirm_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_btn.setStyleSheet('border:none;background-color:rgb(110,140,220);color:rgb(255,255,255);margin:0 0 10px 0;padding:5px 10px')
        self.confirm_btn.setStyleSheet('border:none;background-color:rgb(110,140,220);color:rgb(255,255,255);margin:0 10px 10px 0;padding:5px 10px')
        self.tips_label.setStyleSheet('font-size:15px; padding:2px 10px 2px 10px')
        self.setStyleSheet("TipShow{border: 1px solid rgb(185,188,191)}")
        layout.addWidget(title_bar)
        layout.addWidget(self.tips_label)
        action_layout.addStretch()
        action_layout.addWidget(self.cancel_btn)
        action_layout.addWidget(self.confirm_btn)
        layout.addLayout(action_layout)
        self.setLayout(layout)

    def information(self, title, message):
        self.cancel_btn.hide()
        self.setWindowTitle(title)
        self.tips_label.setText(message)


    def choose(self, title, message):
        self.setWindowTitle(title)
        self.tips_label.setText(message)
