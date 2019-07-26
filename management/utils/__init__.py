# _*_ coding:utf-8 _*_
# date: 20190722
# author: zizle
import requests
import json
import fitz
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QSettings
from win32com.shell import shell, shellcon
import config


def auto_login(mount_window):
    """开机自动登录"""
    # 读取配置
    login = int(config.app_dawn.value('auto_login')) if config.app_dawn.value('auto_login') else 0
    username = config.app_dawn.value('username')
    password = config.app_dawn.value('password')
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
            config.app_dawn.setValue("capsules", user_data['capsules'])
            config.app_dawn.setValue("cookies", user_data['cookies'])
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
            url=config.SERVER_ADDR + "user/passport/?option=login",
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
            return response_data["data"]
        else:
            QMessageBox.warning(mount_window, "错误", '登录失败!\n{}'.format(response_data["message"]), QMessageBox.Yes)
            return False


def user_logout(mount_window):
    """用户退出"""
    try:
        response = requests.post(
            url=config.SERVER_ADDR + 'user/passport/?option=logout',
            headers=config.CLIENT_HEADERS,
            cookies=config.app_dawn.value('cookies')
        )
        if response.status_code != 200:
            response_data = json.loads(response.content.decode('utf-8'))
            QMessageBox.warning(mount_window, "错误", response_data['message'], QMessageBox.Yes)
            return False
    except Exception as error:
        QMessageBox.warning(mount_window, "错误", '注销失败!\n{}'.format(error), QMessageBox.Yes)
        return False
    else:
        return True

def get_desktop_path():
    """获取用户桌面路径"""
    ilist = shell.SHGetSpecialFolderLocation(0, shellcon.CSIDL_DESKTOP)
    return shell.SHGetPathFromIDList(ilist).decode("utf-8")

def get_server_file(url, file, title):
        """获取文件"""
        # 请求文件
        headers = {"User-Agent": "DAssistant-Client/" + config.VERSION}
        try:
            response = requests.get(url=url, headers=headers, data={"file": file})
            f = open("cache/1a2b3c4d5e.file", "wb")
            f.write(response.content)
            f.close()
        except Exception as e:
            print(e)
            return
        doc = fitz.open("cache/1a2b3c4d5e.file")
        # 弹窗显示相应文件内容
        from widgets.dialog import PDFReaderDialog
        read_dialog = PDFReaderDialog(doc, file=file, title=title)
        if not read_dialog.exec():
            del read_dialog  # 弹窗生命周期未结束,手动删除
