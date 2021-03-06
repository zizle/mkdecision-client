# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import pickle
import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QHBoxLayout, QLabel, QComboBox, \
    QTableWidget, QPushButton, QAbstractItemView, QHeaderView, QTableWidgetItem, QMenu, QMessageBox
from widgets.base import LoadedPage
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QPoint
import settings
from widgets.base import TableRowReadButton, TableRowDeleteButton, PDFContentPopup, Paginator, PDFContentShower
from popup.infoServiceCollector import CreateNewSMSLink, EditSMSLink, CreateNewMarketAnalysisPopup, \
    CreateNewSearchReportPopup, CreateNewTopicSearchPopup, ModifyPersonnelTrainPopup, ModifyDeptBuildPopup, \
    ModifyInstExaminePopup, CreateNewTradePolicyPopup, EditTradePolicy, CreateNewInvestPlanPopup, CreateNewHedgePlanPopup, \
    ModifyVarietyIntroPopup


""" 培训服务-品种介绍 """


# 品种介绍
class VarietyIntroMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(VarietyIntroMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        layout.addWidget(QPushButton('修改', clicked=self.modify_file), alignment=Qt.AlignRight)
        # 显示服务端pdf文件
        content_show = PDFContentShower(file=settings.STATIC_PREFIX + 'pserver/varietyintro/品种介绍.pdf', parent=self)
        layout.addWidget(content_show)
        self.setLayout(layout)

    def modify_file(self):
        popup = ModifyVarietyIntroPopup(parent=self)
        popup.exec_()


""" 策略服务-套保方案 """


# 显示套保方案表格
class HedgePlanMaintainTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '文件名称'),
        ('update_time', '日期'),
        ('creator', '创建者'),
    ]

    def __init__(self, *args, **kwargs):
        super(HedgePlanMaintainTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        table_headers = ['序号', '日期', '方案标题']
        self.setColumnCount(len(table_headers))
        self.setRowCount(len(row_list))
        self.setHorizontalHeaderLabels(table_headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, row_item in enumerate(row_list):
            item0 = QTableWidgetItem(str(row + 1))
            item0.setTextAlignment(Qt.AlignCenter)
            item0.id = row_item['id']
            item0.file_url = row_item['file_url']
            self.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item['create_time'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item1)
            item2 = QTableWidgetItem(row_item['title'])
            item2.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, item2)

    def mousePressEvent(self, event):
        index = self.indexAt(QPoint(event.pos().x(), event.pos().y()))
        row, _ = index.row(), index.column()
        if row < 0:
            return
        self.setCurrentIndex(index)
        if event.buttons() == Qt.RightButton:
            rmenu = QMenu()
            rmenu.setAttribute(Qt.WA_DeleteOnClose)
            view_action = rmenu.addAction("查看")
            view_action.triggered.connect(self.view_file_detail)
            delete_action = rmenu.addAction("删除")
            delete_action.triggered.connect(self.delete_row_record)
            rmenu.exec_(QCursor.pos())

        # super(ReportTable, self).mousePressEvent(event)  # 事件不再往外传了

    def view_file_detail(self):
        row = self.currentRow()
        title = self.item(row, 2).text()
        itemfile = self.item(row, 0).file_url
        file_addr = settings.STATIC_PREFIX + itemfile
        popup = PDFContentPopup(title=title, file=file_addr)
        popup.exec_()

    def delete_row_record(self):
        delete_action = QMessageBox.warning(self, "提示", "删除将不可恢复!", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if delete_action != QMessageBox.Yes:
            return
        row = self.currentRow()
        itemid = self.item(row, 0).id
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            r = requests.delete(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/hedgeplan/' + str(itemid) + '/?utoken=' + settings.app_dawn.value('AUTHORIZATION')
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, "错误", str(e))
        else:
            self.removeRow(row)
            QMessageBox.information(self, "成功", '删除成功!')



# 套保方案管理
class HedgePlanMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(HedgePlanMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        message_button_layout = QHBoxLayout()
        self.paginator = Paginator()
        self.paginator.clicked.connect(self.getFileContents)
        message_button_layout.addWidget(self.paginator)
        message_button_layout.addStretch()
        self.network_message_label = QLabel()
        message_button_layout.addWidget(self.network_message_label)
        message_button_layout.addWidget(QPushButton('新增', clicked=self.create_topic_file), alignment=Qt.AlignRight)
        layout.addLayout(message_button_layout)
        # 显示的表格
        self.table = HedgePlanMaintainTable()
        layout.addWidget(self.table)
        self.setLayout(layout)

    # 获取内容
    def getFileContents(self):
        current_page = self.paginator.current_page
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            url = settings.SERVER_ADDR + 'user/'+ str(user_id) + '/hedgeplan/?page=' + str(current_page)
            r = requests.get(url=url)
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.paginator.setTotalPages(response['total_page'])
            self.table.showRowContents(response['records'])
            self.network_message_label.setText(response['message'])

    # 上传套保方案文件
    def create_topic_file(self):
        popup = CreateNewHedgePlanPopup(parent=self)
        popup.exec_()

""" 策略服务-投资方案相关 """


# 显示投资方案表格
class InvestPlanMaintainTable(QTableWidget):
    network_result = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(InvestPlanMaintainTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        table_headers = ['序号', '日期', '方案标题']
        self.setColumnCount(len(table_headers))
        self.setRowCount(len(row_list))
        self.setHorizontalHeaderLabels(table_headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, row_item in enumerate(row_list):
            item0 = QTableWidgetItem(str(row + 1))
            item0.setTextAlignment(Qt.AlignCenter)
            item0.id = row_item['id']
            item0.file_url = row_item['file_url']
            self.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item['create_time'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item1)
            item2 = QTableWidgetItem(row_item['title'])
            item2.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, item2)

    def mousePressEvent(self, event):
        index = self.indexAt(QPoint(event.pos().x(), event.pos().y()))
        row, _ = index.row(), index.column()
        if row < 0:
            return
        self.setCurrentIndex(index)
        if event.buttons() == Qt.RightButton:
            rmenu = QMenu()
            rmenu.setAttribute(Qt.WA_DeleteOnClose)
            view_action = rmenu.addAction("查看")
            view_action.triggered.connect(self.view_file_detail)
            delete_action = rmenu.addAction("删除")
            delete_action.triggered.connect(self.delete_row_record)
            rmenu.exec_(QCursor.pos())

        # super(ReportTable, self).mousePressEvent(event)  # 事件不再往外传了

    def view_file_detail(self):
        row = self.currentRow()
        title = self.item(row, 2).text()
        itemfile = self.item(row, 0).file_url
        file_addr = settings.STATIC_PREFIX + itemfile
        popup = PDFContentPopup(title=title, file=file_addr)
        popup.exec_()

    def delete_row_record(self):
        delete_action = QMessageBox.warning(self, "提示", "删除将不可恢复!", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if delete_action != QMessageBox.Yes:
            return
        row = self.currentRow()
        itemid = self.item(row, 0).id
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            r = requests.delete(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/investmentplan/' + str(itemid) + '/?utoken=' + settings.app_dawn.value('AUTHORIZATION')
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, "错误", str(e))
        else:
            self.removeRow(row)
            QMessageBox.information(self, "成功", '删除成功!')



# 投资方案管理
class InvestPlanMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(InvestPlanMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        message_button_layout = QHBoxLayout()
        self.paginator = Paginator()
        self.paginator.clicked.connect(self.getFileContents)
        message_button_layout.addWidget(self.paginator)
        message_button_layout.addStretch()
        self.network_message_label = QLabel()
        message_button_layout.addWidget(self.network_message_label)
        message_button_layout.addWidget(QPushButton('新增', clicked=self.create_topic_file), alignment=Qt.AlignRight)
        layout.addLayout(message_button_layout)
        # 显示的表格
        self.table = InvestPlanMaintainTable()
        layout.addWidget(self.table)
        self.setLayout(layout)

    # 获取内容
    def getFileContents(self):
        current_page = self.paginator.current_page
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            url = settings.SERVER_ADDR + 'user/' + str(user_id) + '/investmentplan/?page='+ str(current_page)
            r = requests.get(url=url)
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.paginator.setTotalPages(response['total_page'])
            self.table.showRowContents(response['records'])
            self.network_message_label.setText(response['message'])

    # 上传投资方案文件
    def create_topic_file(self):
        popup = CreateNewInvestPlanPopup(parent=self)
        popup.exec_()


"""策略服务-交易策略相关 """


# 维护表格
class TradePolicyTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('date', '日期'),
        ('time', '时间'),
        ('content', '内容'),
        ('creator', '创建者'),
    ]

    def __init__(self, *args, **kwargs):
        super(TradePolicyTable, self).__init__(*args, **kwargs)
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
                url=settings.SERVER_ADDR + 'info/trade-policy/' + str(message_id) + '/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            self.network_result.emit(response['message'])
            # 弹窗设置
            edit_popup = EditTradePolicy(sms_data=response['data'], parent=self)
            if not edit_popup.exec_():
                edit_popup.deleteLater()
                del edit_popup

    # 删除按钮
    def delete_button_clicked(self, delete_button):
        current_row, _ = self.get_widget_index(delete_button)
        message_id = self.item(current_row, 0).id
        try:
            r = requests.delete(
                url=settings.SERVER_ADDR + 'info/trade-policy/' + str(message_id) + '/?mc=' + settings.app_dawn.value('machine'),
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


# 策略服务-交易策略维护主页
class TradePolicyMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(TradePolicyMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        combo_message_layout = QHBoxLayout()
        self.date_combo = QComboBox(activated=self.getCurrentPolicy)
        combo_message_layout.addWidget(self.date_combo, alignment=Qt.AlignLeft)
        self.network_message_label = QLabel()
        combo_message_layout.addWidget(self.network_message_label)
        combo_message_layout.addWidget(QPushButton('新增', clicked=self.create_new_policy), alignment=Qt.AlignRight)
        layout.addLayout(combo_message_layout)
        # 展示短信通的表格
        self.policy_table = TradePolicyTable()
        layout.addWidget(self.policy_table)
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
    def getCurrentPolicy(self):
        current_data = self.date_combo.currentData()
        current_date = QDate.currentDate()
        if current_data != 'all':
            min_date = current_date.addDays(current_data)
            url = settings.SERVER_ADDR + 'info/trade-policy/?mc='+settings.app_dawn.value('machine')+'&min_date=' + min_date.toString('yyyy-MM-dd')
        else:
            url = settings.SERVER_ADDR + 'info/trade-policy/?mc=' + settings.app_dawn.value('machine')
        try:
            r = requests.get(url=url)
            response = json.loads(r.content.decode('utf-8'))
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.policy_table.showRowContents(response['data'])

    # 新增一条交易策略
    def create_new_policy(self):
        popup = CreateNewTradePolicyPopup(parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup


"""" 顾问服务-制度考核 """


# 制度考核管理
class InstExamineMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(InstExamineMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        layout.addWidget(QPushButton('修改', clicked=self.modify_file), alignment=Qt.AlignRight)
        # 显示服务端pdf文件
        content_show = PDFContentShower(file=settings.STATIC_PREFIX + 'pserver/rulexamine/制度考核.pdf', parent=self)
        layout.addWidget(content_show)
        self.setLayout(layout)

    # 修改部门组建显示的文件
    def modify_file(self):
        popup = ModifyInstExaminePopup(parent=self)
        popup.exec_()


""" 顾问服务-部门组建 """


# 部门组建管理
class DeptBuildMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(DeptBuildMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        layout.addWidget(QPushButton('修改', clicked=self.modify_file), alignment=Qt.AlignRight)
        # 显示服务端pdf文件
        content_show = PDFContentShower(file=settings.STATIC_PREFIX + 'pserver/deptbuild/部门组建.pdf', parent=self)
        layout.addWidget(content_show)
        self.setLayout(layout)

    # 修改部门组建显示的文件
    def modify_file(self):
        popup = ModifyDeptBuildPopup(parent=self)
        popup.exec_()

""" 顾问服务-人才培养 """


# 人才培养数据管理主页
class PersonnelTrainMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(PersonnelTrainMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        layout.addWidget(QPushButton('修改', clicked=self.modify_file), alignment=Qt.AlignRight)
        # 显示服务端pdf文件
        content_show = PDFContentShower(file=settings.STATIC_PREFIX + 'pserver/persontrain/人才培养.pdf', parent=self)
        layout.addWidget(content_show)
        self.setLayout(layout)

    # 修改人才培养显示的文件
    def modify_file(self):
        popup = ModifyPersonnelTrainPopup(parent=self)
        popup.exec_()


""" 专题研究相关 """


# 显示专题研究表格
class TopicSearchMaintainTable(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '文件名称'),
        ('update_time', '日期'),
        ('creator', '创建者'),
    ]

    def __init__(self, *args, **kwargs):
        super(TopicSearchMaintainTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        table_headers = ['序号', '创建日期', '标题']
        self.setColumnCount(len(table_headers))
        self.setRowCount(len(row_list))
        self.setHorizontalHeaderLabels(table_headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, row_item in enumerate(row_list):
            item0 = QTableWidgetItem(str(row + 1))
            item0.setTextAlignment(Qt.AlignCenter)
            item0.id = row_item['id']
            item0.file_url = row_item['file_url']
            self.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item['create_time'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item1)
            item2 = QTableWidgetItem(row_item['title'])
            item2.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, item2)

    def mousePressEvent(self, event):
        index = self.indexAt(QPoint(event.pos().x(), event.pos().y()))
        row, _ = index.row(), index.column()
        if row < 0:
            return
        self.setCurrentIndex(index)
        if event.buttons() == Qt.RightButton:
            rmenu = QMenu()
            rmenu.setAttribute(Qt.WA_DeleteOnClose)
            view_action = rmenu.addAction("查看")
            view_action.triggered.connect(self.view_file_detail)
            delete_action = rmenu.addAction("删除")
            delete_action.triggered.connect(self.delete_row_record)
            rmenu.exec_(QCursor.pos())

        # super(ReportTable, self).mousePressEvent(event)  # 事件不再往外传了

    def view_file_detail(self):
        row = self.currentRow()
        title = self.item(row, 2).text()
        itemfile = self.item(row, 0).file_url
        file_addr = settings.STATIC_PREFIX + itemfile
        popup = PDFContentPopup(title=title, file=file_addr)
        popup.exec_()

    def delete_row_record(self):
        delete_action = QMessageBox.warning(self, "提示", "删除将不可恢复!", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if delete_action != QMessageBox.Yes:
            return
        row = self.currentRow()
        itemid = self.item(row, 0).id
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            r = requests.delete(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/topicsearch/' + str(itemid) + '/?utoken=' + settings.app_dawn.value('AUTHORIZATION')
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, "错误", str(e))
        else:
            self.removeRow(row)
            QMessageBox.information(self, "成功", '删除成功!')




class TopicSearchMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(TopicSearchMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        message_button_layout = QHBoxLayout()
        self.paginator = Paginator()
        self.paginator.clicked.connect(self.getFileContents)
        message_button_layout.addWidget(self.paginator)
        message_button_layout.addStretch()
        self.network_message_label = QLabel()
        message_button_layout.addWidget(self.network_message_label)
        message_button_layout.addWidget(QPushButton('新增', clicked=self.create_topic_file), alignment=Qt.AlignRight)
        layout.addLayout(message_button_layout)
        # 显示的表格
        self.table = TopicSearchMaintainTable()
        layout.addWidget(self.table)
        self.setLayout(layout)

    # 获取内容
    def getFileContents(self):
        current_page = self.paginator.current_page
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            url = settings.SERVER_ADDR + 'user/' + str(user_id) + '/topicsearch/?page=' + str(current_page)
            r = requests.get(url=url)
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.paginator.setTotalPages(response['total_page'])
            self.table.showRowContents(response['records'])
            self.network_message_label.setText(response['message'])

    # 上传调研报告文件
    def create_topic_file(self):
        popup = CreateNewTopicSearchPopup(parent=self)
        popup.exec_()



""" 调研报告相关 """


# 显示调研报告表格
class SearchReportMaintainTable(QTableWidget):
    network_result = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(SearchReportMaintainTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        table_headers = ['序号', '创建日期', '标题']
        self.setColumnCount(len(table_headers))
        self.setRowCount(len(row_list))
        self.setHorizontalHeaderLabels(table_headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, row_item in enumerate(row_list):
            item0 = QTableWidgetItem(str(row + 1))
            item0.setTextAlignment(Qt.AlignCenter)
            item0.id = row_item['id']
            item0.file_url = row_item['file_url']
            self.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item['create_time'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item1)
            item2 = QTableWidgetItem(row_item['title'])
            item2.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, item2)

    def mousePressEvent(self, event):
        index = self.indexAt(QPoint(event.pos().x(), event.pos().y()))
        row, _ = index.row(), index.column()
        if row < 0:
            return
        self.setCurrentIndex(index)
        if event.buttons() == Qt.RightButton:
            rmenu = QMenu()
            rmenu.setAttribute(Qt.WA_DeleteOnClose)
            view_action = rmenu.addAction("查看")
            view_action.triggered.connect(self.view_file_detail)
            delete_action = rmenu.addAction("删除")
            delete_action.triggered.connect(self.delete_row_record)
            rmenu.exec_(QCursor.pos())

        # super(ReportTable, self).mousePressEvent(event)  # 事件不再往外传了

    def view_file_detail(self):
        row = self.currentRow()
        title = self.item(row, 2).text()
        itemfile = self.item(row, 0).file_url
        file_addr = settings.STATIC_PREFIX + itemfile
        popup = PDFContentPopup(title=title, file=file_addr)
        popup.exec_()

    def delete_row_record(self):
        delete_action = QMessageBox.warning(self, "提示", "删除将不可恢复!", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if delete_action != QMessageBox.Yes:
            return
        row = self.currentRow()
        itemid = self.item(row, 0).id
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            r = requests.delete(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/searchreport/' + str(itemid) + '/?utoken=' + settings.app_dawn.value('AUTHORIZATION')
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, "错误", str(e))
        else:
            self.removeRow(row)
            QMessageBox.information(self, "成功", '删除成功!')


class SearchReportMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(SearchReportMaintain, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        message_button_layout = QHBoxLayout()
        self.paginator = Paginator()
        self.paginator.clicked.connect(self.getFileContents)
        message_button_layout.addWidget(self.paginator)
        message_button_layout.addStretch()
        self.network_message_label = QLabel()
        message_button_layout.addWidget(self.network_message_label)
        message_button_layout.addWidget(QPushButton('新增', clicked=self.create_report_file), alignment=Qt.AlignRight)
        layout.addLayout(message_button_layout)
        # 显示的表格
        self.table = SearchReportMaintainTable()
        layout.addWidget(self.table)
        self.setLayout(layout)

    # 获取内容
    def getFileContents(self):
        current_page = self.paginator.current_page
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            url = settings.SERVER_ADDR + 'user/' + str(user_id) + '/searchreport/?page=' + str(current_page)
            r = requests.get(url=url)
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.paginator.setTotalPages(response['total_page'])
            self.table.showRowContents(response['records'])
            self.network_message_label.setText(response['message'])

    # 上传调研报告文件
    def create_report_file(self):
        popup = CreateNewSearchReportPopup(parent=self)
        popup.exec_()


""" 市场分析相关 """


class MarketAnalysisMaintainTable(QTableWidget):
    network_result = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(MarketAnalysisMaintainTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        table_headers = ['序号', '创建日期', '标题']
        self.setColumnCount(len(table_headers))
        self.setRowCount(len(row_list))
        self.setHorizontalHeaderLabels(table_headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, row_item in enumerate(row_list):
            item0 = QTableWidgetItem(str(row + 1))
            item0.setTextAlignment(Qt.AlignCenter)
            item0.id = row_item['id']
            item0.file_url = row_item['file_url']
            self.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item['create_time'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item1)
            item2 = QTableWidgetItem(row_item['title'])
            item2.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, item2)

    def mousePressEvent(self, event):
        index = self.indexAt(QPoint(event.pos().x(), event.pos().y()))
        row, _ = index.row(), index.column()
        if row < 0:
            return
        self.setCurrentIndex(index)
        if event.buttons() == Qt.RightButton:
            rmenu = QMenu()
            rmenu.setAttribute(Qt.WA_DeleteOnClose)
            view_action = rmenu.addAction("查看")
            view_action.triggered.connect(self.view_file_detail)
            delete_action = rmenu.addAction("删除")
            delete_action.triggered.connect(self.delete_row_record)
            rmenu.exec_(QCursor.pos())

        # super(ReportTable, self).mousePressEvent(event)  # 事件不再往外传了

    def view_file_detail(self):
        row = self.currentRow()
        title = self.item(row, 2).text()
        itemfile = self.item(row, 0).file_url
        file_addr = settings.STATIC_PREFIX + itemfile
        popup = PDFContentPopup(title=title, file=file_addr)
        popup.exec_()

    def delete_row_record(self):
        delete_action = QMessageBox.warning(self, "提示", "删除将不可恢复!", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if delete_action != QMessageBox.Yes:
            return
        row = self.currentRow()
        itemid = self.item(row, 0).id
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            r = requests.delete(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/marketanalysis/' + str(itemid) + '/?utoken=' + settings.app_dawn.value('AUTHORIZATION')
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, "错误", str(e))
        else:
            self.removeRow(row)
            QMessageBox.information(self, "成功", '删除成功!')


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
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            url = settings.SERVER_ADDR + 'user/' + str(user_id) +'/marketanalysis/?page=' + str(current_page)
            r = requests.get(url=url)
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            print(response)
            self.paginator.setTotalPages(response['total_page'])
            self.table.showRowContents(response['records'])
            self.network_message_label.setText(response['message'])

    # 新增一个文件
    def create_analysis_file(self):
        popup = CreateNewMarketAnalysisPopup(parent=self)
        popup.exec_()


""" 短信通相关 """


# 维护表格
class SMSTable(QTableWidget):
    network_result = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(SMSTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        table_headers = ['序号','时间','内容']
        self.setColumnCount(len(table_headers))
        self.setRowCount(len(row_list))
        self.setHorizontalHeaderLabels(table_headers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, row_item in enumerate(row_list):
            item0 = QTableWidgetItem(str(row + 1))
            item0.setTextAlignment(Qt.AlignCenter)
            item0.id = row_item['id']
            self.setItem(row, 0, item0)
            item1 = QTableWidgetItem(row_item['custom_time'])
            item1.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, item1)
            item2 = QTableWidgetItem(row_item['content'])
            item2.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, item2)

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
        # 页码控制器
        self.paginator = Paginator()
        self.paginator.clicked.connect(self.getCurrentSMS)
        combo_message_layout.addWidget(self.paginator)
        self.network_message_label = QLabel()
        combo_message_layout.addWidget(self.network_message_label)
        combo_message_layout.addStretch()
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
        current_page = self.paginator.current_page
        try:
            user_id = pickle.loads(settings.app_dawn.value('UKEY'))
            r = requests.get(
                url=settings.SERVER_ADDR + 'user/' + str(user_id) + '/shortmessage/'
            )
            response = json.loads(r.content.decode('utf8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            self.sms_table.showRowContents(response['records'])
            self.paginator.setTotalPages(response['total_page'])
        return



        current_data = self.date_combo.currentData()
        current_date = QDate.currentDate()
        if current_data != 'all':
            min_date = current_date.addDays(current_data)
            url = settings.SERVER_ADDR + 'info/sms/?current_page='+str(current_page)+'&mc='+settings.app_dawn.value('machine')+'&min_date=' + min_date.toString('yyyy-MM-dd')
        else:
            url = settings.SERVER_ADDR + 'info/sms/?current_page='+str(current_page)+'&mc=' + settings.app_dawn.value('machine')
        try:
            r = requests.get(url=url)
            response = json.loads(r.content.decode('utf-8'))
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            sms_data = response['data']['contacts']
            self.sms_table.showRowContents(sms_data)
            self.paginator.setTotalPages(response['data']['total_page'])

    # 新增一条短信通
    def create_new_sms(self):
        popup = CreateNewSMSLink(parent=self)
        popup.exec_()



# 产品服务管理主页
class InfoServicePageCollector(QWidget):
    def __init__(self, *args, **kwargs):
        super(InfoServicePageCollector, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0)
        # 左侧管理菜单
        self.left_tree = QTreeWidget(clicked=self.left_tree_clicked, objectName='leftTree')
        self.left_tree.header().hide()
        layout.addWidget(self.left_tree, alignment=Qt.AlignLeft)
        # 右侧显示窗口
        self.right_frame = LoadedPage()
        layout.addWidget(self.right_frame)
        self.setLayout(layout)
        self._addLeftTreeContentes()
        self.setStyleSheet("""
        #leftTree::item{
            height:22px;
        }
        """)

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
        # print(service_id)
        if service_id == 1:  # 短信通
            page = MessageServiceMaintain()
            page.getCurrentSMS()
        elif service_id == 2:  # 市场分析
            page = MarketAnalysisMaintain()
            page.getFileContents()
        elif service_id == 3:  # 专题研究
            page = TopicSearchMaintain()
            page.getFileContents()
        elif service_id == 4:  # 调研报告
            page = SearchReportMaintain()
            page.getFileContents()
        elif service_id == 6:  # 人才培养
            page = PersonnelTrainMaintain()
        elif service_id == 7:  # 部门组建
            page = DeptBuildMaintain()
        elif service_id == 8:  # 制度考核
            page = InstExamineMaintain()
        elif service_id == 9:  # 交易策略
            page = TradePolicyMaintain()
        elif service_id == 10:  # 投资方案
            page = InvestPlanMaintain()
            page.getFileContents()
        elif service_id == 11:  # 套保方案
            page = HedgePlanMaintain()
            page.getFileContents()
        elif service_id == 12:  # 培训服务-品种介绍
            page = VarietyIntroMaintain()
        else:
            page = QLabel('【' + text + '】还不能进行数据管理...',
                          styleSheet='color:rgb(50,180,100); font-size:15px;font-weight:bold', alignment=Qt.AlignCenter)
        self.right_frame.clear()
        self.right_frame.addWidget(page)










