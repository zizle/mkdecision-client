# _*_ coding:utf-8 _*_
"""
all widgets in data-maintenance module
Update: 2019-07-24
Author: zizle
"""
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QCheckBox, QWidget
from PyQt5.QtCore import pyqtSignal, Qt


class TableCheckBox(QWidget):
    """ checkbox in client info table """
    check_change_signal = pyqtSignal(dict)

    def __init__(self, row, col, option_label, *args):
        super(TableCheckBox, self).__init__(*args)
        v_layout = QVBoxLayout()
        layout = QHBoxLayout()
        self.check_box = QCheckBox()
        self.check_box.setMinimumHeight(15)
        self.rowIndex = row
        self.colIndex = col
        self.option_label = option_label
        layout.addWidget(self.check_box, alignment=Qt.AlignCenter)
        self.check_box.stateChanged.connect(self.check_state_changed)
        v_layout.addLayout(layout)
        self.setLayout(v_layout)

    def check_state_changed(self):
        self.check_change_signal.emit({'row': self.rowIndex, 'col': self.colIndex, 'checked': self.check_box.isChecked(), 'option_label': self.option_label})

    def setChecked(self, tag):
        self.check_box.setChecked(tag)

