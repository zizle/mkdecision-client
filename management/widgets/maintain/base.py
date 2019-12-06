# _*_ coding:utf-8 _*_
# Author:zizle QQ:462894999
import re
import json
import requests
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QPushButton,\
    QComboBox, QLabel, QListView, QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
import config

""" 管理表格 """


# 复选框
class CheckBox(QWidget):
    check_changed = pyqtSignal(QCheckBox)

    def __init__(self, checked, *args, **kwargs):
        super(CheckBox, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        self.check_button = QCheckBox(parent=self, checked=checked)
        self.check_button.setMinimumHeight(13)
        layout.addWidget(self.check_button, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        self.check_button.stateChanged.connect(lambda: self.check_changed.emit(self))


# 【角色】下拉框选择
class ComboBox(QComboBox):
    text_changed = pyqtSignal(QComboBox)

    def __init__(self, couple_items, current_text, *args, **kwargs):
        super(ComboBox, self).__init__(*args, **kwargs)
        self.blockSignals(True)  # 关闭信号
        line_edit = QLineEdit(readOnly=True)
        line_edit.setAlignment(Qt.AlignCenter)
        for item in couple_items:
            self.addItem(item[0], item[1])
        self.setLineEdit(line_edit)  # 居中显示
        self.currentTextChanged.connect(lambda: self.text_changed.emit(self))
        # 设置当前项目
        for i in range(self.count()):
            if self.itemData(i) == current_text:
                self.setCurrentIndex(i)
            self.view().model().item(i).setTextAlignment(Qt.AlignCenter)
        self.blockSignals(False)  # 开启信号
        self.setStyleSheet("""
        QComboBox{
            border:none
        }
        QComboBox QAbstractItemView::item{
            height:25px;
            font-size:15px
        }
        /*
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 30px;
            border-left-width: 0px;
            border-left-color: gray;
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
            }
        QComboBox::down-arrow {
            image: url(media/combo/dd-close.png);
        }
        QComboBox::down-arrow:hover{

        }
        QComboBox::down-arrow:pressed {
            border-image: url(media/combo/dd-open.png);
        }*/
        """)
        self.setView(QListView())


# 管理表格
class ManagerAbstractTable(QTableWidget):
    network_result = pyqtSignal(str)
    # 表头key字典列表
    HEADER_LABELS = []
    NO_EDIT_COLUMNS = []  # 不可编辑的列
    CHECKBOX_COLUMNS = []  # 复选框的列
    COMBOBOX_COLUMNS = []  # 下拉框的列

    def __init__(self, *args, **kwargs):
        super(ManagerAbstractTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self._initialTableMode()
        self.itemChanged.connect(self.changed_table_text)
        self.setFocusPolicy(Qt.NoFocus)
        self.text_ready_to_changed = ''
        self.cellDoubleClicked.connect(self.cell_double_clicked)

    # 设置表格头和列宽模式
    def _initialTableMode(self):
        self.setColumnCount(len(self.HEADER_LABELS) + 1)
        self.setHorizontalHeaderLabels([h[1] for h in self.HEADER_LABELS] + [''])  # 加个空列头
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setVerticalSectionResizeMode()

    # 设置列宽模式【子类重写】
    def setVerticalSectionResizeMode(self):
        pass

    # 单元格被双击时保存未修改前的内容
    def cell_double_clicked(self, row, col):
        if col in self.NO_EDIT_COLUMNS:
            return
        else:
            self.text_ready_to_changed = self.item(row, col).text()  # 保存未修改前的数据

    # 重写clear
    def clear(self):
        super(ManagerAbstractTable, self).clear()
        self._initialTableMode()
        print('阻止表格修改信号')
        self.blockSignals(True)  # 阻止信号

    # 显示内容
    def showRowsContent(self, json_list):
        self.clear()
        self.setRowCount(len(json_list))
        # 设置内容
        for row, row_item in enumerate(json_list):
            print('加入行内容：', row_item)
            for col, couple_item in enumerate(self.HEADER_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.row_item_id = row_item['id']
                else:
                    table_item = QTableWidgetItem(str(row_item[couple_item[0]]))
                if col in self.NO_EDIT_COLUMNS:
                    table_item.setFlags(Qt.ItemIsEnabled)
                if col in self.CHECKBOX_COLUMNS:  # 选择框的列
                    check_box = CheckBox(checked=int(table_item.text()))
                    check_box.check_changed.connect(self.check_button_changed)
                    self.setCellWidget(row, col, check_box)
                # 下拉框控件设置
                for combo_item in self.COMBOBOX_COLUMNS:
                    if col == combo_item[0]:
                        combo_box = ComboBox(couple_items=combo_item[1], current_text=table_item.text())
                        combo_box.text_changed.connect(self.combo_text_changed)
                        self.setCellWidget(row, col, combo_box)
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
        print('恢复表格修改信号')
        self.blockSignals(False)  # 恢复信号

    # 设置最后一列控件
    def setLastColumnWidget(self, widget):
        last_column = len(self.HEADER_LABELS)
        for row in range(self.rowCount()):
            self.setCellWidget(row, last_column, widget)

    # 获取控件所在行和列
    def _get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()

    # 修改表格信息
    def _modify_row_content(self, url, fields):
        print('修改当前管理表格的相关信息：', fields)
        try:
            r = requests.patch(
                url=url,
                headers={
                    'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')
                },
                data=json.dumps(fields)
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
            return {}
        else:
            self.network_result.emit(response['message'])
            return response['data']

    # 复选框选择改变
    def check_button_changed(self, check_widget):
        pass

    # 下拉框选择改变
    def combo_text_changed(self, combo_widget):
        pass

    # 修改表格内容处理
    def changed_table_text(self, item):
        pass


""" 客户端管理相关 """


# 【有效】选择按钮
class ClientTableCheckBox(QWidget):
    network_result = pyqtSignal(str)

    def __init__(self, cid, checked, *args, **kwargs):
        super(ClientTableCheckBox, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        self.check_button = QCheckBox(parent=self)
        self.check_button.cid = cid
        self.check_button.setChecked(checked)
        self.check_button.setMinimumHeight(13)
        layout.addWidget(self.check_button, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        self.check_button.stateChanged.connect(self.change_client_active)

    # 修改客户端有效与否
    def change_client_active(self):
        print('修改有效与否', self.check_button.isChecked())
        try:
            r = requests.patch(
                url=config.SERVER_ADDR + 'basic/clients-maintain/?mc=' + config.app_dawn.value('machine'),
                headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'cid': self.check_button.cid,
                    'is_active': self.check_button.isChecked()
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
        else:
            self.network_result.emit(response['message'])


# 客户端管理表格文字修改控件
class ClientTableTextEdit(QWidget):
    network_result = pyqtSignal(str)

    def __init__(self, cid, text, edit_property, *args, **kwargs):  # cid - customer id 使用控件的数据对象id
        super(ClientTableTextEdit, self).__init__(*args, **kwargs)
        self.edit_property = edit_property
        self.cid = cid
        self.text = text
        layout = QHBoxLayout(margin=0, spacing=1)
        # 编辑框
        self.edit = QLineEdit(parent=self, objectName='textEdit')
        self.edit.setText(text)
        self.edit.setAlignment(Qt.AlignCenter)
        self.edit.setEnabled(False)
        # 操作按钮
        self.button = QPushButton('修改', parent=self, objectName='modifyBtn', clicked=self.edit_current_text, cursor=Qt.PointingHandCursor)
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.setStyleSheet("""
        #textEdit{
            border: none;
        }
        #modifyBtn{
            min-width:30px;
            max-width:30px;
        }
        #dateButton:hover{
            color: rgb(180,130,220)
        }
        """)

    # 修改当前文字
    def edit_current_text(self):
        if self.edit.isEnabled():
            print('发起确定修改的请求')  # 可编辑的情况发起确定修改
            if self._commit_modify():
                self.edit.setEnabled(False)
                self.button.setText('修改')
            else:
                self.edit.setFocus()

        else:
            self.edit.setEnabled(True)
            self.edit.setFocus()
            self.button.setText('确定')

    # 发起修改的请求
    def _commit_modify(self):
        print('请求修改')
        # 获取修改的结果
        text = re.sub(r'\s+', '', self.edit.text())  # 去掉空格
        if not text or text == self.text:  # 没有文字或没有发生变化不做修改
            print('没有文字或没有发生变化不做修改')
            return True
        # 提交修改
        print('客户端%d修改了%s为%s' % (self.cid, self.edit_property, text))
        try:
            r = requests.patch(
                url=config.SERVER_ADDR + 'basic/clients-maintain/?mc=' + config.app_dawn.value('machine'),
                headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'cid': self.cid,
                    self.edit_property: text
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
            return False
        else:
            self.network_result.emit(response['message'])
            return True


# 客户端管理显示表格
class ClientManagerTable(QTableWidget):
    network_result = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(ClientManagerTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()

    # 填充表格客户端数据
    def addClients(self, client_list):
        self.clear()
        self.setRowCount(len(client_list))
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(['序号', '名称', '机器码', '客户端类型', '有效'])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, client_item in enumerate(client_list):
            item_0 = QTableWidgetItem(str(row + 1))
            item_0.setTextAlignment(Qt.AlignCenter)
            item_1 = ClientTableTextEdit(cid=client_item['id'], text=client_item['name'], edit_property='name')
            # 控件网络信号连接
            item_1.network_result.connect(self.emit_network_message)
            # 十分注意!!!管理端不能进行有效与机器码修改，避免超级管理员与数据搜集员之间互相修改，致使客户端无效
            if client_item['is_manager'] is True:
                item_2 = QTableWidgetItem(str(client_item['machine_code']))
                item_4 = QTableWidgetItem('管理端不作修改')
                item_2.setTextAlignment(Qt.AlignCenter)
                item_4.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 2, item_2)
                self.setItem(row, 4, item_4)
            else:  # 非管理端
                item_2 = ClientTableTextEdit(cid=client_item['id'], text=client_item['machine_code'], edit_property='machine_code')
                item_4 = ClientTableCheckBox(cid=client_item['id'], checked=client_item['is_active'])
                # 控件网络信号连接
                item_2.network_result.connect(self.emit_network_message)
                item_4.network_result.connect(self.emit_network_message)
                self.setCellWidget(row, 2, item_2)
                self.setCellWidget(row, 4, item_4)
            client_type = '管理端' if client_item['is_manager'] else '普通端'
            item_3 = QTableWidgetItem(client_type)

            item_3.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 0, item_0)
            self.setCellWidget(row, 1, item_1)
            self.setItem(row, 3, item_3)

    # 踢皮球，直接将信号传出
    def emit_network_message(self, message):
        self.network_result.emit(message)


""" 品种管理相关 """


# 品种管理品种所属组修改控件
class TableComboEditWidget(QWidget):
    network_result = pyqtSignal(str)

    def __init__(self, cid, text, *args, **kwargs):  # cid - customer id 使用控件的数据对象id
        super(TableComboEditWidget, self).__init__(*args, **kwargs)
        self.cid = cid
        layout = QHBoxLayout(margin=0, spacing=1)
        # 显示框
        self.label_show = QLabel(text, parent=self)
        self.label_show.setAlignment(Qt.AlignCenter)
        # 编辑框
        self.combo = QComboBox(parent=self, objectName='combo')
        self.combo.hide()
        # 操作按钮
        self.button = QPushButton('修改', parent=self, objectName='modifyBtn', clicked=self.edit_current_combo, cursor=Qt.PointingHandCursor)
        layout.addWidget(self.label_show)
        layout.addWidget(self.combo)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.setStyleSheet("""
        #combo QAbstractItemView::item{
            height: 22px;
        }
        #modifyBtn{
            min-width:30px;
            max-width:30px;
        }
        #dateButton:hover{
            color: rgb(180,130,220)
        }
        """)
        self.combo.setView(QListView())

    # 改变所属分组
    def edit_current_combo(self):
        if self.combo.isHidden():
            # 获取品种的所有分组
            if self.combo.count() <= 0:
                if not self._get_variety_groups():
                    return
            self.label_show.hide()
            self.combo.show()
            self.button.setText('确定')
        else:
            # 上传设置的分组
            self._commit_modify_group()
            self.combo.hide()
            self.label_show.show()
            self.button.setText('修改')

    # 获取品种的所有分组
    def _get_variety_groups(self):
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'basic/variety-groups/?mc=' + config.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
            return False
        # 填充选择框
        self.combo.clear()
        for group_item in response['data']:
            self.combo.addItem(group_item['name'], group_item['id'])  # 在后续传入所需的数据，就是itemData
        # 选择项居中处理
        # for i in range(self.combo.count()):
        #     self.combo.model().item(i).setTextAlignment(Qt.AlignCenter)
        self.network_result.emit(response['message'])
        return True

    # 上传设置的分组
    def _commit_modify_group(self):
        if self.combo.currentText() == self.label_show.text():
            return
        gid = self.combo.currentData()
        try:
            r = requests.patch(
                url=config.SERVER_ADDR + 'basic/variety/?mc=' + config.app_dawn.value('machine'),
                headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'vid': self.cid,
                    'gid': gid
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
            return
        else:
            self.label_show.setText(self.combo.currentText())
            self.network_result.emit(response['message'])


# 品种管理表格文字修改控件
class TableTextEditWidget(QWidget):
    network_result = pyqtSignal(str)

    def __init__(self, cid, text, edit_property, *args, **kwargs):  # cid - customer id 使用控件的数据对象id
        super(TableTextEditWidget, self).__init__(*args, **kwargs)
        self.edit_property = edit_property
        self.cid = cid
        self.text = text
        layout = QHBoxLayout(margin=0, spacing=1)
        # 编辑框
        self.edit = QLineEdit(parent=self, objectName='textEdit')
        self.edit.setText(text)
        self.edit.setAlignment(Qt.AlignCenter)
        self.edit.setEnabled(False)
        # 操作按钮
        self.button = QPushButton('修改', parent=self, objectName='modifyBtn', clicked=self.edit_current_text, cursor=Qt.PointingHandCursor)
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.setStyleSheet("""
        #textEdit{
            border: none;
        }
        #modifyBtn{
            min-width:30px;
            max-width:30px;
        }
        #dateButton:hover{
            color: rgb(180,130,220)
        }
        """)

    # 修改当前文字
    def edit_current_text(self):
        if self.edit.isEnabled():
            print('发起确定修改的请求')  # 可编辑的情况发起确定修改
            if self._commit_modify():
                self.edit.setEnabled(False)
                self.button.setText('修改')
            else:
                self.edit.setFocus()

        else:
            self.edit.setEnabled(True)
            self.edit.setFocus()
            self.button.setText('确定')

    # 发起修改的请求
    def _commit_modify(self):
        # 获取修改的结果
        text = re.sub(r'\s+', '', self.edit.text())  # 去掉空格
        if not text or text == self.text:  # 没有文字或没有发生变化不做修改
            print('没有文字或没有发生变化不做修改')
            return True
        # 提交修改
        print('品种%d修改了%s为%s' % (self.cid, self.edit_property, text))
        try:
            r = requests.patch(
                url=config.SERVER_ADDR + 'basic/variety/?mc=' + config.app_dawn.value('machine'),
                headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'vid': self.cid,
                    self.edit_property: text
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
            return False
        else:
            self.network_result.emit(response['message'])
            return True


# 品种管理显示表格
class VarietyManagerTable(QTableWidget):
    network_result = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(VarietyManagerTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()

    # 显示数据
    def addVarieties(self, variety_list):
        rows = len(variety_list)
        self.setRowCount(rows)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(['编号', '名称', '英文代码', '所属组'])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for row, variety_item in enumerate(variety_list):
            item_0 = QTableWidgetItem(str(row + 1))
            item_0.setTextAlignment(Qt.AlignCenter)
            item_1 = TableTextEditWidget(cid=variety_item['id'], text=str(variety_item['name']), edit_property='name')
            item_2 = TableTextEditWidget(cid=variety_item['id'], text=str(variety_item['name_en']), edit_property='name_en')
            item_3 = TableComboEditWidget(cid=variety_item['id'], text=str(variety_item['group']))
            # 控件网络信号关联
            item_1.network_result.connect(self.emit_network_message)
            item_2.network_result.connect(self.emit_network_message)
            item_3.network_result.connect(self.emit_network_message)
            self.setItem(row, 0, item_0)
            self.setCellWidget(row, 1, item_1)
            self.setCellWidget(row, 2, item_2)
            self.setCellWidget(row, 3, item_3)

    # 踢皮球，直接将信号传出
    def emit_network_message(self, message):
        self.network_result.emit(message)
