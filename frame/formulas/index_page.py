# _*_ coding:utf-8 _*_
# Author: zizle
import json
import requests
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import QUrl
from widgets.base import LoadedPage, ScrollFoldedBox
from frame.formulas import vlib
import settings

# 公式计算主页面
class FormulasCalculate(QWidget):
    def __init__(self, *args, **kwargs):
        super(FormulasCalculate, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=1,spacing=1)
        # 左边是品种的显示折叠窗
        self.variety_folded = ScrollFoldedBox()
        self.variety_folded.left_mouse_clicked.connect(self.variety_clicked)
        layout.addWidget(self.variety_folded)
        # 右侧显示页面的web浏览器
        self.web_browser = QWebEngineView()
        layout.addWidget(self.web_browser)
        self.setLayout(layout)
        # 设置折叠窗的样式
        self.variety_folded.setFoldedStyleSheet("""
            #foldedHead{
                background-color: rgb(145,202,182);
                border-bottom: 1px solid rgb(200,200,200);
                max-height: 30px;
            }
            #headLabel{
                padding:8px 5px;
                font-weight: bold;
                font-size: 15px;
            }
            #foldedBody{
                background-color: rgb(240, 240, 240);
            }
            /*折叠窗内滚动条样式*/
            #foldedBox QScrollBar:vertical{
                width: 5px;
                background: transparent;
            }
            #foldedBox QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 30);
                width: 5px;
                border-radius: 5px;
                border: none;
            }
            #foldedBox QScrollBar::handle:vertical:hover,QScrollBar::handle:horizontal:hover {
                background: rgba(0, 0, 0, 80);
            }
            """)

        # web页面加载
        self.web_browser.page().load(QUrl("file:///pages/formulas/index.html"))

    def resizeEvent(self, event):
        # 设置折叠窗的大小
        print('调整大小')
        box_width = self.parent().width() * 0.228
        self.variety_folded.setFixedWidth(box_width + 5)
        self.variety_folded.setBodyHorizationItemCount()

        # 获取所有品种组和品种

    def getGroupVarieties(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'group-varieties/?mc=' + settings.app_dawn.value('machine')
            )
            if r.status_code != 200:
                raise ValueError('获取失败!')
            response = json.loads(r.content.decode('utf-8'))
        except Exception:
            pass
        else:
            for group_item in response['data']:
                head = self.variety_folded.addHead(group_item['name'])
                body = self.variety_folded.addBody(head=head)
                body.addButtons([variety_item for variety_item in group_item['varieties'] if variety_item['is_active']])
            self.variety_folded.container.layout().addStretch()

    def variety_clicked(self, bid, head_text, v_en):
        # 拼接字符串
        if not v_en:
            return
        if v_en in ["a", "b"]:
            page_file = "file:///pages/formulas/variety/calculate_beans.html".format(v_en)
        else:
            page_file = "file:///pages/formulas/variety/no_found.html".format(v_en)
        self.web_browser.page().load(QUrl(page_file))