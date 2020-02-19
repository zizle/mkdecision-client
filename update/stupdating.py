# _*_ coding:utf-8 _*_
# Author: zizle  QQ:462894999
"""  启动程序入口,检查更新 """
import os
import sys
import time
import json
from hashlib import md5 as hash_md5
from requests import get as request_get
from subprocess import Popen
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap, QFont, QPalette, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings

# HTTP_SERVER = "http://192.168.191.2:8000/"
HTTP_SERVER = "http://210.13.218.130:9004/"
ADMINISTRATOR = True
APP_DAWN = QSettings('dawn/initial.ini', QSettings.IniFormat)


BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))


# 线程检测是否更新版本
class CheckUpdatingVersion(QThread):
    check_successful = pyqtSignal(dict)

    def run(self):
        version = APP_DAWN.value('VERSION')
        # print(version)
        if not version:
            version = ""
        identify = '1' if ADMINISTRATOR else '0'
        try:
            r = request_get(url=HTTP_SERVER + 'updating?identify='+ identify + '&version=' + str(version))
            if r.status_code != 200:
                raise ValueError('检测版本失败。')
            response = json.loads(r.content.decode('utf-8'))
        except Exception as e:
            pass
        else:
            self.check_successful.emit(response['data'])

# 线程下载新版本文件
class DownloadNewVersion(QThread):
    file_downloading = pyqtSignal(int, int, str)
    download_finished = pyqtSignal(bool)
    download_fail = pyqtSignal(str)

    def __init__(self, file_list, new_version, *args, **kwargs):
        super(DownloadNewVersion, self).__init__(*args, **kwargs)
        self.file_list = file_list
        self.file_count = len(file_list)
        self.update_file_list = dict()
        self.new_version = new_version

    def run(self):
        # 获取本地文件
        self.find_local_files(BASE_DIR)
        # print(self.update_file_list)
        for index, file in enumerate(self.file_list):
            local_file_md5 = self.update_file_list.get(file, None)
            # print('文件名：',file, 'MD5：',local_file_md5)
            if local_file_md5 is not None:
                if local_file_md5 == self.file_list[file]: # 对比MD5的值
                    # print('文件{}MD5相等, 无需下载。'.format(file))
                    continue
            #     else:
            #         print('文件存在,md5 不相等，需要下载文件')
            #         self.file_downloading.emit(index, self.file_count, str(file))
            #         self.download_file(file)
            #         time.sleep(0.000002)
            #         self.file_downloading.emit(index + 1, self.file_count, str(file))
            # else:
            #     # 文件不存在，需要下载文件
            #     print('文件不存在,需要下载')
            self.file_downloading.emit(index, self.file_count, str(file))
            self.download_file(file)
            time.sleep(0.000002)
            self.file_downloading.emit(index + 1, self.file_count, str(file))
        # 下载完成，写入新版本号
        APP_DAWN.setValue('VERSION', str(self.new_version))
        self.download_finished.emit(True)

    # 请求下载文件
    def download_file(self, file_name):
        file_path = os.path.join(BASE_DIR, file_name)
        try:
            r = request_get(
                url=HTTP_SERVER + 'updating/download/',
                data=json.dumps({'filename': file_name, 'identify': ADMINISTRATOR})
            )
            if r.status_code != 200:
                response = r.content.decode('utf-8')
                print(response)
                raise ValueError(response['data'])
            file_dir = os.path.split(file_path)[0]
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            file_name = open(file_path, 'wb')
            file_name.write(r.content)
            file_name.close()
        except Exception as e:
            self.download_fail.emit(str(e))

    # 计算文件的MD5
    def get_file_md5(self, filename):
        if not os.path.isfile(filename):
            return
        myHash = hash_md5()
        f = open(filename, 'rb')
        while True:
            b = f.read(8096)
            if not b:
                break
            myHash.update(b)
        f.close()
        return myHash.hexdigest()

    # 查找本地文件清单，并获取MD5值
    def find_local_files(self, path):
        fsinfo = os.listdir(path)
        for fn in fsinfo:
            temp_path = os.path.join(path, fn)
            if not os.path.isdir(temp_path):
                # print(temp_path)
                file_md5 = self.get_file_md5(temp_path)
                fn = str(temp_path.replace(BASE_DIR + '\\', ''))
                # print(fn)
                fn = '/'.join(fn.split('\\'))
                self.update_file_list[fn] = file_md5
            else:
                self.find_local_files(temp_path)


