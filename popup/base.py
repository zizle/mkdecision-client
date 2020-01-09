# _*_ coding:utf-8 _*_
# __Author__： zizle
import re
import uuid
import json
import base64
import requests
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QTextBrowser, QCheckBox, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import pyqtSignal, Qt

import settings


# 登录弹窗
class LoginPopup(QDialog):
    user_listed = pyqtSignal(dict)  # 登录成功发出信号

    def __init__(self, *args, **kwargs):
        super(LoginPopup, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(spacing=0)
        # 手机
        phone_layout = QHBoxLayout()
        phone_label = QLabel()
        phone_label.setPixmap(QPixmap('media/passport_icon/phone.png'))
        phone_layout.addWidget(phone_label)
        # 填写手机
        self.phone_edit = QLineEdit()
        phone_layout.addWidget(self.phone_edit)
        layout.addLayout(phone_layout)
        # 手机号错误提示框
        self.phone_error = QLabel()
        layout.addWidget(QLabel(parent=self, objectName='phoneError'))
        # 密码
        psd_layout = QHBoxLayout()
        password_label = QLabel()
        password_label.setPixmap(QPixmap('media/passport_icon/password.png'))
        psd_layout.addWidget(password_label)
        # 填写密码
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        psd_layout.addWidget(self.password_edit)
        layout.addLayout(psd_layout)
        # 密码错误提示框
        layout.addWidget(QLabel(parent=self, objectName='psdError'))
        # 记住密码
        remember_layout = QHBoxLayout(spacing=2)
        self.remember_psd = QCheckBox('记住密码', objectName='rememberCheck', clicked=self.clicked_remember_psd)
        remember_layout.addWidget(self.remember_psd)
        # 记住登录
        self.remember_login = QCheckBox('自动登录', objectName='rememberCheck', clicked=self.clicked_auto_login)
        remember_layout.addWidget(self.remember_login)
        remember_layout.addStretch()
        layout.addLayout(remember_layout)
        # 登录错误框
        layout.addWidget(QLabel(parent=self, objectName='loginError'))
        # 确认登录
        login_button = QPushButton('登录', clicked=self.commit_login, objectName='loginBtn')
        layout.addWidget(login_button)
        # 样式
        self.setWindowTitle('登录')
        self.setMinimumWidth(300)
        self.setStyleSheet("""
        #phoneError, #psdError, #loginError{
            color: rgb(200,50,30)
        }
        #rememberCheck{
            color: rgb(100,100,100)
        }
        #loginBtn{
            background-color:rgb(46,158,224);
            color: rgb(240,240,240);
            font-weight:bold;
            min-height:28px;
            border:none;
        }
        #loginBtn:pressed{
            background-color:rgb(28,76,202);
        }
        """)
        phone_label.setFixedSize(36, 35)
        phone_label.setScaledContents(True)
        self.phone_edit.setFixedHeight(35)
        password_label.setScaledContents(True)
        password_label.setFixedSize(36, 35)
        self.password_edit.setFixedHeight(35)
        # 布局
        self.setLayout(layout)
        self._init_account()

    # 选择记住密码
    def clicked_remember_psd(self):
        remember = self.remember_psd.isChecked()
        phone, password = self.get_account()
        if not remember:
            # 保存用户名和密码
            password = ''
        account = json.dumps({'phone': phone, 'password': password})
        account = base64.b64encode(account.encode('utf-8')).decode('utf-8')
        settings.app_dawn.setValue('user', account)  # 保存用户名和密码

    # 选择自动登录
    def clicked_auto_login(self):
        auto_login = self.remember_login.isChecked()
        remember_psd_flag = self.remember_psd.isChecked()
        self.remember_psd.setChecked(False)  # 保存用户名和密码
        if auto_login:
            self.remember_psd.click()  # 保存用户资料
            settings.app_dawn.setValue('auto', 1)
        else:
            self.remember_psd.setChecked(remember_psd_flag)
            # 取消自动登录
            settings.app_dawn.setValue('auto', 0)

    # 读取用户名填入
    def _init_account(self):
        account = base64.b64decode(settings.app_dawn.value('user').encode('utf-8'))
        account = json.loads(account.decode('utf-8'))
        phone = account.get('phone', '')
        password = account.get('password', '')
        self.phone_edit.setText(phone)
        self.password_edit.setText(password)
        if password:
            self.remember_psd.setChecked(True)
        if settings.app_dawn.value('auto') == '1':
            self.remember_login.setChecked(True)

    # 获取手机号和密码
    def get_account(self):
        # 获取手机
        phone = re.match(r'^[1][3-9][0-9]{9}$', self.phone_edit.text())
        if not phone:
            phone = ''
        else:
            phone = phone.group()
        # 获取密码
        password = re.sub(r'\s+', '', self.password_edit.text())
        if not password:
            password = ''
        return phone, password

    # 获取手机号和密码提交登录
    def commit_login(self):
        phone, password = self.get_account()
        if not phone:
            self.findChild(QLabel, 'phoneError').setText('请输入正确的手机号')
            return
        if not password:
            self.findChild(QLabel, 'psdError').setText('请输入密码')
            return
        # 判断记住密码和自动登录的情况

        # 登录成功
        if self._login_post(phone, password):
            self.close()

    # 提交登录
    def _login_post(self, phone, password):
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'user/login/?mc=' + settings.app_dawn.value('machine', ''),
                headers={
                    "AUTHORIZATION": settings.app_dawn.value('AUTHORIZATION'),
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
            settings.app_dawn.remove('AUTHORIZATION')
            return False
        else:
            if response['data']:
                self.user_listed.emit(response['data'])
                return True
            else:
                return False


# 图片验证码控件
class ImageCodeLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(ImageCodeLabel, self).__init__(*args, **kwargs)
        self.get_image_code()
        self.setScaledContents(True)

    # 生成uuid
    def generate_uuid(self):
        uid = str(uuid.uuid4())
        return ''.join(uid.split('-'))

    # 获取图片验证码
    def get_image_code(self):
        image_uuid = self.generate_uuid()
        try:
            r = requests.get(url=settings.SERVER_ADDR + 'image_code/' + image_uuid + '/')
            response_img = r.content
            if r.status_code != 200:
                raise ValueError('get screeen image error.')
        except Exception:
            pass
        else:
            # 保存uuid
            settings.app_dawn.setValue('IMGCODEID', image_uuid)
            image = QImage.fromData(response_img)
            self.setPixmap(QPixmap.fromImage(image))

    # 鼠标点击
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.get_image_code()


# 协议弹窗
class LicensePopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(LicensePopup, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        self.text_browser = QTextBrowser()
        self.text_browser.setText('许可协议内容')
        layout.addWidget(self.text_browser)
        self.setLayout(layout)
        self.setWindowTitle('许可协议')


# 注册弹窗
class RegisterPopup(QDialog):
    user_registered = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(RegisterPopup, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(spacing=0)
        # 手机号
        phone_layout = QHBoxLayout()
        phone_label = QLabel()
        phone_label.setPixmap(QPixmap('media/passport_icon/phone.png'))
        phone_layout.addWidget(phone_label)
        # 填写手机
        self.phone_edit = QLineEdit(placeholderText='填写手机号')
        phone_layout.addWidget(self.phone_edit)
        layout.addLayout(phone_layout)
        # 手机号错误提示框
        layout.addWidget(QLabel(parent=self, objectName='phoneError'))
        # 用户名
        username_layout = QHBoxLayout()
        username_label = QLabel()
        username_label.setPixmap(QPixmap('media/passport_icon/username.png'))
        username_layout.addWidget(username_label)
        # 填写用户名
        self.username_edit = QLineEdit(placeholderText='输入用户名/昵称')
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)
        layout.addWidget(QLabel(parent=self, objectName='usernameError'))
        # 密码
        password_layout1 = QHBoxLayout()
        password_label = QLabel()
        password_label.setPixmap(QPixmap('media/passport_icon/password.png'))
        password_layout1.addWidget(password_label)
        # 填写密码
        self.password_edit = QLineEdit(placeholderText='在此设置您的密码')
        self.password_edit.setEchoMode(QLineEdit.Password)
        password_layout1.addWidget(self.password_edit)
        layout.addLayout(password_layout1)
        # 密码错误提示框
        layout.addWidget(QLabel(parent=self, objectName='psdErrorA'))
        # 确认密码
        password_layout2 = QHBoxLayout()
        re_password_label = QLabel()
        re_password_label.setPixmap(QPixmap('media/passport_icon/password.png'))
        password_layout2.addWidget(re_password_label)
        # 填写确认密码
        self.re_password_edit = QLineEdit(placeholderText='再次输入密码')
        self.re_password_edit.setEchoMode(QLineEdit.Password)
        password_layout2.addWidget(self.re_password_edit)
        layout.addLayout(password_layout2)
        # 确认密码错误提示框
        layout.addWidget(QLabel(parent=self, objectName='psdErrorB'))
        # 验证码
        verify_layout = QHBoxLayout()
        image_code_label = QLabel()
        image_code_label.setPixmap(QPixmap('media/passport_icon/yanzheng.png'))
        image_code_label.setScaledContents(True)
        verify_layout.addWidget(image_code_label)
        self.image_code_edit = QLineEdit(placeholderText='填写右侧验证码')
        self.image_code_edit.setFixedHeight(35)
        verify_layout.addWidget(self.image_code_edit)
        self.image_code_show = ImageCodeLabel()
        self.image_code_show.setMaximumSize(80, 35)
        verify_layout.addWidget(self.image_code_show)
        layout.addLayout(verify_layout)
        layout.addWidget(QLabel(parent=self, objectName='verifyError'))
        # 用户协议
        license_layout = QHBoxLayout(spacing=0)
        self.agree_license = QCheckBox('我已阅读并同意', checked=True, clicked=self.agree_check_clicked)
        license_layout.addWidget(self.agree_license)
        license_layout.addWidget(QPushButton('《本软件最终用户许可协议》', cursor=Qt.PointingHandCursor,
                                             objectName='licenseBtn', clicked=self.clicked_license))
        license_layout.addStretch()
        layout.addLayout(license_layout)
        # 注册
        layout.addWidget(QLabel(parent=self, objectName='registerError'))
        self.register_button = QPushButton('立即注册', clicked=self.commit_register, objectName='registerBtn')
        layout.addWidget(self.register_button)

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
        self.setFixedWidth(330)
        self.setStyleSheet("""
        #phoneError, #usernameError, #psdErrorA,#psdErrorB,#verifyError,#registerError{
            color: rgb(200,50,30)
        }
        #registerBtn{
            background-color:rgb(46,158,224);
            color: rgb(240,240,240);
            font-weight:bold;
            min-height:28px;
            border:none;
        }
        #registerBtn:pressed{
            background-color:rgb(28,76,202);
        }
        #licenseBtn{
            border:none;
            color:rgb(48,27,243)
        }
        """)
        # 布局
        self.setLayout(layout)

    # 点击同意许可协议
    def agree_check_clicked(self):
        self.agree_license.setChecked(True)

    # 点击协议
    def clicked_license(self):
        popup = LicensePopup(parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 获取信息提交注册
    def commit_register(self):
        # 获取手机
        phone = re.match(r'^[1][3-9][0-9]{9}$', self.phone_edit.text())
        if not phone:
            self.findChild(QLabel, 'phoneError').setText('请输入正确的手机号')
            return
        phone = phone.group()
        # 用户名
        username = self.username_edit.text().strip()
        if username:
            username = re.match(r'^[\u4e00-\u9fa5_0-9a-z]{2,20}', username)
            if not username:
                self.findChild(QLabel, 'usernameError').setText('用户名需由中文、数字、字母及下划线组成,2-20个字符')
                return
            username = username.group()
        # 获取密码
        password = self.password_edit.text()
        password = re.sub(r'\s+', '', password)
        if not password or len(password) < 6:
            self.findChild(QLabel, 'psdErrorA').setText('密码至少为6位.')
            return
        # 确认密码
        re_password = self.re_password_edit.text()
        re_password = re.sub(r'\s+', '', re_password)
        if re_password != password:
            self.findChild(QLabel, 'psdErrorB').setText('两次输入密码不一致')
            return
        # 图片验证码
        image_code = re.sub(r'\s+', '', self.image_code_edit.text())
        if not image_code:
            self.findChild(QLabel, 'verifyError').setText('请填写验证码。')
            return
        # 提交注册
        data = {
            "phone": phone,
            "username": username,
            "password": password,
            "image_code": image_code,
            "image_code_id": settings.app_dawn.value('IMGCODEID')
        }
        response_data = self._register_post(data)
        if response_data:
            # 注册成功
            self.user_registered.emit(response_data)
            self.close()

    # 提交注册
    def _register_post(self, data):
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'user/?mc=' + settings.app_dawn.value('machine'),
                data=json.dumps(data),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            self.findChild(QLabel, 'registerError').setText(str(e))
            # 移除token
            return {}
        else:  # 注册成功
            return response['data']