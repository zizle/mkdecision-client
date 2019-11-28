# _*_ coding:utf-8 _*_
# Author: zizle QQ:462894999
import re
import sys
import json
import xlrd
import datetime
import requests
from PyQt5.QtWidgets import QWidget, QDialog, QHBoxLayout, QVBoxLayout, QPushButton, QTreeWidget, QGridLayout,\
    QLineEdit, QLabel, QTreeWidgetItem

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QFont

import config
from utils import get_desktop_path


# 新增分组数据弹窗
class NewHomeDataPopup(QDialog):
    network_result = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(NewHomeDataPopup, self).__init__(*args, **kwargs)
        self.setWindowTitle('新增数据')
        # 总左右布局
        layout = QHBoxLayout()
        # 左侧上下布局
        llayout = QVBoxLayout()
        # 左侧分类树
        self.left_tree = QTreeWidget(parent=self)
        self.left_tree.header().hide()
        self.add_group_button = QPushButton('新增大组', parent=self, clicked=self.add_new_group)
        llayout.addWidget(self.left_tree, alignment=Qt.AlignLeft)
        llayout.addWidget(self.add_group_button, alignment=Qt.AlignLeft)
        # 右侧上下布局
        rlayout = QVBoxLayout()
        # 右侧控件
        self.right_widget = QWidget(parent=self)
        # 控件布局
        right_widget_layout = QGridLayout()
        self.right_widget.setLayout(right_widget_layout)
        rlayout.addWidget(self.right_widget)
        # 加入总布局显示
        layout.addLayout(llayout)
        layout.addLayout(rlayout)
        self.setFixedSize(800, 500)
        self.setLayout(layout)
        # 初始化数据分类
        self.get_groups_categories()

    # 获取数据分组(含分组内的类别)
    def get_groups_categories(self):
        self.left_tree.clear()
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'home/groups-categories/?mc=' + config.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
            return
        else:
            # 填充分组树
            for group_item in response['data']:
                group = QTreeWidgetItem(self.left_tree)
                group.setText(0, group_item['name'])
                group.gid = group_item['id']
                # 添加子节点
                for category_item in group_item['categories']:
                    child = QTreeWidgetItem()
                    child.setText(0, category_item['name'])
                    child.vid = category_item['id']
                    group.addChild(child)
            self.network_result.emit('')

    # 新增数据大分组
    def add_new_group(self):
        print('新增大组')
        new_popup = QDialog(parent=self)

        # 提交新建大组
        def commit_new_group():
            print('提交新建大组')
            name = re.sub(r'\s+', '', new_popup.name_edit.text())
            if not name:
                new_popup.name_error.setText('请输入名称')
                return
            try:
                r = requests.post(
                    url=config.SERVER_ADDR + 'home/data-groups/?mc=' + config.app_dawn.value('machine'),
                    headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')},
                    data=json.dumps({
                        'name': name
                    })
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 201:
                    raise ValueError(response['message'])
            except Exception as e:
                new_popup.name_error.setText(str(e))
            else:
                new_popup.close()
                self.get_groups_categories()  # 重新请求分组数据
                self.network_result.emit('hasNewGroup')

        new_popup.setWindowTitle('新增大组')
        nglayout = QGridLayout()
        # 加入编辑名称
        new_popup.name_edit = QLineEdit(parent=new_popup)
        new_popup.name_error = QLabel(parent=new_popup, objectName='nameError')
        nglayout.addWidget(QLabel('名称:', parent=new_popup), 0, 0)
        nglayout.addWidget(new_popup.name_edit, 0, 1)
        nglayout.addWidget(new_popup.name_error, 1, 0, 1, 2)
        abtlayout = QHBoxLayout()
        abtlayout.addWidget(QPushButton('确定提交', parent=new_popup, objectName='addNdgbtn',
                                        clicked=commit_new_group), alignment=Qt.AlignRight)
        nglayout.addLayout(abtlayout, 1, 1)
        new_popup.setLayout(nglayout)
        new_popup.setFixedSize(250, 110)


        if not new_popup.exec_():
            new_popup.deleteLater()
            del new_popup


















class CreateNewBulletin(QDialog):
    new_data_signal = pyqtSignal(dict)
    def __init__(self):
        super(CreateNewBulletin, self).__init__()
        layout = QGridLayout()
        # labels
        title_label = QLabel('标题：')
        style_label = QLabel('展示方式：')
        self.file_label = QLabel('文件：')
        self.content_label = QLabel('内容：')
        self.content_label.hide()
        # edits
        self.title_edit = QLineEdit()
        self.file_edit = QLineEdit()
        self.content_edit = QTextEdit()
        self.content_edit.hide()
        # combos
        self.show_combo = QComboBox()
        self.show_combo.addItems(['文件展示', '显示内容'])
        self.show_combo.currentTextChanged.connect(self.change_show_style)
        # buttons
        self.select_file_btn = QPushButton('选择')
        submit_btn = QPushButton('提交')
        self.select_file_btn.setMaximumWidth(30)
        # select button signal
        self.select_file_btn.clicked.connect(self.select_file_clicked)
        submit_btn.clicked.connect(self.submit_carousel)
        # add layout
        # named
        layout.addWidget(title_label, 0, 0)
        layout.addWidget(self.title_edit, 0, 1, 1, 2)
        # show style
        layout.addWidget(style_label, 1, 0)
        layout.addWidget(self.show_combo, 1, 1, 1, 2)
        # select file
        layout.addWidget(self.file_label, 2, 0)
        layout.addWidget(self.file_edit, 2, 1)
        layout.addWidget(self.select_file_btn, 2, 2)
        # edit content
        layout.addWidget(self.content_label, 3, 0)
        layout.addWidget(self.content_edit, 3, 1, 1, 2)
        # submit
        layout.addWidget(submit_btn, 6, 1, 1, 2)
        self.setLayout(layout)

    def change_show_style(self, text):
        if text == '文件展示':
            # hide content
            self.content_label.hide()
            self.content_edit.clear()
            self.content_edit.hide()
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
            # show content
            self.content_label.show()
            self.content_edit.show()
        else:
            pass

    def select_file_clicked(self):
        # select file
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        file_name_list = file_path.rsplit('/', 1)
        if not self.title_edit.text().strip(' '):
            self.title_edit.setText((file_name_list[1].rsplit('.', 1))[0])
        self.file_edit.setText(file_path)

    def select_img_clicked(self):
        # select image
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "Image files (*.png *.jpg)")
        if not file_path:
            return
        self.file_edit.setText(file_path)

    def submit_carousel(self):
        # submit carousel data
        data = dict()
        show_dict = {
            "文件展示": "show_file",
            "显示内容": "show_text",
        }
        title = self.title_edit.text().strip(' ')
        if not title:
            QMessageBox.warning(self, "错误", "请起一个名字!", QMessageBox.Yes)
            return
        show_style = show_dict.get(self.show_combo.currentText(), None)
        if not show_style:
            QMessageBox.warning(self, "错误", "没有选择展示方式!", QMessageBox.Yes)
            return
        if show_style == "show_file" and not self.file_edit.text():
            QMessageBox.warning(self, "错误", "要显示文件需上传pdf文件!", QMessageBox.Yes)
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
        data["name"] = title
        data["file"] = file_path
        data["content"] = text_content
        data['show_type'] = show_style
        # signal upload
        self.new_data_signal.emit(data)












    #
    # new_data_signal = pyqtSignal(dict)
    #
    # def __init__(self):
    #     super(CreateNewBulletin, self).__init__()
    #     self.setWindowTitle('设置')
    #     self.setWindowIcon(QIcon("media/bulletin.png"))
    #     layout = QVBoxLayout()
    #     # 添加一个tab
    #     tabs = QTabWidget()
    #     self.tab_0 = QWidget()
    #     self.tab_1 = QWidget()
    #     tabs.addTab(self.tab_0, "添加公告")
    #     # tabs.addTab(self.tab_1, "显示天数")
    #     # 初始化tab_0
    #     self.init_tab_0()
    #     self.init_tab_1()
    #     layout.addWidget(tabs)
    #     self.setLayout(layout)
    #
    # def init_tab_0(self):
    #     grid_layout_0 = QGridLayout()
    #     tab_0_label_0 = QLabel("名称：")
    #     tab_0_label_1 = QLabel("展示：")
    #     self.tab_0_label_2 = QLabel('文件：')
    #     self.tab_0_label_3 = QLabel('内容：')
    #     self.tab_0_edit_0 = QLineEdit()  # 名称
    #     self.tab_0_edit_1 = QLineEdit()  # 文件路径
    #     self.tab_0_edit_0.setPlaceholderText("输入条目展示的名称(默认文件名)")
    #     self.tab_0_combo = QComboBox()
    #     self.tab_0_combo.addItems(['文件展示', '显示文字'])
    #     self.tab_0_combo.currentTextChanged.connect(self.tab_0_show_type_changed)
    #     self.tab_0_btn_0  = QPushButton('浏览')
    #     self.tab_0_btn_0.setMaximumWidth(30)
    #     tab_0_btn_1 = QPushButton('提交')
    #     self.tab_0_btn_0.clicked.connect(self.select_file)
    #     tab_0_btn_1.clicked.connect(self.submit_bulletin)
    #     self.tab_0_edit_2 = QTextEdit()  # 内容
    #     # initial hide the content edit
    #     self.tab_0_label_3.hide()
    #     self.tab_0_edit_2.hide()
    #     grid_layout_0.addWidget(tab_0_label_0, 0, 0)
    #     grid_layout_0.addWidget(self.tab_0_edit_0, 0, 1, 1, 2)
    #     grid_layout_0.addWidget(tab_0_label_1, 1, 0)
    #     grid_layout_0.addWidget(self.tab_0_combo, 1, 1, 1, 2)
    #     grid_layout_0.addWidget(self.tab_0_label_2, 2, 0)
    #     grid_layout_0.addWidget(self.tab_0_edit_1, 2, 1)
    #     grid_layout_0.addWidget(self.tab_0_btn_0, 2, 2)
    #     grid_layout_0.addWidget(self.tab_0_label_3, 3, 0)
    #     grid_layout_0.addWidget(self.tab_0_edit_2, 3, 1, 1, 2)
    #     grid_layout_0.addWidget(tab_0_btn_1, 4, 1, 1,2)
    #     self.tab_0.setLayout(grid_layout_0)
    #
    # def init_tab_1(self):
    #     grid_layout_1 = QGridLayout()
    #     tip_label = QLabel("* 设置公告栏展示距今日几天前的内容")
    #     tip_label.setStyleSheet("color: rgb(84,182,230);font-size:12px;")
    #     tab_1_label_0 = QLabel("设置天数：")
    #     self.tab_1_edit_0 = QLineEdit()
    #     self.tab_1_edit_0.setFixedHeight(28)
    #     self.tab_1_edit_0.setPlaceholderText("请输入正整数.")
    #     tab_1_btn_0 = QPushButton("提交")
    #     grid_layout_1.addWidget(tip_label, 0, 0, 1, 2)
    #     grid_layout_1.addWidget(tab_1_label_0, 1, 0)
    #     grid_layout_1.addWidget(self.tab_1_edit_0, 1, 1, 1, 2)
    #     grid_layout_1.addWidget(tab_1_btn_0, 2, 1, 1, 2)
    #     self.tab_1.setLayout(grid_layout_1)
    #
    # def tab_0_show_type_changed(self, text):
    #     if text == '文件展示':
    #         self.resize(318, 214)
    #         self.tab_0_label_2.show()
    #         self.tab_0_edit_1.show()
    #         self.tab_0_btn_0.show()
    #         self.tab_0_label_3.hide()
    #         self.tab_0_edit_2.hide()
    #     elif text == '显示文字':
    #         self.resize(318, 300)
    #         self.tab_0_label_2.hide()
    #         self.tab_0_edit_1.hide()
    #         self.tab_0_btn_0.hide()
    #         self.tab_0_label_3.show()
    #         self.tab_0_edit_2.show()
    #
    # def select_file(self):
    #     """ select file when show type is file """
    #     # 弹窗
    #     desktop_path = get_desktop_path()
    #     file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
    #     if not file_path:
    #         return
    #     if not self.tab_0_edit_0.text().strip(' '):  # set bulletin name
    #         file_raw_name = file_path.rsplit("/", 1)
    #         file_name_list = file_raw_name[1].rsplit(".", 1)
    #         self.tab_0_edit_0.setText(file_name_list[0])
    #     self.tab_0_edit_1.setText(file_path)  # set file path
    #
    # def submit_bulletin(self):
    #     """ create new bulletin in server """
    #     # collect data
    #     data = dict()
    #     show_dict = {
    #         "文件展示": "show_file",
    #         "显示文字": "show_text",
    #     }
    #     show_type = show_dict.get(self.tab_0_combo.currentText(), None)
    #     file_path = self.tab_0_edit_1.text()
    #     if not show_type:
    #         QMessageBox.warning(self, "错误", "未选择展示方式!", QMessageBox.Yes)
    #         return
    #     if show_type == "show_file" and not file_path:
    #         QMessageBox.warning(self, "错误", "请选择文件!", QMessageBox.Yes)
    #         return
    #     if show_type == "show_file" and not self.tab_0_edit_0.text().strip(' '):
    #         # doesn't names for this bulletin when show type is file
    #         file_raw_name = file_path.rsplit("/", 1)
    #         file_name_list = file_raw_name.rsplit(".", 1)
    #         self.tab_0_edit_0.setText(file_name_list[0])
    #     if show_type == "show_text" and not self.tab_0_edit_0.text().strip(' '):
    #         # doesn't names for this bulletin when show type is text
    #         QMessageBox.warning(self, "错误", "展示文本时需输入条目名称!", QMessageBox.Yes)
    #         return
    #     content_list = self.tab_0_edit_2.toPlainText().strip(' ').split('\n') # 去除前后空格和分出换行
    #     if show_type == "show_text" and not content_list[0]:
    #         QMessageBox.warning(self, "错误", "请输入展示文本的内容!", QMessageBox.Yes)
    #         return
    #     # 处理文本内容
    #     text_content = ""
    #     if show_type == "show_text":
    #         for p in content_list:
    #             text_content += "<p style='margin:0;'><span>&nbsp;&nbsp;</span>" + p + "</p>"
    #     data["title"] = self.tab_0_edit_0.text().strip(' ')
    #     data["show_type"] = show_type
    #     data["file"] = file_path
    #     data["content"] = text_content
    #     data["set_option"] = "new_bulletin"
    #     print('popup.maintain.home.py {} : '.format(str(sys._getframe().f_lineno)), "上传公告:", data)
    #     self.new_data_signal.emit(data)


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