class StartPage(QLabel):
    def __init__(self, *args, **kwargs):
        super(StartPage, self).__init__(*args, *kwargs)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self._pressed = False
        self._mouse_pos = None
        icon_path = os.path.join(BASE_DIR, "media/logo.png")
        pix_path = os.path.join(BASE_DIR, "media/start.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setPixmap(QPixmap(pix_path))
        self.red = QPalette()
        self.red.setColor(QPalette.WindowText, Qt.red)
        self.blue = QPalette()
        self.blue.setColor(QPalette.WindowText, Qt.blue)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.setFixedSize(660, 400)
        self.setScaledContents(True)
        self.setFont(font)
        self.show_text = QLabel("欢迎使用分析决策系统\n正在检查新版本...", self)
        self.show_text.setFont(font)
        self.show_text.setFixedSize(self.width(), self.height())
        self.show_text.setAlignment(Qt.AlignCenter)
        self.show_text.setPalette(self.red)
        # layout.addLayout(self.show_text)
        # self.showMessage("欢迎使用分析决策系统\n正在检查新版本...", Qt.AlignCenter, Qt.blue)

    def mousePressEvent(self, event):
        super(StartPage, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self._mouse_pos = event.pos()

    def mouseReleaseEvent(self, event):
        super(StartPage, self).mouseReleaseEvent(event)
        self._pressed = False
        self._mouse_pos = None

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._mouse_pos:
            self.move(self.mapToGlobal(event.pos() - self._mouse_pos))
        event.accept()

    # 启动检查版本
    def check_version(self):
        self.checking_thread = CheckUpdatingVersion()
        self.checking_thread.finished.connect(self.checking_thread.deleteLater)
        self.checking_thread.check_successful.connect(self.version_checked)
        self.checking_thread.start()

    def version_checked(self, result):
        # print('版本检测成功', result)
        if result['update']:
            self.show_text.setText("欢迎使用分析决策系统,正在准备更新\n检测到新版本{}".format(result['version']))
            # 线程下载文件到目录中
            self.downloading = DownloadNewVersion(result['file_list'], new_version=result['version'])
            self.downloading.finished.connect(self.downloading.deleteLater)
            self.downloading.file_downloading.connect(self.setProcessing)
            self.downloading.download_finished.connect(self.update_finished)
            self.downloading.download_fail.connect(self.update_fail)
            self.downloading.start()
        else:
            self.show_text.setText("欢迎使用分析决策系统\n系统正在启动中...")
            self.show_text.setPalette(self.blue)
            self.update_finished()

    def setProcessing(self, current_index, total_count, file_name):
        rate = (current_index / total_count) * 100
        file_name = os.path.split(file_name)[1]
        self.show_text.setText("欢迎使用分析决策系统\n系统正在更新中...\n"+file_name+"\n{:.0f}%".format(rate))
        self.show_text.setPalette(self.blue)

    def update_fail(self, error):
        self.show_text.setText("欢迎使用分析决策系统\n系统更新失败...\n{}".format(error))
        self.show_text.setPalette(self.red)
        time.sleep(2)
        self.close()
        sys.exit()

    def update_finished(self):
        # 更新完成，执行系统主程序mkdecision.py
        # if os.path.exists("mkdecision.py"):
        #     os.system("python mkdecision.py")
        #     sys.exit()
        # self.deleteLater()
        if os.path.exists("mkdecision.exe"):
            # os.system("mkdecision.exe")
            Popen('mkdecision.exe', shell=False)
        self.close()
        sys.exit()


app = QApplication(sys.argv)
splash = StartPage()
splash.show()
app.processEvents()
splash.check_version()
sys.exit(app.exec_())
