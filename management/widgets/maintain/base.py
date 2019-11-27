# _*_ coding:utf-8 _*_
"""

Create: 2019-08-09
Author: zizle
"""
import re
import json
import requests
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QPushButton,\
    QComboBox, QLabel, QListView
from PyQt5.QtCore import Qt
import config
from piece.base import TableCheckBox


# 品种管理品种所属组修改控件
class TableComboEditWidget(QWidget):
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
                headers=config.CLIENT_HEADERS,
                cookies=config.app_dawn.value('cookies')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception:
            return False
        # 填充选择框
        self.combo.clear()
        for group_item in response['data']:
            self.combo.addItem(group_item['name'], group_item['id'])  # 在后续传入所需的数据，就是itemData
        # 选择项居中处理
        # for i in range(self.combo.count()):
        #     self.combo.model().item(i).setTextAlignment(Qt.AlignCenter)
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
        except Exception:
            return
        else:
            self.label_show.setText(self.combo.currentText())


# 品种管理表格文字修改控件
class TableTextEditWidget(QWidget):
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
        except Exception:
            return False
        else:
            return True







# 品种管理显示表格
class VarietyManagerTable(QTableWidget):
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
            self.setItem(row, 0, item_0)
            self.setCellWidget(row, 1, item_1)
            self.setCellWidget(row, 2, item_2)
            self.setCellWidget(row, 3, item_3)





















class TableShow(QTableWidget):
    def __init__(self, *args):
        super(TableShow, self).__init__(*args)
        self.verticalHeader().setVisible(False)

    def show_content(self, contents, header_couple, show='file'):
        if show not in ['file', 'content']:
            raise ValueError('table can not show this content.')
        if not isinstance(contents, list):
            raise ValueError('content must be a list.')
        row = len(contents)
        self.setRowCount(row)
        self.setColumnCount(len(header_couple))  # 列数
        labels = []
        set_keys = []
        for key_label in header_couple:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        self.setHorizontalHeaderLabels(labels)
        self.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
        self.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
        self.horizontalHeader().setSectionResizeMode(self.columnCount()-1, 3)  # 最后1列随文字宽度
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if col == 0:
                    item = QTableWidgetItem(str(row + 1))
                else:
                    label_key = set_keys[col]
                    if label_key == 'is_active':
                        checkbox = TableCheckBox(row=row, col=col, option_label=label_key)
                        checkbox.setChecked(int(contents[row][label_key]))
                        checkbox.clicked_changed.connect(self.update_item_info)
                        self.setCellWidget(row, col, checkbox)
                    if label_key == 'to_look':
                        item = QTableWidgetItem('查看')
                        item.title = contents[row]['title']
                        if show == 'file':
                            item.file = contents[row]['file']
                        elif show == 'content':
                            item.content = contents[row]['content']
                        else:
                            pass
                    else:
                        item = QTableWidgetItem(str(contents[row][label_key]))
                item.setTextAlignment(Qt.AlignCenter)
                item.content_id = contents[row]['id']
                self.setItem(row, col, item)

    def clear(self):
        super().clear()
        self.setRowCount(0)
        self.setColumnCount(0)

    def update_item_info(self, signal):
        print('widgets.maintain.base.py',signal)


class ContentShowTable(QTableWidget):
    def __init__(self, *args):
        super(ContentShowTable, self).__init__(*args)
        self.verticalHeader().setVisible(False)

    def set_contents(self, contents, header_couple):
        row = len(contents)
        self.setRowCount(row)
        self.setColumnCount(len(header_couple))  # 列数
        labels = []
        set_keys = []
        for key_label in header_couple:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        self.setHorizontalHeaderLabels(labels)
        self.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
        self.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
        self.horizontalHeader().setSectionResizeMode(self.columnCount()-1, 3)  # 第1列随文字宽度
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if col == 0:
                    item = QTableWidgetItem(str(row + 1))
                else:
                    label_key = set_keys[col]
                    if label_key == 'is_active':
                        checkbox = TableCheckBox(row=row, col=col, option_label=label_key)
                        checkbox.setChecked(int(contents[row][label_key]))
                        checkbox.clicked_changed.connect(self.update_item_info)
                        self.setCellWidget(row, col, checkbox)
                    if label_key == 'to_look':
                        item = QTableWidgetItem('查看')
                        item.content = contents[row]['content']
                    else:
                        item = QTableWidgetItem(str(contents[row][set_keys[col]]))
                item.setTextAlignment(Qt.AlignCenter)
                item.content_id = contents[row]['id']
                self.setItem(row, col, item)

    def clear(self):
        super().clear()
        self.setRowCount(0)
        self.setColumnCount(0)

    def update_item_info(self, signal):
        print('widgets.maintain.base.py',signal)


class FileShowTable(QTableWidget):
    def __init__(self):
        super(FileShowTable, self).__init__()
        self.verticalHeader().setVisible(False)

    def set_contents(self, contents, header_couple):
        row = len(contents)
        self.setRowCount(row)
        self.setColumnCount(len(header_couple))  # 列数
        labels = []
        set_keys = []
        for key_label in header_couple:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        self.setHorizontalHeaderLabels(labels)
        self.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
        self.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
        self.horizontalHeader().setSectionResizeMode(self.columnCount() - 1, 3)  # 最后1列随文字宽度
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if col == 0:
                    item = QTableWidgetItem(str(row + 1))
                else:
                    label_key = set_keys[col]
                    if label_key == 'is_active':
                        checkbox = TableCheckBox(row=row, col=col, option_label=label_key)
                        checkbox.setChecked(int(contents[row][label_key]))
                        checkbox.clicked_changed.connect(self.update_item_info)
                        self.setCellWidget(row, col, checkbox)
                    if label_key == 'to_look':
                        item = QTableWidgetItem('查看')
                        item.file = contents[row]['file']
                        item.name = contents[row]['title']
                    else:
                        item = QTableWidgetItem(str(contents[row][set_keys[col]]))
                item.setTextAlignment(Qt.AlignCenter)
                item.content_id = contents[row]['id']
                self.setItem(row, col, item)

    def clear(self):
        super().clear()
        self.setRowCount(0)
        self.setColumnCount(0)

    def update_item_info(self, signal):
        print('widgets.maintain.base.py',signal)

