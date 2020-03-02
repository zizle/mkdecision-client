# _*_ coding:utf-8 _*_
"""

Create: 2019-09-03
Author: zizle
"""

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class ChannelObj(QObject):
    moreCommunicationSig = pyqtSignal(bool)
    newsBulletinShowSig = pyqtSignal(list)
    fileUrlSig = pyqtSignal(str)
    serviceGuideSig = pyqtSignal(list)
    userTokenSig = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtSlot(list)
    def serviceGuide(self, service_list):
        self.serviceGuideSig.emit(service_list)

    @pyqtSlot(bool)  # 暴露函数给JS调用
    def moreCommunication(self, boolean):
        self.moreCommunicationSig.emit(boolean)

    @pyqtSlot(list)
    def newsBulletinShow(self, list_param):
        self.newsBulletinShowSig.emit(list_param)

    @pyqtSlot(str)
    def fileUrlMessage(self, str_param):
        self.fileUrlSig.emit(str_param)

    @pyqtSlot(str)
    def userTokenMessage(self, str_param):
        self.userTokenSig.emit(str_param)


class NewsChannelObj(QObject):
    newsBulletinContentSig = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
    @pyqtSlot(list)
    def showDetail(self, list_param):
        self.newsBulletinContentSig.emit(list_param)

