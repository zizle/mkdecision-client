# _*_ coding:utf-8 _*_
# __Author__： zizle
import re
import json
import hashlib
import requests
from PIL import Image
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QLabel, QPushButton, QLineEdit, \
    QTextEdit, QFileDialog, QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem, QDateEdit, QHeaderView, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QBrush, QColor
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
        image_path, _ = QFileDialog.getOpenFileName(self, '打开图片', '', "png file(*.png)")
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


# 上传常规报告线程
class UploadReportThread(QThread):
    response_signal = pyqtSignal(int, bool)

    def __init__(self, file_list, machine_code, token, *args, **kwargs):
        super(UploadReportThread, self).__init__(*args, **kwargs)
        self.file_list = file_list
        self.machine_code = machine_code
        self.token = token

    def run(self):
        for file_item in self.file_list:
            # 读取文件
            try:
                data_file = dict()
                # 增加其他字段
                data_file['name'] = file_item['file_name']
                data_file['date'] = file_item['file_date']
                data_file['category_id'] = file_item['category_id']
                data_file['variety_ids'] = str(file_item['variety_ids'])
                # 读取文件
                file = open(file_item['file_path'], "rb")
                file_content = file.read()
                file.close()
                # 文件内容字段
                data_file["file"] = (file_item['file_name'], file_content)
                encode_data = encode_multipart_formdata(data_file)
                data_file = encode_data[0]
                # 发起上传请求
                r = requests.post(
                    url=settings.SERVER_ADDR + 'home/normal-report/?mc=' + self.machine_code,
                    headers={
                        'AUTHORIZATION': self.token,
                        'Content-Type': encode_data[1]
                    },
                    data=data_file
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 201:
                    raise ValueError(response['message'])
            except Exception as e:
                with open('debug/normal_report.log', 'w') as f:
                    f.write(str(e) + '\n')
                self.response_signal.emit(file_item['row_index'], False)
            else:
                self.response_signal.emit(file_item['row_index'], True)


# 新增常规报告
class CreateReportPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateReportPopup, self).__init__(*args, **kwargs)
        # 总布局-左右
        layout = QHBoxLayout()
        # 左侧上下布局
        llayout = QVBoxLayout()
        # 左侧是品种树
        self.left_tree = QTreeWidget(clicked=self.variety_tree_clicked)
        self.left_tree.header().hide()
        self.left_tree.setMaximumWidth(160)
        llayout.addWidget(self.left_tree)
        layout.addLayout(llayout)
        # 右侧上下布局
        rlayout = QVBoxLayout()
        # 所属品种
        attach_varieties_layout = QHBoxLayout()
        attach_varieties_layout.addWidget(QLabel('所属品种:'))
        self.attach_varieties = QLabel()
        self.attach_varieties.variety_ids = list()  # id字符串
        attach_varieties_layout.addWidget(self.attach_varieties)
        attach_varieties_layout.addStretch()
        attach_varieties_layout.addWidget(QPushButton('清空', objectName='deleteBtn', cursor=Qt.PointingHandCursor, clicked=self.clear_attach_varieties), alignment=Qt.AlignRight)
        rlayout.addLayout(attach_varieties_layout)
        rlayout.addWidget(QLabel(parent=self, objectName='varietyError'))
        # 所属分类
        attach_category_layout = QHBoxLayout()
        attach_category_layout.addWidget(QLabel('所属分类:'))
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(400)
        attach_category_layout.addWidget(self.category_combo)
        attach_category_layout.addStretch()
        attach_category_layout.addWidget(QPushButton('新分类?', objectName='newCategoryBtn', cursor=Qt.PointingHandCursor, clicked=self.add_new_category), alignment=Qt.AlignRight)
        rlayout.addLayout(attach_category_layout)
        rlayout.addWidget(QLabel(parent=self, objectName='categoryError'))
        # 选择报告
        rlayout.addWidget(QPushButton('选择报告', clicked=self.select_reports), alignment=Qt.AlignLeft)
        # 预览表格
        self.review_table = QTableWidget()
        self.review_table.verticalHeader().hide()
        rlayout.addWidget(self.review_table)
        # 提交按钮
        self.commit_button = QPushButton('提交', clicked=self.commit_upload_report)
        rlayout.addWidget(self.commit_button, alignment=Qt.AlignRight)
        layout.addLayout(rlayout)
        self.setLayout(layout)
        self.setMinimumWidth(800)
        self.setStyleSheet("""
        #deleteBtn{
            border: none;
            color:rgb(200,100,80)
        }
        #newCategoryBtn{
            border:none;
            color:rgb(80,100,200)
        }
        """)

    # 获取分类选框内容
    def getCategoryCombo(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/data-category/normal_report/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            self.category_combo.clear()
            for category_item in response['data']:
                self.category_combo.addItem(category_item['name'], category_item['id'])
            # 加入其它
            self.category_combo.addItem('其它', 0)

    # 清空所属品种
    def clear_attach_varieties(self):
        self.attach_varieties.setText('')
        self.attach_varieties.variety_ids.clear()  # id列表

    # 新增报告分类
    def add_new_category(self):
        popup = QDialog(parent=self)
        def commit_new_category():
            print('提交新建分类')
            name = re.sub(r'\s+', '', popup.category_name_edit.text())
            if not name:
                popup.name_error_label.setText('请输入正确的分类名称!')
                return
            # 提交常规报告分类
            try:
                r = requests.post(
                    url=settings.SERVER_ADDR + 'home/data-category/normal_report/?mc=' + settings.app_dawn.value('machine'),
                    headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                    data=json.dumps({'name': name})
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 201:
                    raise ValueError(response['message'])
            except Exception as e:
                popup.name_error_label.setText(str(e))
            else:
                # 重新获取填充分类选框
                self.getCategoryCombo()
                popup.close()

        popup.setWindowTitle('新建分类')
        new_layout = QGridLayout()
        new_layout.addWidget(QLabel('名称:'), 0, 0)
        popup.category_name_edit = QLineEdit()
        new_layout.addWidget(popup.category_name_edit, 0, 1)
        popup.name_error_label = QLabel()
        new_layout.addWidget(popup.name_error_label, 1, 0, 1, 2)
        new_layout.addWidget(QPushButton('确定', clicked=commit_new_category), 2, 1)
        popup.setLayout(new_layout)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 获取左侧品种树的品种内容
    def geTreeVarieties(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'group-varieties/?mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            # 填充品种树
            for group_item in response['data']:
                group = QTreeWidgetItem(self.left_tree)
                group.setText(0, group_item['name'])
                group.gid = group_item['id']
                # 添加子节点
                for variety_item in group_item['varieties']:
                    child = QTreeWidgetItem()
                    child.setText(0, variety_item['name'])
                    child.vid = variety_item['id']
                    group.addChild(child)
            self.left_tree.expandAll()  # 展开所有

    # 点击左侧品种树
    def variety_tree_clicked(self):
        item = self.left_tree.currentItem()
        if item.childCount():  # has children open the root
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        text = item.text(0)
        if item.parent() and item.vid not in self.attach_varieties.variety_ids:  # 所属品种中增加当前品种
            self.attach_varieties.setText(self.attach_varieties.text() + text + '、')
            self.attach_varieties.variety_ids.append(item.vid)

    # 选择报告文件
    def select_reports(self):
        path_list, _ = QFileDialog.getOpenFileNames(self, '打开文件', '', "PDF files(*.pdf)")
        # 遍历报告文件填充预览表格与设置状态
        self.review_table.setRowCount(len(path_list))
        self.review_table.setColumnCount(4)
        self.review_table.setHorizontalHeaderLabels(['序号', '报告名', '报告日期', '状态'])
        self.review_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.review_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, file_path in enumerate(path_list):
            item_1 = QTableWidgetItem(str(row + 1))
            item_1.file_path = file_path
            item_1.setTextAlignment(Qt.AlignCenter)
            self.review_table.setItem(row, 0, item_1)
            file_name = file_path.rsplit('/', 1)[1]
            item_2 = QTableWidgetItem(file_name)
            item_2.setTextAlignment(Qt.AlignCenter)
            self.review_table.setItem(row, 1, item_2)
            # 日期控件
            date_edit = QDateEdit(QDate.currentDate())
            date_edit.setCalendarPopup(True)
            date_edit.setDisplayFormat('yyyy-MM-dd')
            self.review_table.setCellWidget(row, 2, date_edit)
            # 装态
            item_4 = QTableWidgetItem('等待上传')
            item_4.setTextAlignment(Qt.AlignCenter)
            self.review_table.setItem(row, 3, item_4)

    # 确认上传报告
    def commit_upload_report(self):
        self.commit_button.setEnabled(False)
        # 获取所属品种列表id
        attach_variety_ids = self.attach_varieties.variety_ids
        if not attach_variety_ids:
            self.findChild(QLabel, 'varietyError').setText('请选择所属品种(支持多选)')
            return
        # 获取所属分类
        attach_category = self.category_combo.currentData()
        # 遍历表格打包文件信息(上传线程处理，每上传一个发个信号过来修改上传状态)
        file_message_list = list()
        for row in range(self.review_table.rowCount()):
            message_item = self.review_table.item(row, 3)  # 设置上传状态
            message_item.setText('正在上传...')
            message_item.setForeground(QBrush(QColor(20, 50, 200)))
            # 设置颜色
            file_message_list.append({
                'file_name': self.review_table.item(row, 1).text(),
                'file_path': self.review_table.item(row, 0).file_path,
                'category_id': attach_category,
                'variety_ids': attach_variety_ids,
                'file_date': self.review_table.cellWidget(row, 2).text(),
                'row_index': row
            })
        # 开启线程
        if hasattr(self, 'uploading_thread'):
            del self.uploading_thread
        self.uploading_thread = UploadReportThread(
            file_list=file_message_list,
            machine_code=settings.app_dawn.value('machine'),
            token=settings.app_dawn.value('AUTHORIZATION'),
        )
        self.uploading_thread.finished.connect(self.uploading_thread.deleteLater)
        self.uploading_thread.response_signal.connect(self.change_loading_state)
        self.uploading_thread.start()

    # 上传的线程返回消息
    def change_loading_state(self, row, succeed):
        item = self.review_table.item(row, 3)
        if succeed:
            item.setText('上传成功!')
            item.setForeground(QBrush(QColor(20, 200, 50)))
        else:
            item.setText('上传失败...')
            item.setForeground(QBrush(QColor(200, 20, 50)))
        if row == self.review_table.rowCount() - 1:
            self.commit_button.setEnabled(True)


# 上传交易通知线程
class UploadTransactionNoticeThread(QThread):
    response_signal = pyqtSignal(int, bool)

    def __init__(self, file_list, machine_code, token, *args, **kwargs):
        super(UploadTransactionNoticeThread, self).__init__(*args, **kwargs)
        self.file_list = file_list
        self.machine_code = machine_code
        self.token = token

    def run(self):
        for file_item in self.file_list:
            # 读取文件
            try:
                data_file = dict()
                # 增加其他字段
                data_file['name'] = file_item['file_name']
                data_file['date'] = file_item['file_date']
                data_file['category_id'] = file_item['category_id']
                # 读取文件
                file = open(file_item['file_path'], "rb")
                file_content = file.read()
                file.close()
                # 文件内容字段
                data_file["file"] = (file_item['file_name'], file_content)
                encode_data = encode_multipart_formdata(data_file)
                data_file = encode_data[0]
                # 发起上传请求
                r = requests.post(
                    url=settings.SERVER_ADDR + 'home/transaction_notice/?mc=' + self.machine_code,
                    headers={
                        'AUTHORIZATION': self.token,
                        'Content-Type': encode_data[1]
                    },
                    data=data_file
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 201:
                    raise ValueError(response['message'])
            except Exception as e:
                with open('debug/home_notice.log', 'w') as f:
                    f.write(str(e) + '\n')
                self.response_signal.emit(file_item['row_index'], False)
            else:
                self.response_signal.emit(file_item['row_index'], True)


# 新增交易通知
class CreateTransactionNoticePopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateTransactionNoticePopup, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        # 左侧上下布局
        llayout = QVBoxLayout()
        self.left_list = QListWidget(clicked=self.left_list_clicked)
        self.left_list.setMaximumWidth(160)
        llayout.addWidget(self.left_list)
        llayout.addWidget(QPushButton('新增分类', clicked=self.add_new_category), alignment=Qt.AlignLeft)
        layout.addLayout(llayout)
        # 右侧上下布局
        rlayout = QVBoxLayout()
        attach_categoty_layout = QHBoxLayout()
        attach_categoty_layout.addWidget(QLabel('所属分类:'))
        self.attach_category = QLabel()
        self.attach_category.category_id = None
        attach_categoty_layout.addWidget(self.attach_category)
        attach_categoty_layout.addStretch()
        rlayout.addLayout(attach_categoty_layout)
        rlayout.addWidget(QLabel(parent=self, objectName='categoryError'), alignment=Qt.AlignLeft)
        # 选择文件
        rlayout.addWidget(QPushButton('选择通知', clicked=self.select_notices), alignment=Qt.AlignLeft)
        # 预览表格
        self.review_table = QTableWidget()
        rlayout.addWidget(self.review_table)
        # 提交按钮
        self.commit_button = QPushButton('确定提交')
        rlayout.addWidget(self.commit_button, alignment=Qt.AlignRight)
        layout.addLayout(rlayout)
        self.setLayout(layout)
        self.setMinimumWidth(800)

    # 获取左侧通知分类
    def getCategoryList(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'home/data-category/transaction_notice/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            self.left_list.clear()
            for category_item in response['data']:
                list_item = QListWidgetItem(category_item['name'])
                list_item.category_id = category_item['id']
                self.left_list.addItem(list_item)
            # 加入其它
            other_item = QListWidgetItem('其他')
            other_item.category_id = 0
            self.left_list.addItem(other_item)

    # 点击左侧分类
    def left_list_clicked(self):
        current_item = self.left_list.currentItem()
        self.attach_category.category_id = current_item.category_id
        self.attach_category.setText(current_item.text())
        print(current_item.text(), self.attach_category.category_id)


    # 选择文件
    def select_notices(self):
        path_list, _ = QFileDialog.getOpenFileNames(self, '打开通知', '', "PDF files(*.pdf)")
        # 遍历通知文件填充预览表格与设置状态
        self.review_table.setRowCount(len(path_list))
        self.review_table.setColumnCount(4)
        self.review_table.setHorizontalHeaderLabels(['序号', '文件名', '通知日期', '状态'])
        self.review_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.review_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, file_path in enumerate(path_list):
            item_1 = QTableWidgetItem(str(row + 1))
            item_1.file_path = file_path
            item_1.setTextAlignment(Qt.AlignCenter)
            self.review_table.setItem(row, 0, item_1)
            file_name = file_path.rsplit('/', 1)[1]
            item_2 = QTableWidgetItem(file_name)
            item_2.setTextAlignment(Qt.AlignCenter)
            self.review_table.setItem(row, 1, item_2)
            # 日期控件
            date_edit = QDateEdit(QDate.currentDate())
            date_edit.setCalendarPopup(True)
            date_edit.setDisplayFormat('yyyy-MM-dd')
            self.review_table.setCellWidget(row, 2, date_edit)
            # 装态
            item_4 = QTableWidgetItem('等待上传')
            item_4.setTextAlignment(Qt.AlignCenter)
            self.review_table.setItem(row, 3, item_4)

    # 确认上传交易通知
    def commit_upload_report(self):
        self.commit_button.setEnabled(False)
        # 获取所属分类
        attach_category = self.attach_category.category_id
        # 遍历表格打包文件信息(上传线程处理，每上传一个发个信号过来修改上传状态)
        file_message_list = list()
        for row in range(self.review_table.rowCount()):
            message_item = self.review_table.item(row, 3)  # 设置上传状态
            message_item.setText('正在上传...')
            message_item.setForeground(QBrush(QColor(20, 50, 200)))
            # 设置颜色
            file_message_list.append({
                'file_name': self.review_table.item(row, 1).text(),
                'file_path': self.review_table.item(row, 0).file_path,
                'category_id': attach_category,
                'file_date': self.review_table.cellWidget(row, 2).text(),
                'row_index': row
            })
        # 开启线程
        if hasattr(self, 'uploading_thread'):
            del self.uploading_thread
        self.uploading_thread = UploadTransactionNoticeThread(
            file_list=file_message_list,
            machine_code=settings.app_dawn.value('machine'),
            token=settings.app_dawn.value('AUTHORIZATION'),
        )
        self.uploading_thread.finished.connect(self.uploading_thread.deleteLater)
        self.uploading_thread.response_signal.connect(self.change_loading_state)
        self.uploading_thread.start()

    # 上传的线程返回消息
    def change_loading_state(self, row, succeed):
        item = self.review_table.item(row, 3)
        if succeed:
            item.setText('上传成功!')
            item.setForeground(QBrush(QColor(20, 200, 50)))
        else:
            item.setText('上传失败...')
            item.setForeground(QBrush(QColor(200, 20, 50)))
        if row == self.review_table.rowCount() - 1:
            self.commit_button.setEnabled(True)

    # 新增交易通知分类
    def add_new_category(self):
        popup = QDialog(parent=self)
        popup.setWindowTitle('新增通知分类')
        def commit_new_category():
            name = re.sub(r'\s+', '', popup.category_name_edit.text())
            if not name:
                popup.error_label.setText('请输入分类名称!')
                return
            # 提交请求
            try:
                r = requests.post(
                    url=settings.SERVER_ADDR + 'home/data-category/transaction_notice/?mc=' + settings.app_dawn.value(
                        'machine'),
                    headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                    data=json.dumps({'name': name})
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 201:
                    raise ValueError(response['message'])
            except Exception as e:
                popup.error_label.setText(str(e))
            else:
                self.getCategoryList()
                popup.close()
        layout = QGridLayout()
        layout.addWidget(QLabel('名称:'), 0, 1)
        popup.category_name_edit = QLineEdit()
        layout.addWidget(popup.category_name_edit, 0, 1)
        popup.error_label = QLabel()
        layout.addWidget(popup.error_label, 1, 0, 1,2)
        layout.addWidget(QPushButton('确认提交', clicked=commit_new_category), 2, 0, 1, 2)
        popup.setLayout(layout)
        if not popup.exec_():
            popup.deleteLater()
            del popup




