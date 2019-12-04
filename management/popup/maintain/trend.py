# _*_ coding:utf-8 _*_
# __Author__： zizle
import re
import xlrd
import json
import requests
import datetime
from xlrd import xldate_as_tuple
from PyQt5.QtWidgets import QDialog,QWidget, QLabel, QLineEdit, QGridLayout, QVBoxLayout, QTreeWidget, QTreeWidgetItem,\
    QPushButton, QComboBox, QFileDialog, QTableWidgetItem, QHeaderView, QHBoxLayout, QTableWidget
from PyQt5.QtCore import Qt
import config


# 新建数据弹窗
class NewTrendTablePopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(NewTrendTablePopup, self).__init__(*args, **kwargs)
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
        llayout.addWidget(QPushButton('新建组别', clicked=self.create_tgroup), alignment=Qt.AlignLeft)
        rlayout.addWidget(self.udwidget)
        rlayout.addLayout(addlayout)
        layout.addLayout(llayout)
        layout.addLayout(rlayout)
        self.setLayout(layout)
        # 样式
        self.setWindowTitle('新建数据')
        self.setFixedSize(1000, 600)
        self.review_table.horizontalHeader().hide()
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
        self.date_type.setCurrentIndex(self.date_type.count()-1)

    # 该变时间类型
    def change_date_type(self, t):
        fmt = self.date_type.currentData()
        for row in range(self.review_table.rowCount()):
            for col in range(self.review_table.columnCount()):
                item = self.review_table.item(row, 0)
                if hasattr(item, 'date'):  # date属性是在填充表格时绑定，详见self._show_file_data函数
                    text = item.date.strftime(fmt)
                    item.setText(text)

    # 获取品种树内容
    def getVarietyTableGroups(self):
        self.variety_tree.clear()
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'trend/varieties-table-groups/?mc=' + config.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            return
        for index, variety_item in enumerate(response['data']):
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

    # 新增数据大类
    def create_tgroup(self):
        # 获取当前选择的品种
        variety = self.attach_variety.text()
        self.tgpopup = QDialog(parent=self)
        self.tgpopup.deleteLater()
        self.tgpopup.attach_variety = self.attach_variety.vid
        playout = QGridLayout()  # table group popup layout
        playout.addWidget(QLabel('所属品种：'), 0, 0)
        playout.addWidget(QLabel(variety, parent=self.tgpopup, objectName='tgpopAttachTo'), 0, 1)
        playout.addWidget(QLabel(parent=self.tgpopup, objectName='tgpopupVError'), 1, 0, 1, 2)  # variety error
        playout.addWidget(QLabel('大类名称：'), 2, 0)
        playout.addWidget(QLineEdit(parent=self.tgpopup, objectName='ngEdit', textChanged=self.ngedit_foucs))
        playout.addWidget(QLabel(parent=self.tgpopup, objectName='tgpopupNError'), 3, 0, 1, 2)  # name error
        abtlayout = QHBoxLayout()
        abtlayout.addWidget(QPushButton('增加', objectName='addGroupBtn', clicked=self.add_table_group),
                            alignment=Qt.AlignRight)
        playout.addLayout(abtlayout, 4, 1)
        self.tgpopup.setLayout(playout)
        self.tgpopup.setFixedSize(400, 150)
        self.tgpopup.setWindowTitle('增加数据组')
        if not self.tgpopup.exec_():
            del self.tgpopup

    # 关闭新建数据组控件
    def ng_widget_close(self):
        self.current_option = 0
        self.ng_widget.close()
        self.add_table_btn.show()

    # 新建数据组别
    def add_table_group(self):
        edit = self.tgpopup.findChild(QLineEdit, 'ngEdit')
        group_name = re.sub(r'\s+', '', edit.text())
        attach_variety = self.tgpopup.attach_variety
        if not attach_variety:
            el = self.tgpopup.findChild(QLabel, 'tgpopupVError')
            el.setText('请选择品种再进行增加.')
        if not group_name:
            el = self.tgpopup.findChild(QLabel, 'tgpopupNError')
            el.setText('还没输入组别名称.')
            return
        # 提交
        commit_btn = self.tgpopup.findChild(QPushButton, 'addGroupBtn')
        commit_btn.setEnabled(False)
        try:
            r = requests.post(
                url=config.SERVER_ADDR + 'trend/variety-table-group/' + str(attach_variety) + '/?mc=' + config.app_dawn.value('machine'),
                headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    "name": group_name
                }),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            el = self.tgpopup.findChild(QLabel, 'tgpopupNError')
            el.setText(str(e))
        else:
            # 重新刷新目录树
            self.getVarietyTableGroups()
            self.tgpopup.close()
        commit_btn.setEnabled(True)

    # 新建组别的名称编辑框文字改变
    def ngedit_foucs(self, t):
        error_label = self.tgpopup.findChild(QLabel, 'tgpopupNError')
        error_label.setText('')

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
        # labels = sheet1.row_values(0)
        # xlrd读取的类型ctype： 0 empty,1 string, 2 number, 3 date, 4 boolean, 5 error
        nrows = sheet1.nrows
        ncols = sheet1.ncols
        self.review_table.clear()
        self.review_table.setRowCount(nrows)
        self.review_table.setColumnCount(ncols)
        # self.review_table.setHorizontalHeaderLabels([str(i) for i in labels])
        self.review_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 时间类型约束
        date_type = self.date_type.currentData()
        # 数据填入预览表格
        for row in range(0, nrows):  # skip header
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
                self.review_table.setItem(row, col, item)
                row_content.append(cell)

    # 读取预览表格的数据
    def _read_review_data(self):
        row_count = self.review_table.rowCount()
        column_count = self.review_table.columnCount()
        data_dict = dict()
        data_dict['value_list'] = list()
        for row in range(row_count):
            row_content = list()
            for col in range(column_count):
                item = self.review_table.item(row, col)
                row_content.append(item.text())
            if row == 0:
                data_dict['header_labels'] = row_content
            data_dict['value_list'].append(row_content)
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
                url=config.SERVER_ADDR + 'trend/table/' + str(gid) + '/',
                headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    "table_name": tbname,
                    "table_data": table_data
                }),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            el = self.findChild(QLabel, 'commitError')
            el.setText(str(e))
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
