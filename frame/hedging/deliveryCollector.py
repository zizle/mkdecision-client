# _*_ coding:utf-8 _*_

import requests
import xlrd
import json
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QStackedWidget, QListWidgetItem,\
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
# from delivery.thread.request import RequestThread
# from delivery.widgets.table import TableCheckBox
from popup.tips import InformationPopup
import settings

class NotFoundMaintain(QWidget):
    def __init__(self):
        super(NotFoundMaintain, self).__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 0, 0, 0)  # 左上右下
        layout.addWidget(QLabel('404 Not Found !'))
        self.setLayout(layout)


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
        # self.get_data()

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
            token = settings.app_dawn.value('AUTHORIZATION')
            response = requests.post(
                url=self.data_url,
                headers={
                    'Content-Type': 'application/json',
                    'AUTHORIZATION': token
                },
                data=json.dumps(new_list)
            )
            response_message = json.loads(response.content)
            if response.status_code != 200:
                raise ValueError(response_message["message"])
        except Exception as e:
            popup = InformationPopup(title="错误", message=str(e))
        else:
            popup = InformationPopup(title="成功", message='上传数据成功.\n刷新看看吧.')
        if not popup.exec_():
            popup.deleteLater()
            del popup
            # self.review_table.clear()
        # 执行完毕开放可提交
        self.submit_btn.setEnabled(True)

    def update_item_info(self, pos):
        pass

    def submit_new_data(self):
        # 上传数据，整理数据与查重或规则限制，本方法需子类重写
        pass


class StorehouseMaintain(AbstractMaintainWidget):
    data_url = settings.SERVER_ADDR + 'delivery/storehouses/'

    def data_thread_back(self, content):
        if content['error']:
            return
        keys = [('serial_num', '序号'), ("name", "名称"),('longitude', '地址经度'), ('latitude', '地址纬度')]
        # keys = [('serial_num', '序号'), ('house_code', '仓库编号'), ('update_time', '最近更新'), ("name", "名称"),
        #         ("variety", "交割品种"), ('area', '所在省'), ('arrived', "到达站、港"), ('premium', '升贴水'),
        #         ('address', '地址'), ('link', '联系人'), ('tel_phone', '联系电话'), ('fax', '传真'),
        #         ('longitude', '地址经度'),('latitude', '地址纬度'), ('is_active', '有效')]
        self.fill_data_show_table(data=content['data']['data'], keys=keys)

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
    data_url = settings.SERVER_ADDR + 'maintain/housereports/'

    def data_thread_back(self, content):
        # print('获取仓单数据：', content)
        if content['error']:
            return
        # print(content)
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


# 上传品种的基本信息
class VarietyInformationMaintain(AbstractMaintainWidget):
    data_url = settings.SERVER_ADDR + 'delivery/variety-info/'

    def data_thread_back(self, content):
        if content['error']:
            return
        keys = [('serial_num', '序号'), ("name", "名称"),("name_en", "品种代码"), ('delivery_date', '最后交易日'),
                ('warrant_expire_date', "仓单有效期"), ('delivery_unit_min', '最小交割单位')]
        self.fill_data_show_table(data=content['data'], keys=keys)

    def get_header_labels(self):
        return ["名称", '品种代码', '最后交易日', '仓单有效期', '最小交割单位']

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
            old_item_text = self.show_table.item(old_row, 1)  # 品种名称
            old_item_code = self.show_table.item(old_row, 2)  # 品种代码
            for new_row in range(new_table_row):
                new_item_text = self.review_table.item(new_row, 0)  # 品种名称
                new_item_code = self.review_table.item(new_row, 1)
                if old_item_code.text() == new_item_code.text() and old_item_text.text() == new_item_text.text():
                    print('相等了：', new_row, 1)
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
            item['name'] = self.review_table.item(row, 0).text()
            item['name_en'] = self.review_table.item(row, 1).text()
            item['delivery_date'] = self.review_table.item(row, 2).text()
            item['warrant_expire_date'] = self.review_table.item(row, 3).text()
            item['delivery_unit_min'] = self.review_table.item(row, 4).text()
            # 检测数据完整性
            if not all([item['name_en'], item['name']]):
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


class DeliveryPageCollector(QWidget):
    def __init__(self, *args, **kwargs):
        super(DeliveryPageCollector, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(spacing=0, margin=0)
        self.left_menu = QListWidget()
        self.right_stack = QStackedWidget()
        layout.addWidget(self.left_menu)
        layout.addWidget(self.right_stack)
        self.setLayout(layout)
        # style
        self.left_menu.setMaximumWidth(130)
        # signal
        self.left_menu.clicked.connect(self.menu_clicked)
        # 请求菜单
        self.get_left_menu()
        # 样式
        self.left_menu.setFocusPolicy(Qt.NoFocus)
        self.left_menu.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
        QListWidget{
            background-color: rgb(240,240,240);
            border: none;
            font-size: 13px;
        }
        QListWidget::item{
            min-height: 30px;
            border: none;
            padding-left: 5px;
        }
        QListWidget::item:selected {
            border:none;
            background-color: rgb(255,255,255);
        }
        QListWidget::item:!selected{

        }
        QListWidget::item:hover {
            background-color: rgb(230,230,230);
            cursor: pointer;
        }
        QStackedWidget{

        }
        QPushButton{
            border:none;
            min-height: 23px;
            min-width: 50px;
        }
        QPushButton:hover{
            color: rgb(80, 100, 200);
            background-color: rgb(240,240,240)
        }
        #submitButton{
            background-color: rgb(121,205,205);
            margin: 5px 0;
            border-radius: 5px; 
        }
        QMessageBox::QPushButton{
            border: 1px solid rgb(80,80,80)
        }
        """)

    def get_left_menu(self):
        # 请求菜单
        menu_list = [
            {"name": u"仓库管理"},
            {"name": u"仓单管理"},
            {"name": u"品种信息"}
        ]
        for menu_dict in menu_list:
            menu_item = QListWidgetItem(menu_dict['name'])
            menu_item.name = menu_dict['name']
            self.left_menu.addItem(menu_item)
            if menu_item.name == u"仓库管理":
                stack_widget = StorehouseMaintain()
                stack_widget.name = u"仓库管理"
            elif menu_item.name == u"仓单管理":
                stack_widget = HouseReportMaintain()
                stack_widget.name = u"仓单管理"
            elif menu_item.name == u"品种信息":
                stack_widget = VarietyInformationMaintain()
                stack_widget.name = u"品种信息"
            else:
                stack_widget = NotFoundMaintain()
                stack_widget.name = ""
            self.right_stack.addWidget(stack_widget)
        self.left_menu.setCurrentRow(0)  # 默认选择第一个

    def menu_clicked(self, index):
        clicked_text = self.left_menu.currentItem().text()
        for index in range(self.right_stack.count()):
            win_frame = self.right_stack.widget(index)
            if win_frame.name == clicked_text:
                self.right_stack.setCurrentWidget(win_frame)
