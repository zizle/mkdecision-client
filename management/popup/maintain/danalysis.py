# _*_ coding:utf-8 _*_
# __Author__： zizle
import re
import xlrd
import json
import requests
import datetime
from xlrd import xldate_as_tuple
from PyQt5.QtWidgets import QDialog,QWidget, QLabel, QLineEdit, QGridLayout, QVBoxLayout, QTreeWidget, QTreeWidgetItem,\
    QPushButton, QComboBox, QFileDialog, QTableWidgetItem, QMessageBox, QHeaderView, QFormLayout, QHBoxLayout, QTableWidget
# from PyQt5.QtChart import QChart, QChartView, QLineSeries, QBarSet, QBarSeries
from PyQt5.QtGui import QPainter, QIcon
from PyQt5.QtCore import pyqtSignal, Qt
import config
from thread.request import RequestThread


# 新增品种弹窗
class NewVarietyPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(NewVarietyPopup, self).__init__(*args, **kwargs)
        # 左侧分组树
        self.group_tree = QTreeWidget(clicked=self.group_tree_clicked)
        # 新增品种控件
        self.nvwidget = QWidget()  # new variety widget
        # 新增品种控件布局
        nvwlayout = QGridLayout(margin=0)
        nvwlayout.addWidget(QLabel('所属分组：'), 0, 0)
        self.attach_group = QLabel(objectName='attachGroup')
        self.attach_group.gid = None
        nvwlayout.addWidget(self.attach_group, 0, 1)
        nvwlayout.addWidget(QLabel(parent=self, objectName='groupError'), 1, 0, 1, 2)
        nvwlayout.addWidget(QLabel('新的品种：'), 2, 0)
        self.vnedit = QLineEdit(textChanged=self.vn_changed)  # variety name edit
        nvwlayout.addWidget(self.vnedit, 2, 1)
        nvwlayout.addWidget(QLabel(parent=self, objectName='nvnameError'), 3, 0, 1, 2)
        nvwlayout.addWidget(QLabel('英文代码：'), 4, 0)
        self.venedit = QLineEdit(textChanged=self.ven_changed)  # variety english name edit
        nvwlayout.addWidget(self.venedit, 4, 1)
        nvwlayout.addWidget(QLabel(parent=self, objectName='nvenameError'), 5, 0, 1, 2)
        addlayout = QHBoxLayout()
        self.add_variety_btn = QPushButton('确认添加', parent=self, objectName='addVariety', clicked=self.add_new_variety)
        addlayout.addWidget(self.add_variety_btn, alignment=Qt.AlignRight)
        # 布局
        self.nvwidget.setLayout(nvwlayout)
        layout = QHBoxLayout()
        llayout = QVBoxLayout()  # left layout
        rlayout = QVBoxLayout()  # right layout
        llayout.addWidget(self.group_tree)
        llayout.addWidget(QPushButton('新建组别', clicked=self.create_vgroup), alignment=Qt.AlignLeft)
        rlayout.addWidget(self.nvwidget)
        rlayout.addLayout(addlayout)
        rlayout.addStretch()
        layout.addLayout(llayout)
        layout.addLayout(rlayout)
        self.setLayout(layout)
        # 样式
        self.setWindowTitle('新增品种')
        self.setFixedSize(800, 500)
        self.group_tree.header().hide()
        self.group_tree.setMaximumWidth(180)
        self.setObjectName('myself')
        self.setStyleSheet("""
            
        """)
        # 初始化
        self.get_groups()

    # 获取分组树内容(分组+品种)
    def get_groups(self):
        self.group_tree.clear()
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'danalysis/groups-varieties/?mc=' + config.app_dawn.value('machine'),
                headers=config.CLIENT_HEADERS,
                cookies=config.app_dawn.value('cookies')
            )
            response = json.loads(r.content.decode('utf-8'))
        except Exception:
            return
        # 填充品种树
        for group_item in response['data']:
            group = QTreeWidgetItem(self.group_tree)
            group.setText(0, group_item['name'])
            group.gid = group_item['id']
            # 添加子节点
            for variety_item in group_item['varieties']:
                child = QTreeWidgetItem()
                child.setText(0, variety_item['name'])
                child.vid = variety_item['id']
                group.addChild(child)

    # 点击分组树
    def group_tree_clicked(self):
        item = self.group_tree.currentItem()
        if item.childCount():  # has children open the root
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        text = item.text(0)
        if item.parent():
            # 提示只能在大类下创建品种
            el = self.findChild(QLabel, 'groupError')
            el.setText('只能在分组下新增品种,如需新建,请点击左下角【新建组别】')
            self.add_variety_btn.setEnabled(False)
        else:
            # 该表所属分组
            self.attach_group.setText(text)
            self.attach_group.gid = item.gid
            # 清除提示消息
            el = self.findChild(QLabel, 'groupError')
            el.setText('')
            self.add_variety_btn.setEnabled(True)

    # 新增品种提交
    def add_new_variety(self):
        # 获取当前选择的分组
        if not self.attach_group.gid:
            # 提示只能在大类下创建品种
            el = self.findChild(QLabel, 'groupError')
            el.setText('请选择品种所属的分组,如需新建,请点击左下角【新建组别】')
            self.add_variety_btn.setEnabled(False)
            return
        vname = re.sub(r'\s+', '', self.vnedit.text())
        vname_en = re.sub(r'\s+', '', self.venedit.text())
        vname_en = re.match('[a-z0-9]+', vname_en)
        if not vname:
            el = self.findChild(QLabel, 'nvnameError')
            el.setText('还没输入品种的名称')
            self.add_variety_btn.setEnabled(False)
            return
        if not vname_en:
            el = self.findChild(QLabel, 'nvenameError')
            el.setText('请输入正确的英文代码,小写字母和数字一种或多种组成')
            self.add_variety_btn.setEnabled(False)
            return
        vname_en = vname_en.group()
        # 提交
        try:
            r = requests.post(
                url=config.SERVER_ADDR + 'danalysis/variety-groups/' + str(self.attach_group.gid) + '/',
                headers=config.CLIENT_HEADERS,
                data=json.dumps({
                    'machine_code': config.app_dawn.value('machine'),
                    "name": vname,
                    "name_en": vname_en
                }),
                cookies=config.app_dawn.value('cookies')
            )
            response = json.loads(r.content.decode('utf-8'))
            if response['error']:
                raise ValueError(response['message'])
        except Exception as e:
            el = self.findChild(QLabel, 'nvenameError')
            el.setText(str(e))
        else:
            self.vnedit.clear()
            self.venedit.clear()
            self.get_groups()

    # 品种中文编辑框的信号函数
    def vn_changed(self):
        el = self.findChild(QLabel, 'nvnameError')
        el.setText('')
        self.add_variety_btn.setEnabled(True)

    # 品种英文编辑框的信号函数
    def ven_changed(self):
        el = self.findChild(QLabel, 'nvenameError')
        el.setText('')
        self.add_variety_btn.setEnabled(True)

    # 新增品种分组
    def create_vgroup(self):
        print('新增品种分组')
        self.vgpopup = QDialog(parent=self)  # variety group popup
        self.vgpopup.deleteLater()
        playout = QGridLayout()  # popup layout
        playout.addWidget(QLabel('组名称：'), 0, 0)
        playout.addWidget(QLineEdit(parent=self.vgpopup, objectName='nvgEdit'), 0, 1)  # nvg = new variety group
        playout.addWidget(QLabel(parent=self.vgpopup, objectName='nvgError'), 1, 0, 1, 2)
        abtlayout = QHBoxLayout()
        abtlayout.addWidget(QPushButton('增加', parent=self.vgpopup, objectName='addNvgbtn',
                                        clicked=self.add_new_vgroup),alignment=Qt.AlignRight)
        playout.addLayout(abtlayout, 1, 1)
        self.vgpopup.setLayout(playout)
        self.vgpopup.resize(300, 120)
        self.vgpopup.setWindowTitle('增加品种组')
        if not self.vgpopup.exec_():
            del self.vgpopup

    # 新增品种大分类
    def add_new_vgroup(self):
        print('新增品种大类')
        edit = self.vgpopup.findChild(QLineEdit, 'nvgEdit')
        group_name = re.sub(r'\s+', '', edit.text())
        if not group_name:
            el = self.vgpopup.findChild(QLabel, 'nvgError')
            el.setText('请输入正确的组名称.')
            return
        # 提交
        commit_btn = self.vgpopup.findChild(QPushButton, 'addNvgbtn')
        commit_btn.setEnabled(False)
        try:
            r = requests.post(
                url=config.SERVER_ADDR + 'danalysis/variety-groups/',
                headers=config.CLIENT_HEADERS,
                data=json.dumps({
                    'machine_code': config.app_dawn.value('machine'),
                    "name": group_name
                }),
                cookies=config.app_dawn.value('cookies')
            )
            response = json.loads(r.content.decode('utf-8'))
            if response['error']:
                raise ValueError(response['message'])
        except Exception as e:
            el = self.vgpopup.findChild(QLabel, 'nvgError')
            el.setText(str(e))
        else:
            # 重新刷新目录树
            self.get_groups()
            self.vgpopup.close()
        commit_btn.setEnabled(True)


