# _*_ coding:utf-8 _*_
"""
product service frame
Create: 2019-08-07
Author: zizle
"""
import sys
import json
import requests
from lxml import etree
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QTextBrowser, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

import config
from thread.request import RequestThread
from widgets.base import Loading, TableShow


class MarketAnalysis(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(MarketAnalysis, self).__init__(*args, **kwargs)
        # widget
        self.table = TableShow()
        # style
        # self.table.verticalHeader().setSectionResizeMode(0)
        self.setWidgetResizable(True)
        self.setWidget(self.table)
        # init data
        self.get_thread = None
        self.get_market_analysis()

    def get_market_analysis(self):
        if self.get_thread:
            del self.get_thread
        self.get_thread = RequestThread(
            url=config.SERVER_ADDR + 'pservice/consult/mks/',
            method='get',
            data=json.dumps({'machine_code': config.app_dawn.value('machine')}),
            cookies=config.app_dawn.value('cookies')
        )
        self.get_thread.response_signal.connect(self.get_thread_back)
        self.get_thread.finished.connect(self.get_thread.deleteLater)
        self.get_thread.start()

    def get_thread_back(self, signal):
        print('frame.pservice.py {} 市场分析数据: '.format(sys._getframe().f_lineno), signal)
        if signal['error']:
            return
        # 展示数据
        header_couple = [('serial_num', '序号'), ('title', '标题'), ('create_time', '上传时间'), ('to_look', '')]
        self.table.show_content(contents=signal['data'], header_couple=header_couple)


class MessageComm(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(MessageComm, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.expandingDirections()
        # widgets
        self.container = QWidget()
        # style
        self.container.setLayout(layout)
        self.setWidgetResizable(True)
        self.setStyleSheet("""
        QTextBrowser{
            border: none;
            border-bottom: 1px solid rgb(200,200,200)
        }
        QTextBrowser:hover{
            background:rgb(220,220,220);
        }
        """)
        # 添加显示widget只能在填充内容之后，不然无法看见内容，所以在线程回来处理内容后添加
        # initial data
        self.msg_thread = None
        self.get_message_comm()

    def get_message_comm(self):
        if self.msg_thread:
            del self.msg_thread
        self.msg_thread = RequestThread(
            url=config.SERVER_ADDR + 'pservice/consult/msg/',
            method='get',
            data=json.dumps({'machine_code': config.app_dawn.value('machine')}),
            cookies=config.app_dawn.value('cookies')
        )
        self.msg_thread.response_signal.connect(self.msg_thread_back)
        self.msg_thread.finished.connect(self.msg_thread.deleteLater)
        self.msg_thread.start()

    def msg_thread_back(self, signal):
        print('frame.pservice.py {} 短信通数据: '.format(sys._getframe().f_lineno), signal)
        if signal['error']:
            return
        for item in signal['data'] * 5:
            content = "<h2>" + item['title'] + "</h2>" + \
                              "<span style='display:inline-block'>" + item['create_time'] + "</span>" + \
                          item['content']
            text_browser = QTextBrowser()
            text_browser.document().adjustSize()
            text_browser.setText(content)
            h = text_browser.document().size().height()
            text_browser.setMinimumHeight(h + 20)
            self.container.layout().addWidget(text_browser)
        self.container.layout().addStretch()
        self.setWidget(self.container)


class TopicalStudy(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(TopicalStudy, self).__init__(*args, **kwargs)
        # widget
        self.table = TableShow()
        # style
        self.table.verticalHeader().setSectionResizeMode(0)
        self.setWidgetResizable(True)
        self.setWidget(self.table)
        # init data
        self.get_thread = None
        self.get_topical_study()

    def get_topical_study(self):
        if self.get_thread:
            del self.get_thread
        self.get_thread = RequestThread(
            url=config.SERVER_ADDR + 'pservice/consult/tps/',
            method='get',
            data=json.dumps({'machine_code': config.app_dawn.value('machine')}),
            cookies=config.app_dawn.value('cookies')
        )
        self.get_thread.response_signal.connect(self.get_thread_back)
        self.get_thread.finished.connect(self.get_thread.deleteLater)
        self.get_thread.start()

    def get_thread_back(self, signal):
        print('frame.pservice.py {} 专题研究数据: '.format(sys._getframe().f_lineno), signal)
        if signal['error']:
            return
        # 展示数据
        header_couple = [('serial_num', '序号'), ('title', '标题'), ('create_time', '上传时间'), ('to_look', '')]
        self.table.show_content(contents=signal['data'], header_couple=header_couple)


class ResearchReport(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(ResearchReport, self).__init__(*args, **kwargs)
        # widget
        self.table = TableShow()
        # style
        self.table.verticalHeader().setSectionResizeMode(0)
        self.setWidgetResizable(True)
        self.setWidget(self.table)
        # init data
        self.get_thread = None
        self.get_research_report()

    def get_research_report(self):
        if self.get_thread:
            del self.get_thread
        self.get_thread = RequestThread(
            url=config.SERVER_ADDR + 'pservice/consult/rsr/',
            method='get',
            data=json.dumps({'machine_code': config.app_dawn.value('machine')}),
            cookies=config.app_dawn.value('cookies')
        )
        self.get_thread.response_signal.connect(self.get_thread_back)
        self.get_thread.finished.connect(self.get_thread.deleteLater)
        self.get_thread.start()

    def get_thread_back(self, signal):
        print('frame.pservice.py {} 调研报告数据: '.format(sys._getframe().f_lineno), signal)
        if signal['error']:
            return
        # 展示数据
        header_couple = [('serial_num', '序号'), ('title', '标题'), ('create_time', '上传时间'), ('to_look', '')]
        self.table.show_content(contents=signal['data'], header_couple=header_couple)









class PersonTrain(QScrollArea):
    def __init__(self):
        super(PersonTrain, self).__init__()
        self.setWidgetResizable(True)
        layout = QVBoxLayout(spacing=0)
        self.loading = Loading()
        layout.addWidget(self.loading)
        self.window = QWidget()
        self.window.setLayout(layout)
        self.show_content()
        self.setWidget(self.window)
        self.setStyleSheet("""
        QTextBrowser{
            border:none;
            line-height:30px;
        }
        QLabel{
            background-color:rgb(255,255,255);
            font-size:20px;
            font-weight:bold;
        }
        """)

    def show_content(self):
        # get article from server
        self.loading.show()
        try:
            response = requests.get(
                url=config.SERVER_ADDR + 'pservice/adviser/pst/',
                data=json.dumps({'machine_code': config.app_dawn.value('machine')}),
                cookies=config.app_dawn.value('cookies')
            )
        except Exception as error:
            QMessageBox(self, '错误', '请求数据失败.{}'.format(error), QMessageBox.Yes)
            self.loading.hide()
            return
        response_data = json.loads(response.content.decode('utf-8'))
        article = response_data['data']
        html = etree.HTML(article['content'])
        all_element = html.xpath('//*')
        text = ''
        title = QLabel(article['title'])
        title.setAlignment(Qt.AlignCenter)
        self.window.layout().addWidget(title)
        for element in all_element:
            if element.tag == 'p':
                # print('p标签', element.xpath('string()'))
                # 整理要显示文本
                text += '<p style=text-indent:30px;font-size:15px;line-height:20px>' + element.xpath('string()') + '</p>'
            elif element.tag == 'image':
                # 重置已显示文本,  添加图片
                # print('image标签', element)
                text_browser = QTextBrowser()
                text_browser.setText(text)
                text_browser.setMaximumHeight(50*text_browser.document().lineCount())
                self.window.layout().addWidget(text_browser)
                text = ''
                # 处理图片
                src = config.SERVER_ADDR + element.xpath('@src')[0]
                pixmap = QPixmap()
                img_label = QLabel()
                response = requests.get(src).content
                pixmap.loadFromData(response)
                img_label.setPixmap(pixmap)
                self.window.layout().addWidget(img_label)
            else:
                continue
        if text:
            # 还有文本，还需显示
            text_browser = QTextBrowser()
            text_browser.setText(text)
            text_browser.setMaximumHeight(50 * text_browser.document().lineCount())
            self.window.layout().addWidget(text_browser)
            text = ''
        self.window.layout().addStretch()
        self.loading.hide()

class ResearchReport1(MarketAnalysis):
    def get_content_to_show(self):
        self.loading.show()
        self.show_table.clear()
        self.rsr_thread = RequestThread(
            url=config.SERVER_ADDR + 'pservice/consult/file/?mark=rsr',
            method='get',
            data=json.dumps({'machine_code': config.app_dawn.value('machine')}),
            cookies=config.app_dawn.value('cookies')
        )
        self.rsr_thread.response_signal.connect(self.rsr_thread_back)
        self.rsr_thread.finished.connect(self.rsr_thread.deleteLater)
        self.rsr_thread.start()

    def rsr_thread_back(self, content):
        print('frame.pservice.py {} 市场分析文件: '.format(sys._getframe().f_lineno), content)
        if content['error']:
            self.loading.retry()
            return
        if not content['data']:
            self.loading.no_data()
            return
        self.loading.hide()
        # fill show table
        header_couple = [
            ('serial_num', '序号'),
            ('title', '标题'),
            ('create_time', '上传时间'),
            ('to_look', ' ')
        ]
        self.show_table.show_content(contents=content['data'], header_couple=header_couple)
        self.setWidget(self.container)




