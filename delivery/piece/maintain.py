# _*_ coding:utf-8 _*_
# __Author__： zizle

"""数据上传的窗口"""
import xlrd
import json
from delivery import config
import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton,\
    QTableWidget, QHeaderView, QTableWidgetItem, QFileDialog, QMessageBox, QLabel
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import Qt
from delivery.thread.request import RequestThread
from delivery.widgets.table import TableCheckBox


class AbstractMaintainWidget(QWidget):
    """
    # 管理页面的基类
    data_thread_back 需在子类实现 (需重写)
    fill_data_show_table 给子类调用的填充数据表的方法
    get_header_labels 子类重写改方法获取上传新数据时的表头限制 (需重写)
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
        try:
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
        except Exception as e:
            print(e)

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
            token = config.APP_DAWN.value('token') if config.APP_DAWN.value('token') else ''
            response = requests.post(
                url=self.data_url,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'JWT ' + token
                },
                data=json.dumps(new_list)
            )
            response_message = response.content.decode('utf-8')
            if response.status_code != 200:
                raise ValueError(response_message)
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


class NotFoundMaintain(QWidget):
    def __init__(self):
        super(NotFoundMaintain, self).__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 0, 0, 0)  # 左上右下
        layout.addWidget(QLabel('404 Not Found !'))
        self.setLayout(layout)


class AreaMaintain(AbstractMaintainWidget):
    data_url = config.SERVER + 'maintain/areas/'

    def data_thread_back(self, content):
        # print('请求地区数据成功', content)
        if content['error']:
            return
        keys = [('serial_num', '序号'), ('update_time', '最近更新'), ("name", "名称"), ("short_name", "中文简称"),
                ("en_code", "英文代称"), ('is_active', "启用")]
        self.fill_data_show_table(data=content['data'], keys=keys)

    def get_header_labels(self):
        return ["名称", "中文简称", "英文代称"]

    def submit_new_data(self):
        repeat_flag = False  # 标记重复
        self.submit_btn.setEnabled(False)  # 禁止重复点击提交
        # 遍历表格中所有数据# 对比是否有重复(标准：中文简称或英文代称一致)
        old_table_row = self.show_table.rowCount()
        new_table_row = self.review_table.rowCount()
        for old_row in range(old_table_row):
            old_item_zh = self.show_table.item(old_row, 3)
            old_item_en = self.show_table.item(old_row, 4)
            for new_row in range(new_table_row):
                new_item_zh = self.review_table.item(new_row, 1)
                new_item_en = self.review_table.item(new_row, 2)
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
            item['short_name'] = self.review_table.item(row, 1).text()
            item['en_code'] = self.review_table.item(row, 2).text()
            new_list.append(item)

        self.upload_data(new_list)


class ExchangeMaintain(AbstractMaintainWidget):
    data_url = config.SERVER + 'maintain/exchanges/'

    def data_thread_back(self, content):
        # print('请求交易所数据成功', content)
        if content['error']:
            return
        keys = [('serial_num', '序号'), ('update_time', '最近更新'), ("name", "名称"),
                ("en_code", "英文代号"), ('web_url', '网址'), ('is_active', "启用")]
        self.fill_data_show_table(data=content['data'], keys=keys)

    def get_header_labels(self):
        return ["名称", "英文代号", "网址"]

    def submit_new_data(self):
        repeat_flag = False  # 标记重复
        self.submit_btn.setEnabled(False)  # 禁止重复点击提交
        # 遍历表格中所有数据# 对比是否有重复(标准：名称或英文代号一致)
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
            item['en_code'] = self.review_table.item(row, 1).text()
            item['web_url'] = self.review_table.item(row, 2).text()
            new_list.append(item)

        self.upload_data(new_list)


class VarietyMaintain(AbstractMaintainWidget):
    data_url = config.SERVER + 'maintain/varieties/'

    def data_thread_back(self, content):
        # print('请求品种数据成功', content)
        if content['error']:
            return
        keys = [('serial_num', '序号'), ('update_time', '最近更新'), ("name", "名称"),
                ("en_code", "英文代号"), ('exchange', '所属交易所'), ("delivery_date", "最后交易日"),
                ("warrant_expire_date", "仓单有效期"), ("delivery_unit_min", "最小交割单位"),
                ('is_active', "有效")]
        self.fill_data_show_table(data=content['data'], keys=keys)

    def get_header_labels(self):
        return ["名称", "英文代号(小写)", '所属交易所', '交易所英文代号(小写)', '最后交易日', '仓单有效期', '最小交割单位']

    def set_show_table_scale(self):
        self.show_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def submit_new_data(self):
        repeat_flag = False  # 标记重复
        self.submit_btn.setEnabled(False)  # 禁止重复点击提交
        # 遍历表格中所有数据# 对比是否有重复(标准：名称或英文代号一致)
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
            item['en_code'] = self.review_table.item(row, 1).text()
            item['exchange_en'] = self.review_table.item(row, 3).text()
            item['delivery_date'] = self.review_table.item(row, 4).text()
            item['warrant_expire_date'] = self.review_table.item(row, 5).text()
            # item['delivery_unit'] = self.review_table.item(row, 6).text()
            item['delivery_unit_min'] = self.review_table.item(row, 6).text()
            new_list.append(item)
        self.upload_data(new_list)


class StorehouseMaintain(AbstractMaintainWidget):
    data_url = config.SERVER + 'maintain/storehouses/'

    def data_thread_back(self, content):
        # print('请求仓库数据成功', content)
        if content['error']:
            return
        keys = [('serial_num', '序号'), ('house_code', '仓库编号'), ('update_time', '最近更新'), ("name", "名称"),
                ("variety", "交割品种"), ('area', '所在省'), ('arrived', "到达站、港"), ('premium', '升贴水'),
                ('address', '地址'), ('link', '联系人'), ('tel_phone', '联系电话'), ('fax', '传真'),
                ('longitude', '地址经度'),('latitude', '地址纬度'), ('is_active', '有效')]
        self.fill_data_show_table(data=content['data'], keys=keys)

    def get_header_labels(self):
        return ["仓库编码", "名称", '交割品种', '品种代号(小写)', '所属省份',
                         '省份英文代称(小写)', '到达站、港', '升贴水', '地址', '联系人', '联系电话',
                         '传真', '地址经度', '地址纬度']

    def set_show_table_scale(self):
        self.show_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # 列自适应
        self.show_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 第一列根据文字宽自适应

    def submit_new_data(self):
        repeat_flag = False  # 标记重复
        null_flag = False
        self.submit_btn.setEnabled(False)  # 禁止重复点击提交
        # 遍历表格中所有数据# 对比是否有重复(标准：名称或英文代号一致)
        old_table_row = self.show_table.rowCount()
        new_table_row = self.review_table.rowCount()
        for old_row in range(old_table_row):
            old_item_code = self.show_table.item(old_row, 1)  # 仓库编号代码
            for new_row in range(new_table_row):
                new_item_code = self.review_table.item(new_row, 0)  # 仓库编号代码
                if old_item_code.text() == new_item_code.text():
                    # print('编码相等了：', new_row, 1)
                    # 重复了就改变当前行字体颜色
                    [self.review_table.item(new_row, col).setForeground(QBrush(QColor(255, 10, 20))) for col in
                     range(self.review_table.columnCount())]
                    # new_item_zh.setForeground(QBrush(QColor(255, 10, 20)))  # 改变了当前的item字体色
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
            item['house_code'] = self.review_table.item(row, 0).text()
            item['name'] = self.review_table.item(row, 1).text()
            item['varieties'] = (self.review_table.item(row, 2).text()).split(',')
            item['varieties_en'] = (self.review_table.item(row, 3).text()).split(',')
            item['province'] = self.review_table.item(row, 4).text()
            item['province_en'] = self.review_table.item(row, 5).text()
            item['arrived'] = self.review_table.item(row, 6).text()
            item['premium'] = self.review_table.item(row, 7).text()
            item['address'] = self.review_table.item(row, 8).text()
            item['link'] = self.review_table.item(row, 9).text()
            item['tel_phone'] = self.review_table.item(row, 10).text()
            item['fax'] = self.review_table.item(row, 11).text()
            item['longitude'] = self.review_table.item(row, 12).text()
            item['latitude'] = self.review_table.item(row, 13).text()
            # 检测数据完整性(仓库编码、名称、品种、省份、经度、纬度)
            if not all([item['house_code'], item['name'], item['varieties_en'], item['province_en'], item['longitude'],
                        item['latitude']]):
                null_flag = True
                # 标记出本行
                [self.review_table.item(row, col).setForeground(QBrush(QColor(255, 10, 20))) for col in
                 range(self.review_table.columnCount())]
                # break
            new_list.append(item)
        if null_flag:
            # 数据缺失禁止上传
            QMessageBox.warning(self, '错误', '红色标记数据条目有缺少.\n请检查后上传.', QMessageBox.Yes)
            # 开放可提交
            self.submit_btn.setEnabled(True)
            return

        self.upload_data(new_list)


class HouseReportMaintain(AbstractMaintainWidget):
    data_url = config.SERVER + 'maintain/housereports/'

    def data_thread_back(self, content):
        # print('获取仓单数据：', content)
        if content['error']:
            return
        keys = [('serial_num', '序号'), ('date', '日期'), ('storehouse', '仓库编号'), ('house_name', '仓库'),
                ('variety', '品种'), ("yesterday_report", "昨日仓单量"), ("today_report", "今日仓单量"),
                ('regulation', '增减'), ('is_active', '有效')]
        self.fill_data_show_table(data=content['data'], keys=keys)

    def get_header_labels(self):
        return ['日期', '仓库编号', '仓库简称', '品种', '品种代号', '昨日仓单量', '仓单量', '增减']

    def submit_new_data(self):
        repeat_flag = False  # 标记重复
        null_flag = False  # 标记为空
        self.submit_btn.setEnabled(False)  # 禁止重复点击提交
        # 遍历表格中所有数据# 对比是否有重复(标准：日期和品种一致)
        old_table_row = self.show_table.rowCount()
        new_table_row = self.review_table.rowCount()
        for old_row in range(old_table_row):
            old_item_date = self.show_table.item(old_row, 1)  # 日期
            old_item_variety = self.show_table.item(old_row, 4)  # 品种
            for new_row in range(new_table_row):
                new_item_date = self.review_table.item(new_row, 0)  # 日期
                new_item_variety = self.review_table.item(new_row, 3)  # 品种
                if old_item_date.text() == new_item_date.text() and old_item_variety.text() == new_item_variety.text():
                    # print('日期和品种相等了：', new_row, 1)
                    [self.review_table.item(new_row, col).setForeground(QBrush(QColor(255, 10, 20))) for col in
                     range(self.review_table.columnCount())]
                    repeat_flag = True
        # 重复数据标出, 禁止上传
        if repeat_flag:
            # print('数据重复,请检查后上传')
            QMessageBox.warning(self, '错误', '红色标记数据重复.\n请检查后上传.', QMessageBox.Yes)
            # 开放可提交
            self.submit_btn.setEnabled(True)
            return
        # print('数据重复检测通过')
        # 所有数据非重复，获取数据,上传.
        new_list = list()
        for row in range(self.review_table.rowCount()):
            item = dict()
            item['date'] = self.review_table.item(row, 0).text()
            item['house_code'] = self.review_table.item(row, 1).text()
            item['house_name'] = self.review_table.item(row, 2).text()
            item['variety'] = self.review_table.item(row, 4).text()
            item['yesterday_report'] = self.review_table.item(row, 5).text()
            item['today_report'] = self.review_table.item(row, 6).text()
            item['regulation'] = self.review_table.item(row, 7).text()

            # 检测数据完整性(日期、仓库编号、名称、品种代号、昨日仓单量、今日仓单量、增减)
            if not all([item['date'], item['house_code'], item['house_name'], item['variety'], item['yesterday_report'],
                        item['today_report'], item['regulation']]):
                null_flag = True
                # 标记出本行
                [self.review_table.item(row, col).setForeground(QBrush(QColor(255, 10, 20))) for col in
                 range(self.review_table.columnCount())]
            new_list.append(item)
        if null_flag:  # 数据缺失禁止上传
            QMessageBox.warning(self, '错误', '红色标记数据条目有缺少.\n请检查后上传.', QMessageBox.Yes)
            self.submit_btn.setEnabled(True)  # 开放可提交
            return
        # 上传数据
        self.upload_data(new_list)


class NewsMaintain(AbstractMaintainWidget):
    data_url = config.SERVER + 'maintain/news/'

    def data_thread_back(self, content):
        # print('请求新闻数据成功', content)
        if content['error']:
            return
        keys = [('message', '序号'), ('message', '信息')]
        self.fill_data_show_table(data=content['data'], keys=keys)

    def get_header_labels(self):
        return ['日期', '交易所', '交易所英文', '新闻标题', '内容']

    def submit_new_data(self):
        null_flag = False  # 标记为空
        self.submit_btn.setEnabled(False)  # 禁止重复点击提交
        new_list = list()
        for row in range(self.review_table.rowCount()):
            item = dict()
            item['date'] = self.review_table.item(row, 0).text()
            item['exchange_en'] = self.review_table.item(row, 2).text()
            item['title'] = self.review_table.item(row, 3).text()
            item['content'] = self.review_table.item(row, 4).text()
            # 检测数据完整性(日期、标题、内容、交易所代号)
            if not all([item['date'], item['title'], item['content'], item['exchange_en']]):
                null_flag = True
                # 标记出本行
                [self.review_table.item(row, col).setForeground(QBrush(QColor(255, 10, 20))) for col in
                 range(self.review_table.columnCount())]
            new_list.append(item)
        if null_flag:  # 数据缺失禁止上传
            QMessageBox.warning(self, '错误', '红色标记数据条目有缺少.\n请检查后上传.', QMessageBox.Yes)
            self.submit_btn.setEnabled(True)  # 开放可提交
            return
        # 上传数据
        self.upload_data(new_list)


class BulletinMaintain(NewsMaintain):
    data_url = config.SERVER + 'maintain/bulletin/'

    def get_header_labels(self):
        return ['日期', '交易所', '交易所英文', '公告标题', '内容']
