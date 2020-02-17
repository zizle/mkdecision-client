# _*_ coding:utf-8 _*_
# Author: zizle  QQ:462894999
"""  启动程序,检查更新 """
import os
import sys
import json
import time
import hashlib
import requests
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import settings


# 文件所在目录
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))


# 线程检测是否更新版本
class CheckUpdatingVersion(QThread):
    check_successful = pyqtSignal(dict)

    def run(self):
        version = settings.app_dawn.value('VERSION')
        print(version)
        if not version:
            version = ""
        try:
            r = requests.get(url=settings.SERVER_ADDR + 'updating?version=' + str(version))
            if r.status_code != 200:
                raise ValueError('检测版本失败。')
            response = json.loads(r.content.decode('utf-8'))
        except Exception as e:
            pass
        else:
            self.check_successful.emit(response['data'])



# 线程下载新版本文件
class DownloadNewVersion(QThread):
    file_downloading = pyqtSignal(int, int)
    download_finished = pyqtSignal(bool)

    def __init__(self, file_list, new_version, *args, **kwargs):
        super(DownloadNewVersion, self).__init__(*args, **kwargs)
        self.file_list = file_list
        self.file_count = len(file_list)
        self.update_file_list = dict()
        self.new_version = new_version

    def run(self):
        # 获取本地文件
        self.find_local_files(BASE_DIR)
        for index, file in enumerate(self.file_list):
            time.sleep(0.00002)
            local_file_md5 = self.update_file_list.get(file)
            if local_file_md5 is not None:
                if local_file_md5 == self.file_list[file]: # 对比MD5的值
                    continue
            #     else:
            #         print('文件存在,md5 不相等，需要下载文件')
            # else:
            #     # 文件不存在，需要下载文件
            #     print('文件不存在,需要下载')
            self.download_file(file)
            self.file_downloading.emit(index + 1, self.file_count)
        # 下载完成
        settings.app_dawn.setValue('VERSION', str(self.new_version))
        self.download_finished.emit(True)

    # 请求下载文件
    def download_file(self, file_name):
        try:
            r = requests.get(url=settings.SERVER_ADDR + 'updating/download/',
                             data=json.dumps({'filename': file_name})
                             )
            file_path = os.path.join(BASE_DIR, file_name)
            file_name = open(file_path, 'wb')
            file_name.write(r.content)
        except Exception as e:
            pass

    # 计算文件的MD5
    def get_file_md5(self, filename):
        if not os.path.isfile(filename):
            return
        myHash = hashlib.md5()
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


class StartPage(QSplashScreen):
    def __init__(self, *args, **kwargs):
        super(StartPage, self).__init__(*args, *kwargs)
        self.setPixmap(QPixmap('media/start.png'))
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.setFont(font)
        self.showMessage("欢迎使用分析决策系统\n正在检查新版本...", Qt.AlignCenter, Qt.blue)

    # 启动检查版本
    def check_version(self):
        self.checking_thread = CheckUpdatingVersion()
        self.checking_thread.finished.connect(self.checking_thread.deleteLater)
        self.checking_thread.check_successful.connect(self.version_checked)
        self.checking_thread.start()

    def version_checked(self, result):
        print('版本检测成功', result)
        if result['update']:
            self.showMessage("欢迎使用分析决策系统\n检测到新版本{}".format(result['version']), Qt.AlignCenter, Qt.red)
            # 线程下载文件到目录中
            self.downloading = DownloadNewVersion(result['file_list'], new_version=result['version'])
            self.downloading.finished.connect(self.downloading.deleteLater)
            self.downloading.file_downloading.connect(self.setProcessing)
            self.downloading.download_finished.connect(self.update_finished)
            self.downloading.start()
        else:
            self.showMessage("欢迎使用分析决策系统\n系统正在启动中...", Qt.AlignCenter, Qt.blue)
            self.update_finished()

    def setProcessing(self, current_count, total_count):
        print(current_count, total_count)
        try:
            rate = (current_count / total_count ) * 100
            self.showMessage("欢迎使用分析决策系统\n系统正在更新中... {:.0f}%".format(rate), Qt.AlignCenter, Qt.red)
        except Exception as e:
            pass

    def update_finished(self):
        # self.showMessage("欢迎使用分析决策系统\n系统正在启动中...", Qt.AlignCenter, Qt.blue)
        # 写入新版本号
        self.close()
        # 更新完成，执行系统主程序main.py
        # if os.path.exists("main.py"):
        #     os.system("python main.py")
        #     sys.exit()
        if os.path.exists("main.exe"):
            os.system("main.exe")
            sys.exit()



app = QApplication(sys.argv)
splash = StartPage()
splash.show()
app.processEvents()
splash.check_version()
sys.exit(app.exec_())