# 新建数据弹窗
class NewTablePopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(NewTablePopup, self).__init__(*args, **kwargs)
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
        llayout.addWidget(self.variety_tree)
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
        self.variety_tree.setMaximumWidth(180)
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
        self.get_varieties()
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
    def get_varieties(self):
        self.variety_tree.clear()
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'danalysis/table_groups/?mc=' + config.app_dawn.value('machine'),
                cookies=config.app_dawn.value('cookies')
            )
            response = json.loads(r.content.decode('utf-8'))
            if response['error']:
                raise ValueError('')
        except Exception:
            return
        for count, variety_item in enumerate(response['data']):
            variety = QTreeWidgetItem(self.variety_tree)
            variety.setText(0, variety_item['name'])
            variety.vid = variety_item['id']
            for group_item in variety_item['groups']:
                group = QTreeWidgetItem(variety)
                group.setText(0, group_item['name'])
                group.gid = group_item['id']
        # 目录树填充完毕手动设置当前第一个，并触发点击事件
        self.variety_tree.setCurrentIndex(self.variety_tree.model().index(0, 0))  # 最顶层设置为当前
        self.variety_tree_clicked()  # 手动调用点击事件

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
                url=config.SERVER_ADDR + 'danalysis/table_groups/' + str(attach_variety) + '/',
                headers=config.CLIENT_HEADERS,
                data=json.dumps({
                    'machine_code': config.app_dawn.value('machine'),
                    "name": group_name
                }),
                cookies=config.app_dawn.value('cookies')
            )
            response = json.loads(r.content.decode('utf-8'))
            if response['error']:
                raise ValueError(response['message'])
        except Exception as e:
            el = self.tgpopup.findChild(QLabel, 'tgpopupNError')
            el.setText(str(e))
        else:
            # 重新刷新目录树
            self.get_varieties()
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
                url=config.SERVER_ADDR + 'danalysis/table/' + str(gid) + '/',
                headers=config.CLIENT_HEADERS,
                data=json.dumps({
                    "machine_code": config.app_dawn.value("machine"),
                    "table_name": tbname,
                    "table_data": table_data
                }),
                cookies=config.app_dawn.value('cookies')
            )
            response = json.loads(r.content.decode('utf-8'))
            if response['error']:
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















