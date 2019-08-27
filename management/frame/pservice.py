# _*_ coding:utf-8 _*_
"""
product service frame
Create: 2019-08-07
Author: zizle
"""
import sys
import json
import fitz
import requests
from lxml import etree
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QTextBrowser, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

import config
from thread.request import RequestThread
from widgets.base import Loading, TableShow


"""咨询服务"""
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


"""顾问服务"""
class AdviserShow(QScrollArea):
    def __init__(self, category, *args):
        super(AdviserShow, self).__init__(*args)
        self.category = category
        self.file_name = '查看文件'
        layout = QVBoxLayout()
        self.container = QWidget()
        self.container.setLayout(layout)
        # init pages
        # 请求文件
        file_url = self.get_file_url()
        print(file_url)
        self.add_pages(file_url)
        self.setWidget(self.container)

    def get_file_url(self):
        try:
            response = requests.get(
                url=config.SERVER_ADDR + 'pservice/adviser/',
                headers=config.CLIENT_HEADERS,
                data=json.dumps({'machine_code': config.app_dawn.value('machine'), 'category': self.category})
            )
            response_data = json.loads(response.content.decode('utf-8'))
            if response.status_code != 200:
                raise ValueError(response_data['message'])
        except Exception as e:
            return None
        return response_data['data']['file']

    def add_pages(self, file):
        # 请求文件
        if not file:
            message_label = QLabel('没有数据.')
            self.container.layout().addWidget(message_label)
            return
        try:
            response = requests.get(config.SERVER_ADDR + file)
            doc = fitz.Document(filename=self.file_name, stream=response.content)
        except Exception as e:
            message_label = QLabel('获取文件内容失败.\n{}'.format(e))
            self.container.layout().addWidget(message_label)
            return
        for page_index in range(doc.pageCount):
            page = doc.loadPage(page_index)
            page_label = QLabel()
            page_label.setMinimumSize(self.width() - 20, self.height())  # 设置label大小
            # show PDF content
            zoom_matrix = fitz.Matrix(1.58, 1.5)  # 图像缩放比例
            pagePixmap = page.getPixmap(
                matrix=zoom_matrix,
                alpha=False)
            imageFormat = QImage.Format_RGB888  # get image format
            pageQImage = QImage(
                pagePixmap.samples,
                pagePixmap.width,
                pagePixmap.height,
                pagePixmap.stride,
                imageFormat)  # init QImage
            page_map = QPixmap()
            page_map.convertFromImage(pageQImage)
            page_label.setPixmap(page_map)
            page_label.setScaledContents(True)  # pixmap resize with label
            self.container.layout().addWidget(page_label)


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
