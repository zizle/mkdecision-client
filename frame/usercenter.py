# _*_ coding:utf-8 _*_
# __Author__： zizle
import requests
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel, QPushButton
from PyQt5.QtCore import Qt, QSize, QMargins, pyqtSignal
from widgets.CAvatar import CAvatar
from widgets.base import LoadedPage
from popup.usercenter import EditUserAvatar
import settings


# 基本资料窗口
class BaseInfo(QWidget):
    avatar_url = pyqtSignal(str)
    def __init__(self, uid, *args, **kwargs):
        super(BaseInfo, self).__init__(*args, **kwargs)
        self.user_id = uid
        layout = QVBoxLayout()
        # 手机号
        phone_layout = QHBoxLayout()
        self.phone_edit = QLineEdit(objectName='phoneEdit')
        self.phone_edit.setFocusPolicy(Qt.NoFocus)
        phone_layout.addWidget(QLabel('手机：', objectName='phoneLabel'))
        phone_layout.addWidget(self.phone_edit)
        layout.addLayout(phone_layout)
        # 用户名
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel('昵称：', objectName='nameLabel'))
        self.username_edit = QLineEdit(objectName='usernameEdit')
        name_layout.addWidget(self.username_edit)
        layout.addLayout(name_layout)
        # 邮箱
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel('邮箱：', objectName='emailLabel'))
        self.email_edit = QLineEdit(objectName='emailEdit')
        email_layout.addWidget(self.email_edit)
        layout.addLayout(email_layout)
        # 确认修改
        confirm_layout = QHBoxLayout()
        self.submit_button = QPushButton('确定', objectName='submitBtn', cursor=Qt.PointingHandCursor)
        confirm_layout.addWidget(self.submit_button, alignment=Qt.AlignRight)
        layout.addLayout(confirm_layout)
        self.setLayout(layout)
        self.setObjectName('baseInfo')
        self.setStyleSheet("""
        #baseInfo{
            background-color: rgb(150, 200, 150)
        }
        #phoneLabel,#nameLabel,#emailLabel{
            font-size: 15px;
            font-weight: bold;
        }
        #phoneEdit{
            font-size: 18px;
            background-color: rgb(240, 240, 240);
            border: none;
        }
        #usernameEdit,#emailEdit{
            font-size: 18px;
        }
        #submitBtn{
            font-size: 16px;
            border: none;
            background-color: rgb(20, 150, 200);
            color: rgb(255, 255, 255);
            padding: 8px 15px;
            border-radius: 5px;
        }
        """)

    # 请求用户信息
    def on_load_info(self):
        try:
            machine = settings.app_dawn.value('machine')
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/' + str(self.user_id) + '/baseInfo/?mc=' + machine
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError('请求信息错误')
        except Exception:
            pass
        else:
            user_data = response['data']
            self.phone_edit.setText(user_data['phone'])
            self.username_edit.setText(user_data['username'])
            self.email_edit.setText(user_data['email'])
            self.avatar_url.emit(user_data['avatar'])



# 修改密码窗口
class ModifyPassword(QWidget):
    new_password = pyqtSignal(bool)

    def __init__(self, user_id,*args, **kwargs):
        super(ModifyPassword, self).__init__(*args, **kwargs)
        self.user_id = user_id
        layout = QVBoxLayout()
        # 新密码
        new_psd_layout1 = QHBoxLayout()
        new_psd_layout1.addWidget(QLabel('<div>新&nbsp;密&nbsp;码：</div>', objectName='newLabel1'))
        self.new_psd1 = QLineEdit(objectName='newEdit1')
        self.new_psd1.setEchoMode(QLineEdit.Password)
        new_psd_layout1.addWidget(self.new_psd1)
        layout.addLayout(new_psd_layout1)
        # 确认新密码
        new_psd_layout2 = QHBoxLayout()
        new_psd_layout2.addWidget(QLabel('再次确认密码：', objectName='newLabel2'))
        self.new_psd2 = QLineEdit(objectName='newEdit2')
        self.new_psd2.setEchoMode(QLineEdit.Password)
        new_psd_layout2.addWidget(self.new_psd2)
        layout.addLayout(new_psd_layout2)
        # 错误提示
        error_layout = QHBoxLayout()
        error_layout.addWidget(QLabel(parent=self, objectName='errorTips'))
        layout.addLayout(error_layout)
        # 确认修改
        confirm_layout = QHBoxLayout()
        self.submit_button = QPushButton('确定', objectName='submitBtn',clicked=self.submit_new_password, cursor=Qt.PointingHandCursor)
        confirm_layout.addWidget(self.submit_button, alignment=Qt.AlignRight)
        layout.addLayout(confirm_layout)
        self.setLayout(layout)
        self.setStyleSheet("""
        #newLabel1,#newLabel2{
            font-size: 15px;
            font-weight: bold;
        }
        #newEdit1,#newEdit2{
            font-size: 18px;
        }
        #errorTips{
            max-height: 22px;
        }
        #submitBtn{
            font-size: 16px;
            width: 80px;
            border: none;
            background-color: rgb(20, 150, 200);
            color: rgb(255, 255, 255);
            padding: 8px 15px;
            border-radius: 5px;
        }
        #submitBtn:pressed{
            background-color: rgb(20, 120, 170);
        }
        """)

    # 确认新密码
    def submit_new_password(self):
        psd1 = self.new_psd1.text().strip()
        psd2 = self.new_psd2.text().strip()
        if psd1 != psd2:
            self.findChild(QLabel, 'errorTips').setText('两次输入的密码不一致!')
            return
        # 请求修改密码
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'user/' + str(self.user_id) + '/psd/?mc=' + settings.app_dawn.value(
                    'machine'),
                headers={
                    'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')
                },
                data=json.dumps({'password': psd2})
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.findChild(QLabel, 'errorTips').setText(str(e))
        else:
            # 修改成功,重新登录
            self.findChild(QLabel, 'errorTips').setText('密码修改成功,请重新登录.')
            settings.app_dawn.remove('AUTHORIZATION')  # 移除token
            self.new_password.emit(True)


