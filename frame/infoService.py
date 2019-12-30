# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import chardet
import requests
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QTableWidget, QTextBrowser
from widgets.base import ScrollFoldedBox, LoadedPage
from PyQt5.QtCore import Qt, QDate, QTime, QMargins
import settings

""" 市场分析 """


# 市场分析主页
class MarketAnalysisPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(MarketAnalysisPage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setLayout(layout)


""" 短信通 """


# 短信通控件
class SMSLinkWidget(QWidget):
    def __init__(self, sms_data, *args, **kwargs):
        super(SMSLinkWidget, self).__init__(*args, **kwargs)
        self.sms_id = sms_data['id']
        layout = QVBoxLayout(margin=0, spacing=1)
        date = QDate.fromString(sms_data['date'], 'yyyy-MM-dd')
        time = QTime.fromString(sms_data['time'], 'HH:mm:ss')
        date_time = date.toString('yyyy-MM-dd ') + time.toString('HH:mm') if date != QDate.currentDate() else time.toString('HH:mm')
        layout.addWidget(QLabel(date_time, objectName='timeLabel'))
        self.text_browser = QTextBrowser(objectName='textBrowser')
        self.text_browser.setText(sms_data['content'])
        layout.addWidget(self.text_browser)
        self.setLayout(layout)
        self.setStyleSheet("""
        #timeLabel{
            font-size:12px;
            color: rgb(50,70,100);
            font-weight: bold;
        }
        #textBrowser{
            margin:0 0 2px 25px;
            border:1px solid rgb(210,210,210);
            font-size:13px;
            color: rgb(0,0,0);
            border-radius: 5px;
            background-color:rgb(225,225,225)
        }
        """)


# 短信通主页
class SMSLinkPage(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(SMSLinkPage, self).__init__(*args, **kwargs)
        self.container = QWidget()
        layout = QVBoxLayout()
        self.container.setLayout(layout)
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        # # 设置滚动条样式
        # with open("media/ScrollBar.qss", "rb") as fp:
        #     content = fp.read()
        #     encoding = chardet.detect(content) or {}
        #     content = content.decode(encoding.get("encoding") or "utf-8")
        # self.setStyleSheet(content)

    # 请求数据
    def getSMSContents(self):
        try:
            r = requests.get(url=settings.SERVER_ADDR + 'info/sms/?mc=' + settings.app_dawn.value('machine'))
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError('获取数据失败.')
        except Exception:
            return
        else:
            for sms_item in response['data']:
                self.container.layout().addWidget(SMSLinkWidget(sms_item))


# 产品服务主页
class InfoServicePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(InfoServicePage, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=2)
        self.variety_folded = ScrollFoldedBox()
        self.variety_folded.left_mouse_clicked.connect(self.enter_service)
        self.variety_folded.setMaximumWidth(250)
        layout.addWidget(self.variety_folded)
        self.frame = LoadedPage()
        layout.addWidget(self.frame)
        self.setLayout(layout)
        self._addServiceContents()

    # 获取所有品种组和品种
    def _addServiceContents(self):
        contents = [
            {
                'name': u'咨询服务',
                'subs': [
                    {'id': 1, 'name': u'短信通'},
                    {'id': 2, 'name': u'市场分析'},
                    {'id': 3, 'name': u'专题研究'},
                    {'id': 4, 'name': u'调研报告'},
                    {'id': 5, 'name': u'市场路演'},
                ]
            },
            {
                'name': u'顾问服务',
                'subs': [
                    {'id': 6, 'name': u'人才培养'},
                    {'id': 7, 'name': u'部门组建'},
                    {'id': 8, 'name': u'制度考核'},
                ]
            },
            {
                'name': u'策略服务',
                'subs': [
                    {'id': 9, 'name': u'交易策略'},
                    {'id': 10, 'name': u'投资方案'},
                    {'id': 11, 'name': u'套保方案'},
                ]
            },
            {
                'name': u'培训服务',
                'subs': [
                    {'id': 12, 'name': u'品种介绍'},
                    {'id': 13, 'name': u'基本分析'},
                    {'id': 14, 'name': u'技术分析'},
                    {'id': 15, 'name': u'制度规则'},
                    {'id': 16, 'name': u'交易管理'},
                    {'id': 17, 'name': u'经验分享'},
                ]
            },
        ]
        for group_item in contents:
            head = self.variety_folded.addHead(group_item['name'])
            body = self.variety_folded.addBody(head=head)
            body.addButtons(group_item['subs'])
        self.variety_folded.container.layout().addStretch()

    # 点击服务，显示页面
    def enter_service(self, sid, text):
        if sid == 1:  # 短信通
            page = SMSLinkPage(parent=self.frame)
            page.getSMSContents()
        elif sid == 2: # 市场分析
            page = MarketAnalysisPage(parent=self.frame)
        else:
            page = QLabel('当前模块正在加紧开放...',
                          styleSheet='color:rgb(50,180,100); font-size:15px;font-weight:bold', alignment=Qt.AlignCenter)
        self.frame.clear()
        self.frame.addWidget(page)
