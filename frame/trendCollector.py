# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QComboBox, QTableWidget, \
    QPushButton, QAbstractItemView, QHeaderView, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
import settings
from widgets.base import LoadedPage, TableRowDeleteButton
from popup.trendCollector import CreateNewTrendTablePopup


""" 数据表管理相关 """


# 数据表显示表格
class TrendDataTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '名称'),
        ('start_date', '起始时间'),
        ('end_date', '结束时间'),
        ('update_time', '最近更新'),
        ('editor', '更新者'),
    ]

    def __init__(self, *args, **kwargs):
        super(TrendDataTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS) + 1)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + [''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(len(self.KEY_LABELS), QHeaderView.ResizeToContents)
        for row, content_item in enumerate(row_list):
            print(content_item)
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = content_item[header[0]]
                else:
                    table_item = QTableWidgetItem(str(content_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
                if col == len(self.KEY_LABELS) - 1:
                    # 增加【删除】按钮
                    delete_button = TableRowDeleteButton('删除')
                    delete_button.button_clicked.connect(self.delete_button_clicked)
                    self.setCellWidget(row, col + 1, delete_button)

    # 删除一条数据
    def delete_button_clicked(self, delete_button):
        def delete_row_content():
            current_row, _ = self.get_widget_index(delete_button)
            spot_id = self.item(current_row, 0).id
            # 发起删除通知请求
            try:
                r = requests.delete(
                    url=settings.SERVER_ADDR + 'home/spot-commodity/' + str(
                        spot_id) + '/?mc=' + settings.app_dawn.value('machine'),
                    headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')}
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 200:
                    raise ValueError(response['message'])
            except Exception as e:
                self.network_result.emit(str(e))
            else:
                self.network_result.emit(response['message'])
                popup.close()
                # 移除本行
                self.removeRow(current_row)

        # 警示框
        popup = WarningPopup(parent=self)
        popup.confirm_button.connect(delete_row_content)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()



# 数据表管理页面
class TrendTableManagePage(QWidget):
    def __init__(self, *args, **kwargs):
        super(TrendTableManagePage, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 品种三联动菜单
        combo_link_layout = QHBoxLayout(spacing=2)
        combo_link_layout.addWidget(QLabel('类别:'))
        self.variety_group_combo = QComboBox(activated=self.getCurrentVarieties)
        combo_link_layout.addWidget(self.variety_group_combo)
        combo_link_layout.addWidget(QLabel('品种:'))
        self.variety_combo = QComboBox(activated=self.getCurrentTrendGroup)
        combo_link_layout.addWidget(self.variety_combo)
        combo_link_layout.addWidget(QLabel('数据:'))
        self.table_group_combo = QComboBox(activated=self.getCurrentTrendTable)
        combo_link_layout.addWidget(self.table_group_combo)
        # 网络请求信息
        self.network_message_label = QLabel()
        combo_link_layout.addWidget(self.network_message_label)
        combo_link_layout.addStretch()
        # 新建表
        self.create_trend_table = QPushButton('新建表', clicked=self.create_new_trend_table)
        combo_link_layout.addWidget(self.create_trend_table, alignment=Qt.AlignRight)
        layout.addLayout(combo_link_layout)
        # 数据表显示
        self.trend_data_table = TrendDataTable()
        layout.addWidget(self.trend_data_table)
        self.setLayout(layout)

    # 获取品种分组
    def getGroups(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'group-varieties/?mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.variety_group_combo.clear()
            self.variety_combo.clear()
            self.table_group_combo.clear()
            for group_item in response['data']:
                self.variety_group_combo.addItem(group_item['name'], group_item['id'])
            self.network_message_label.setText(response['message'])

    # 当前组下的品种
    def getCurrentVarieties(self):
        current_gid = self.variety_group_combo.currentData()
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'group-varieties/'+str(current_gid)+'/?mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.variety_combo.clear()
            self.table_group_combo.clear()
            for variety_item in response['data']:
                self.variety_combo.addItem(variety_item['name'], variety_item['id'])
            self.network_message_label.setText(response['message'])

    # 获取当前品种下的数据组
    def getCurrentTrendGroup(self):
        current_vid = self.variety_combo.currentData()
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/' + str(current_vid) + '/group-tables/?mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.table_group_combo.clear()
            for group_item in response['data']:
                self.table_group_combo.addItem(group_item['name'], group_item['id'])
            self.network_message_label.setText(response['message'])

    # 获取当前数据组下的所有数据表
    def getCurrentTrendTable(self):
        current_gid = self.table_group_combo.currentData()
        if not current_gid:
            return
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/group/' + str(current_gid) + '/table/?mc=' + settings.app_dawn.value(
                    'machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.trend_data_table.showRowContents(response['data'])
            self.network_message_label.setText(response['message'])







    # 新建数据表
    def create_new_trend_table(self):
        popup = CreateNewTrendTablePopup(parent=self)
        popup.getVarietyTableGroups()  # 获取左侧内容
        if not popup.exec_():
            popup.deleteLater()
            del popup


# 数据分析管理主页
class TrendPageCollector(QWidget):
    def __init__(self, *args, **kwargs):
        super(TrendPageCollector, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0)
        # 左侧管理菜单列表
        self.left_list = QListWidget(clicked=self.left_list_clicked)
        layout.addWidget(self.left_list, alignment=Qt.AlignLeft)
        # 右侧显示的frame
        self.frame_loaded = LoadedPage(parent=self)
        layout.addWidget(self.frame_loaded)
        self.setLayout(layout)
        self._addLeftListMenu()

    # 添加左侧管理菜单
    def _addLeftListMenu(self):
        for item in [u'数据表管理', '品种页表管理']:
            self.left_list.addItem(QListWidgetItem(item))

    # 点击左侧菜单列表
    def left_list_clicked(self):
        text = self.left_list.currentItem().text()
        if text == u'数据表管理':
            frame_page = TrendTableManagePage(parent=self.frame_loaded)
            frame_page.getGroups()  # 获取当前分组
            frame_page.getCurrentVarieties()  # 获取当前组下的品种
            frame_page.getCurrentTrendGroup()  # 获取当前品种下的数据组
            frame_page.getCurrentTrendTable()  # 获取当前数据组下的数据表

        else:
            frame_page = QLabel('【' + text + '】正在加紧开发中...')
        self.frame_loaded.clear()
        self.frame_loaded.addWidget(frame_page)


