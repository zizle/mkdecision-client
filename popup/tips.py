# _*_ coding:utf-8 _*_
# __Author__： zizle


from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap


# 提示信息
class InformationPopup(QDialog):
    def __init__(self, title='提示', message='在这里设置提示信息', *args, **kwargs):
        super(InformationPopup, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        self.setWindowTitle(title)
        ico_label = QLabel()
        ico_label.setFixedSize(48,48)
        pix = QPixmap('media/tips/information.png')
        ico_label.setPixmap(pix)
        ico_label.setScaledContents(True)
        layout.addWidget(ico_label, 0, 0)
        layout.addWidget(QLabel(message, styleSheet='color:rgb(10,10,10);font-weight:bold'), 0, 1)
        layout.addWidget(QPushButton('确定', clicked=self.close, cursor=Qt.PointingHandCursor), 1, 1)
        self.setLayout(layout)
        self.setMaximumWidth(320)
        self.setStyleSheet("""
        QPushButton{
            border: none;
            font-size:14px;
            background-color: rgb(74,115,134);
            padding:5px;
            color:rgb(254,254,254)
        }
        """)


# 警示信息
class WarningPopup(QDialog):
    confirm_button = pyqtSignal(bool)

    def __init__(self, message='删除将不可恢复!', *args, **kwargs):
        super(WarningPopup, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        self.setWindowTitle('注意')
        ico_label = QLabel()
        pix = QPixmap('media/tips/warning.png')
        ico_label.setPixmap(pix)
        ico_label.setScaledContents(True)
        layout.addWidget(ico_label, 0, 0)
        layout.addWidget(QLabel(message, styleSheet='color:rgb(255,10,10);font-weight:bold'), 0, 1, 1, 2)
        layout.addWidget(QPushButton('确定', clicked=self.confirm), 1, 1)
        layout.addWidget(QPushButton('取消', clicked=self.cancel), 1, 2)
        self.setLayout(layout)

    def confirm(self):
        self.confirm_button.emit(True)

    def cancel(self):
        self.close()

