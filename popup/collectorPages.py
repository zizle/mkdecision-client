# _*_ coding:utf-8 _*_
# __Author__： zizle
import re
import json
import hashlib
import requests
from PIL import Image
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton, QLineEdit, \
    QTextEdit, QFileDialog
from PyQt5.QtCore import Qt
import settings


# 新增新闻
class CreateNewsPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateNewsPopup, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        category_select_layout = QHBoxLayout()
        category_select_layout.addWidget(QLabel('显示类型:'), alignment=Qt.AlignLeft)
        self.category_combo = QComboBox(currentIndexChanged=self.category_combo_selected)
        category_select_layout.addWidget(self.category_combo)
        # 错误提示
        self.error_message_label = QLabel()
        category_select_layout.addWidget(self.error_message_label)
        category_select_layout.addStretch()
        layout.addLayout(category_select_layout)
        # 公告名称
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel('公告名称:'))
        self.news_title_edit = QLineEdit()
        title_layout.addWidget(self.news_title_edit)
        layout.addLayout(title_layout)

        # 文件选择
        self.file_widget = QWidget(parent=self)
        file_widget_layout = QHBoxLayout(margin=0)
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setEnabled(False)
        file_widget_layout.addWidget(QLabel('文件:'), alignment=Qt.AlignLeft)
        file_widget_layout.addWidget(self.file_path_edit)
        file_widget_layout.addWidget(QPushButton('浏览', clicked=self.browser_file))
        self.file_widget.setLayout(file_widget_layout)
        layout.addWidget(self.file_widget)
        # 文字输入
        self.text_widget = QWidget(parent=self)
        text_widget_layout = QHBoxLayout(margin=0)
        self.text_edit = QTextEdit()
        text_widget_layout.addWidget(QLabel('内容:'), alignment=Qt.AlignLeft)
        text_widget_layout.addWidget(self.text_edit)
        self.text_widget.setLayout(text_widget_layout)
        layout.addWidget(self.text_widget)
        # 提交按钮
        self.commit_button = QPushButton('确认提交', clicked=self.commit_news_bulletin)
        layout.addWidget(self.commit_button)
        layout.addStretch()
        self.setLayout(layout)
        self.setWindowTitle('新增公告')
        self._addCategoryCombo()

    # 类型选择的内容
    def _addCategoryCombo(self):
        for item in [(u'上传文件', 'file'), (u'上传内容', 'content')]:
            self.category_combo.addItem(item[0], item[1])

    # 确认上传新闻公告
    def commit_news_bulletin(self):
        self.commit_button.setEnabled(False)
        # 获取上传的类型
        category = self.category_combo.currentData()
        title = re.sub(r'\s+', '', self.news_title_edit.text())
        if not title:
            self.error_message_label.setText('请输入公告名称!')
            return
        data = dict()
        data['title'] = title  # 标题
        if category == 'file':  # 上传文件
            file_path = self.file_path_edit.text()
            if not file_path:
                self.error_message_label.setText('请选择文件!')
                return
            file_name = file_path.rsplit('/', 1)[1]
            file = open(file_path, "rb")   # 获取文件
            file_content = file.read()
            file.close()
            # 文件内容字段
            data["file"] = (file_name, file_content)
        else:
            data['content'] = self.text_edit.toPlainText()
        encode_data = encode_multipart_formdata(data)
        final_data = encode_data[0]
        self.upload_news(data=final_data, content_type=encode_data[1])

    # 选择了显示的样式
    def category_combo_selected(self):
        current_category = self.category_combo.currentData()
        self.news_title_edit.clear()
        if current_category == 'file':
            self.text_widget.hide()
            self.file_widget.show()
        else:
            self.text_widget.show()
            self.file_widget.hide()

    # 选择上传的文件
    def browser_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files(*.pdf)")
        self.file_path_edit.setText(file_path)

    # 公告上传的请求
    def upload_news(self, data, content_type):
        try:
            # 发起上传请求
            r = requests.post(
                url=settings.SERVER_ADDR + 'home/news/?mc=' + settings.app_dawn.value('machine'),
                headers={
                    'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION'),
                    'Content-Type': content_type
                },
                data=data
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            self.error_message_label.setText(str(e))
        else:
            self.error_message_label.setText(response['message'])
        self.commit_button.setEnabled(True)
        self.close()


