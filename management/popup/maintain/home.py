# _*_ coding:utf-8 _*_
"""
all dialog of data-maintenance module, in the home page
Update: 2019-07-25
Author: zizle
"""
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon

from utils import get_desktop_path


class CreateNewBulletin(QDialog):
    new_data_signal = pyqtSignal(dict)

    def __init__(self):
        super(CreateNewBulletin, self).__init__()
        self.setWindowTitle('设置')
        self.setWindowIcon(QIcon("media/bulletin.png"))
        layout = QVBoxLayout()
        # 添加一个tab
        tabs = QTabWidget()
        self.tab_0 = QWidget()
        self.tab_1 = QWidget()
        tabs.addTab(self.tab_0, "添加公告")
        tabs.addTab(self.tab_1, "显示天数")
        # 初始化tab_0
        self.init_tab_0()
        self.init_tab_1()
        layout.addWidget(tabs)
        self.setLayout(layout)

    def init_tab_0(self):
        grid_layout_0 = QGridLayout()
        tab_0_label_0 = QLabel("名称：")
        tab_0_label_1 = QLabel("展示：")
        self.tab_0_label_2 = QLabel('文件：')
        self.tab_0_label_3 = QLabel('内容：')
        self.tab_0_edit_0 = QLineEdit()  # 名称
        self.tab_0_edit_1 = QLineEdit()  # 文件路径
        self.tab_0_edit_0.setPlaceholderText("输入条目展示的名称(默认文件名)")
        self.tab_0_combo = QComboBox()
        self.tab_0_combo.addItems(['文件展示', '显示文字'])
        self.tab_0_combo.currentTextChanged.connect(self.tab_0_show_type_changed)
        self.tab_0_btn_0  = QPushButton('浏览')
        self.tab_0_btn_0.setMaximumWidth(30)
        tab_0_btn_1 = QPushButton('提交')
        self.tab_0_btn_0.clicked.connect(self.select_file)
        tab_0_btn_1.clicked.connect(self.submit_bulletin)
        self.tab_0_edit_2 = QTextEdit()  # 内容
        # initial hide the content edit
        self.tab_0_label_3.hide()
        self.tab_0_edit_2.hide()
        grid_layout_0.addWidget(tab_0_label_0, 0, 0)
        grid_layout_0.addWidget(self.tab_0_edit_0, 0, 1, 1, 2)
        grid_layout_0.addWidget(tab_0_label_1, 1, 0)
        grid_layout_0.addWidget(self.tab_0_combo, 1, 1, 1, 2)
        grid_layout_0.addWidget(self.tab_0_label_2, 2, 0)
        grid_layout_0.addWidget(self.tab_0_edit_1, 2, 1)
        grid_layout_0.addWidget(self.tab_0_btn_0, 2, 2)
        grid_layout_0.addWidget(self.tab_0_label_3, 3, 0)
        grid_layout_0.addWidget(self.tab_0_edit_2, 3, 1, 1, 2)
        grid_layout_0.addWidget(tab_0_btn_1, 4, 1, 1,2)
        self.tab_0.setLayout(grid_layout_0)

    def init_tab_1(self):
        grid_layout_1 = QGridLayout()
        tip_label = QLabel("* 设置公告栏展示距今日几天前的内容")
        tip_label.setStyleSheet("color: rgb(84,182,230);font-size:12px;")
        tab_1_label_0 = QLabel("设置天数：")
        self.tab_1_edit_0 = QLineEdit()
        self.tab_1_edit_0.setFixedHeight(28)
        self.tab_1_edit_0.setPlaceholderText("请输入正整数.")
        tab_1_btn_0 = QPushButton("提交")
        grid_layout_1.addWidget(tip_label, 0, 0, 1, 2)
        grid_layout_1.addWidget(tab_1_label_0, 1, 0)
        grid_layout_1.addWidget(self.tab_1_edit_0, 1, 1, 1, 2)
        grid_layout_1.addWidget(tab_1_btn_0, 2, 1, 1, 2)
        self.tab_1.setLayout(grid_layout_1)

    def tab_0_show_type_changed(self, text):
        if text == '文件展示':
            self.resize(318, 214)
            self.tab_0_label_2.show()
            self.tab_0_edit_1.show()
            self.tab_0_btn_0.show()
            self.tab_0_label_3.hide()
            self.tab_0_edit_2.hide()
        elif text == '显示文字':
            self.resize(318, 300)
            self.tab_0_label_2.hide()
            self.tab_0_edit_1.hide()
            self.tab_0_btn_0.hide()
            self.tab_0_label_3.show()
            self.tab_0_edit_2.show()

    def select_file(self):
        """ select file when show type is file """
        # 弹窗
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        if not self.tab_0_edit_0.text().strip(' '):  # set bulletin name
            file_raw_name = file_path.rsplit("/", 1)
            file_name_list = file_raw_name[1].rsplit(".", 1)
            self.tab_0_edit_0.setText(file_name_list[0])
        self.tab_0_edit_1.setText(file_path)  # set file path

    def submit_bulletin(self):
        """ create new bulletin in server """
        # collect data
        data = dict()
        show_dict = {
            "文件展示": "show_file",
            "显示文字": "show_text",
        }
        show_type = show_dict.get(self.tab_0_combo.currentText(), None)
        file_path = self.tab_0_edit_1.text()
        if not show_type:
            QMessageBox.warning(self, "错误", "未选择展示方式!", QMessageBox.Yes)
            return
        if show_type == "show_file" and not file_path:
            QMessageBox.warning(self, "错误", "请选择文件!", QMessageBox.Yes)
            return
        if show_type == "show_file" and not self.tab_0_edit_0.text().strip(' '):
            # doesn't names for this bulletin when show type is file
            file_raw_name = file_path.rsplit("/", 1)
            file_name_list = file_raw_name.rsplit(".", 1)
            self.tab_0_edit_0.setText(file_name_list[0])
        if show_type == "show_text" and not self.tab_0_edit_0.text().strip(' '):
            # doesn't names for this bulletin when show type is text
            QMessageBox.warning(self, "错误", "展示文本时需输入条目名称!", QMessageBox.Yes)
            return
        content_list = self.tab_0_edit_2.toPlainText().strip(' ').split('\n') # 去除前后空格和分出换行
        if show_type == "show_text" and not content_list[0]:
            QMessageBox.warning(self, "错误", "请输入展示文本的内容!", QMessageBox.Yes)
            return
        # 处理文本内容
        text_content = ""
        if show_type == "show_text":
            for p in content_list:
                text_content += "<p style='margin:0;'><span>&nbsp;&nbsp;</span>" + p + "</p>"
        data["name"] = self.tab_0_edit_0.text().strip(' ')
        data["show_type"] = show_type
        data["file"] = file_path
        data["content"] = text_content
        data["set_option"] = "new_bulletin"
        print('popup.maintain.home.py {} : '.format(str(sys._getframe().f_lineno)), "上传公告:", data)
        self.new_data_signal.emit(data)


