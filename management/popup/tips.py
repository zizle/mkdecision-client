# _*_ coding:utf-8 _*_
# __Author__： zizle


from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


# 错误提示弹窗
class InformationPopup(QDialog):
    def __init__(self, title='提示', message='在这里设置提示信息', *args, **kwargs):
        super(InformationPopup, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        self.message = QLabel(message)
        layout.addWidget(self.message, alignment=Qt.AlignCenter)
        self.setWindowTitle(title)
        self.setLayout(layout)