# 新增广告
class CreateAdvertisementPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateAdvertisementPopup, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        category_select_layout = QHBoxLayout()
        category_select_layout.addWidget(QLabel('显示类型:'), alignment=Qt.AlignLeft)
        self.category_combo = QComboBox(currentIndexChanged=self.category_combo_selected)
        category_select_layout.addWidget(self.category_combo)
        # 错误提示
        self.error_message_label = QLabel()
        category_select_layout.addWidget(self.error_message_label)
        category_select_layout.addStretch()
        layout.addLayout(category_select_layout)
        # 广告名称
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel('广告名称:'))
        self.advertisement_name_edit = QLineEdit()
        title_layout.addWidget(self.advertisement_name_edit)
        layout.addLayout(title_layout)
        # 广告图片
        image_layout = QHBoxLayout()
        image_layout.addWidget(QLabel('广告图片:'))
        self.advertisement_image_edit = QLineEdit()
        self.advertisement_image_edit.setEnabled(False)
        image_layout.addWidget(self.advertisement_image_edit)
        image_layout.addWidget(QPushButton('浏览', clicked=self.browser_image))
        layout.addLayout(image_layout)
        # 文件选择
        self.file_widget = QWidget(parent=self)
        file_widget_layout = QHBoxLayout(margin=0)
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setEnabled(False)
        file_widget_layout.addWidget(QLabel('广告文件:'), alignment=Qt.AlignLeft)
        file_widget_layout.addWidget(self.file_path_edit)
        file_widget_layout.addWidget(QPushButton('浏览', clicked=self.browser_file))
        self.file_widget.setLayout(file_widget_layout)
        layout.addWidget(self.file_widget)
        # 文字输入
        self.text_widget = QWidget(parent=self)
        text_widget_layout = QHBoxLayout(margin=0)
        self.text_edit = QTextEdit()
        text_widget_layout.addWidget(QLabel('广告内容:'), alignment=Qt.AlignLeft)
        text_widget_layout.addWidget(self.text_edit)
        self.text_widget.setLayout(text_widget_layout)
        layout.addWidget(self.text_widget)
        # 提交按钮
        self.commit_button = QPushButton('确认提交', clicked=self.commit_advertisement)
        layout.addWidget(self.commit_button)
        layout.addStretch()
        self.setWindowTitle('新增广告')
        self.setLayout(layout)
        self._addCategoryCombo()

    # 类型选择的内容
    def _addCategoryCombo(self):
        for item in [(u'上传文件', 'file'), (u'上传内容', 'content')]:
            self.category_combo.addItem(item[0], item[1])

    # 类型选择变化
    def category_combo_selected(self):
        current_category = self.category_combo.currentData()
        self.advertisement_name_edit.clear()
        if current_category == 'file':
            self.text_widget.hide()
            self.file_widget.show()
        else:
            self.text_widget.show()
            self.file_widget.hide()

    # 选择上传的文件
    def browser_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files(*.pdf)")
        self.file_path_edit.setText(file_path)

    # 选择广告图片
    def browser_image(self):
        self.error_message_label.setText('')
        image_path, _ = QFileDialog.getOpenFileName(self, '打开图片', '', "png files(*.png)")
        if image_path:
            # 对文件的大小进行限制
            img = Image.open(image_path)
            print(img.size[0], img.size[1])
            if 520 <= img.size[0] <= 660 and 260 <= img.size[1] <= 330:
                self.advertisement_image_edit.setText(image_path)
            else:
                self.error_message_label.setText('宽:520~660像素;高:260~330像素')

    def commit_advertisement(self):
        self.commit_button.setEnabled(False)
        # 获取上传的类型
        category = self.category_combo.currentData()
        name = re.sub(r'\s+', '', self.advertisement_name_edit.text())
        if not name:
            self.error_message_label.setText('请输入逛名称!')
            return
        image_path = self.advertisement_image_edit.text()
        if not image_path:
            self.error_message_label.setText('请选择广告图片!')
            return
        data = dict()
        image_name = self.hash_image_name(image_path.rsplit('/', 1)[1])
        image = open(image_path, 'rb')
        image_content = image.read()
        image.close()
        data['image'] = (image_name, image_content)
        data['name'] = name  # 标题
        if category == 'file':  # 上传文件
            file_path = self.file_path_edit.text()
            if not file_path:
                self.error_message_label.setText('请选择文件!')
                return
            file_name = file_path.rsplit('/', 1)[1]
            file = open(file_path, "rb")  # 获取文件
            file_content = file.read()
            file.close()
            # 文件内容字段
            data["file"] = (file_name, file_content)
            data['content'] = ''
        else:
            content = self.text_edit.toPlainText()
            if not re.sub(r'\s+', '', content):
                self.error_message_label.setText('请输入内容！')
                return
            data['content'] = content
        encode_data = encode_multipart_formdata(data)
        final_data = encode_data[0]
        self.upload_advertisement(data=final_data, content_type=encode_data[1])

    # 哈希图片名称
    @staticmethod
    def hash_image_name(image_name):
        md = hashlib.md5()
        md.update(image_name.encode('utf-8'))
        return md.hexdigest() + '.png'

    # 上传广告内容
    def upload_advertisement(self, data, content_type):
        try:
            # 发起上传请求
            r = requests.post(
                url=settings.SERVER_ADDR + 'home/advertise/?mc=' + settings.app_dawn.value('machine'),
                headers={
                    'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION'),
                    'Content-Type': content_type
                },
                data=data
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            self.error_message_label.setText(str(e))
        else:
            self.error_message_label.setText(response['message'])
        self.commit_button.setEnabled(True)
        self.close()


