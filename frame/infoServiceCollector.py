# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QHBoxLayout, QLabel, QComboBox, \
    QTableWidget, QPushButton, QAbstractItemView, QHeaderView, QTableWidgetItem
from widgets.base import LoadedPage
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QPoint
import settings
from widgets.base import TableRowReadButton, TableRowDeleteButton, PDFContentPopup, Paginator
from popup.infoServiceCollector import CreateNewMarketAnalysisPopup


""" 市场分析相关 """


class MarketAnalysisMaintainTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '文件名称'),
        ('update_time', '日期'),
        ('creator', '创建者'),
    ]

    def __init__(self, *args, **kwargs):
        super(MarketAnalysisMaintainTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS) + 2)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + ['', ''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        for row, content_item in enumerate(row_list):
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = content_item[header[0]]
                    table_item.file = content_item['file']
                else:
                    table_item = QTableWidgetItem(str(content_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
                # if col in self.COLUMNS_CHECKED:  # 复选框按钮
                #     check_button = TableCheckBox(checked=content_item[header[0]])
                #     check_button.check_activated.connect(self.checked_button_changed)
                #     self.setCellWidget(row, col, check_button)
                if col == len(self.KEY_LABELS) - 1:
                    # 增加【查看】按钮
                    read_button = TableRowReadButton('查看')
                    read_button.button_clicked.connect(self.read_button_clicked)
                    self.setCellWidget(row, col + 1, read_button)
                    # 增加【删除】按钮
                    delete_button = TableRowDeleteButton('删除')
                    delete_button.button_clicked.connect(self.delete_button_clicked)
                    self.setCellWidget(row, col + 2, delete_button)

    # 查看一个市场分析
    def read_button_clicked(self, read_button):
        current_row, _ = self.get_widget_index(read_button)
        file = self.item(current_row, 0).file
        # 显示文件
        file = settings.STATIC_PREFIX + file
        popup = PDFContentPopup(title='阅读文件', file=file, parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 删除一个市场分析
    def delete_button_clicked(self, delete_button):
        current_row, _ = self.get_widget_index(delete_button)
        file_id = self.item(current_row, 0).id
        try:
            r = requests.delete(
                url=settings.SERVER_ADDR + 'info/market-analysis/' + str(file_id) + '/?mc=' + settings.app_dawn.value(
                    'machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')}
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            self.removeRow(current_row)

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 市场分析管理主页
class MarketAnalysisMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(MarketAnalysisMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        message_button_layout = QHBoxLayout()
        self.paginator = Paginator()
        self.paginator.clicked.connect(self.getFileContents)
        message_button_layout.addWidget(self.paginator)
        message_button_layout.addStretch()
        self.network_message_label = QLabel()
        message_button_layout.addWidget(self.network_message_label)
        message_button_layout.addWidget(QPushButton('新增', clicked=self.create_analysis_file), alignment=Qt.AlignRight)
        layout.addLayout(message_button_layout)
        # 显示的表格
        self.table = MarketAnalysisMaintainTable()
        layout.addWidget(self.table)
        self.setLayout(layout)

    # 获取内容
    def getFileContents(self):
        current_page = self.paginator.current_page
        try:
            url = settings.SERVER_ADDR + 'info/market-analysis/?page=' + str(
                current_page) + '&mc=' + settings.app_dawn.value('machine')

            r = requests.get(url=url)
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.paginator.setTotalPages(response['data']['total_page'])
            self.table.showRowContents(response['data']['contacts'])
            self.network_message_label.setText(response['message'])

    # 新增一个文件
    def create_analysis_file(self):
        popup = CreateNewMarketAnalysisPopup(parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup


""" 短信通相关 """


# 维护表格
class SMSTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('date', '日期'),
        ('time', '时间'),
        ('content', '内容'),
        ('creator', '创建者'),
    ]

    def __init__(self, *args, **kwargs):
        super(SMSTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS) + 2)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + ['', ''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        for row, content_item in enumerate(row_list):
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = content_item[header[0]]
                else:
                    table_item = QTableWidgetItem(str(content_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
                # if col in self.COLUMNS_CHECKED:  # 复选框按钮
                #     check_button = TableCheckBox(checked=content_item[header[0]])
                #     check_button.check_activated.connect(self.checked_button_changed)
                #     self.setCellWidget(row, col, check_button)
                if col == len(self.KEY_LABELS) - 1:
                    # 增加【查看】按钮
                    edit_button = TableRowReadButton('编辑')
                    edit_button.button_clicked.connect(self.edit_button_clicked)
                    self.setCellWidget(row, col + 1, edit_button)
                    # # 增加【删除】按钮
                    delete_button = TableRowDeleteButton('删除')
                    delete_button.button_clicked.connect(self.delete_button_clicked)
                    self.setCellWidget(row, col + 2, delete_button)

    # 编辑按钮
    def edit_button_clicked(self, edit_button):
        current_row, _ = self.get_widget_index(edit_button)
        message_id = self.item(current_row, 0).id
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'info/sms/' + str(message_id) + '/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            self.network_result.emit(response['message'])
            # 弹窗设置
            try:
                from popup.infoServiceCollector import EditSMSLink
                edit_popup = EditSMSLink(sms_data=response['data'], parent=self)
                if not edit_popup.exec_():
                    edit_popup.deleteLater()
                    del edit_popup
            except Exception as e:
                print(e)


    # 删除按钮
    def delete_button_clicked(self, delete_button):
        current_row, _ = self.get_widget_index(delete_button)
        message_id = self.item(current_row, 0).id
        try:
            r = requests.delete(
                url=settings.SERVER_ADDR + 'info/sms/' + str(message_id) + '/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')}
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            self.removeRow(current_row)
            self.network_result.emit(response['message'])

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 短信通维护主页
class MessageServiceMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(MessageServiceMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        combo_message_layout = QHBoxLayout()
        self.date_combo = QComboBox(activated=self.getCurrentSMS)
        combo_message_layout.addWidget(self.date_combo, alignment=Qt.AlignLeft)
        self.network_message_label = QLabel()
        combo_message_layout.addWidget(self.network_message_label)
        combo_message_layout.addWidget(QPushButton('新增', clicked=self.create_new_sms), alignment=Qt.AlignRight)
        layout.addLayout(combo_message_layout)
        # 展示短信通的表格
        self.sms_table = SMSTable()
        layout.addWidget(self.sms_table)
        self.setLayout(layout)
        self._addCombo()

    # 添加时间选择
    def _addCombo(self):
        for date_item in [
            {'name': '今日', 'days': 0},
            {'name': '最近3天', 'days': -3},
            {'name': '最近7天', 'days': -7},
            {'name': '全部', 'days': 'all'},
        ]:
            self.date_combo.addItem(date_item['name'], date_item['days'])

    # 获取当前短信通信息
    def getCurrentSMS(self):
        current_data = self.date_combo.currentData()
        current_date = QDate.currentDate()
        if current_data != 'all':
            min_date = current_date.addDays(current_data)
            url = settings.SERVER_ADDR + 'info/sms/?mc='+settings.app_dawn.value('machine')+'&min_date=' + min_date.toString('yyyy-MM-dd')
        else:
            url = settings.SERVER_ADDR + 'info/sms/?mc=' + settings.app_dawn.value('machine')
        try:
            r = requests.get(url=url)
            response = json.loads(r.content.decode('utf-8'))
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            print(response)
            self.sms_table.showRowContents(response['data'])


    # 新增一条短信通
    def create_new_sms(self):
        from popup.infoServiceCollector import CreateNewSMSLink
        popup = CreateNewSMSLink(parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup


# 产品服务管理主页
class InfoServicePageCollector(QWidget):
    def __init__(self, *args, **kwargs):
        super(InfoServicePageCollector, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0)
        # 左侧管理菜单
        self.left_tree = QTreeWidget(clicked=self.left_tree_clicked)
        self.left_tree.header().hide()
        layout.addWidget(self.left_tree, alignment=Qt.AlignLeft)
        # 右侧显示窗口
        self.right_frame = LoadedPage()
        layout.addWidget(self.right_frame)
        self.setLayout(layout)
        self._addLeftTreeContentes()

    # 添加管理菜单
    def _addLeftTreeContentes(self):
        contents = [
            {
                'name': u'咨询服务',
                'subs': [
                    {'id': 1, 'name': u'短信通'},
                    {'id': 2, 'name': u'市场分析'},
                    {'id': 3, 'name': u'专题研究'},
                    {'id': 4, 'name': u'调研报告'},
                    {'id': 5, 'name': u'市场路演'},
                ]
            },
            {
                'name': u'顾问服务',
                'subs': [
                    {'id': 6, 'name': u'人才培养'},
                    {'id': 7, 'name': u'部门组建'},
                    {'id': 8, 'name': u'制度考核'},
                ]
            },
            {
                'name': u'策略服务',
                'subs': [
                    {'id': 9, 'name': u'交易策略'},
                    {'id': 10, 'name': u'投资方案'},
                    {'id': 11, 'name': u'套保方案'},
                ]
            },
            {
                'name': u'培训服务',
                'subs': [
                    {'id': 12, 'name': u'品种介绍'},
                    {'id': 13, 'name': u'基本分析'},
                    {'id': 14, 'name': u'技术分析'},
                    {'id': 15, 'name': u'制度规则'},
                    {'id': 16, 'name': u'交易管理'},
                    {'id': 17, 'name': u'经验分享'},
                ]
            },
        ]
        # 填充树
        for group_item in contents:
            group = QTreeWidgetItem(self.left_tree)
            group.setText(0, group_item['name'])
            # 添加子节点
            for variety_item in group_item['subs']:
                child = QTreeWidgetItem()
                child.setText(0, variety_item['name'])
                child.sid = variety_item['id']
                group.addChild(child)
        self.left_tree.expandAll()  # 展开所有

    # 点击左侧菜单
    def left_tree_clicked(self):
        item = self.left_tree.currentItem()
        if item.childCount():  # has children open the root
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
            return
        service_id = item.sid
        text = item.text(0)
        print(service_id)
        if service_id == 1:  # 短信通
            page = MessageServiceMaintain()
            page.getCurrentSMS()
        elif service_id == 2:  # 市场分析
            page = MarketAnalysisMaintain()
            page.getFileContents()
        else:
            page = QLabel('【' + text + '】还不能进行数据管理...',
                          styleSheet='color:rgb(50,180,100); font-size:15px;font-weight:bold', alignment=Qt.AlignCenter)

        self.right_frame.clear()
        self.right_frame.addWidget(page)










