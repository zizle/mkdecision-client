# _*_ coding:utf-8 _*_
# __Author__： zizle

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton,QTableWidget, QAbstractItemView,\
    QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal, QPoint


__all__ = ['TableCheckBox', 'ManageTable']  # 别的模块 import * 时控制可导入的类

""" 管理信息的表格及其相关控件 """


# 【有效】勾选按钮
class TableCheckBox(QWidget):
    check_activated = pyqtSignal(QWidget)

    def __init__(self, checked=False, *args, **kwargs):
        super(TableCheckBox, self).__init__(*args, **kwargs)
        self.check_box = QCheckBox(checked=checked)
        self.check_box.setMinimumHeight(14)
        layout = QVBoxLayout()
        layout.addWidget(self.check_box, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        self.check_box.stateChanged.connect(lambda: self.check_activated.emit(self))


# 【编辑】按钮
class EditButton(QPushButton):
    button_clicked = pyqtSignal(QPushButton)

    def __init__(self, *args, **kwargs):
        super(EditButton, self).__init__(*args, **kwargs)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(lambda: self.button_clicked.emit(self))
        self.setObjectName('tableEdit')
        self.setStyleSheet("""
        #tableEdit{
            border: none;
            padding: 1px 8px;
            color: rgb(100,200,240);
        }
        #tableEdit:hover{
            color: rgb(240,200,100)
        }
        """)


# 信息管理的表格，最后一列[编辑]按钮
class ManageTable(QTableWidget):
    network_result = pyqtSignal(str)
    KEY_LABELS = []
    CHECK_COLUMNS = []

    def __init__(self, *args, **kwargs):
        super(ManageTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.setFocusPolicy(Qt.NoFocus)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # 设置表格数据
    def setRowContents(self, row_list):
        self.resetTableMode(len(row_list))
        for row, user_item in enumerate(row_list):
            for col, header in enumerate(self.KEY_LABELS):
                if col == 0:
                    table_item = QTableWidgetItem(str(row + 1))
                    table_item.id = user_item[header[0]]
                else:
                    table_item = QTableWidgetItem(str(user_item[header[0]]))
                if col in self.CHECK_COLUMNS:
                    check_box = TableCheckBox(checked=user_item[header[0]])
                    check_box.check_activated.connect(self.check_box_changed)
                    self.setCellWidget(row, col, check_box)
                table_item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, table_item)
                # 增加【编辑】按钮
                if col == len(self.KEY_LABELS) - 1:
                    edit_button = EditButton('编辑')
                    edit_button.button_clicked.connect(self.edit_button_clicked)
                    self.setCellWidget(row, col + 1, edit_button)

    # 选择框状态发生改变
    def check_box_changed(self, check_box):
        pass

    # 编辑框点击
    def edit_button_clicked(self, edit_button):
        pass

    # 获取控件所在行和列
    def get_widget_index(self, widget):
        index = self.indexAt(QPoint(widget.frameGeometry().x(), widget.frameGeometry().y()))
        return index.row(), index.column()

    # 填充数据前初始化表格
    def resetTableMode(self, row_count):
        self.clear()
        self.setRowCount(row_count)
        self.setColumnCount(len(self.KEY_LABELS) + 1)
        self.setHorizontalHeaderLabels([header[1] for header in self.KEY_LABELS] + [''])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)