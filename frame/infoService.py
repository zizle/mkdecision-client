# _*_ coding:utf-8 _*_
# __Author__： zizle
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from widgets.base import ScrollFoldedBox, LoadedPage


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
        print(sid, text)
