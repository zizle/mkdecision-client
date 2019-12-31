# _*_ coding:utf-8 _*_
# __Author__： zizle
import re
import json
import xlrd
import datetime
import requests
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype
from xlrd import xldate_as_tuple
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QDialog, QTreeWidget, QWidget, QGridLayout, QLabel, QLineEdit,\
    QPushButton, QComboBox, QTableWidget, QTreeWidgetItem, QFileDialog, QHeaderView, QTableWidgetItem, QAbstractItemView, \
    QListWidget, QDateEdit, QCheckBox
from PyQt5.QtChart import QChartView, QChart, QLineSeries, QCategoryAxis, QDateTimeAxis, QValueAxis
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QDateTime, QDate
from PyQt5.QtGui import QPainter, QFont
import settings
from widgets.base import TableRowDeleteButton, TableRowReadButton
from popup.tips import WarningPopup, InformationPopup
from utils.charts import draw_lines_stacked, draw_bars_stacked


# 新建数据表
class CreateNewTrendTablePopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateNewTrendTablePopup, self).__init__(*args, **kwargs)
        # 绑定当前显示的页面(0, 上传数据表)、(1, 新增数据组别)
        self.current_option = 0
        # 左侧类别树
        self.variety_tree = QTreeWidget(clicked=self.variety_tree_clicked)
        # 上传表格数据控件
        self.udwidget = QWidget()  # upload data widget
        # 右侧上传数据控件布局
        udwlayout = QGridLayout(margin=0)
        udwlayout.addWidget(QLabel('所属品种:'), 0, 0)
        udwlayout.addWidget(QLabel(parent=self, objectName='VarietyError'), 1, 0, 1, 2)
        self.attach_variety = QLabel(objectName='AttachVariety')
        self.attach_variety.vid = None
        udwlayout.addWidget(self.attach_variety, 0, 1)
        udwlayout.addWidget(QLabel('所属组别:'), 2, 0)
        udwlayout.addWidget(QLabel(parent=self, objectName='groupError'), 3, 0, 1, 2)
        self.attach_group = QLabel(objectName='AttachGroup')
        self.attach_group.gid = None
        udwlayout.addWidget(self.attach_group, 2, 1)
        udwlayout.addWidget(QLabel('数据名称:'), 4, 0)
        udwlayout.addWidget(QLabel(parent=self, objectName='tbnameError'), 5, 0, 1, 2)
        self.tnedit = QLineEdit()  # table name edit数据组名称编辑
        self.tnedit.textChanged.connect(self.tbname_changed)
        udwlayout.addWidget(self.tnedit, 4, 1)
        udwlayout.addWidget(QLabel('时间类型:'), 6, 0)
        self.date_type = QComboBox(parent=self, objectName='dateTypeCombo')
        self.date_type.currentTextChanged.connect(self.change_date_type)
        udwlayout.addWidget(self.date_type, 6, 1)
        udwlayout.addWidget(QPushButton('导入', objectName='selectTable', clicked=self.select_data_table), 7, 0)
        udwlayout.addWidget(QLabel(parent=self, objectName='commitError'), 7, 1)
        self.review_table = QTableWidget(objectName='reviewTable')
        # self.review_table.verticalHeader().hide()
        udwlayout.addWidget(self.review_table, 8, 0, 1, 2)
        # 上传添加数据表按钮布局
        addlayout = QHBoxLayout()
        self.add_table_btn = QPushButton('确认添加', parent=self, objectName='addTable', clicked=self.add_new_table)
        addlayout.addWidget(self.add_table_btn, alignment=Qt.AlignRight)
        self.udwidget.setLayout(udwlayout)
        # 布局
        layout = QHBoxLayout()  # 总的左右布局
        llayout = QVBoxLayout()  # 左侧上下布局
        rlayout = QVBoxLayout()  # 右侧上下布局
        llayout.addWidget(self.variety_tree, alignment=Qt.AlignLeft)
        llayout.addWidget(QPushButton('新建组别', clicked=self.create_table_group), alignment=Qt.AlignLeft)
        rlayout.addWidget(self.udwidget)
        rlayout.addLayout(addlayout)
        layout.addLayout(llayout)
        layout.addLayout(rlayout)
        self.setLayout(layout)
        # 样式
        self.setWindowTitle('新建数据')
        self.setFixedSize(1000, 550)
        self.variety_tree.header().hide()
        self.setObjectName('myself')
        self.setStyleSheet("""
        #AttachVariety, #AttachGroup, #tgpopAttachTo{
            color:rgb(180,20,30)
        }
        #ngWidget{
            background-color: rgb(245,245,245);
            border-radius: 3px;
        }
        #addTable {
            max-width: 55px;
        }
        #selectTable{
            max-width: 55px;
        }
        #closeBtn, #addGroupBtn{
            max-width: 55px
        }
        #tgpopupVError,#tgpopupNError,#tbnameError,#groupError{
            color:rgb(200,10,20)
        }
        """)
        # 初始化
        self.get_date_type()

    # 数据时间类型选择
    def get_date_type(self):
        date_type = [
            {'name': '年度（年）', 'fmt': '%Y'},
            {'name': '月度（年-月）', 'fmt': '%Y-%m'},
            {'name': '日度（年-月-日）', 'fmt': '%Y-%m-%d'},
            {'name': '时度（年-月-日 时）', 'fmt': '%Y-%m-%d %H'},
            {'name': '分度（年-月-日 时:分）', 'fmt': '%Y-%m-%d %H:%M'},
            {'name': '秒度（年-月-日 时:分:秒）', 'fmt': '%Y-%m-%d %H:%M:%S'},
        ]
        for t in date_type:
            self.date_type.addItem(t['name'], t['fmt'])
        self.date_type.setCurrentIndex(self.date_type.count() - 1)

    # 该变时间类型
    def change_date_type(self, t):
        fmt = self.date_type.currentData()
        row_count = self.review_table.rowCount()
        for row in range(row_count):
            item = self.review_table.item(row, 0)
            if hasattr(item, 'date'):  # date属性是在填充表格时绑定，详见self._show_file_data函数
                text = item.date.strftime(fmt)
                item.setText(text)

    # 获取品种树内容
    def getVarietyTableGroups(self):
        self.variety_tree.clear()
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/varieties/group/?mc=' + settings.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            return
        for index, variety_item in enumerate(response['data']):
            print(index, variety_item)
            variety = QTreeWidgetItem(self.variety_tree)
            variety.setText(0, variety_item['name'])
            variety.vid = variety_item['id']
            for group_item in variety_item['trend_table_groups']:
                group = QTreeWidgetItem(variety)
                group.setText(0, group_item['name'])
                group.gid = group_item['id']
        # # 目录树填充完毕手动设置当前第一个，并触发点击事件
        # self.variety_tree.setCurrentIndex(self.variety_tree.model().index(0, 0))  # 最顶层设置为当前
        # self.variety_tree_clicked()  # 手动调用点击事件

    # 新增数据表的组别
    def create_table_group(self):
        # 获取当前选择的品种
        variety = self.attach_variety.text()
        table_group_popup = QDialog(parent=self)
        table_group_popup.attach_variety_id = self.attach_variety.vid
        def commit_table_group():
            if not table_group_popup.attach_variety_id:  # 所属品种
                table_group_popup.findChild(QLabel, 'tgpopAttachTo').setText('请选择品种后再添加!')
                return
            group_name = re.sub(r'\s+', '', table_group_popup.group_name_edit.text())
            if not group_name:
                table_group_popup.findChild(QLabel, 'tgpopupNError').setText('请输入数据组名称！')
                return
            # 提交
            try:
                r = requests.post(
                    url=settings.SERVER_ADDR + 'trend/' + str(table_group_popup.attach_variety_id) + '/group-tables/?mc=' + settings.app_dawn.value('machine'),
                    headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                    data=json.dumps({'group_name': group_name})
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 201:
                    raise ValueError(response['message'])
            except Exception as e:
                table_group_popup.findChild(QLabel, 'tgpopupNError').setText(str(e))
            else:
                table_group_popup.close()
        playout = QGridLayout()  # table group popup layout
        playout.addWidget(QLabel('所属品种：'), 0, 0)
        playout.addWidget(QLabel(variety, parent=table_group_popup, objectName='tgpopAttachTo'), 0, 1)
        playout.addWidget(QLabel(parent=table_group_popup, objectName='tgpopupVError'), 1, 0, 1, 2)  # variety error
        playout.addWidget(QLabel('数据组名：'), 2, 0)
        table_group_popup.group_name_edit = QLineEdit(parent=table_group_popup, objectName='ngEdit')
        playout.addWidget(table_group_popup.group_name_edit, 2, 1)
        playout.addWidget(QLabel(parent=table_group_popup, objectName='tgpopupNError'), 3, 0, 1, 2)  # name error
        abtlayout = QHBoxLayout()
        abtlayout.addWidget(QPushButton('增加', objectName='addGroupBtn', clicked=commit_table_group),
                            alignment=Qt.AlignRight)
        playout.addLayout(abtlayout, 4, 1)
        table_group_popup.setLayout(playout)
        table_group_popup.setFixedSize(400, 150)
        table_group_popup.setWindowTitle('增加数据组')
        if not table_group_popup.exec_():
            table_group_popup.deleteLater()
            self.getVarietyTableGroups() # 重新请求当前左侧列表数据
            del table_group_popup

    # 新建表的表名称编辑框文字改变
    def tbname_changed(self, t):
        el = self.findChild(QLabel, 'tbnameError')
        el.setText('')

    # 选择数据表文件
    def select_data_table(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "Excel files(*.xls *.xlsx)")
        if not file_path:
            return
        # 处理文件名称填入表名称框
        file_name_ext = file_path.rsplit('/', 1)[1]
        file_name = file_name_ext.rsplit('.', 1)[0]
        tbname = re.sub(r'\s+', '', file_name)
        self.tnedit.setText(tbname)
        # 读取文件内容预览
        self._show_file_data(file_path)

    # 读取文件内容填入预览表格
    def _show_file_data(self, file_path):
        # 处理Excel数据写入表格预览
        rf = xlrd.open_workbook(filename=file_path)
        sheet1 = rf.sheet_by_index(0)
        labels = sheet1.row_values(0)
        # xlrd读取的类型ctype： 0 empty,1 string, 2 number, 3 date, 4 boolean, 5 error
        nrows = sheet1.nrows
        ncols = sheet1.ncols
        self.review_table.clear()
        self.review_table.setRowCount(nrows - 1)
        self.review_table.setColumnCount(ncols)
        self.review_table.setHorizontalHeaderLabels([str(i) for i in labels])
        self.review_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # 时间类型约束
        date_type = self.date_type.currentData()
        # 数据填入预览表格
        for row in range(1, nrows):
            row_content = []
            for col in range(ncols):
                ctype = sheet1.cell(row, col).ctype
                cell = sheet1.cell_value(row, col)
                if ctype == 2 and cell % 1 == 0:  # 如果是整形
                    cell = int(cell)
                    item = QTableWidgetItem(str(cell))
                elif ctype == 3:
                    # 转成datetime对象
                    date = datetime.datetime(*xldate_as_tuple(cell, 0))
                    cell = date.strftime(date_type)
                    # 填入预览表格cell就是每个数据
                    item = QTableWidgetItem(str(cell))
                    item.date = date
                else:
                    item = QTableWidgetItem(str(cell))
                item.setTextAlignment(Qt.AlignCenter)
                self.review_table.setItem(row - 1, col, item)
                row_content.append(cell)

    # 读取预览表格的数据
    def _read_review_data(self):
        row_count = self.review_table.rowCount()
        column_count = self.review_table.columnCount()
        data_dict = dict()
        data_dict['value_list'] = list()
        data_dict['header_labels'] = list()
        for row in range(row_count):
            row_content = list()
            for col in range(column_count):
                if row == 0:  # 获取表头内容
                    data_dict['header_labels'].append(self.review_table.horizontalHeaderItem(col).text())
                item = self.review_table.item(row, col)
                row_content.append(item.text())
            data_dict['value_list'].append(row_content)
        # 添加第一行表头数据
        data_dict['value_list'].insert(0, data_dict['header_labels'])
        return data_dict

    # 新增数据表
    def add_new_table(self):
        self.add_table_btn.setEnabled(False)
        # vid = self.attach_variety.vid
        gid = self.attach_group.gid
        if not gid:
            el = self.findChild(QLabel, 'groupError')
            el.setText('请选择数据所属组.如需新建组,请点击左下角【新建组别】.')
            self.add_table_btn.setEnabled(True)
            return
        # 表名称与正则替换空格
        tbname = re.sub(r'\s+', '', self.tnedit.text())
        if not tbname:
            el = self.findChild(QLabel, 'tbnameError')
            el.setText('请输入数据表名称.')
            self.add_table_btn.setEnabled(True)
            return
        # 读取预览表格的数据
        table_data = self._read_review_data()
        if not table_data['value_list']:
            el = self.findChild(QLabel, 'commitError')
            el.setText('请先导入数据再上传.')
            self.add_table_btn.setEnabled(True)
            return
        # 数据上传
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'trend/group/' + str(gid) + '/table/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    "table_name": tbname,
                    "table_data": table_data
                }),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            self.findChild(QLabel, 'commitError').setText(str(e))
            self.add_table_btn.setEnabled(True)
            return
        self.close()

    # 点击品种树
    def variety_tree_clicked(self):
        item = self.variety_tree.currentItem()
        if item.childCount():  # has children open the root
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        text = item.text(0)
        if item.parent():
            if self.current_option == 0:
                # 改变数据所属（品种的id是'vid', 组的id是gid。详情见'self.get_varieties'函数）
                self.attach_variety.vid = item.parent().vid
                self.attach_group.gid = item.gid
                self.attach_variety.setText(item.parent().text(0))
                self.attach_group.setText(text)
                # 提示消息清除
                el = self.findChild(QLabel, 'groupError')
                el.setText('')

            else:
                # 只能在品种下创建数据组别
                el = self.ng_widget.findChild(QLabel, 'errorLabel')
                el.setText('只能在品种下创建数据组别')
                addBtn = self.ng_widget.findChild(QPushButton, 'addGroupBtn')
                addBtn.setEnabled(False)
        else:
            if self.current_option == 0:
                # 该表所属品种(只有显示提示作用)
                self.attach_variety.setText(text)
                self.attach_variety.vid = item.vid
                # 清除所属组别和提示消息
                self.attach_group.setText('')
                self.attach_group.gid = None
                el = self.findChild(QLabel, 'groupError')
                el.setText('')
            else:
                # 显示所属品种
                self.ng_widget.attach_variety = item.vid
                ngwAttachTo = self.ng_widget.findChild(QLabel, 'ngwAttachTo')
                ngwAttachTo.setText(text)
                error_label = self.ng_widget.findChild(QLabel, 'errorLabel')
                error_label.setText('')
                addBtn = self.ng_widget.findChild(QPushButton, 'addGroupBtn')
                addBtn.setEnabled(True)
                
                
