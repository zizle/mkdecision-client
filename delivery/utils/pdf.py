# _*_ coding:utf-8 _*_
"""

Create: 2019-
Author: zizle
"""
import fitz
import requests
from PyQt5.QtWidgets import QWidget, QPushButton, QScrollArea, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtGui import QIcon, QImage, QPixmap

class ShowServerPDF(QWidget):
    def __init__(self, file_url=None, file_name="查看PDF", *args):
        super(ShowServerPDF, self).__init__(*args)
        self.file = file_url
        self.file_name = file_name
        # auth doc type
        self.setWindowTitle(file_name)
        self.setMinimumSize(1000, 600)
        self.download = QPushButton("下载PDF")
        self.download.setIcon(QIcon('media/download-file.png'))
        self.setWindowIcon(QIcon("media/reader.png"))
        # scroll
        scroll_area = QScrollArea()
        scroll_area.horizontalScrollBar().setVisible(False)
        # content
        self.page_container = QWidget()
        self.page_container.setLayout(QVBoxLayout(margin=5))
        layout = QVBoxLayout(spacing=0)
        layout.setContentsMargins(0,0,0,0)
        # initial data
        self.add_pages()
        # add to show
        scroll_area.setWidget(self.page_container)
        # add layout
        # layout.addWidget(self.download, alignment=Qt.AlignLeft)
        layout.addWidget(scroll_area)
        self.setLayout(layout)
        self.setStyleSheet("QLabel {margin:5px 0} QTextEdit {border: none; color: rgb(0,0,0)} ShowServerPDF{border:none}")

    def add_pages(self):
        # ### 请求文件 ###
        if not self.file:
            message_label = QTextEdit('没有文件.')
            message_label.setEnabled(False)
            self.page_container.layout().addWidget(message_label)
            return
        try:
            response = requests.get(self.file)
            doc = fitz.Document(filename=self.file_name, stream=response.content)
        except Exception as e:
            message_label = QTextEdit('获取内容失败.404 Not Found!')
            message_label.setEnabled(False)
            self.page_container.layout().addWidget(message_label)
            return
        ### 请求文件 ###

        #### 打开文件 ######
        # try:
        #     with open('media/pdf/' + self.file_name, 'rb') as f:
        #         content = f.read()
        #     doc = fitz.Document(filename=self.file_name, stream=content)
        # except Exception as e:
        #     message_label = QLabel('没有相关内容.')
        #     self.page_container.layout().addWidget(message_label)
        #     return
        #### 打开文件 ######

        for page_index in range(doc.pageCount):
            page = doc.loadPage(page_index)
            page_label = QLabel()
            page_label.setMinimumSize(self.width() - 20, self.height())  # 设置label大小
            # show PDF content
            zoom_matrix = fitz.Matrix(1.5, 1.8)  # 图像缩放比例
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
            self.page_container.layout().addWidget(page_label)