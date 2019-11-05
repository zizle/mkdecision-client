# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import xlrd
import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,\
    QHeaderView, QMessageBox, QFileDialog, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
import config
from piece.base import TableCheckBox
from thread.request import RequestThread
from popup.maintain.danalysis import DANewHomeChart, DANewVarietyChart


class AbstractMaintainWidget(QWidget):
    """
    # 管理页面的基类
    data_thread_back 需在子类实现 (需重写)
    fill_data_show_table 给子类调用的填充数据表的方法
    get_header_labels 子类重写获取上传新数据时的表头限制 (需重写)
    set_review_table_scale 设置选定预览数据的表格伸缩方式  (重写随意)
    upload_data  供子类调用的上传数据的方法
    update_item_info  修改数据的[有效]框 (暂不实现此功能)
    submit_new_data  上传新数据整理与查重或规则限制 (需重写)
    """
    data_url = None  # 获取和上传数据，具体url子类需重写

    def __init__(self):
        super(AbstractMaintainWidget, self).__init__()
        layout = QVBoxLayout(spacing=0)
        layout.setContentsMargins(8, 0, 0, 0)  # 左上右下
        action_layout = QHBoxLayout()
        # widgets
        self.create_btn = QPushButton("+新增")
        self.refresh_btn = QPushButton('刷新')
        self.show_table = QTableWidget()
        self.review_table = QTableWidget()
        self.submit_btn = QPushButton("确认无误·提交")
        # 按钮风格
        self.create_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.submit_btn.setObjectName('submitButton')
        # signal
        self.create_btn.clicked.connect(self.create_new_data)
        self.refresh_btn.clicked.connect(self.get_data)
        self.submit_btn.clicked.connect(self.submit_new_data)
        # style
        self.show_table.verticalHeader().setVisible(False)
        self.review_table.hide()
        self.submit_btn.hide()
        # add layout
        action_layout.addWidget(self.create_btn)
        action_layout.addWidget(self.refresh_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        layout.addWidget(self.show_table)
        layout.addWidget(self.review_table)
        layout.addWidget(self.submit_btn)
        self.setLayout(layout)
        # initial data
        self.get_data_thread = None
        self.get_data()

    def get_data(self):
        self.review_table.hide()
        self.show_table.show()
        self.submit_btn.hide()
        if not self.data_url:
            return
        if self.get_data_thread:
            del self.get_data_thread
            # self.get_data_thread = None
        self.refresh_btn.setEnabled(False)
        self.get_data_thread = RequestThread(
            url=self.data_url,
            method='get',
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"machine_code": config.app_dawn.value("machine"), "maintain": True}),
            cookies=config.app_dawn.value('cookies')
        )
        # print('locals()[self.response_function]:', globals()[self.response_function])
        self.get_data_thread.finished.connect(self.get_data_thread.deleteLater)
        self.get_data_thread.response_signal.connect(self.data_thread_back)
        self.get_data_thread.start()

    def data_thread_back(self, content):
        # 子类实现
        pass

    def fill_data_show_table(self, data, keys):
        # 填充，供子类调用
        row = len(data)
        self.show_table.setRowCount(row)
        self.show_table.setColumnCount(len(keys))  # 列数
        labels = []
        set_keys = []
        for key_label in keys:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        self.show_table.setHorizontalHeaderLabels(labels)
        self.set_show_table_scale()  # 设置展示表格的伸缩
        self.show_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 第一列根据文字宽自适应
        self.show_table.verticalHeader().setVisible(False)
        for r in range(row):
            for c in range(self.show_table.columnCount()):
                if c == 0:
                    item = QTableWidgetItem(str(r + 1))  # 序号
                else:
                    label_key = set_keys[c]
                    if label_key == 'is_active':  # 是否启用选择框展示
                        checkbox = TableCheckBox(row=r, col=c, option_label=label_key)
                        checkbox.setChecked(int(data[r][label_key]))
                        checkbox.clicked_changed.connect(self.update_item_info)
                        self.show_table.setCellWidget(r, c, checkbox)
                    if label_key == 'variety':
                        if isinstance(data[r][label_key], list):
                            # print('品种字段为列表')
                            item = QTableWidgetItem(','.join(data[r][label_key]))
                        else:
                            # print('品种非列表')
                            item = QTableWidgetItem(str(data[r][label_key]))
                    else:
                        item = QTableWidgetItem(str(data[r][label_key]))
                item.setTextAlignment(132)
                self.show_table.setItem(r, c, item)
        # 刷新按钮可用
        self.refresh_btn.setEnabled(True)

    def create_new_data(self):
        self.show_table.hide()
        self.review_table.show()
        self.submit_btn.show()
        # 弹窗选择文件
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files (*.xlsx)")
        if not file_path:
            return
        # excel file header match
        header_labels = self.get_header_labels()  # 获取固定格式的表头
        if not header_labels:
            return
        # 处理Excel数据写入表格
        rf = xlrd.open_workbook(filename=file_path)
        sheet1 = rf.sheet_by_index(0)
        row_header = sheet1.row_values(0)
        if row_header != header_labels:
            QMessageBox.warning(self, '错误', '选择的文件格式有误.', QMessageBox.Yes)
            return
        # table initial
        self.review_table.setRowCount(sheet1.nrows - 1)
        self.review_table.setColumnCount(len(header_labels))
        self.review_table.setHorizontalHeaderLabels(header_labels)
        self.set_review_table_scale()  # 设置表格的伸缩
        for row in range(1, sheet1.nrows):  # skip header
            row_content = sheet1.row_values(row)
            # data to review table
            for col, col_data in enumerate(row_content):
                item = QTableWidgetItem(str(col_data))
                item.setTextAlignment(132)
                self.review_table.setItem(row - 1, col, item)

    def get_header_labels(self):
        # 子类需重写，确定每个数据源的表头, 数据格式为列表
        return []

    def set_review_table_scale(self):
        # 设置，子类可重写
        self.review_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 列自适应

    def set_show_table_scale(self):
        # 设置，子类可重写
        self.show_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 列自适应

    def upload_data(self, new_list):
        # 上传数据，供子类调用
        try:
            if not self.data_url:
                raise ValueError('上传的路径错误.')
            response = requests.post(
                url=self.data_url,
                headers={
                    "User-Agent": "DAssistant-Client/" + config.VERSION,
                },
                data=json.dumps(
                    {"machine_code": config.app_dawn.value("machine"),
                     "maintain": True,
                     "new_data": new_list
                     }),
                cookies=config.app_dawn.value('cookies')
            )
            response_message = json.loads(response.content.decode('utf-8'))
            if response.status_code != 200:
                raise ValueError(response_message["message"])
        except Exception as e:
            QMessageBox.information(self, '出错', str(e), QMessageBox.Yes)
        else:
            QMessageBox.information(self, '成功', '上传数据成功.\n刷新看看吧.', QMessageBox.Yes)
            # self.review_table.clear()
        # 执行完毕开放可提交
        self.submit_btn.setEnabled(True)

    def update_item_info(self, pos):
        pass

    def submit_new_data(self):
        # 上传数据，整理数据与查重或规则限制，本方法需子类重写
        pass


