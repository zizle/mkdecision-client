# _*_ coding:utf-8 _*_
# Author: zizle  QQ:462894999
"""  启动程序,检查更新 """
import os
import sys
import json
import time
import requests
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import settings

# 线程检测是否更新版本
class CheckUpdatingVersion(QThread):
    check_successful = pyqtSignal(dict)
    def run(self):
        try:
            version = settings.app_dawn.value('VERSION')
            if version:
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

    def __init__(self, file_list, *args, **kwargs):
        super(DownloadNewVersion, self).__init__(*args, **kwargs)
        self.file_list = file_list
        self.file_count = len(file_list)

    def run(self):
        for index, file in enumerate(self.file_list):
            time.sleep(0.001)
            self.file_downloading.emit(index + 1, self.file_count)
        # 下载完成
        self.download_finished.emit(True)


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
            self.showMessage("欢迎使用分析决策系统\n系统正在更新中 0%", Qt.AlignCenter, Qt.red)
            # 线程下载文件到目录中
            self.downloading = DownloadNewVersion(result['file_list'])
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
            if rate > 100:
                rate = 100
            self.showMessage("欢迎使用分析决策系统\n系统正在更新中... {:.0f}%".format(rate), Qt.AlignCenter, Qt.red)
        except Exception as e:
            print(e)

    def update_finished(self):
        # self.showMessage("欢迎使用分析决策系统\n系统正在启动中...", Qt.AlignCenter, Qt.blue)
        self.close()
        # 更新完成，执行系统主程序main.py
        os.system("python main.py")
        # os.system("main.exe")


app = QApplication(sys.argv)
splash = StartPage()
splash.show()
app.processEvents()
splash.check_version()
sys.exit(app.exec_())



