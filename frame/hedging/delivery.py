# _*_ coding: utf-8 _*_
# Author: zizle QQ: 462894999
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
import settings
from widgets.base import PDFContentPopup

from frame.hedging.channels import DeliveryChannel


# 交割服务页面承载
class DeliveryServicePage(QWebEngineView):
    def __init__(self, navigation_bar_channel, *args, **kwargs):
        super(DeliveryServicePage, self).__init__(*args, **kwargs)
        navigation_bar_channel.userHasLogin.connect(self.send_token_to_web)  # 当用户登录时发送token到网页面
        # 定时向网页发送用户token
        self.send_token_timer = QTimer()
        self.send_token_timer.timeout.connect(self.send_token_to_web)  # 发送token给网页
        self.page().load(QUrl("file:///pages/hedging/delivery/index.html"))  # 加载页面
        channel_qt_obj = QWebChannel(self.page())  # 实例化qt信道对象,必须传入页面参数
        self.contact_channel = DeliveryChannel()  # 页面信息交互通道
        self.contact_channel.receivedUserTokenBack.connect(self.web_has_received_token)  # 收到token的回馈
        self.contact_channel.moreCommunicationSig.connect(self.more_communication)  # 更多讨论交流页面
        self.contact_channel.linkUsPageSig.connect(self.to_link_us_page)  # 关于我们的界面
        self.contact_channel.getVarietyInfoFile.connect(self.get_variety_information_file)  # 弹窗显示品种的相关PDF文件
        self.page().setWebChannel(channel_qt_obj)
        channel_qt_obj.registerObject("pageContactChannel", self.contact_channel)  # 信道对象注册信道，只能注册一个
        self.send_token_timer.start(8000)

    def contextMenuEvent(self, event):
        # 禁止右击菜单行为
        pass

    # 定时向网页发送用户token
    def send_token_to_web(self):
        token = settings.app_dawn.value('AUTHORIZATION')
        self.contact_channel.senderUserToken.emit(token)

    def web_has_received_token(self, boolean):
        if self.send_token_timer.isActive():
            self.send_token_timer.stop()

    # 更多交流讨论
    def more_communication(self, b):
        if b:
            self.page().load(QUrl("file:///pages/hedging/delivery/communication.html"))

    def to_link_us_page(self, b):
        if b:
            self.page().load(QUrl("file:///pages/hedging/delivery/linkus.html"))

    def get_variety_information_file(self, file_url):
        file_name = file_url.rsplit('/', 1)[1]
        popup = PDFContentPopup(title=file_name, file=file_url, parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup

