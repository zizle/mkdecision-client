
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class DeliveryChannel(QObject):
    senderUserToken = pyqtSignal(str)
    receivedUserTokenBack = pyqtSignal(bool)
    moreCommunicationSig = pyqtSignal(bool)
    linkUsPageSig = pyqtSignal(bool)
    getVarietyInfoFile = pyqtSignal(str)

    @pyqtSlot(bool)  # 暴露函数给JS调用
    def moreCommunication(self, boolean):  # 页面点击更多时调用
        self.moreCommunicationSig.emit(boolean)

    @pyqtSlot(bool)
    def hasReceivedUserToken(self, boolean):  # 收到token调用
        self.receivedUserTokenBack.emit(boolean)

    @pyqtSlot(bool)
    def toLinkUsPage(self, boolean):  # 跳转关于我们页面
        self.linkUsPageSig.emit(boolean)

    @pyqtSlot(str)
    def uiWebgetVarietyInfoFile(self, file_url):
        self.getVarietyInfoFile.emit(file_url)