#
# # 新建品种弹窗
# class NewVarietyPopup1(QDialog):
#     data_url = config.SERVER_ADDR + 'danalysis/variety/?mc=' + config.app_dawn.value('machine')
#
#     def __init__(self, *args, **kwargs):
#         super(NewVarietyPopup, self).__init__(*args, **kwargs)
#         layout = QVBoxLayout()
#         tflayout = QHBoxLayout()  # tree(品种) form(添加表单) 布局
#         # 左侧品种树
#         self.variety_tree = QTreeWidget(clicked=self.variety_tree_clicked)
#         # 右侧新增品种表单控件
#         self.form_widget = QWidget()
#         qfl = QFormLayout()
#         self.attach_to = QLabel(styleSheet='color:rgb(180,20,30)')
#         self.attach_to.gid = None
#         self.variety_zh = QLineEdit()
#         self.variety_en = QLineEdit()
#         qfl.addRow("所属类别：", self.attach_to)
#         qfl.addRow("", QLabel(parent=self.form_widget, objectName='errorLabel', styleSheet='color:rgb(200,10,20)'))
#         qfl.addRow("品种名称：", self.variety_zh)
#         qfl.addRow("英文代码：", self.variety_en)
#         qfl.addRow('', QPushButton('确认添加', parent=self.form_widget, objectName='addBtn', clicked=self.add_new_variety))
#         self.form_widget.setLayout(qfl)
#         tflayout.addWidget(self.variety_tree)
#         tflayout.addWidget(self.form_widget)
#         layout.addLayout(tflayout)
#         # 新增类别按钮
#         layout.addWidget(QPushButton('新增', clicked=self.add_new_group), alignment=Qt.AlignLeft)
#         # 样式设置
#         self.setFixedSize(800, 600)
#         self.variety_tree.header().hide()
#         self.variety_tree.setMaximumWidth(180)
#         self.setStyleSheet('background-color: rgb(255,255,255)')
#         # 显示总布局
#         self.setLayout(layout)
#         # 初始数据获取
#         self.get_varieties()
#
#     # 获取品种目录树的内容
#     def get_varieties(self):
#         if hasattr(self, 'variety_thread'):
#             del self.variety_thread
#         self.variety_thread = RequestThread(
#             url=self.data_url,
#             method='get',
#             headers=config.CLIENT_HEADERS,
#             data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
#             cookies=config.app_dawn.value('cookies')
#         )
#         self.variety_thread.finished.connect(self.variety_thread.deleteLater)
#         self.variety_thread.response_signal.connect(self.variety_thread_back)
#         self.variety_thread.start()
#
#     # 获取品种的线程回调函数
#     def variety_thread_back(self, content):
#         if content['error']:
#             return
#         self.variety_tree.clear()
#         # 填充品种树
#         for group_item in content['data']:
#             group = QTreeWidgetItem(self.variety_tree)
#             group.setText(0, group_item['name'])
#             group.gid = group_item['id']
#             # 添加子节点
#             for sub_item in group_item['subs']:
#                 print(sub_item)
#                 child = QTreeWidgetItem()
#                 child.setText(0, sub_item['name'])
#                 child.gid = sub_item['id']
#                 group.addChild(child)
#
#     # 品种树节点点击
#     def variety_tree_clicked(self):
#         item = self.variety_tree.currentItem()
#         if item.childCount():  # has children open the root
#             if item.isExpanded():
#                 item.setExpanded(False)
#             else:
#                 item.setExpanded(True)
#         text = item.text(0)
#         # text填入右侧显示
#         self.attach_to.setText(text)
#         self.attach_to.gid = item.gid
#         el = self.form_widget.findChild(QLabel, 'errorLabel')
#         add_btn = self.form_widget.findChild(QPushButton, 'addBtn')
#         if item.parent():
#             el.setText("只允许在大类下创建品种.")
#             add_btn.setEnabled(False)
#         else:
#             el.setText("")
#             add_btn.setEnabled(True)
#
#     # 新增大类别
#     def add_new_group(self):
#         if not hasattr(self, 'ng_widget'):
#             self.ng_widget = QWidget(self.form_widget,
#                                      styleSheet='background:rgb(255,255,255)')  # 新大类new group widget
#             # 关闭按钮
#             cly = QHBoxLayout()
#             cly.addWidget(
#                 QPushButton(clicked=self.ng_widget_close, icon=QIcon('media/drop-down.png')),
#                 alignment=Qt.AlignTop | Qt.AlignRight
#             )
#             # 添加按钮
#             aly = QHBoxLayout()
#             aly.addWidget(QPushButton('添加', clicked=self.post_new_group), alignment=Qt.AlignTop|Qt.AlignRight)
#             # QPushButton('close', self.ng_widget)
#             gly = QFormLayout()  # 新增大类布局 group layout
#             gly.addRow(cly)
#             gly.addRow('', QLabel(''))
#             gly.addRow('', QLabel(parent=self.ng_widget, objectName='errorLabel', styleSheet='color:rgb(200,10,20)'))
#             gly.addRow('名称', QLineEdit(parent=self.ng_widget, objectName='newGroup'))
#             gly.addRow(aly)
#             self.ng_widget.setLayout(gly)
#         self.ng_widget.resize(self.form_widget.width(), self.form_widget.height())
#         self.ng_widget.show()
#
#     # 上传添加新大类
#     def post_new_group(self):
#         edit = self.ng_widget.findChild(QLineEdit, 'newGroup')
#         variety = {
#             'name': edit.text().strip(' '),
#             'parent_id': None
#         }
#         self.post_new_variety(variety=variety)
#
#     # 关闭新增大类的窗口
#     def ng_widget_close(self):
#         self.ng_widget.close()
#
#     # 新增品种
#     def add_new_variety(self):
#         variety = {
#             'name': self.variety_zh.text().strip(' '),
#             'name_en': self.variety_en.text().strip(' '),
#             'parent_id': self.attach_to.gid
#         }
#         self.post_new_variety(variety=variety, flag='variety')
#
#     # 上传新品种
#     def post_new_variety(self, variety, flag='group'):
#         try:
#             if flag != 'group':
#                 if not variety['parent_id']:
#                     raise ValueError('您还没选择所属大类.')
#             if not variety['name']:
#                 raise ValueError('您还没输入名称.')
#             response = requests.post(
#                 url=self.data_url,
#                 headers=config.CLIENT_HEADERS,
#                 data=json.dumps({
#                     "machine_code": config.app_dawn.value("machine"),
#                     "variety": variety
#                 }),
#                 cookies=config.app_dawn.value('cookies')
#             )
#             r_data = json.loads(response.content.decode('utf-8'))
#             if r_data['error']:
#                 raise ValueError(r_data['message'])
#         except Exception as e:
#             # 上传出错
#             if flag == 'group':
#                 el = self.ng_widget.findChild(QLabel, 'errorLabel')  # error label
#                 el.setText(str(e))
#             else:
#                 el = self.form_widget.findChild(QLabel, 'errorLabel')  # error label
#                 el.setText(str(e))
#         else:
#             # 上传成功
#             if flag == 'group':
#                 self.ng_widget_close()
#                 self.get_varieties()
#             else:
#                 self.close()