class CreateNewCommodity(QDialog):
    new_data_signal = pyqtSignal(list)
    def __init__(self):
        super(CreateNewCommodity, self).__init__()
        self.resize(850,550)
        layout = QVBoxLayout()
        load_file_btn = QPushButton('+数据')
        self.review_table = QTableWidget()
        tip_label = QLabel('*请检查无误上传,提交后将不可更改.')
        submit_btn = QPushButton("提交")
        # widget style
        tip_label.setStyleSheet('font-size:12px; color:rgb(255,10,10)')
        self.review_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.review_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # button signal
        load_file_btn.clicked.connect(self.read_new_commodity)
        submit_btn.clicked.connect(self.submit_commodity)
        # add layout
        layout.addWidget(load_file_btn, alignment=Qt.AlignLeft)
        layout.addWidget(self.review_table)
        layout.addWidget(tip_label)
        layout.addWidget(submit_btn, alignment=Qt.AlignRight)
        self.setLayout(layout)

    def read_new_commodity(self):
        # upload data to review table
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.xlsx *.xls)")
        if not file_path:
            return
        rf = xlrd.open_workbook(filename=file_path)
        sheet1 = rf.sheet_by_index(0)
        row_header = sheet1.row_values(0)
        # excel file header match
        header_labels = ["品种", "地区", "等级", "报价", "日期", "备注"]
        if row_header != header_labels:
            return
        # table initial
        self.review_table.setRowCount(sheet1.nrows - 1)
        self.review_table.setColumnCount(len(header_labels))
        self.review_table.setHorizontalHeaderLabels(header_labels)
        for row in range(1, sheet1.nrows):  # skip header
            row_content = sheet1.row_values(row)
            row_content[4] = datetime.datetime.strftime(xlrd.xldate_as_datetime(row_content[4], rf.datemode), "%Y-%m-%d")
            # data to review table
            for col, col_data in enumerate(row_content):
                item = QTableWidgetItem(str(col_data))
                item.setTextAlignment(132)
                self.review_table.setItem(row - 1, col, item)

    def submit_commodity(self):
        # submit commodity
        data = []
        header_labels = ["variety", "area", "level", "price", "date", "note"]
        for row in range(self.review_table.rowCount()):
            item = dict()
            for col in range(len(header_labels)):
                col_item = self.review_table.item(row, col)
                if not col_item or not col_item.text():
                    continue
                item[header_labels[col]] = col_item.text()
            # 验证信息
            for key in header_labels:
                if key == "note":
                    continue
                if len(item) > 1 and not item.get(key):
                    QMessageBox.warning(self, "错误", "请将信息填写完整!", QMessageBox.Yes)
                    return
            if len(item) >= 5:
                data.append(item)
        if not data:
            QMessageBox.warning(self, "错误", "您未填写任何信息!", QMessageBox.Yes)
            return
        self.review_table.clear()
        self.review_table.setRowCount(0)
        self.review_table.setHorizontalHeaderLabels(["品种", "地区", "等级", "报价", "时间", "备注"])
        self.new_data_signal.emit(data)


