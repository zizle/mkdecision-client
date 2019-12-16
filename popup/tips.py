# _*_ coding:utf-8 _*_
# __Author__： zizle


from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QGridLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap


# 错误提示弹窗
class InformationPopup(QDialog):
    def __init__(self, title='提示', message='在这里设置提示信息', *args, **kwargs):
        super(InformationPopup, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        self.message = QLabel(message)
        layout.addWidget(self.message, alignment=Qt.AlignCenter)
        self.setWindowTitle(title)
        self.setFixedSize(250,200)
        self.setLayout(layout)


# 警示信息
class WarningPopup(QDialog):
    confirm_button = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        super(WarningPopup, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        self.setWindowTitle('注意')
        ico_label = QLabel()
        pix = QPixmap('media/tips/warning.png')
        ico_label.setPixmap(pix)
        ico_label.setScaledContents(True)
        layout.addWidget(ico_label, 0, 0)
        layout.addWidget(QLabel('删除将不可恢复!', styleSheet='color:rgb(255,10,10);font-weight:bold'), 0, 1, 1, 2)
        layout.addWidget(QPushButton('确定', clicked=self.confirm), 1, 1)
        layout.addWidget(QPushButton('取消', clicked=self.cancel), 1, 2)
        self.setLayout(layout)

    def confirm(self):
        self.confirm_button.emit(True)

    def cancel(self):
        self.close()

