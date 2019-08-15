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
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QCheckBox, QTextBrowser, QScrollArea, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtGui import QCursor, QIcon, QImage, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

import config
from piece.base import TitleBar

class Login(QDialog):
    successful_login = pyqtSignal(str)

    def __init__(self):
        super(Login, self).__init__()
        register_forget_style = """
        QPushButton {
           font-size:11px;
           color:rgb(0,0,200);
           border:none;
        } 
        """
        style_sheet = """
        LoginDialog {
            border:1px solid rgb(54, 157, 180)
            }
        QLineEdit {
            font-size:13px;
            border-width:0;
            border-style:outset;
            border-top:1px solid rgb(150,150,150);
            border-bottom:1px solid rgb(150,150,150)
        }
        """
        self.resize(480, 300)
        # 设置无边框
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 添加个head
        title_bar = TitleBar(self)
        title_bar.setGeometry(0, 0, 480, 50)
        # deal with window signal
        self.windowIconChanged.connect(title_bar.setIcon)
        self.windowTitleChanged.connect(title_bar.setTitle)
        self.setWindowTitle('登录')
        self.setWindowIcon(QIcon("media/logo.png"))
        # 按钮处理
        title_bar.buttonMinimum.hide()
        title_bar.buttonMaximum.hide()
        title_bar.buttonClose.setCursor(QCursor(Qt.PointingHandCursor))
        title_bar.windowClosed.connect(self.close)  # close dialog
        title_bar.windowMoved.connect(self.move)
        account_label = QLabel(self)
        account_label.setStyleSheet("image:url(media/user_icon.jpg)")
        account_label.setGeometry(75, 100, 36, 35)
        password_label = QLabel(self)
        password_label.setStyleSheet("image:url(media/mima_icon.jpg)")
        password_label.setGeometry(75, 150, 36, 35)
        # 用户名输入
        self.account_edit = QLineEdit(self)
        self.account_edit.setGeometry(111, 100, 250, 35)
        self.account_edit.setPlaceholderText("用户名/手机号")
        # 无用户名注册账号
        register_account = QPushButton("还没账号?", self)
        register_account.setGeometry(365, 100, 60, 35)
        register_account.setStyleSheet(register_forget_style)
        register_account.setCursor(QCursor(Qt.PointingHandCursor))
        register_account.clicked.connect(self.to_register)
        # 密码输入
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setGeometry(111, 150, 250, 35)
        self.password_edit.setPlaceholderText("请输入密码")
        # 忘记密码
        forget_password = QPushButton("忘记密码?", self)
        forget_password.setGeometry(365, 150, 60, 35)
        forget_password.setStyleSheet(register_forget_style)
        forget_password.setCursor(QCursor(Qt.PointingHandCursor))
        forget_password.clicked.connect(self.forget_psd_clicked)
        # 记住密码
        self.remember_check = QCheckBox("记住密码",self)
        self.remember_check.setGeometry(75, 190, 80, 30)
        # 自动登录
        self.auto_login = QCheckBox("自动登录", self)
        self.auto_login.setGeometry(155, 190, 120, 30)
        self.auto_login.stateChanged.connect(self.auto_login_checked_change)
        # 登录
        login_button = QPushButton("登录", self)
        login_button.setGeometry(75, 220, 286, 35)
        login_button.setStyleSheet("color:#FFFFFF;font-size:15px;border:none;background-color:rgb(30,50,190);")
        login_button.setCursor(QCursor(Qt.PointingHandCursor))
        login_button.clicked.connect(self.submit_login)
        self.setStyleSheet(style_sheet)
        # 获取是否记住了用户名和密码
        self.remember_username()

    def remember_username(self):
        username = config.app_dawn.value('username')
        password = config.app_dawn.value('password')
        if not all([username, password]):
            return
        self.account_edit.setText(username)
        self.password_edit.setText(password)
        self.remember_check.setChecked(True)

    def auto_login_checked_change(self):
        # auto login or not
        if self.auto_login.isChecked():
            self.remember_check.setChecked(True)

    def forget_psd_clicked(self):
        # forget password button clicked signal slot function
        popup = TipShow()
        popup.information('忘记密码', '请联系管理员修改密码.')
        popup.confirm_btn.clicked.connect(popup.close)
        popup.deleteLater()
        popup.exec()
        del popup

    def submit_login(self):
        # collect login information
        account = self.account_edit.text().strip(' ')
        password = self.password_edit.text().strip(' ')
        remember = 1 if self.remember_check.isChecked() else 0
        auto_login = 1 if self.auto_login.isChecked() else 0
        if not account or not password:
            popup = TipShow()
            popup.information('错误', '请输入用户名或密码.')
            popup.confirm_btn.clicked.connect(popup.close)
            popup.exec()
            popup.deleteLater()
            del popup
            return
        if auto_login and not remember:
            popup = TipShow()
            popup.information('提示', '自动登录请记住密码.')
            popup.confirm_btn.clicked.connect(popup.close)
            popup.exec()
            popup.deleteLater()
            del popup
            return
        # login
        try:
            response = requests.post(
                url=config.SERVER_ADDR + "user/passport/?option=login",
                headers=config.CLIENT_HEADERS,
                data=json.dumps({
                    "username": account,
                    "password": password,
                    'machine_code': config.app_dawn.value('machine'),
                }),
                cookies=config.app_dawn.value('cookies')
            )
        except Exception as error:
            popup = TipShow()
            popup.information('错误', str(error))
            popup.confirm_btn.clicked.connect(popup.close)
            popup.deleteLater()
            popup.exec()
            del popup
            return
        response_data = json.loads(response.content.decode('utf-8'))
        if response.status_code != 200:
            popup = TipShow()
            popup.information('错误', response_data['message'])
            popup.confirm_btn.clicked.connect(popup.close)
            popup.deleteLater()
            popup.exec()
            del popup
            return
        # login successfully
        user_data = response_data['data']
        config.app_dawn.setValue('cookies', response.cookies)  # save cookies
        config.app_dawn.setValue('auto_login', auto_login)  # save auto login option
        config.app_dawn.setValue('access_main_module', user_data['access_main_module'])
        if remember:
            config.app_dawn.setValue('username', user_data['username'])
            config.app_dawn.setValue('password', password)
        else:
            config.app_dawn.remove('password')
            config.app_dawn.remove('username')
        show_name = user_data['nick_name'] if user_data["nick_name"] else user_data["username"]
        self.successful_login.emit(show_name)
        self.close()  # close dialog

    def to_register(self):
        # close self and to register dialog widget
        self.close()
        popup = Register()
        popup.deleteLater()
        popup.exec()
        del popup


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


class PDFReader(QDialog):
    def __init__(self, doc=None, title="查看PDF"):
        super(PDFReader, self).__init__()
        # auth doc type
        self.setWindowTitle(title)
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
        if not doc:
            label = QLabel('没有内容.')
            self.page_container.layout().addWidget(label)
        else:
            self.add_pages(doc)
        scroll_area.setWidget(self.page_container)
        # add layout
        layout.addWidget(self.download, alignment=Qt.AlignLeft)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def add_pages(self, doc):
        if not isinstance(doc, fitz.Document):
            raise ValueError("doc must be instance of class fitz.fitz.Document")
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

