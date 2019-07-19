# _*_ coding:utf-8 _*_
# author: zizle
# Date: 20190513
import requests
import json
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QSettings
from win32com.shell import shell, shellcon
import config


def auto_login(mount_window):
    """开机自动登录"""
    # 读取配置
    app_init_config = QSettings("conf/config.ini", QSettings.IniFormat)
    login = int(app_init_config.value('auto_login')) if app_init_config.value('auto_login') else 0
    username = app_init_config.value('username')
    password = app_init_config.value('password')
    capsules = app_init_config.value('capsules')
    print("从init配置文件读取设置login:", login, type(login))
    print("从init配置文件读取设置username", username)
    print("从init配置文件读取设置password", password)
    print("从init配置文件读取设置capsules", capsules, type(capsules))
    # login = app_conf.get("login", None)
    # if login is None:
    if not username:
        print('没有自动登录信息')
        return
    if not login:
        from widgets.dialog import LoginDialog
        mount_window.login_dialog = LoginDialog()
        # 填写用户名密码
        mount_window.login_dialog.account_edit.setText(username)  # 用户名
        mount_window.login_dialog.password_edit.setText(password)  # 密码
        if password:
            mount_window.login_dialog.remember_check.setChecked(True)  # 记住密码
        mount_window.login_dialog.button_clicked_signal.connect(mount_window.in_login_dialog_clicked)
        mount_window.login_dialog.exec()
    elif username and password:
        # 直接发送登录请求登录
        user_data = user_login(username=username, password=password, mount_window=mount_window)
        if user_data:
            # 成功写入模块权限
            app_init_config.setValue("capsules", user_data['capsules'])
            app_init_config.setValue("cookies", user_data['cookies'])
            show_name = user_data["nick_name"] if user_data["nick_name"] else user_data["username"]
            mount_window.loginBar.setLoginMessage(message="欢迎您! " + show_name)  # 设置显示登录信息
    else:
        pass


def user_login(username, password, mount_window):
    """用户登录"""
    # 读取客户端
    app_config = QSettings("dawn/initial.ini", QSettings.IniFormat)
    machine = app_config.value('machine')
    try:
        response = requests.post(
            url=config.SERVER_ADDR + "user/login/",
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"username": username, "password": password, 'machine_code': machine})
        )
        response_data = json.loads(response.content.decode('utf-8'))
    except Exception as error:
        QMessageBox.warning(mount_window, "错误", '登录错误!\n请检查网络设置.{}'.format(error), QMessageBox.Yes)
        return False
    else:
        if response.status_code == 200:
            response_data['data']['cookies'] = response.cookies
            from requests.cookies import RequestsCookieJar
            return response_data["data"]
        else:
            QMessageBox.warning(mount_window, "错误", '登录失败!\n{}'.format(response_data["message"]), QMessageBox.Yes)
            return False


def get_desktop_path():
    """获取用户桌面路径"""
    ilist = shell.SHGetSpecialFolderLocation(0, shellcon.CSIDL_DESKTOP)
    return shell.SHGetPathFromIDList(ilist).decode("utf-8")