# 用户个人中心
class UserCenter(QWidget):
    avatar_changed = pyqtSignal(str)
    psd_changed = pyqtSignal(bool)

    def __init__(self, user_id, *args, **kwargs):
        super(UserCenter, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.set_new_avatar = False
        layout = QVBoxLayout()  # 总布局
        layout.setContentsMargins(QMargins(100, 10, 100, 10))
        middle_layout = QHBoxLayout()  # 中间布局
        # 左侧显示头像和菜单
        left_layout = QVBoxLayout()  # 左侧布局
        # left_layout.setContentsMargins(QMargins(100, 0, 0, 0))
        # avatar_layout = QHBoxLayout()
        self.avatar = CAvatar(size=QSize(180, 180))
        self.avatar.clicked.connect(self.modify_user_avatar)
        left_layout.addWidget(self.avatar, alignment=Qt.AlignCenter)
        # avatar_layout.addWidget(self.avatar)
        # left_layout.addLayout(avatar_layout)
        # 菜单
        self.left_list = QListWidget(clicked=self.menu_clicked, objectName='leftList')
        self.left_list.setMaximumWidth(250)
        # self.left_list.addItems(['基本资料', '修改密码'])
        item1 = QListWidgetItem('基本资料')
        item2 = QListWidgetItem('修改密码')
        item1.setTextAlignment(Qt.AlignCenter)
        item2.setTextAlignment(Qt.AlignCenter)
        self.left_list.addItem(item1)
        self.left_list.addItem(item2)
        left_layout.addWidget(self.left_list)
        middle_layout.addLayout(left_layout)
        # 右侧显示具体窗口
        self.right_win = LoadedPage()
        middle_layout.addWidget(self.right_win)
        layout.addLayout(middle_layout)
        # 底部显示机器码
        machine_code = settings.app_dawn.value('machine')
        msg = ''
        if machine_code:
            msg = '本机id：' + machine_code
        code_label = QLineEdit(msg, parent=self, objectName='machineCode')
        code_label.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(code_label, alignment=Qt.AlignBottom)
        self.setLayout(layout)
        self.setStyleSheet("""
        #machineCode{
            border: none;
            background:rgb(240,240,240);
        }
        #leftList{
            font-size:14px;
        }
        #leftList::item{
            height: 25px;
        }
        """)
        self.left_list.setCurrentRow(0)
        self.menu_clicked()

    def setAvatar(self, avatar_url):
        if avatar_url:
            url = settings.SERVER_ADDR[:-1] + avatar_url
            self.avatar.setUrl(url)
            self.avatar_changed.emit(url)
        else:
            self.avatar.setUrl('media/avatar.jpg')

    def password_changed(self):
        print('密码修改了')
        self.psd_changed.emit(True)

    # 修改用户头像
    def modify_user_avatar(self):
        popup = EditUserAvatar(user_id=self.user_id, current_url=self.avatar.url, parent=self)
        popup.new_avatar_url.connect(self.setAvatar)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 点击左侧菜单
    def menu_clicked(self):
        current_item = self.left_list.currentItem()
        text = current_item.text()
        if text == '基本资料':
            frame_page = BaseInfo(uid=self.user_id)
            frame_page.avatar_url.connect(self.setAvatar)
            frame_page.on_load_info()
        elif text == '修改密码':
            frame_page = ModifyPassword(user_id=self.user_id)
            frame_page.new_password.connect(self.password_changed)
        else:
            frame_page = QLabel()
        self.right_win.clear()
        self.right_win.addWidget(frame_page)