class VarietyMenuMaintain(AbstractMaintainWidget):
    data_url = config.SERVER_ADDR + 'danalysis/variety_menu/'

    def data_thread_back(self, content):
        if content['error']:
            return
        keys = [('serial_num', '序号'), ('create_time', '创建时间'), ("name", "名称"), ("name_en", "英文"),
                ("parent", "父级"), ('is_active', "启用")]
        self.fill_data_show_table(data=content['data'], keys=keys)

    def get_header_labels(self):
        return ["名称", "英文代码", "父级"]

    def submit_new_data(self):
        repeat_flag = False  # 标记重复（与原有数据，本身无作对比）
        self.submit_btn.setEnabled(False)  # 禁止重复点击提交
        # 遍历表格中所有数据# 对比是否有重复(标准：名称或英文代码一致)
        old_table_row = self.show_table.rowCount()
        new_table_row = self.review_table.rowCount()
        for old_row in range(old_table_row):
            old_item_zh = self.show_table.item(old_row, 2)
            old_item_en = self.show_table.item(old_row, 3)
            for new_row in range(new_table_row):
                new_item_zh = self.review_table.item(new_row, 0)
                new_item_en = self.review_table.item(new_row, 1)
                if old_item_zh.text() == new_item_zh.text():
                    # print('中文简称相等了：', new_row, 1)
                    # 重复了就改变当前行字体颜色
                    [self.review_table.item(new_row, col).setForeground(QBrush(QColor(255, 10, 20))) for col in
                     range(self.review_table.columnCount())]
                    # new_item_zh.setForeground(QBrush(QColor(255, 10, 20)))  # 改变了当前的item字体色
                    # item.setBackground(QBrush(QColor(220, 220, 220)))
                    repeat_flag = True
                if old_item_en.text() == new_item_en.text():
                    # print('英文代称相等了：', new_row, 2)
                    [self.review_table.item(new_row, col).setForeground(QBrush(QColor(255, 10, 20))) for col in
                     range(self.review_table.columnCount())]
                    # new_item_en.setForeground(QBrush(QColor(255, 10, 20)))  # 改变了当前的item字体色
                    # item.setBackground(QBrush(QColor(220, 220, 220)))
                    repeat_flag = True
        # 重复数据标出, 禁止上传
        if repeat_flag:
            # print('数据重复,请检查后上传')
            QMessageBox.warning(self, '错误', '红色标记数据重复.\n请检查后上传.', QMessageBox.Yes)
            # 开放可提交
            self.submit_btn.setEnabled(True)
            return
        # 所有数据非重复，上传
        # print('数据重复检测通过')
        # 获取数据
        new_list = list()
        for row in range(self.review_table.rowCount()):
            item = dict()
            item['name'] = self.review_table.item(row, 0).text()
            item['name_en'] = self.review_table.item(row, 1).text()
            item['parent'] = self.review_table.item(row, 2).text()
            new_list.append(item)
        self.upload_data(new_list)


