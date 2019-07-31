# _*_ coding:utf-8 _*_
"""
popup in homepage
Create: 2019-07-31
Author: zizle
"""
import fitz
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QPushButton, QScrollArea, QLabel, QTextBrowser
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap

class ContentReader(QDialog):
    def __init__(self, content="<p>没有内容</p>", title="内容"):
        super(ContentReader, self).__init__()
        layout = QVBoxLayout()
        text_browser = QTextBrowser()
        text_browser.setStyleSheet("font-size:14px;")
        text_browser.setHtml(content)
        layout.addWidget(text_browser)
        self.setWindowTitle(title)
        self.setLayout(layout)

class PDFReader(QDialog):
    def __init__(self, doc=None, title="查看PDF"):
        super(PDFReader, self).__init__()
        # auth doc type
        self.setWindowTitle(title)
        self.setMinimumSize(1000, 600)
        self.download = QPushButton("下载PDF")
        self.download.setIcon(QIcon('media/download-file.png'))
        self.setWindowIcon(QIcon("media/reader.png"))
        # scroll
        scroll_area = QScrollArea()
        scroll_area.horizontalScrollBar().setVisible(False)
        # content
        self.page_container = QWidget()
        self.page_container.setLayout(QVBoxLayout())
        layout = QVBoxLayout()
        if not doc:
            label = QLabel('没有内容.')
            self.page_container.layout().addWidget(label)
        else:
            self.add_pages(doc)
        scroll_area.setWidget(self.page_container)
        # add layout
        layout.addWidget(self.download, alignment=Qt.AlignLeft)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def add_pages(self, doc):
        if not isinstance(doc, fitz.Document):
            raise ValueError("doc must be instance of class fitz.fitz.Document")
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
            self.page_container.layout().addWidget(page_label)