class CreateNewCarousel(QDialog):
    new_data_signal = pyqtSignal(dict)

    def __init__(self):
        super(CreateNewCarousel, self).__init__()
        self.setFixedSize(430, 220)
        layout = QGridLayout()
        # labels
        name_label = QLabel('名称：')
        image_label = QLabel('图片：')
        style_label = QLabel('广告方式：')
        self.file_label = QLabel('文件：')
        self.content_label = QLabel('内容：')
        self.url_label = QLabel('网址：')
        self.content_label.hide()
        self.url_label.hide()
        # edits
        self.name_edit = QLineEdit()
        self.image_edit = QLineEdit()
        self.file_edit = QLineEdit()
        self.url_edit = QLineEdit()
        self.content_edit = QTextEdit()
        self.content_edit.hide()
        self.url_edit.hide()
        # combos
        self.show_combo = QComboBox()
        self.show_combo.addItems(['文件展示', '显示内容', '链接网址'])
        self.show_combo.currentTextChanged.connect(self.change_show_style)
        # buttons
        self.select_file_btn = QPushButton('选择')
        select_img_btn = QPushButton('图片')
        submit_btn = QPushButton('提交')
        self.select_file_btn.setMaximumWidth(30)
        select_img_btn.setMaximumWidth(30)
        # select button signal
        self.select_file_btn.clicked.connect(self.select_file_clicked)
        select_img_btn.clicked.connect(self.select_img_clicked)
        submit_btn.clicked.connect(self.submit_carousel)
        # add layout
        # named
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(self.name_edit, 0, 1, 1, 2)
        # select image
        layout.addWidget(image_label, 1, 0)
        layout.addWidget(self.image_edit, 1, 1)
        layout.addWidget(select_img_btn, 1, 2)
        # show style
        layout.addWidget(style_label, 2, 0)
        layout.addWidget(self.show_combo, 2, 1, 1, 2)
        # select file
        layout.addWidget(self.file_label, 3, 0)
        layout.addWidget(self.file_edit, 3, 1)
        layout.addWidget(self.select_file_btn, 3, 2)
        # edit content
        layout.addWidget(self.content_label, 4, 0)
        layout.addWidget(self.content_edit, 4, 1, 1, 2)
        # edit url address
        layout.addWidget(self.url_label, 5, 0)
        layout.addWidget(self.url_edit, 5, 1, 1,2)
        # submit
        layout.addWidget(submit_btn, 6, 1, 1, 2)
        self.setLayout(layout)

    def change_show_style(self, text):
        if text == '文件展示':
            # hide content
            self.content_label.hide()
            self.content_edit.clear()
            self.content_edit.hide()
            # hide url
            self.url_label.hide()
            self.url_edit.clear()
            self.url_edit.hide()
            # show file
            self.file_label.show()
            self.file_edit.show()
            self.select_file_btn.show()
        elif text == '显示内容':
            # hide file
            self.file_label.hide()
            self.file_edit.clear()
            self.file_edit.hide()
            self.select_file_btn.hide()
            # hide url link
            self.url_label.hide()
            self.url_edit.clear()
            self.url_edit.hide()
            # show content
            self.content_label.show()
            self.content_edit.show()
        elif text == '链接网址':
            # hide file
            self.file_label.hide()
            self.file_edit.clear()
            self.file_edit.hide()
            self.select_file_btn.hide()
            # hide content
            self.content_label.hide()
            self.content_edit.clear()
            self.content_edit.hide()
            # show url link
            self.url_label.show()
            self.url_edit.show()
        else:
            pass

    def select_file_clicked(self):
        # select file
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        self.file_edit.setText(file_path)

    def select_img_clicked(self):
        # select image
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "Image files (*.png *.jpg)")
        if not file_path:
            return
        self.image_edit.setText(file_path)

    def submit_carousel(self):
        # submit carousel data
        data = dict()
        show_dict = {
            "文件展示": "show_file",
            "显示内容": "show_text",
            "链接网址": "redirect"
        }
        name = self.name_edit.text().strip(' ')
        if not name:
            QMessageBox.warning(self, "错误", "请起一个名字!", QMessageBox.Yes)
            return
        image_path = self.image_edit.text()
        if not image_path:
            QMessageBox.warning(self, "错误", "请上传展示的图片!", QMessageBox.Yes)
            return
        show_style = show_dict.get(self.show_combo.currentText(), None)
        if not show_style:
            QMessageBox.warning(self, "错误", "没有选择展示方式!", QMessageBox.Yes)
            return
        if show_style == "show_file" and not self.file_edit.text():
            QMessageBox.warning(self, "错误", "要显示文件需上传pdf文件!", QMessageBox.Yes)
            return
        if show_style == "redirect" and not self.url_edit.text().strip(' '):
            QMessageBox.warning(self, "错误", "跳转网址需填写网址.", QMessageBox.Yes)
            return
        if show_style == 'show_text' and not self.content_edit.toPlainText().strip(' '):
            QMessageBox.warning(self, '错误', '显示内容需填写内容.')
            return
        file_path = self.file_edit.text()
        content_list = self.content_edit.toPlainText().split('\n')
        # 处理文本内容
        text_content = ""
        if content_list[0]:
            for p in content_list:
                text_content += "<p style='margin:0;'><span>&nbsp;&nbsp;</span>" + p + "</p>"
        redirect_url = self.url_edit.text().strip(' ')
        data["name"] = name
        data["image"] = image_path
        data["file"] = file_path
        data["content"] = text_content
        data["redirect"] = redirect_url
        # signal upload
        print('popup.maintain.home.py {} : 上传轮播：'.format(str(sys._getframe().f_lineno)), data )
        self.new_data_signal.emit(data)