class CreateNewFinance(QDialog):
    new_data_signal = pyqtSignal(list)
    def __init__(self):
        super(CreateNewFinance, self).__init__()
        self.resize(850, 550)
        layout = QVBoxLayout()
        load_file_btn = QPushButton('+数据')
        self.review_table = QTableWidget()
        tip_label = QLabel('*请检查无误上传,提交后将不可更改.')
        submit_btn = QPushButton("提交")
        # widget style
        tip_label.setStyleSheet('font-size:12px; color:rgb(255,10,10)')
        self.review_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.review_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # button signal
        load_file_btn.clicked.connect(self.read_new_finance)
        submit_btn.clicked.connect(self.submit_finance)
        # add layout
        layout.addWidget(load_file_btn, alignment=Qt.AlignLeft)
        layout.addWidget(self.review_table)
        layout.addWidget(tip_label)
        layout.addWidget(submit_btn, alignment=Qt.AlignRight)
        self.setLayout(layout)

    def read_new_finance(self):
        # upload data to review table
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.xlsx *.xls)")
        if not file_path:
            return
        rf = xlrd.open_workbook(filename=file_path)
        sheet1 = rf.sheet_by_index(0)
        row_header = sheet1.row_values(0)
        # excel file header match
        header_labels = ["日期", "时间", "地区", "事件描述", "预期值"]
        if row_header != header_labels:
            return
        # table initial
        self.review_table.setRowCount(sheet1.nrows - 1)
        self.review_table.setColumnCount(len(header_labels))
        self.review_table.setHorizontalHeaderLabels(header_labels)
        for row in range(1, sheet1.nrows):  # skip header
            row_content = sheet1.row_values(row)
            row_content[0] = datetime.datetime.strftime(xlrd.xldate_as_datetime(row_content[0], rf.datemode), "%Y-%m-%d")
            row_content[1] = datetime.datetime.strftime(xlrd.xldate_as_datetime(row_content[1], rf.datemode), "%H:%M")
            # data to review table
            for col, col_data in enumerate(row_content):
                item = QTableWidgetItem(str(col_data))
                item.setTextAlignment(132)
                self.review_table.setItem(row - 1, col, item)

    def submit_finance(self):
        # submit commodity
        data = []
        header_labels = ["date", "time", "country", "event", "expected"]
        for row in range(self.review_table.rowCount()):
            item = dict()
            for col in range(len(header_labels)):
                col_item = self.review_table.item(row, col)
                if not col_item or not col_item.text():
                    continue
                item[header_labels[col]] = col_item.text()
            # 验证信息
            for key in header_labels:
                if len(item) > 1 and not item.get(key):
                    QMessageBox.warning(self, "错误", "请将信息填写完整!", QMessageBox.Yes)
                    return
            if len(item) >= 5:
                data.append(item)
        if not data:
            QMessageBox.warning(self, "错误", "您未填写任何信息!", QMessageBox.Yes)
            return
        self.review_table.clear()
        self.review_table.setRowCount(0)
        self.review_table.setHorizontalHeaderLabels(["品种", "地区", "等级", "报价", "时间", "备注"])
        self.new_data_signal.emit(data)


