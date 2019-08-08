# _*_ coding:utf-8 _*_
"""
base widget in project
Create: 2019-08-07
Author: zizle
"""
from PyQt5.QtWidgets import QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QTimer, Qt

class Loading(QLabel):
    def __init__(self, *args):
        super(Loading, self).__init__()
        self.loading_text = '数据请求中···'
        self.setText(self.loading_text)
        self.setAlignment(Qt.AlignCenter)
        self.timer = QTimer()
        self.timeout_count = -1
        self.timer.timeout.connect(self.time_out)
        super().hide()

    def time_out(self):
        self.timeout_count += 1
        self.setText(self.loading_text[:5 + self.timeout_count])
        if self.timeout_count >= 3:
            self.timeout_count = -1


    def start(self):
        self.timer.start(500)

    def stop(self):
        self.timer.stop()

    def hide(self):
        self.stop()
        super().hide()

    def show(self):
        self.start()
        super().show()


class TableShow(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(TableShow, self).__init__(*args)
        self.verticalHeader().setVisible(False)

    def show_content(self, content, keys):
        if not isinstance(content, list):
            raise ValueError('content must be a list.')
        for item in content:
            if not isinstance(item, dict):
                raise ValueError('the item in content must be a dict.')
            row = len(content)
            self.setRowCount(row)
            self.setColumnCount(len(keys))  # 列数
            labels = []
            set_keys = []
            for key_label in keys:
                set_keys.append(key_label[0])
                labels.append(key_label[1])
            self.setHorizontalHeaderLabels(labels)
            self.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
            self.horizontalHeader().setSectionResizeMode(0, 3)  # 第1列随文字宽度
            self.horizontalHeader().setSectionResizeMode(self.columnCount()-1, 3)  # 最后1列随文字宽度
            for row in range(self.rowCount()):
                for col in range(self.columnCount()):
                    label_key = set_keys[col]
                    if label_key == 'to_look':
                        item = QTableWidgetItem('查看')
                        item.unum = content[row]['id']
                        item.unique = content[row]['to_look']
                    else:
                        item = QTableWidgetItem(str(content[row][label_key]))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.setItem(row, col, item)