class CreateNewReport(QDialog):
    new_data_signal = pyqtSignal(dict)

    def __init__(self):
        super(CreateNewReport, self).__init__()
        layout = QGridLayout()
        # labels
        name_label = QLabel("名称：")
        type_label = QLabel("类型：")
        file_label = QLabel("文件：")
        # edits
        self.name_edit = QLineEdit()
        self.file_edit = QLineEdit()
        # combo
        self.type_combo = QComboBox()
        self.type_combo.addItems(["日报", "周报", "月报", "年报", "专题", "投资报告", "其他"])
        # buttons
        select_file_btn = QPushButton('选择')
        submit_btn = QPushButton('提交')
        # styles
        select_file_btn.setMaximumWidth(30)
        # signal
        select_file_btn.clicked.connect(self.select_file_clicked)
        submit_btn.clicked.connect(self.submit_report)
        # add layout
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(self.name_edit, 0, 1, 1,2)
        layout.addWidget(type_label, 1, 0)
        layout.addWidget(self.type_combo, 1, 1, 1,2)
        layout.addWidget(file_label, 2, 0)
        layout.addWidget(self.file_edit, 2, 1)
        layout.addWidget(select_file_btn, 2,2)
        layout.addWidget(submit_btn, 3, 1, 1,2)
        self.setLayout(layout)

    def select_file_clicked(self):
        # select file
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        file_name_list = file_path.rsplit('/', 1)
        if not self.name_edit.text().strip(' '):
            self.name_edit.setText((file_name_list[1].rsplit('.', 1))[0])
        self.file_edit.setText(file_path)

    def submit_report(self):
        type_dict = {
            "日报": "daily",
            "周报": "weekly",
            "月报": "monthly",
            "年报": "annual",
            "专题": "special",
            "投资报告": "invest",
            "其他": "others"
        }
        # collect data
        name = self.name_edit.text().strip(' ')
        type_text = self.type_combo.currentText()
        file_path = self.file_edit.text()
        if not name:
            QMessageBox.warning(self, "错误", "请起一个名字!", QMessageBox.Yes)
            return
        if not type_text:
            QMessageBox.warning(self, "错误", "请选择报告类型!", QMessageBox.Yes)
            return
        if not file_path:
            QMessageBox.warning(self, "错误", "请选择报告文件!", QMessageBox.Yes)
            return
        self.new_data_signal.emit({
            'name': name,
            'type_zh': type_text,
            'type_en': type_dict.get(type_text, None),
            'file_path': file_path
        })


