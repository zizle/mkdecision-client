# _*_ coding:utf-8 _*_
# company: RuiDa Futures
# author: zizle
import json
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt, pyqtSignal, QSettings
from widgets import FrameLessWindow
from widgets.dialog import LoginDialog, RegisterDialog
from windows.home import HomePageScrollWindow
from windows import ProductServiceWindow, FundamentalWindow, TechnicalAnalysisWindow, ArbitrageAnalysisWindow, HedgingAnalysisWindow, SystemSetupWindow

import config
# from settings import BASE_DIR, VERSION, SERVER_ADDR, app_conf, CLIENT_HEADERS
from utils import user_login, user_logout


class MasterWindow(FrameLessWindow):
    def __init__(self):
        super(MasterWindow, self).__init__()
        self.__init_ui()

    def __init_ui(self):  # 初始化
        self.menus = []  # 菜单容器
        self.setWindowIcon(QIcon(config.BASE_DIR + "/media/logo.png"))  # 设置图标
        self.setWindowTitle("瑞达期货研究院分析决策系统v" + config.VERSION)  # 设置版本号
        self.resize(1280, 768)  # 调整大小
        self.center()  # 居中
        # 设置各模块窗口容器
        self.models = QStackedWidget()
        # 设置菜单栏
        self.set_menu_bar()
        self.menuBar.addMenus(self.menus)
        self.menuBar.addStretch()
        # 登录状态信息栏被点击
        self.loginBar.clicked_signal.connect(self.login_bar_clicked)
        self.setWidget(self.models)

    def center(self):  # 设置居中
        myself = self.frameGeometry()  # 自身窗体信息(虚拟框架)
        myself.moveCenter(QDesktopWidget().availableGeometry().center())  # 框架中心移动到用户桌面中心
        self.move(myself.topLeft())  # 窗口左上角与虚拟框架左上角对齐

    def change_menu_status(self, menu):
        """改变按钮状态"""
        menu.setStyleSheet("background-color: #CD3333;")

        for menu_item in self.menus:
            if menu.id == menu_item.id:
                pass
            else:
                menu_item.setStyleSheet("background-color: rgb(54, 157, 180);")
                
    def close(self):
        """退出要删除权限"""
        # 登出
        if user_logout(self):
            config.app_dawn.remove('capsules')
            config.app_dawn.remove('cookies')
            super(MasterWindow, self).close()
        else:
            return

    def in_login_dialog_clicked(self, signal):
        """登录弹窗里的按钮点击"""
        if signal == "login":
            # 设置登录信息
            open_login = 0  # 默认不打开登录
            account = self.login_dialog.account_edit.text().strip(' ')
            password = self.login_dialog.password_edit.text().strip(' ')
            auto_login = self.login_dialog.automatic.isChecked()  # 自动登录
            remember = self.login_dialog.remember_check.isChecked()  # 记住密码
            if auto_login:
                self.login_dialog.remember_check.setChecked(True)
                open_login = 1
            # print("用户", account)
            # print("密码", password)
            # print("记住？", remember)
            # print("自动？", auto_login)
            if not account or not password:
                ret = QMessageBox.information(self.login_dialog, "错误", "用户名或密码错误!", QMessageBox.Yes)
                if ret == QMessageBox.Yes:
                    self.login_dialog.show()
                    return
            user_data = user_login(username=account, password=password, mount_window=self.login_dialog)
            if user_data:
                # 成功写入模块权限
                # settings.app_conf["capsules"] = user_data['capsules']
                config.app_dawn.setValue("capsules", user_data['capsules'])
                config.app_dawn.setValue('auto_login', open_login)
                config.app_dawn.setValue('cookies', user_data['cookies'])
                # app_init_config = QSettings("conf/config.ini", QSettings.IniFormat)
                # app_init_config.setValue("capsules", user_data['capsules'])
                # app_init_config.setValue('auto_login', open_login)
                # app_init_config.setValue('cookies', user_data['cookies'])
                # 有记住写入信息
                if remember:
                    # settings.app_conf["login"] = {"id": user_data["id"],"username": user_data["username"], "password": password, "open_login": open_login}
                    config.app_dawn.setValue('username', user_data['username'])
                    config.app_dawn.setValue('password', password)
                else:
                    config.app_dawn.remove('password')
                    config.app_dawn.remove('username')
                show_name = user_data['nick_name'] if user_data["nick_name"] else user_data["username"]
                self.loginBar.setLoginMessage(message="欢迎您! " + show_name)  # 设置显示登录信息
            else:
                return
            # 最后删除对话框
            self.login_dialog.close()
            del self.login_dialog

        elif signal == "forget":
            QMessageBox.information(self.login_dialog, "错误", "忘记密码!", QMessageBox.Yes)

        elif signal == "register":
            # 删除登录框
            self.login_dialog.close()
            del self.login_dialog
            # 显示注册框
            self.login_bar_clicked(signal)
        else:
            # 删除登录框
            self.login_dialog.close()
            del self.login_dialog

    def in_register_dialog_clicked(self, signal):
        """注册弹窗结果,取消或登录"""
        if signal == "register":
        # 查看信息
            account = self.register_dialog.account_edit.text().strip(' ')
            nick_name = self.register_dialog.nick_edit.text().strip(' ')
            password = self.register_dialog.password_edit.text().strip(' ')
            confirm_password = self.register_dialog.confirm_edit.text().strip(' ')
            agreement = self.register_dialog.agreement.isChecked()
            if not all([account, password, confirm_password]):
                QMessageBox.warning(self.register_dialog, "错误", "请将信息填写完整!", QMessageBox.Yes)
                return
            if password != confirm_password:
                QMessageBox.warning(self.register_dialog, "错误", "两次输入密码不一致!", QMessageBox.Yes)
                return
            # print("账户", account)
            # print("昵称", nick_name)
            # print("密码", password)
            # print("确认", confirm_password)
            # print("同意？", agreement)
            try:
                response = requests.post(
                    url=config.SERVER_ADDR + "user/register/",
                    headers=config.CLIENT_HEADERS,
                    data=json.dumps({
                        "phone": account,
                        'nick_name':nick_name,
                        'password':password,
                        'machine_code': config.app_conf["machine_code"]
                    })
                )
                response_content = json.loads(response.content.decode("utf-8"))
            except Exception as e:
                QMessageBox.warning(self.register_dialog, "错误", "注册失败!\n{}".format(e), QMessageBox.Yes)
                return
            if response.status_code == 400:
                QMessageBox.warning(self.register_dialog, "错误", response_content["message"], QMessageBox.Yes)
                return
            if response.status_code == 200:
                option = QMessageBox.warning(self.register_dialog, "成功", response_content["message"] + "\n返回登录。", QMessageBox.No|QMessageBox.Yes)
                if option == QMessageBox.Yes:
                    # 删除对话框
                    self.register_dialog.close()
                    del self.register_dialog
                    self.login_bar_clicked("login")
        elif signal == "agreement":
            QMessageBox.information(self.register_dialog, "协议", "本协议暂未拟定", QMessageBox.Yes)

        elif signal == "login":
            # 删除注册框
            self.register_dialog.close()
            del self.register_dialog
            # 显示登录框
            self.login_bar_clicked(signal)
        else:
            self.register_dialog.close()
            del self.register_dialog

    def instantiate_windows(self, menu_data):
        """实例化各菜单对应的窗口"""
        for menu in menu_data:
            if menu["name"] == '首页':
                homepage = HomePageScrollWindow(menus=menu['subs'])
                homepage.id = menu["id"]
                homepage.name = menu["name"]
                self.models.addWidget(homepage)
            elif menu['name'] == '产品服务':
                product_service = ProductServiceWindow()
                product_service.id = menu["id"]
                product_service.name = menu["name"]
                self.models.addWidget(product_service)
            elif menu['name'] == '基本分析':
                fundamental = FundamentalWindow()
                fundamental.id = menu["id"]
                fundamental.name = menu["name"]
                self.models.addWidget(fundamental)
            elif menu['name'] == '系统设置':
                systematic = SystemSetupWindow()
                systematic.id = menu['id']
                systematic.name = menu['name']
                self.models.addWidget(systematic)
            else:
                pass

    def login_bar_clicked(self, signal):
        """登录信息状态栏被点击"""
        if signal == "login":
            self.login_dialog = LoginDialog()
            self.login_dialog.button_clicked_signal.connect(self.in_login_dialog_clicked)
            self.login_dialog.exec()

        elif signal == "register":
            self.register_dialog = RegisterDialog()
            self.register_dialog.button_click_signal.connect(self.in_register_dialog_clicked)
            self.register_dialog.exec()

        elif signal == "exit":
            is_exit = QMessageBox.information(self, "提示", "确定注销？\n注销后下次不再享受便捷登录.", QMessageBox.Yes|QMessageBox.No)
            if is_exit == QMessageBox.Yes:
               if user_logout(self):
                    # 清除记录的登录信息
                    config.app_dawn.remove('capsules')
                    config.app_dawn.remove('password')
                    config.app_dawn.remove('cookies')
            else:
                return
            self.loginBar.exitLogin()  # 退出登录相应状态栏的改变
        else:
            return

    def menu_clicked(self, menu):
        """点击菜单"""
        frame_id = list()
        # 遍历窗口显示当前
        for index in range(self.models.count()):
            frame_window = self.models.widget(index)
            if frame_window.id == menu.id:
                if menu.text() == "首页" or menu.text() == '系统设置':
                    pass
                else:
                    # 检查权限
                    # capsules = settings.app_conf.get("capsules", None)
                    app_config = QSettings('conf/config.ini', QSettings.IniFormat)
                    capsules = app_config.value('capsules')
                    if capsules is None:
                    # 没有登录，默认开放的【首页】和【系统设置】
                        login_option = QMessageBox.information(self, "提示", "您不能查看本模块，赶紧登录看看吧!", QMessageBox.No|QMessageBox.Yes)
                        if login_option == QMessageBox.Yes:
                            self.login_dialog = LoginDialog()
                            self.login_dialog.button_clicked_signal.connect(self.in_login_dialog_clicked)
                            self.login_dialog.exec()
                        else:
                            pass
                        return
                    if menu.id not in capsules:
                        # 没有权限
                        QMessageBox.information(self, "提示", "您不能查看本模块，赶紧联系管理员开放吧!", QMessageBox.Yes)
                        return
                self.models.setCurrentWidget(frame_window)  # 显示当前窗口
                self.change_menu_status(menu)
            frame_id.append(frame_window.id)
        if menu.id not in frame_id:
            QMessageBox.information(self, "提示", "本功能未开放，敬请期待!", QMessageBox.Yes)

    def set_menu_bar(self):
        """设置菜单栏"""
        try:
            # 请求主菜单数据
            response = requests.get(
                url=config.SERVER_ADDR + "basic/module/",
                headers=config.CLIENT_HEADERS,
                data=json.dumps({"machine_code": config.app_dawn.value('machine')})
            )
            response_content = json.loads(response.content.decode("utf-8"))
            message = response_content['message']
            menu_data = response_content["data"]
        except Exception as e:
            QMessageBox.information(self, "获取数据错误", "请检查网络设置.\n{}".format(e), QMessageBox.Yes)
            return
        if response.status_code != 200:
            QMessageBox.information(self, "获取数据错误", message, QMessageBox.Yes)
            return
        # print(response_content)
        if menu_data:
            # 根据menu实例化窗口
            self.instantiate_windows(menu_data)
        for index, item in enumerate(menu_data):
            menu = MenuButton(item["name"])
            menu.clicked_signal.connect(self.menu_clicked)
            menu.setIndex(index)
            menu.setId(item["id"])
            if index == 0:
                menu.setStyleSheet("background-color: #CD3333;")
            self.menus.append(menu)
        # 设置鼠标样式
        for menu in self.menus:
            menu.setCursor(QCursor(Qt.ArrowCursor))  # 设置鼠标普通样式


        # menu_0 = QPushButton("首页")
        # menu_0.setStyleSheet("background-color: #CD3333;")
        # menu_1 = QPushButton("产品服务")
        # menu_2 = QPushButton("基本分析")
        # menu_3 = QPushButton("技术分析")
        # menu_4 = QPushButton("套利分析")
        # menu_5 = QPushButton("套保分析")
        # menu_6 = QPushButton("系统设置")
        # self.menus.append(menu_0)
        # self.menus.append(menu_1)
        # self.menus.append(menu_2)
        # self.menus.append(menu_3)
        # self.menus.append(menu_4)
        # self.menus.append(menu_5)
        # self.menus.append(menu_6)
        # menu_0.clicked.connect(self.menu_0_clicked)
        # menu_1.clicked.connect(self.menu_1_clicked)
        # menu_2.clicked.connect(self.menu_2_clicked)
        # menu_3.clicked.connect(self.menu_3_clicked)
        # menu_4.clicked.connect(self.menu_4_clicked)
        # menu_5.clicked.connect(self.menu_5_clicked)
        # menu_6.clicked.connect(self.menu_6_clicked)
        # 设置鼠标样式
        # for menu in self.menus:
        #     menu.setCursor(QCursor(Qt.ArrowCursor))  # 设置鼠标普通样式


class MenuButton(QPushButton):
    clicked_signal = pyqtSignal(QPushButton)
    def __init__(self, *args):
        super(MenuButton, self).__init__(*args)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.clicked.connect(self._button_clicked)

    def setIndex(self, index):
        self.index = index

    def setId(self, id):
        self.id = id

    def _button_clicked(self):
        self.clicked_signal.emit(self)

