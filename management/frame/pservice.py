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
from fitz.fitz import Document
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QTextBrowser, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

import config
from thread.request import RequestThread
from widgets.base import Loading, TableShow


class MarketAnalysis(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(MarketAnalysis, self).__init__(*args, **kwargs)
        self.setWidgetResizable(True)
        layout = QVBoxLayout()
        loading_layout = QHBoxLayout(self)
        self.loading = Loading()
        self.show_table = TableShow()
        self.container = QWidget()
        # signal
        self.show_table.cellClicked.connect(self.show_table_clicked)
        loading_layout.addWidget(self.loading)
        layout.addWidget(self.show_table)
        self.container.setLayout(layout)
        self.get_content_to_show()

    def get_content_to_show(self):
        self.loading.show()
        self.show_table.clear()
        self.mls_thread = RequestThread(
            url=config.SERVER_ADDR + 'pservice/consult/file/?mark=mls',
            method='get',
            data=json.dumps({'machine_code': config.app_dawn.value('machine')}),
            cookies=config.app_dawn.value('cookies')
        )
        self.mls_thread.response_signal.connect(self.mls_thread_back)
        self.mls_thread.finished.connect(self.mls_thread.deleteLater)
        self.mls_thread.start()

    def mls_thread_back(self, content):
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

    def show_table_clicked(self, row, col):
        print('frame.pservice.py {} 点击市场分析:'.format(str(sys._getframe().f_lineno)), row, col)
        if col == 3:
            item = self.show_table.item(row, col)
            try:
                response = requests.get(url=config.SERVER_ADDR + item.file, headers=config.CLIENT_HEADERS)
                doc = Document(filename=item.title, stream=response.content)
                popup = PDFReader(doc=doc, title=item.title)
            except Exception as error:
                QMessageBox.information(self, "错误", '查看文件失败.\n{}'.format(error), QMessageBox.Yes)
                return
            if not popup.exec():
                del popup


class MsgCommunication(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(MsgCommunication, self).__init__(*args, **kwargs)
        self.setWidgetResizable(True)
        self.container = QWidget()
        layout = QVBoxLayout()
        # show data loading
        self.loading = Loading()
        self.loading.clicked.connect(self.get_message_communication)
        loading_layout = QVBoxLayout(self)
        loading_layout.addWidget(self.loading)
        self.container.setLayout(layout)
        self.setStyleSheet("""
        QTextBrowser{
            border: none;
            border-bottom: 1px solid rgb(200,200,200)
        }
        QTextBrowser:hover{
            background:rgb(220,220,220);   
        }
        """)
        self.get_message_communication()


    def get_message_communication(self):
        self.loading.show()
        self.msg_thread = RequestThread(
            url=config.SERVER_ADDR + 'pservice/consult/msg/',
            method='get',
            data=json.dumps({'machine_code': config.app_dawn.value('machine')}),
            cookies=config.app_dawn.value('cookies')
        )
        self.msg_thread.response_signal.connect(self.msg_thread_back)
        self.msg_thread.finished.connect(self.msg_thread.deleteLater)
        self.msg_thread.start()

    def msg_thread_back(self, content):
        print('frame.pservice.py {} 短信通数据: '.format(sys._getframe().f_lineno), content)
        if content['error']:
            self.loading.retry()
            return
        if not content['data']:
            self.loading.no_data()
            return
        self.loading.hide()
        # show content
        for item in content['data']:
            content = "<h2 style='display:inline-block'>" + item['title'] + "</h2>" + \
                              "<span style='display:inline-block'>" + item['create_time'] + "</span>" + \
                          item['content']
            text_browser = QTextBrowser()
            text_browser.setText(content)
            text_browser.setMinimumHeight(text_browser.document().lineCount() * 30)
            self.container.layout().addWidget(text_browser)

        self.setWidget(self.container)


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

class ResearchReport(MarketAnalysis):
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



class TopicalStudy(QScrollArea):
    def __init__(self, *args, **kwargs):
        super(TopicalStudy, self).__init__(*args, **kwargs)
        self.setWidgetResizable(True)
        layout = QVBoxLayout()
        loading_layout = QHBoxLayout(self)
        self.loading = Loading()
        self.show_table = TableShow()
        self.container = QWidget()
        # signal
        self.show_table.cellClicked.connect(self.show_table_clicked)
        loading_layout.addWidget(self.loading)
        layout.addWidget(self.show_table)
        self.container.setLayout(layout)
        self.get_content_to_show()

    def get_content_to_show(self):
        self.loading.show()
        self.show_table.clear()
        self.tps_thread = RequestThread(
            url=config.SERVER_ADDR + 'pservice/consult/file/?mark=tps',
            method='get',
            data=json.dumps({'machine_code': config.app_dawn.value('machine')}),
            cookies=config.app_dawn.value('cookies')
        )
        self.tps_thread.response_signal.connect(self.tps_thread_back)
        self.tps_thread.finished.connect(self.tps_thread.deleteLater)
        self.tps_thread.start()

    def tps_thread_back(self, content):
        print('frame.pservice.py {} 专题研究文件: '.format(sys._getframe().f_lineno), content)
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

    def show_table_clicked(self, row, col):
        print('frame.pservice.py {} 点击专题研究:'.format(str(sys._getframe().f_lineno)), row, col)
        if col == 3:
            item = self.show_table.item(row, col)
            try:
                response = requests.get(url=config.SERVER_ADDR + item.file, headers=config.CLIENT_HEADERS)
                doc = Document(filename=item.title, stream=response.content)
                popup = PDFReader(doc=doc, title=item.title)
            except Exception as error:
                QMessageBox.information(self, "错误", '查看文件失败.\n{}'.format(error), QMessageBox.Yes)
                return
            if not popup.exec():
                del popup