#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# # 上传数据分析首页图表
# class DANewHomeChart(QDialog):
#     upload_new = pyqtSignal(dict)
#
#     def __init__(self):
#         super(DANewHomeChart, self).__init__()
#         layout = QVBoxLayout()
#         name = QLabel('图表名称:')
#         self.name_edit = QLineEdit()
#         self.name_en = QLabel('英文名称:')
#         self.name_en_edit = QLineEdit()
#         option = QLabel('图表类型:')
#         self.type_selection = QComboBox()
#         self.chart_type = list()
#         chart_type_zh = list()
#         for t in config.CHART_TYPE:
#             self.chart_type.append(t[0])
#             chart_type_zh.append(t[1])
#         self.type_selection.addItems(chart_type_zh)
#         edit_layout = QGridLayout()
#         edit_layout.addWidget(name, 0, 0)
#         edit_layout.addWidget(self.name_edit, 0, 1)
#         edit_layout.addWidget(self.name_en, 1, 0)
#         edit_layout.addWidget(self.name_en_edit, 1, 1)
#         edit_layout.addWidget(option, 2, 0)
#         edit_layout.addWidget(self.type_selection, 2, 1)
#         new_data_btn = QPushButton('添加数据')
#         new_data_btn.setObjectName("addDataButton")
#         upload_button = QPushButton('确认新增')
#         review_label = QLabel("预览")
#         edit_layout.addWidget(new_data_btn, 3, 0)
#         edit_layout.addWidget(review_label, 4, 0)
#         layout.addLayout(edit_layout)
#         # self.review_table = QTableWidget()
#         # layout.addWidget(self.review_table)
#         self.review_chart = QChartView()
#         layout.addWidget(self.review_chart)
#         layout.addWidget(upload_button)
#         self.setLayout(layout)
#         # style
#         self.setMinimumSize(800, 560)
#         new_data_btn.setCursor(Qt.PointingHandCursor)
#         self.review_chart.setStyleSheet("""
#             background-image: url('media/chartbg-watermark.png');
#         """)
#         self.setStyleSheet("""
#         #addDataButton{
#             border:1px solid gray;
#             min-height:22px;
#             color: rgb(20,10,220);
#             padding:0 10px;
#         }
#         QComboBox {
#             border: 1px solid gray;
#             border-radius: 2px;
#             padding: 1px 2px 1px 2px;
#             min-width: 9em;
#             min-height:18px;
#         }
#         QComboBox::drop-down {
#             subcontrol-origin: padding;
#             subcontrol-position: top right;
#             width: 20px;
#             border-left-width: 1px;
#             border-left-color: darkgray;
#             border-left-style: solid; /* just a single line */
#             border-top-right-radius: 2px; /* same radius as the QComboBox */
#             border-bottom-right-radius: 3px;
#         }
#         QComboBox::down-arrow {
#             image: url(media/drop-dowm.png);
#         }
#         """)
#         # signal
#         new_data_btn.clicked.connect(self.add_chart_data)
#         self.type_selection.currentIndexChanged.connect(self.chart_type_changed)
#         upload_button.clicked.connect(self.create_new_chart)
#         # 数据源
#         self.chart_labels = list()
#         self.x1_axis = list()
#         self.x2_axis = list()
#         self.y1_axis = list()
#         self.y2_axis = list()
#         self.has_data = False
#
#     def add_chart_data(self):
#         # 获取数据
#         # 弹窗选择文件
#         file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files (*.xlsx)")
#         if not file_path:
#             return
#         # 处理Excel数据写入表格预览
#         rf = xlrd.open_workbook(filename=file_path)
#         sheet1 = rf.sheet_by_index(0)
#         self.chart_labels = sheet1.row_values(0)
#         self.x1_axis.clear()
#         self.x2_axis.clear()
#         self.y1_axis.clear()
#         self.y2_axis.clear()
#         for row in range(1, sheet1.nrows):  # skip header
#             row_content = sheet1.row_values(row)
#             self.x1_axis.append(row_content[0])
#             self.y1_axis.append(row_content[1])
#             self.x2_axis.append(row_content[2])
#             self.y2_axis.append(row_content[3])
#         self.has_data = True
#         self.chart_type_changed()
#
#     def chart_type_changed(self):
#         if self.has_data:
#             if self.type_selection.currentIndex() == 0:
#                 chart = QChart()
#                 series = QLineSeries()
#                 for idx, x in enumerate(self.x1_axis):
#                     series.append(x, self.y1_axis[idx])
#                 chart.addSeries(series)
#                 chart.setTitle(self.name_edit.text())
#                 self.review_chart.setChart(chart)
#                 self.review_chart.setRenderHint(QPainter.Antialiasing)
#                 chart.createDefaultAxes()
#                 chart.setBackgroundVisible(False)
#             elif self.type_selection.currentIndex() == 1:
#                 chart = QChart()
#                 chart.setTitle(self.name_edit.text())
#                 # 添加水印背景图片
#                 chart.setBackgroundVisible(False)
#                 series = QBarSeries()
#                 bar = QBarSet('')
#                 for index in range(len(self.x1_axis)):
#                     bar.append(self.y1_axis[index])
#                 series.append(bar)
#                 chart.addSeries(series)
#                 chart.createDefaultAxes()
#                 self.review_chart.setChart(chart)
#             else:
#                 pass
#
#     def create_new_chart(self):
#         # 整理数据发出信号
#         data = dict()
#         chart_name = self.name_edit.text().strip(' ')
#         chart_name_en = self.name_en_edit.text().strip(' ')
#         if not chart_name or not chart_name_en:
#             QMessageBox.information(self, '错误', '请填入图表名称和英文名称.', QMessageBox.Yes)
#             return
#         data['chart_name'] = chart_name
#         data['chart_name_en'] = chart_name_en
#         data['chart_type'] = self.chart_type[self.type_selection.currentIndex()]
#         data['chart_labels'] = self.chart_labels
#         data['x1'] = self.x1_axis
#         data['y1'] = self.y1_axis
#         data['x2'] = self.x2_axis
#         data['y2'] = self.y2_axis
#         self.upload_new.emit(data)
#
#
# # 上传某个品种的图表
# class DANewVarietyChart(QDialog):
#     upload_new = pyqtSignal(dict)
#
#     def __init__(self):
#         super(DANewVarietyChart, self).__init__()
#         layout = QVBoxLayout()
#         name = QLabel('图表名称:')
#         self.name_edit = QLineEdit()
#         name_en = QLabel('英文名称:')
#         self.name_en_edit = QLineEdit()
#         option = QLabel('图表类型:')
#         self.type_selection = QComboBox()
#         self.chart_type = list()
#         chart_type_zh = list()
#         for t in config.CHART_TYPE:
#             self.chart_type.append(t[0])
#             chart_type_zh.append(t[1])
#         self.type_selection.addItems(chart_type_zh)
#         variety_label = QLabel('所属品种:')
#         self.variety_selection = QComboBox()
#         edit_layout = QGridLayout()
#         edit_layout.addWidget(name, 0, 0, 1, 3)
#         edit_layout.addWidget(self.name_edit, 0, 1, 1, 3)
#         edit_layout.addWidget(name_en, 1, 0, 1, 3)
#         edit_layout.addWidget(self.name_en_edit, 1, 1, 1, 3)
#         edit_layout.addWidget(option, 2, 0)
#         edit_layout.addWidget(self.type_selection, 2, 1)
#         edit_layout.addWidget(variety_label, 2, 2)
#         edit_layout.addWidget(self.variety_selection, 2, 3)
#         new_data_btn = QPushButton('添加数据')
#         new_data_btn.setObjectName("addDataButton")
#         upload_button = QPushButton('确认新增')
#         review_label = QLabel("预览")
#         edit_layout.addWidget(new_data_btn, 3, 0)
#         edit_layout.addWidget(review_label, 4, 0)
#         layout.addLayout(edit_layout)
#         # self.review_table = QTableWidget()
#         # layout.addWidget(self.review_table)
#         self.review_chart = QChartView()
#         layout.addWidget(self.review_chart)
#         layout.addWidget(upload_button)
#         self.setLayout(layout)
#         # style
#         name.setMaximumWidth(60)
#         name_en.setMaximumWidth(60)
#         variety_label.setMaximumWidth(60)
#         option.setMaximumWidth(60)
#         self.setMinimumSize(800, 560)
#         self.review_chart.setStyleSheet("""
#             background-image: url('media/chartbg-watermark.png');
#         """)
#         self.setStyleSheet("""
#         #addDataButton{
#             border:1px solid gray;
#             min-height:22px;
#             color: rgb(20,10,220);
#             padding:0 10px;
#         }
#         QComboBox {
#             border: 1px solid gray;
#             border-radius: 2px;
#             padding: 1px 2px 1px 2px;
#             min-width: 9em;
#             min-height:18px;
#         }
#         QComboBox::drop-down {
#             subcontrol-origin: padding;
#             subcontrol-position: top right;
#             width: 20px;
#             border-left-width: 1px;
#             border-left-color: darkgray;
#             border-left-style: solid; /* just a single line */
#             border-top-right-radius: 2px; /* same radius as the QComboBox */
#             border-bottom-right-radius: 3px;
#         }
#         QComboBox::down-arrow {
#             image: url(media/drop-dowm.png);
#         }
#         """)
#         # signal
#         new_data_btn.clicked.connect(self.add_chart_data)
#         self.type_selection.currentIndexChanged.connect(self.chart_type_changed)
#         upload_button.clicked.connect(self.create_new_chart)
#         # 数据源
#         self.chart_labels = list()
#         self.x1_axis = list()
#         self.x2_axis = list()
#         self.y1_axis = list()
#         self.y2_axis = list()
#         self.has_data = False
#         self.variety_thread = None
#         self.varieties = list()
#         # 获取品种数据
#         self.get_variety_selection(url=config.SERVER_ADDR + 'danalysis/variety_menu/')
#
#     def get_variety_selection(self, url):
#         if not url:
#             return
#         if self.variety_thread:
#             del self.variety_thread
#         self.variety_thread = RequestThread(
#             url=url,
#             method='get',
#             headers=config.CLIENT_HEADERS,
#             data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
#             cookies=config.app_dawn.value('cookies')
#         )
#         self.variety_thread.response_signal.connect(self.variety_thread_back)
#         self.variety_thread.finished.connect(self.variety_thread.deleteLater)
#         self.variety_thread.start()
#
#     def variety_thread_back(self, content):
#         if content['error']:
#             return
#         for item in content['data']:
#             self.varieties += item['subs']
#         for variety_item in self.varieties:
#             self.variety_selection.addItem(variety_item['name'])
#
#     def add_chart_data(self):
#         # 弹窗选择文件，获取数据
#         file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files (*.xlsx)")
#         if not file_path:
#             return
#         # 处理Excel数据写入表格预览
#         rf = xlrd.open_workbook(filename=file_path)
#         sheet1 = rf.sheet_by_index(0)
#         self.chart_labels = sheet1.row_values(0)
#         self.x1_axis.clear()
#         self.x2_axis.clear()
#         self.y1_axis.clear()
#         self.y2_axis.clear()
#         for row in range(1, sheet1.nrows):  # skip header
#             row_content = sheet1.row_values(row)
#             self.x1_axis.append(row_content[0])
#             self.y1_axis.append(row_content[1])
#             self.x2_axis.append(row_content[2])
#             self.y2_axis.append(row_content[3])
#         self.has_data = True
#         self.chart_type_changed()
#
#     def chart_type_changed(self):
#         if self.has_data:
#             if self.type_selection.currentIndex() == 0:
#                 chart = QChart()
#                 series = QLineSeries()
#                 for idx, x in enumerate(self.x1_axis):
#                     series.append(x, self.y1_axis[idx])
#                 chart.addSeries(series)
#                 chart.setTitle(self.name_edit.text())
#                 self.review_chart.setChart(chart)
#                 self.review_chart.setRenderHint(QPainter.Antialiasing)
#                 chart.createDefaultAxes()
#                 chart.setBackgroundVisible(False)
#             elif self.type_selection.currentIndex() == 1:
#                 chart = QChart()
#                 chart.setTitle(self.name_edit.text())
#                 # 添加水印背景图片
#                 chart.setBackgroundVisible(False)
#                 series = QBarSeries()
#                 bar = QBarSet('')
#                 for index in range(len(self.x1_axis)):
#                     bar.append(self.y1_axis[index])
#                 series.append(bar)
#                 chart.addSeries(series)
#                 chart.createDefaultAxes()
#                 self.review_chart.setChart(chart)
#             else:
#                 pass
#
#     def create_new_chart(self):
#         # 整理数据发出信号
#         data = dict()
#         chart_name = self.name_edit.text().strip(' ')
#         chart_name_en = self.name_en_edit.text().strip(' ')
#         if not chart_name or not chart_name_en:
#             QMessageBox.information(self, '错误', '请填入图表名称和英文名称.', QMessageBox.Yes)
#             return
#         data['chart_name'] = chart_name
#         data['chart_name_en'] = chart_name_en
#         data['chart_type'] = self.chart_type[self.type_selection.currentIndex()]
#         data['chart_labels'] = self.chart_labels
#         data['variety'] = self.varieties[self.variety_selection.currentIndex()]['name_en']
#         data['x1'] = self.x1_axis
#         data['y1'] = self.y1_axis
#         data['x2'] = self.x2_axis
#         data['y2'] = self.y2_axis
#         self.upload_new.emit(data)
