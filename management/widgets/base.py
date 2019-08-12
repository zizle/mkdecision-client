# _*_ coding:utf-8 _*_
"""
base widget in project
Create: 2019-08-07
Author: zizle
"""
from PyQt5.QtWidgets import QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QTimer, Qt, pyqtSignal

class Loading(QLabel):
    clicked = pyqtSignal(bool)

    def __init__(self, *args):
        super(Loading, self).__init__()
        self.click_able = False
        self.loading_text = '数据请求中···'
        self.setText(self.loading_text)
        self.setAlignment(Qt.AlignCenter)
        self.timer = QTimer()
        self.timeout_count = -1
        self.timer.timeout.connect(self.time_out)
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.hide_timer_out)
        self.count_hide = 5
        super().hide()

    def time_out(self):
        self.timeout_count += 1
        self.setText(self.loading_text[:5 + self.timeout_count])
        if self.timeout_count >= 3:
            self.timeout_count = -1

    def hide(self):
        self.timer.stop()
        super().hide()
        self.click_able = False

    def show(self):
        self.setText(self.loading_text)
        self.timer.start(500)
        super().show()
        self.click_able = False

    def no_data(self):
        self.timer.stop()
        self.setText('没有数据.{}秒后可新增'.format(self.count_hide))
        self.hide_timer.start(1000)
        self.click_able = False

    def hide_timer_out(self):
        self.count_hide -= 1
        self.setText('没有数据.{}秒后可新增'.format(self.count_hide))
        if self.count_hide <= 0:
            self.hide_timer.stop()
            self.hide()
            self.count_hide = 5

    def retry(self):
        self.timer.stop()
        self.setText('请求失败.请重试!')
        self.click_able = True

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.click_able:
            self.clicked.emit(True)


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