class CreateNewNotice(QDialog):
    new_data_signal = pyqtSignal(dict)
    def __init__(self):
        super(CreateNewNotice, self).__init__()
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
        self.type_combo.addItems(["交易所", "公司", "系统", "其他"])
        # buttons
        select_file_btn = QPushButton('选择')
        submit_btn = QPushButton('提交')
        # styles
        select_file_btn.setMaximumWidth(30)
        # signal
        select_file_btn.clicked.connect(self.select_file_clicked)
        submit_btn.clicked.connect(self.submit_notice)
        # add layout
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(self.name_edit, 0, 1, 1, 2)
        layout.addWidget(type_label, 1, 0)
        layout.addWidget(self.type_combo, 1, 1, 1, 2)
        layout.addWidget(file_label, 2, 0)
        layout.addWidget(self.file_edit, 2, 1)
        layout.addWidget(select_file_btn, 2, 2)
        layout.addWidget(submit_btn, 3, 1, 1, 2)
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

    def submit_notice(self):
        type_dict = {
            "公司": "company",
            "交易所": "changelib",
            "系统": "system",
            "其他":"others"
        }
        # collect data
        title = self.name_edit.text().strip(' ')
        type_text = self.type_combo.currentText()
        file_path = self.file_edit.text()
        if not title:
            QMessageBox.warning(self, "错误", "请起一个名字!", QMessageBox.Yes)
            return
        if not type_text:
            QMessageBox.warning(self, "错误", "请选择报告类型!", QMessageBox.Yes)
            return
        if not file_path:
            QMessageBox.warning(self, "错误", "请选择报告文件!", QMessageBox.Yes)
            return
        self.new_data_signal.emit({
            'title': title,
            'type_zh': type_text,
            'type_en': type_dict.get(type_text, None),
            'file_path': file_path
        })


class CreateNewReport(QDialog):
    new_data_signal = pyqtSignal(dict)

    def __init__(self):
        super(CreateNewReport, self).__init__()
        layout = QGridLayout()
        # labels
        title_label = QLabel("名称：")
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
        layout.addWidget(title_label, 0, 0)
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
        title = self.name_edit.text().strip(' ')
        type_text = self.type_combo.currentText()
        file_path = self.file_edit.text()
        if not title:
            QMessageBox.warning(self, "错误", "请起一个名字!", QMessageBox.Yes)
            return
        if not type_text:
            QMessageBox.warning(self, "错误", "请选择报告类型!", QMessageBox.Yes)
            return
        if not file_path:
            QMessageBox.warning(self, "错误", "请选择报告文件!", QMessageBox.Yes)
            return
        self.new_data_signal.emit({
            'title': title,
            'type_zh': type_text,
            'type_en': type_dict.get(type_text, None),
            'file_path': file_path
        })