class VarietyDetailMenuMaintain(AbstractMaintainWidget):
    data_url = config.SERVER_ADDR + 'danalysis/detail_menu/all/'

    def data_thread_back(self, content):
        # print(content)
        if content['error']:
            return
        keys = [('serial_num', '序号'), ('create_time', '创建时间'), ("name", "名称"), ("name_en", "英文"),
                ("parent", "父级"), ('is_active', "启用")]
        # 每个item含有subs,原来的方法不适用
        # self.fill_data_show_table(data=content['data'], keys=keys)

    def get_header_labels(self):
        return ['名称', '英文代码', '父级', '所属品种']

    def submit_new_data(self):
        blank_item = False  # 标记为空，品种不得为空
        self.submit_btn.setEnabled(False)  # 禁止重复点击提交
        # 原数据暂无填充无法判重
        # repeat_flag = False  # 标记重复（与原有数据，本身无作对比）
        # # 遍历表格中所有数据# 对比是否有重复(标准：名称或英文代码一致)
        # old_table_row = self.show_table.rowCount()
        new_table_row = self.review_table.rowCount()
        # for old_row in range(old_table_row):
        #     old_item_zh = self.show_table.item(old_row, 2)
        #     old_item_en = self.show_table.item(old_row, 3)
        #     for new_row in range(new_table_row):
        #         new_item_zh = self.review_table.item(new_row, 0)
        #         new_item_en = self.review_table.item(new_row, 1)
        #         if old_item_zh.text() == new_item_zh.text():
        #             # print('中文简称相等了：', new_row, 1)
        #             # 重复了就改变当前行字体颜色
        #             [self.review_table.item(new_row, col).setForeground(QBrush(QColor(255, 10, 20))) for col in
        #              range(self.review_table.columnCount())]
        #             # new_item_zh.setForeground(QBrush(QColor(255, 10, 20)))  # 改变了当前的item字体色
        #             # item.setBackground(QBrush(QColor(220, 220, 220)))
        #             repeat_flag = True

        # 判空
        for new_row in range(new_table_row):
            if not self.review_table.item(new_row, 3).text():
                [self.review_table.item(new_row, col).setForeground(QBrush(QColor(20, 10, 255))) for col in
                 range(self.review_table.columnCount())]
                blank_item = True

        # # 重复数据标出, 禁止上传
        # if repeat_flag:
        #     # print('数据重复,请检查后上传')
        #     QMessageBox.warning(self, '错误', '红色标记数据重复.\n请检查后上传.', QMessageBox.Yes)
        #     # 开放可提交
        #     self.submit_btn.setEnabled(True)
        #     return

        if blank_item:
            QMessageBox.warning(self, '错误', '蓝色标记数据所属品种为空.\n请检查后上传.', QMessageBox.Yes)
            # 开放可提交
            self.submit_btn.setEnabled(True)
            return
        # 所有数据非重复，上传
        # print('数据重复检测通过')
        # 获取数据
        new_list = list()
        for row in range(self.review_table.rowCount()):
            item = dict()
            item['name'] = self.review_table.item(row, 0).text()
            item['name_en'] = self.review_table.item(row, 1).text()
            item['parent'] = self.review_table.item(row, 2).text()
            item['variety'] = self.review_table.item(row, 3).text()
            new_list.append(item)
        self.upload_data(new_list)


# 首页图表管理页面
class DAHomeChartMaintain(AbstractMaintainWidget):
    data_url = config.SERVER_ADDR + 'danalysis/charts/home/'

    def data_thread_back(self, content):
        if content['error']:
            return
        # print(content)

    # 重写新增方法（弹窗新增）
    def create_new_data(self):
        popup = DANewHomeChart() # 上传首页图表的弹窗
        popup.upload_new.connect(self.upload_data)
        if not popup.exec_():
            del popup


# 品种页图表管理页面
class DAVarietyChartMaintain(AbstractMaintainWidget):
    data_url = config.SERVER_ADDR + 'danalysis/charts/variety/'

    def data_thread_back(self, content):
        if content['error']:
            return

    # 重写新增方法（弹窗新增）
    def create_new_data(self):
        popup = DANewVarietyChart()  # 上传品种图表的弹窗
        popup.upload_new.connect(self.upload_data)
        if not popup.exec_():
            del popup

