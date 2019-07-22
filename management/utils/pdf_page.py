# _*_ coding:utf-8 _*_
# author: zizle
# Date: 20190507

import fitz
from PyQt5.QtGui import *


def render_pdf_page(page_data, *, size=(1.58, 1.5)):
    """显示 PDF 每页内容"""
    # 图像缩放比例
    a, b = size
    zoom_matrix = fitz.Matrix(a, b)
    # 获取封面对应的 Pixmap 对象
    # alpha 设置背景为白色
    pagePixmap = page_data.getPixmap(
        matrix=zoom_matrix,
        alpha=False)
    # 获取 image 格式
    imageFormat = QImage.Format_RGB888
    # 生成 QImage 对象
    pageQImage = QImage(
        pagePixmap.samples,
        pagePixmap.width,
        pagePixmap.height,
        pagePixmap.stride,
        imageFormat)

    # 生成 pixmap 对象
    pixmap = QPixmap()
    pixmap.convertFromImage(pageQImage)
    return pixmap

