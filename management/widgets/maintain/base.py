# _*_ coding:utf-8 _*_
"""

Create: 2019-08-09
Author: zizle
"""
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt

from piece.base import TableCheckBox

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