# 显示当前数据表
class ShowTableDetailPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(ShowTableDetailPopup, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.setMinimumSize(820, 450)
        self.setLayout(layout)

    # 显示数据
    def showTableData(self, headers, table_contents):
        # 设置行列
        self.table.setRowCount(len(table_contents))
        headers.pop(0)
        col_count = len(headers)
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for row, row_content in enumerate(table_contents):
            for col in range(1, col_count + 1):
                item = QTableWidgetItem(row_content[col])
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col-1, item)


# 编辑当前数据表
class EditTableDetailPopup(QDialog):
    def __init__(self, table_id, *args, **kwargs):
        super(EditTableDetailPopup, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        self.table_id = table_id
        # 操作按钮布局
        operate_button_layout = QHBoxLayout()
        self.add_rows_button = QPushButton('粘贴新数据', clicked=self.copy_new_rows)  # 添加数据
        operate_button_layout.addWidget(self.add_rows_button)
        # 删除选中行
        self.delete_current_button = QPushButton('删除选中行', clicked=self.delete_current_row)
        operate_button_layout.addWidget(self.delete_current_button)
        self.delete_current_button.hide()
        # 新增一行
        self.add_new_row_button = QPushButton('新增一行', clicked=self.new_table_add_row)
        operate_button_layout.addWidget(self.add_new_row_button)
        self.add_new_row_button.hide()
        operate_button_layout.addStretch()
        # 删除这张表
        self.delete_table = QPushButton('删除整张表', styleSheet='color:rgb(240,20,50); border:none',
                                        cursor=Qt.PointingHandCursor, clicked=self.delete_this_table)
        operate_button_layout.addWidget(self.delete_table, alignment=Qt.AlignRight)
        layout.addLayout(operate_button_layout)
        self.table = QTableWidget()
        layout.addWidget(self.table)
        # 新数据的表格
        self.new_table = QTableWidget()
        self.new_table_headers = []
        self.new_table.hide()
        layout.addWidget(self.new_table)
        # 确认增加新数据
        self.commit_new_button = QPushButton('确认增加', clicked=self.commit_new_table_rows)
        self.commit_new_button.hide()
        layout.addWidget(self.commit_new_button, alignment=Qt.AlignRight)
        # 错误提示
        self.network_result_label = QLabel()
        layout.addWidget(self.network_result_label, alignment=Qt.AlignLeft)
        self.setMinimumSize(820, 450)
        self.setLayout(layout)

    # 黏贴新数据
    def copy_new_rows(self):
        self.table.hide()
        self.new_table.show()
        self.commit_new_button.show()
        self.delete_current_button.show()
        self.add_new_row_button.show()
        # 获取当前剪贴板的内容
        clipboard = QApplication.clipboard()
        # 处理数据
        contents = re.split(r'\n', clipboard.text())
        # 在新表格中添加数据
        new_row_count = len(self.new_table_headers)
        self.new_table.setRowCount(len(contents))
        self.new_table.setColumnCount(new_row_count)
        self.new_table.setHorizontalHeaderLabels(self.new_table_headers)
        self.new_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for row, row_content in enumerate(contents):
            row_content = re.split(r'\t', row_content)
            if not row_content[0]:
                continue
            for col, item_text in enumerate(row_content):
                if col > new_row_count - 1:
                    continue
                new_item = QTableWidgetItem(item_text)
                new_item.setTextAlignment(Qt.AlignCenter)
                self.new_table.setItem(row, col, new_item)

    # 删除选中行（追加数据时）
    def delete_current_row(self):
        self.new_table.removeRow(self.new_table.currentRow())

    # 新增一行(追加数据时)
    def new_table_add_row(self):
        self.new_table.insertRow(self.new_table.rowCount())

    # 确认新增新数据
    def commit_new_table_rows(self):
        self.commit_new_button.setEnabled(False)
        self.network_result_label.setText('上传中...')
        # 读取表格中的数
        row_count = self.new_table.rowCount()
        column_count = self.new_table.columnCount()
        data_dict = dict()
        data_dict['value_list'] = list()
        # data_dict['header_labels'] = list()
        for row in range(row_count):
            if not self.new_table.item(row, 0):
                continue
            row_content = list()
            for col in range(column_count):
                # if row == 0:  # 获取表头内容
                #     data_dict['header_labels'].append(self.review_table.horizontalHeaderItem(col).text())
                item = self.new_table.item(row, col)
                row_content.append(item.text() if item else '')
            data_dict['value_list'].append(row_content)
        # # 添加第一行表头数据
        # data_dict['value_list'].insert(0, data_dict['header_labels'])
        # 上传新数据至当前表
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'trend/table/' + str(self.table_id) + '/?look=1&mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps(data_dict)
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result_label.setText(str(e))
            self.commit_new_button.setEnabled(True)
        else:
            self.network_result_label.setText(response['message'])

    # 显示数据
    def showTableData(self, headers, table_contents):
        # 设置行列
        self.table.setRowCount(len(table_contents))
        headers.pop(0)
        self.new_table_headers = headers
        col_count = len(headers) + 1
        self.table.setColumnCount(col_count)
        self.table.setHorizontalHeaderLabels(headers + [''])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for row, row_content in enumerate(table_contents):
            for col, col_text in enumerate(row_content):
                if col == 0:
                    continue
                item = QTableWidgetItem(row_content[col])
                item.setTextAlignment(Qt.AlignCenter)
                if col == 1:
                    item.col_id = row_content[0]
                self.table.setItem(row, col - 1, item)
                # 添加删除按钮
                if col == len(row_content) - 1:
                    delete_button = TableRowDeleteButton('删除')
                    delete_button.button_clicked.connect(self.delete_button_clicked)
                    self.table.setCellWidget(row, col, delete_button)

    # 删除一行数据
    def delete_button_clicked(self, delete_button):
        try:
            current_row, _ = self.get_widget_index(delete_button)
            row_id = self.table.item(current_row, 0).col_id
            def delete_row_content():
                try:
                    r = requests.delete(
                        url=settings.SERVER_ADDR + 'trend/table/' + str(
                            self.table_id) + '/?mc=' + settings.app_dawn.value('machine'),
                        headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                        data=json.dumps({'row_id': row_id})
                    )
                    response = json.loads(r.content.decode('utf-8'))
                    if r.status_code != 200:
                        raise ValueError(response['message'])
                except Exception as e:
                    self.network_result_label.setText(str(e))
                else:
                    # 表格移除当前行
                    self.table.removeRow(current_row)
                    popup.close()
                    self.network_result_label.setText(response['message'])
            # 警示框
            popup = WarningPopup(parent=self)
            popup.confirm_button.connect(delete_row_content)
            if not popup.exec_():
                popup.deleteLater()
                del popup
        except Exception as e:
            print(e)

    # 删除整张表
    def delete_this_table(self):
        def delete_table():
            try:
                r = requests.delete(
                    url=settings.SERVER_ADDR + 'trend/table/' + str(
                        self.table_id) + '/?mc=' + settings.app_dawn.value('machine'),
                    headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                    data=json.dumps({'operate': 'all'})
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 200:
                    raise ValueError(response['message'])
            except Exception as e:
                self.network_result_label.setText(str(e))
            else:
                popup.close()
                self.close()
        # 警示框
        popup = WarningPopup(parent=self)
        popup.confirm_button.connect(delete_table)
        if not popup.exec_():
            popup.deleteLater()
            del popup

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.table.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


""" 设置图表相关弹窗 """


# 设置图表详情的弹窗
class SetChartDetailPopup(QDialog):
    def __init__(self, table_id, *args, **kwargs):
        super(SetChartDetailPopup, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=2)
        # left_layout = QVBoxLayout()
        self.table_id = table_id
        # 图表参数设置的控件
        self.chart_parameter = QWidget(parent=self)
        parameter_layout = QVBoxLayout(margin=0)
        parameter_layout.addWidget(QLabel('参数设置', objectName='widgetTip'))
        # 图表名称
        chart_name_layout = QHBoxLayout()
        chart_name_layout.addWidget(QLabel('图表名称：', objectName='headTip'))
        self.chart_name = QLineEdit()
        chart_name_layout.addWidget(self.chart_name)
        parameter_layout.addLayout(chart_name_layout)
        # 图表类型
        chart_category_layout = QHBoxLayout()
        chart_category_layout.addWidget(QLabel('图表类型：', objectName='headTip'))
        self.chart_category_combo = QComboBox()
        self.chart_category_combo.addItems([u'折线图', u'柱形图', u'双轴折线图', u'双轴柱形图'])
        chart_category_layout.addWidget(self.chart_category_combo)
        chart_category_layout.addStretch()
        parameter_layout.addLayout(chart_category_layout)
        # 选择X轴
        chart_xaxis_layout = QHBoxLayout()
        chart_xaxis_layout.addWidget(QLabel('X 轴列名：', objectName='headTip'))
        self.x_axis_combo = QComboBox(currentIndexChanged=self.x_axis_changed)
        chart_xaxis_layout.addWidget(self.x_axis_combo)
        chart_xaxis_layout.addStretch()
        parameter_layout.addLayout(chart_xaxis_layout)
        # Y轴设置
        parameter_layout.addWidget(QLabel('Y 轴列名：', objectName='headTip'))
        yaxis_layout = QHBoxLayout()
        left_yaxis_layout = QVBoxLayout()
        self.column_header_list = QListWidget()
        self.column_header_list.setMaximumWidth(180)
        left_yaxis_layout.addWidget(self.column_header_list)
        yaxis_layout.addLayout(left_yaxis_layout)
        # 中间按钮
        middle_yasis_layout = QVBoxLayout()
        middle_yasis_layout.addWidget(QPushButton('左轴→', objectName='addAxis', clicked=self.add_y_left))
        middle_yasis_layout.addWidget(QPushButton('右轴→', objectName='addAxis', clicked=self.add_y_right))
        yaxis_layout.addLayout(middle_yasis_layout)
        # 右侧列头显示
        right_yaxis_layout = QVBoxLayout()
        self.right_top_list = QListWidget(doubleClicked=self.remove_toplist_item)
        self.right_top_list.setMaximumWidth(180)
        right_yaxis_layout.addWidget(self.right_top_list)
        self.right_bottom_list = QListWidget(doubleClicked=self.remove_bottomlist_item)
        self.right_bottom_list.setMaximumWidth(180)
        right_yaxis_layout.addWidget(self.right_bottom_list)
        yaxis_layout.addLayout(right_yaxis_layout)
        parameter_layout.addLayout(yaxis_layout)
        # 轴名称设置
        parameter_layout.addWidget(QLabel('轴名称设置：', objectName='headTip'), alignment=Qt.AlignLeft)
        # x轴
        bottom_xaxis_name_layout = QHBoxLayout()
        bottom_xaxis_name_layout.addWidget(QLabel('X 轴:'))
        self.bottom_x_label_edit = QLineEdit(placeholderText='请输入轴名称')
        bottom_xaxis_name_layout.addWidget(self.bottom_x_label_edit)
        parameter_layout.addLayout(bottom_xaxis_name_layout)
        # Y轴
        yaxis_name_layout = QHBoxLayout()
        yaxis_name_layout.addWidget(QLabel('左轴:'))
        self.left_y_label_edit = QLineEdit(placeholderText='据左轴名分号";"间隔')
        yaxis_name_layout.addWidget(self.left_y_label_edit)
        yaxis_name_layout.addWidget(QLabel('右轴:'))
        self.right_y_label_edit = QLineEdit(placeholderText='据右轴名分号";"间隔')
        yaxis_name_layout.addWidget(self.right_y_label_edit)
        parameter_layout.addLayout(yaxis_name_layout)
        # 数据范围
        parameter_layout.addWidget(QLabel('数据范围设置：', objectName='headTip'), alignment=Qt.AlignLeft)
        chart_scope_layout1 = QHBoxLayout()
        chart_scope_layout1.addWidget(QLabel('起始日期:'))
        self.scope_start_date = QDateEdit()
        self.scope_start_date.setCalendarPopup(True)
        self.scope_start_date.setEnabled(False)
        self.scope_start_date.disconnect()
        chart_scope_layout1.addWidget(self.scope_start_date)
        chart_scope_layout1.addWidget(QLabel('截止日期:'))
        self.scope_end_date = QDateEdit()
        self.scope_end_date.setCalendarPopup(True)
        self.scope_end_date.setEnabled(False)
        self.scope_end_date.disconnect()
        chart_scope_layout1.addWidget(self.scope_end_date)
        parameter_layout.addLayout(chart_scope_layout1)
        # 个数范围
        chart_scope_layout2 = QHBoxLayout()
        chart_scope_layout2.addWidget(QLabel('起始记录:'))
        self.scope_start_record = QLineEdit()
        chart_scope_layout2.addWidget(self.scope_start_record)
        chart_scope_layout2.addWidget(QLabel('截止记录:'))
        self.scope_end_record = QLineEdit()
        chart_scope_layout2.addWidget(self.scope_end_record)
        parameter_layout.addLayout(chart_scope_layout2)
        parameter_layout.addWidget(QPushButton('画图预览', clicked=self.review_chart_clicked), alignment=Qt.AlignRight)
        self.chart_parameter.setMaximumWidth(350)
        self.chart_parameter.setLayout(parameter_layout)
        # 参数设置控件加入布局
        layout.addWidget(self.chart_parameter)
        # 预览控件
        self.review_widget = QWidget(parent=self)
        review_layout = QVBoxLayout(margin=0)
        review_layout.addWidget(QLabel('图表预览', objectName='widgetTip'))
        self.review_chart = QChartView()
        self.review_chart.setRenderHint(QPainter.Antialiasing)
        review_layout.addWidget(self.review_chart)
        # 确认设置
        commit_layout = QHBoxLayout()
        commit_layout.addStretch()
        self.current_start = QCheckBox('当前起始')
        commit_layout.addWidget(self.current_start)
        self.current_end = QCheckBox('当前截止')
        commit_layout.addWidget(self.current_end)
        commit_layout.addWidget(QPushButton('确认设置', clicked=self.commit_add_chart))
        review_layout.addLayout(commit_layout)
        # 表详情数据显示
        self.detail_trend_table = QTableWidget()
        self.detail_trend_table.setMaximumHeight(200)
        review_layout.addWidget(self.detail_trend_table)
        self.review_widget.setLayout(review_layout)
        layout.addWidget(self.review_widget)
        self.setLayout(layout)
        self.setMinimumWidth(950)
        self.setMaximumHeight(550)
        self.has_review_chart = False
        self.setStyleSheet("""
        #widgetTip{
            color: rgb(50,80,180);
            font-weight:bold
        }
        #headTip{
            font-weight:bold
        }
        #addAxis{
            max-width:40px
        }
        """)

    # x轴选择改变
    def x_axis_changed(self):
        self.column_header_list.clear()
        for header_index in range(self.detail_trend_table.horizontalHeader().count()):
            text = self.detail_trend_table.horizontalHeaderItem(header_index).text()
            if text == self.x_axis_combo.currentText():
                continue
            self.column_header_list.addItem(text)

    # 移除当前列表中的item
    def remove_toplist_item(self, index):
        print('移除', index)
        row = self.right_top_list.currentRow()
        self.right_top_list.takeItem(row)

    def remove_bottomlist_item(self, index):
        row = self.right_bottom_list.currentRow()
        self.right_bottom_list.takeItem(row)

    # 加入左轴
    def add_y_left(self):
        text_in = list()
        for i in range(self.right_top_list.count()):
            text_in.append(self.right_top_list.item(i).text())
        item = self.column_header_list.currentItem() # 获取item
        if item is not None:
            if item.text() not in text_in:
                self.right_top_list.addItem(item.text())

    # 加入右轴
    def add_y_right(self):
        text_in = list()
        for i in range(self.right_bottom_list.count()):
            text_in.append(self.right_bottom_list.item(i).text())
        item = self.column_header_list.currentItem()  # 获取item
        if item is not None:
            if item.text() not in text_in:
                self.right_bottom_list.addItem(item.text())

    # 预览数据
    def review_chart_clicked(self):
        try:
            chart_name = self.chart_name.text()
            chart_category = self.chart_category_combo.currentText()
            # 根据设置从表格中获取画图源数据
            x_axis = self.x_axis_combo.currentText()  # x轴
            left_y_axis = [self.right_top_list.item(i).text() for i in range(self.right_top_list.count())]
            right_y_axis = [self.right_bottom_list.item(i).text() for i in range(self.right_bottom_list.count())]
            # 根据表头将这些列名称换为索引
            x_axis_col = list()
            left_y_cols = list()
            right_y_cols = list()
            header_data = list()
            for header_index in range(self.detail_trend_table.horizontalHeader().count()):
                text = self.detail_trend_table.horizontalHeaderItem(header_index).text()
                header_data.append(text)
                if text == x_axis:
                    x_axis_col.append(header_index)
                for y_left in left_y_axis:
                    if y_left == text:
                        left_y_cols.append(header_index)
                for y_right in right_y_axis:
                    if y_right == text:
                        right_y_cols.append(header_index)
            # 判断是否选择了左轴
            if not left_y_cols:
                popup = InformationPopup(message='请至少选择一列左轴数据。', parent=self)
                if not popup.exec_():
                    popup.deleteLater()
                    del popup
                return
            # 获取表格数据
            table_data = list()
            for row in range(self.detail_trend_table.rowCount()):
                row_content = list()
                for col in range(self.detail_trend_table.columnCount()):
                    row_content.append(self.detail_trend_table.item(row, col).text())
                table_data.append(row_content)
            # 表格数据转为pandas DataFrame
            table_df = pd.DataFrame(table_data)
            """ 硬性要求第一列为时间类型的字符串列 """
            table_df[0] = pd.to_datetime(table_df[0])  # 第一列转为时间类型
            table_df.sort_values(by=0, inplace=True)  # 根据时间排序
            # 判断x轴的数据类型
            x_bottom = x_axis_col[0]
            print(table_df[x_bottom].dtype)
            if is_datetime64_any_dtype(table_df[x_bottom]):
                print('时间类型x轴')
                # 计算数据时间跨度大小
                x_axis_data = table_df.iloc[:, [0]]  # 取得第一行数据
                min_x, max_x = x_axis_data.min(0).tolist()[0], x_axis_data.max(0).tolist()[0]  # 第一列时间数据(x轴)的最大值和最小值
                # self.scope_start_date.setDisplayFormat('yyyy-MM-dd')
                # self.scope_end_date.setDisplayFormat('yyyy-MM-dd')
                self.scope_start_date.setDateRange(QDate(min_x), QDate(max_x))
                self.scope_end_date.setDateRange(QDate(min_x), QDate(max_x))
                self.scope_start_date.setEnabled(True)
                self.scope_end_date.setEnabled(True)
                self.scope_end_date.setDate(self.scope_end_date.maximumDate())
                self.scope_start_date.dateChanged.connect(self.date_scope_changed)
                self.scope_end_date.dateChanged.connect(self.date_scope_changed)
                # 记录不可选择
                self.scope_start_record.setEnabled(False)
                self.scope_end_record.setEnabled(False)
                # self.scope_start_record.disconnect()
                # self.scope_end_record.disconnect()
            else:
                print('非时间类型x轴')
                self.scope_start_record.setEnabled(True)
                self.scope_end_record.setEnabled(True)
                self.scope_start_record.setText('1')
                self.scope_end_record.setText(str(table_df.shape[0]))
                # 时间不可选择
                self.scope_start_date.setEnabled(False)
                self.scope_end_date.setEnabled(False)
                self.scope_start_date.disconnect()
                self.scope_end_date.disconnect()
            # 根据类型进行画图
            if chart_category == u'折线图':  # 折线图
                chart = draw_lines_stacked(name=chart_name, table_df=table_df, x_bottom=x_axis_col, y_left=left_y_cols,
                                          legends=header_data, tick_count=12)
            elif chart_category == u'柱形图':
                chart = draw_bars_stacked(name=chart_name, table_df=table_df, x_bottom=x_axis_col, y_left=left_y_cols,
                                          legends=header_data, tick_count=100)
            else:
                popup = InformationPopup(message='当前设置不适合作图或系统暂不支持作图。', parent=self)
                if not popup.exec_():
                    popup.deleteLater()
                    del popup
                return
            self.review_chart.setChart(chart)
            self.has_review_chart = True
            return




            # 计算数据时间跨度大小
            x_axis_data = table_df.iloc[:, [0]]  # 取得第一行数据
            min_x, max_x = x_axis_data.min(0).tolist()[0], x_axis_data.max(0).tolist()[0]  # 第一列时间数据(x轴)的最大值和最小值
            # self.scope_start_date.setDisplayFormat('yyyy-MM-dd')
            # self.scope_end_date.setDisplayFormat('yyyy-MM-dd')
            self.scope_start_date.setDateRange(QDate(min_x), QDate(max_x))
            self.scope_end_date.setDateRange(QDate(min_x), QDate(max_x))
            if x_axis_col[0] == 0 and chart_category == u'折线图':  # x轴为时间画图
                # 绘图
                chart = draw_line_series(name=chart_name, table_df=table_df, x_bottom=x_axis_col, y_left=left_y_cols,
                                         legends=header_data, tick_count=12)
                self.review_chart.setChart(chart)
            elif chart_category == u'柱形图':
                chart = draw_bar_series(name=chart_name, table_df=table_df, x_bottom=x_axis_col, y_left=left_y_cols,
                                        legends=header_data, tick_count=12)
                self.review_chart.setChart(chart)
            else:
                popup = InformationPopup(message='当前设置不适合作图或系统暂不支持作图。', parent=self)
                if not popup.exec_():
                    popup.deleteLater()
                    del popup
                return
            self.scope_start_date.setEnabled(True)
            self.scope_end_date.setEnabled(True)
            self.scope_end_date.setDate(self.scope_end_date.maximumDate())
            self.scope_start_date.dateChanged.connect(self.date_scope_changed)
            self.scope_end_date.dateChanged.connect(self.date_scope_changed)
            self.has_review_chart = True
        except Exception as e:
            print(e)

    # 时间范围改变
    def date_scope_changed(self):
        start_date = self.scope_start_date.date()
        end_date = self.scope_end_date.date()
        if start_date >= end_date:  # 开始时间大于等于结束时间
            return
        # 改变图表的范围
        self.review_chart.chart().axisX().setRange(QDateTime(start_date), QDateTime(end_date))

    # 确认添加本张图表
    def commit_add_chart(self):
        if not self.has_review_chart:
            info = InformationPopup(message='请先预览图表，再进行设置!', parent=self)
            if not info.exec_():
                info.deleteLater()
                del info
            return
        category_dict = {
            '折线图': 'line',
            '柱形图': 'bar',
            '双轴折线图': 'double_line',
            '双轴柱形图': 'double_bar'
        }
        chart_name = re.sub(r'\s+', '', self.chart_name.text())
        category = category_dict.get(self.chart_category_combo.currentText(), None)
        if not all([chart_name, category]):
            info = InformationPopup(message='请设置图表名称和图表类型!',parent=self)
            if not info.exec_():
                info.deleteLater()
                del info
            return
        # 根据设置从表格中获取数据把选择的列头变为索引
        x_axis = self.x_axis_combo.currentText()  # x轴
        left_y_axis = [self.right_top_list.item(i).text() for i in range(self.right_top_list.count())]
        right_y_axis = [self.right_bottom_list.item(i).text() for i in range(self.right_bottom_list.count())]
        # 根据表头将这些列名称换为索引
        x_axis_cols = list()
        left_y_cols = list()
        right_y_cols = list()
        for header_index in range(self.detail_trend_table.horizontalHeader().count()):
            text = self.detail_trend_table.horizontalHeaderItem(header_index).text()
            if text == x_axis:
                x_axis_cols.append(header_index)
            for y_left in left_y_axis:
                if y_left == text:
                    left_y_cols.append(header_index)
            for y_right in right_y_axis:
                if y_right == text:
                    right_y_cols.append(header_index)
        if not x_axis_cols:
            info = InformationPopup(message='请设置图表X轴！', parent=self)
            if not info.exec_():
                info.deleteLater()
                del info
            return
        if not left_y_cols:
            info = InformationPopup(message='至少左轴要有一列数据!', parent=self)
            if not info.exec_():
                info.deleteLater()
                del info
            return
        # 获取轴名称
        x_bottom_labels = re.split(r';',self.bottom_x_label_edit.text())
        y_left_labels = re.split(r';', self.left_y_label_edit.text())
        y_right_labels = re.split(r';', self.right_y_label_edit.text())
        chart_params = dict()
        chart_params['table_id'] = self.table_id
        chart_params['name'] = chart_name
        chart_params['category'] = category
        chart_params['x_bottom'] = x_axis_cols
        chart_params['x_bottom_label'] = x_bottom_labels
        chart_params['x_top'] = []
        chart_params['x_top_label'] = []
        chart_params['y_left'] = left_y_cols
        chart_params['y_left_label'] = y_left_labels
        chart_params['y_right'] = right_y_cols
        chart_params['y_right_label'] = y_right_labels
        chart_params['is_top'] = False
        if self.current_start.isChecked():
            print('设置当前起始范围')
            chart_params['start'] = self.scope_start_date.date().toString('yyyy-MM-dd')
        if self.current_end.isChecked():
            print('设置当前截止')
            chart_params['end'] = self.scope_end_date.date().toString('yyyy-MM-dd')
        print(chart_params)
        # 上传数据
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'trend/chart/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps(chart_params)
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
            message = response['message']
        except Exception as e:
            message = str(e)
        info = InformationPopup(message=message, parent=self)
        if not info.exec_():
            info.deleteLater()
            del info

    # 获取当前表的数据
    def getCurrentTrendTable(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/table/' + str(
                    self.table_id) + '/?look=1&mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            pass
        else:
            column_headers = response['data']['header_data']
            self.x_axis_combo.addItems(column_headers[1:])  # X轴选择
            print(column_headers)
            for text in column_headers[1:]:
                if text in self.x_axis_combo.currentText():
                    continue
                self.column_header_list.addItem(text)  # 列头待选表
            # 填充表格
            self.showTableData(response['data']['header_data'], response['data']['table_data'])

    # 设置表格显示表数据内容
    def showTableData(self, headers, table_contents):
        # 设置行列
        self.detail_trend_table.setRowCount(len(table_contents))
        headers.pop(0)
        col_count = len(headers)
        self.detail_trend_table.setColumnCount(col_count)
        self.detail_trend_table.setHorizontalHeaderLabels(headers)
        self.detail_trend_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        for row, row_content in enumerate(table_contents):
            for col in range(1, col_count + 1):
                item = QTableWidgetItem(row_content[col])
                item.setTextAlignment(Qt.AlignCenter)
                self.detail_trend_table.setItem(row, col - 1, item)


# 创建品种页的数据选择设置表
class VarietyTrendTablesShow(QTableWidget):
    network_result = pyqtSignal(str)

    KEY_LABELS = [
        ('id', '序号'),
        ('name', '名称'),
        ('start_date', '起始时间'),
        ('end_date', '结束时间'),
        ('update_time', '最近更新'),
        ('editor', '更新者'),
        ('group', '所属组'),
    ]

    def __init__(self, *args, **kwargs):
        super(VarietyTrendTablesShow, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

    def showRowContents(self, row_list):
        self.clear()
        self.setRowCount(len(row_list))
        self.setColumnCount(len(self.KEY_LABELS) + 1)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + [''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        for row, content_item in enumerate(row_list):
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = content_item[header[0]]
                else:
                    table_item = QTableWidgetItem(str(content_item[header[0]]))
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
                if col == len(self.KEY_LABELS) - 1:
                    # 增加【设置】按钮
                    option_button = TableRowReadButton('设置')
                    option_button.button_clicked.connect(self.option_button_clicked)
                    self.setCellWidget(row, col + 1, option_button)

    # 设置图表
    def option_button_clicked(self, option_button):
        current_row, _ = self.get_widget_index(option_button)
        table_id = self.item(current_row, 0).id
        table_text = self.item(current_row, 1).text()
        # 弹窗设置
        try:
            popup = SetChartDetailPopup(table_id, parent=self)
            popup.setWindowTitle(table_text)
            popup.getCurrentTrendTable()
            if not popup.exec_():
                popup.deleteLater()
                del popup
        except Exception as e:
            print(e)

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()


# 创建品种页图表
class CreateNewVarietyChartPopup(QDialog):
    def __init__(self, variety_id, variety_text, *args, **kwargs):
        super(CreateNewVarietyChartPopup, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=2)
        self.variety_id = variety_id
        # 显示品种
        show_info_layout = QHBoxLayout()
        show_info_layout.addWidget(QLabel('当前品种:'))
        show_info_layout.addWidget(QLabel(variety_text, objectName='attachVariety'))
        show_info_layout.addStretch()
        self.network_message_label = QLabel()
        show_info_layout.addWidget(self.network_message_label)
        layout.addLayout(show_info_layout)
        # 当前品种数据表格
        self.variety_tables = VarietyTrendTablesShow()
        layout.addWidget(self.variety_tables)
        self.setLayout(layout)
        self.setWindowTitle('创建图表')
        self.setMinimumSize(900, 500)
        self.setStyleSheet("""
        #attachVariety{
            color: rgb(200,20,50);
            font-weight:bold;
        }
        """)

    # 获取当前品种的所有数据表
    def getCurrentVarietyTables(self):
        try:
            r = requests.get(
                url=settings.SERVER_ADDR + 'trend/' + str(
                    self.variety_id) + '/group-tables/?mc=' + settings.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_message_label.setText(str(e))
        else:
            all_tables = list()
            for group_item in response['data']:
                all_tables += group_item['tables']
            # 显示表格
            self.variety_tables.showRowContents(all_tables)


# 显示图表
class ShowChartPopup(QDialog):
    def __init__(self, chart_data, *args, **kwargs):
        super(ShowChartPopup, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        chart = self._initial_chart(chart_data)
        chart_view = QChartView()
        chart_view.setChart(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        layout.addWidget(chart_view)
        self.resize(880, 380)
        self.setLayout(layout)

    # 初始化图表
    def _initial_chart(self, chart_data):
        self.setWindowTitle(chart_data['name'])
        header_data = chart_data['header_data']
        header_data.pop(0)  # 去掉id
        table_data = chart_data['table_data']
        # 转为pandas DataFrame
        table_df = pd.DataFrame(table_data)
        table_df.drop(columns=[0], inplace=True)  # 删除id列
        table_df.columns = [i for i in range(table_df.shape[1])]  # 重置列索引
        table_df[0] = pd.to_datetime(table_df[0])  # 第一列转为时间类型
        table_df.sort_values(by=0, inplace=True)
        try:
            if chart_data['start'] and chart_data['end']:
                start_date = pd.to_datetime(chart_data['start'])
                end_date = pd.to_datetime(chart_data['end'])
                table_df = table_df[(start_date <= table_df[0]) & (table_df[0] <= end_date)]
            elif chart_data['start']:
                start_date = pd.to_datetime(chart_data['start'])
                table_df = table_df[(start_date <= table_df[0])]
            elif chart_data['end']:
                end_date = pd.to_datetime(chart_data['end'])
                table_df = table_df[(table_df[0] <= end_date)]
            else:
                pass
            x_bottom = (json.loads(chart_data['x_bottom']))[0]
            y_left = json.loads(chart_data['y_left'])
            if x_bottom == 0:  # 以时间序列画图（目前仅支持一个x轴）
                chart = draw_line_series(name=chart_data['name'], table_df=table_df, x_bottom=x_bottom, y_left=y_left,
                                         legends=header_data, tick_count=40)
                # # 计算x轴的最值
                # x_axis_data = table_df.iloc[:, [x_bottom]]  # 取得第一列数据
                # min_x, max_x = x_axis_data.min(0).tolist()[0], x_axis_data.max(0).tolist()[0]  # 第一列时间数据(x轴)的最大值和最小值
                # if chart_data['category'] == 'line':  # 折线图
                #     for line in y_left:
                #         line_data = table_df.iloc[:, [x_bottom, line]]  # 取得图线的源数据
                #         series = QLineSeries()
                #         series.setName(header_data[line])
                #         for point_item in line_data.values.tolist():
                #             series.append(QDateTime(point_item[0]).toMSecsSinceEpoch(), float(point_item[1]))
                #         chart.addSeries(series)
                #         # 设置X轴
                #         axis_X = QDateTimeAxis()
                #         axis_X.setRange(min_x, max_x)
                #         axis_X.setFormat('yyyy-MM-dd')
                #         axis_X.setLabelsAngle(-90)
                #         axis_X.setTickCount(40)
                #         font = QFont()
                #         font.setPointSize(7)
                #         axis_X.setLabelsFont(font)
                #         # 设置Y轴
                #         axix_Y = QValueAxis()
                #         axix_Y.setLabelsFont(font)
                #         series = chart.series()[0]
                #         chart.createDefaultAxes()
                #         chart.setAxisX(axis_X, series)
                #         min_y, max_y = int(chart.axisY().min()), int(chart.axisY().max())
                #         # 根据位数取整数
                #         axix_Y.setRange(min_y, max_y)
                #         axix_Y.setLabelFormat('%i')
                #         chart.setAxisY(axix_Y, series)
                #         chart.legend().setAlignment(Qt.AlignBottom)
        except Exception as e:
            print(e)

        return chart
