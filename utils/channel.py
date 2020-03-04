# _*_ coding:utf-8 _*_
# Author: zizle

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


# 主窗口与webView交互信道
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


class DeliveryChannel(QObject):
    userHasLogin = pyqtSignal(str)  # 用户已经登录的信号，由此发出给js
    hasReceivedUserToken = pyqtSignal(bool)
    moreCommunicationSig = pyqtSignal(bool)

    @pyqtSlot(bool)  # 暴露函数给JS调用
    def moreCommunication(self, boolean):  # 页面点击更多时调用
        self.moreCommunicationSig.emit(boolean)

    @pyqtSlot(bool)
    def webHasReceivedUserToken(self, boolean):  # 收到token调用
        self.hasReceivedUserToken.emit(boolean)



