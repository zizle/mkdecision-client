# _*_ coding:utf-8 _*_
# company: RuiDa Futures
# author: zizle
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QBrush, QColor, QCursor


class CustomTableWidget(QTableWidget):
    def leaveEvent(self, *args, **kwargs):
        """鼠标离开控件"""
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                self.item(row, col).setBackground(QBrush(QColor(240, 240, 240)))  # 改变了其他的item背景色

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        # 获取当前这个item
        current_item = self.itemAt(event.pos())
        if current_item:
            row = current_item.row()
            for item in [self.item(row, col) for col in range(self.columnCount())]:
                item.setBackground(QBrush(QColor(200, 200, 200)))  # 改变了当前的item背景色
            for other_row in range(self.rowCount()):
                if other_row == row:
                    continue
                for other_item in [self.item(other_row, col) for col in range(self.columnCount())]:
                    other_item.setBackground(QBrush(QColor(240, 240, 240)))  # 改变了其他的item背景色


class ListWidget(QListWidget):
    def __init__(self):
        super(ListWidget, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        style_sheet = """
        ListWidget {
            font-size:13px;
            border:none;
            background-color: rgb(190,24,24);
            color:#FFFFFF;
            outline:0px;
        }
        QListWidget::item {
            height: 30px;
            border:1px solid rgb(190,24,24);
        }
        QListWidget::Item:hover{
            background:rgb(190,24,24); 
        }
        QListWidget::item:selected{
            background:rgb(240,240,240); 
            color:#000; 
            border-right:none;
        }
        """
        self.setStyleSheet(style_sheet)

    def init_style(self, item):
        item.setSelected(True)

    def setHeight(self, height):
        self.setFixedHeight(height)

    def setWidth(self, width):
        self.setFixedWidth(width)
        # self.setMinimumWidth(width)
        # self.setMaximumWidth(width)


class TableWidget(QWidget):
    page_control_signal = pyqtSignal(list)
    cell_clicked_signal = pyqtSignal(list)
    set_height_signal = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super(TableWidget, self).__init__(*args, **kwargs)
        self.hasPageController = False
        self.__init_ui()

    def __init_ui(self):
        style_sheet = """
        QTableWidget {
            border:none;
            background-color: rgb(240,240,240);
        }  
        QPushButton{
            max-width: 18ex;
            max-height: 6ex;
            font-size: 11px;
            background-color: rgb(240,240,240);
            border: 1px solid rgb(210,210,210);
            padding: 2px 10px;
            cursor: pointer;
        }
        """
        self.__layout = QVBoxLayout(margin=0)
        self.table = CustomTableWidget()  # 表格
        self.table.setMouseTracking(True)  # 鼠标检测
        self.table.cellClicked.connect(self.__table_item_clicked)  # 单元格点击
        self.table.setSelectionBehavior(1)  # 点击选中为一行
        self.table.horizontalHeader().setStyleSheet("""
        QHeaderView::section {
            background-color:rgb(187,214,227);
            border: 1px solid #6c6c6c;
            border-left: 0px;
            height: 30px;
            font-weight:bold;
            }
        """)
        self.__layout.addWidget(self.table)
        self.setLayout(self.__layout)
        self.setStyleSheet(style_sheet)

    def __home_page(self):
        """点击首页信号"""
        self.page_control_signal.emit(["home", self.curPage.text()])

    def __pre_page(self):
        """点击上一页信号"""
        self.page_control_signal.emit(["pre", self.curPage.text()])

    def __next_page(self):
        """点击下一页信号"""
        self.page_control_signal.emit(["next", self.curPage.text()])

    def __final_page(self):
        """尾页点击信号"""
        self.page_control_signal.emit(["final", self.curPage.text()])

    def __confirm_skip(self):
        """跳转页码确定"""
        if not self.skipPage.text():
            return
        self.page_control_signal.emit(["confirm", self.skipPage.text()])

    def __fixed_cur_page_width(self):
        """当前页码发生改变固定控件宽度"""
        cur_page = self.curPage.text()
        length = len(cur_page) if cur_page else 0
        self.curPage.setFixedWidth(length * 10)
        if cur_page and int(cur_page) == 1:
            self.homePage.setEnabled(False)
            self.prePage.setEnabled(False)
        else:
            self.homePage.setEnabled(True)
            self.prePage.setEnabled(True)
        if cur_page and int(cur_page) == self.totalPage():
            self.finalPage.setEnabled(False)
            self.nextPage.setEnabled(False)
        else:
            self.finalPage.setEnabled(True)
            self.nextPage.setEnabled(True)

    def __table_item_clicked(self, row, col):
        """表格Item被点击"""
        self.cell_clicked_signal.emit([row, col])

    def columnCount(self):
        return self.table.columnCount()

    def item(self, row, col):
        return self.table.item(row, col)

    def removePageController(self):
        """去掉页码控制器"""
        self.homePage.close()
        self.prePage.close()
        self.curPage.close()
        self.nextPage.close()
        self.finalPage.close()
        self.totalPageLabel.close()
        self.skipLable_0.close()
        self.skipPage.close()
        self.skipLabel_1.close()
        self.confirmSkip.close()
        del self.homePage
        del self.prePage
        del self.curPage
        del self.nextPage
        del self.finalPage
        del self.totalPageLabel
        del self.skipLable_0
        del self.skipPage
        del self.skipLabel_1
        self.control_layout.addWidget(self.confirmSkip)
        self.__layout.removeItem(self.control_layout)
        self.hasPageController = False

    def rowCount(self):
        return self.table.rowCount()

    def setCellWidget(self, *args, **kwargs):
        self.table.setCellWidget(*args, **kwargs)

    def setDataContents(self, data, keys, id_col=-1, id_key=None):
        """
        设置表格内容, 并根据内容自适应调整固定高度，以撑开整个窗口，使得窗口滚动条显示作用，表格不出现滚动条
        :param cur_page: 当前页码
        :param data: 列表嵌套字典格式，为每一行内容
        :param keys: 类别嵌套字典，表格的列表头
        :param id_col: 点击响应的表格列，这个TableItem会加入对应url
        :param id_key: 当有id_col的时候必须要有id_key
        :return: None
        """
        if id_col != -1:
            if not id_key:
                return
        row = len(data)
        self.table.setRowCount(row)
        self.table.setColumnCount(len(keys))  # 列数
        labels = []
        set_keys = []
        for key_label in keys:
            set_keys.append(key_label[0])
            labels.append(key_label[1])
        self.setHorizontalHeaderLabels(labels)
        self.setSectionResizeMode()  # 自适应大小
        for r in range(row):
            for c in range(self.table.columnCount()):
                if c == id_col:
                    item = TableWidgetItem(data[r][id_key], str(data[r][set_keys[c]]))
                else:
                    item = QTableWidgetItem(str(data[r][set_keys[c]]))
                item.setTextAlignment(132)
                self.table.setItem(r, c, item)
        self.set_height_signal.emit(35 + row * 32)

    def setEditTriggers(self, edit=True):
        """表格是否可编辑"""
        if edit:
            return
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def setHorizontalHeaderLabels(self, labels):
        """设置表格的横向标题"""
        self.table.setHorizontalHeaderLabels(labels)

    def setMouseTracking(self, bool):
        self.table.setMouseTracking(bool)

    def setPageController(self, page):
        """设置页码控制器"""
        self.control_layout = QHBoxLayout()
        self.homePage = QPushButton("首页")
        self.prePage = QPushButton("<上一页")
        self.curPage = QLineEdit("")
        self.curPage.setStyleSheet("background-color:rgb(240,240,240);font-size:14px;border:none;color:rgb(0,0,0)")
        self.curPage.setAlignment(Qt.AlignCenter)
        self.curPage.setEnabled(False)  # 不可编辑,看起来像QLabel
        self.curPage.textChanged.connect(self.__fixed_cur_page_width) # 文字变化改变宽度, 更想QLabel
        self.nextPage = QPushButton("下一页>")
        self.finalPage = QPushButton("尾页")
        self.totalPageLabel = QLabel("共" + str(page) + "页")
        self.skipLable_0 = QLabel("跳到")
        self.skipPage = QLineEdit()
        self.skipPage.setFixedWidth(25)
        self.skipLabel_1 = QLabel("页")
        self.confirmSkip = QPushButton("确定")
        self.homePage.clicked.connect(self.__home_page)
        self.prePage.clicked.connect(self.__pre_page)
        self.nextPage.clicked.connect(self.__next_page)
        self.finalPage.clicked.connect(self.__final_page)
        self.confirmSkip.clicked.connect(self.__confirm_skip)
        self.control_layout.addStretch(1)
        # 设置手型
        self.homePage.setCursor(QCursor(Qt.PointingHandCursor))
        self.prePage.setCursor(QCursor(Qt.PointingHandCursor))
        self.nextPage.setCursor(QCursor(Qt.PointingHandCursor))
        self.finalPage.setCursor(QCursor(Qt.PointingHandCursor))
        self.confirmSkip.setCursor(QCursor(Qt.PointingHandCursor))
        self.control_layout.addWidget(self.homePage)
        self.control_layout.addWidget(self.prePage)
        self.control_layout.addWidget(self.curPage)
        self.control_layout.addWidget(self.nextPage)
        self.control_layout.addWidget(self.finalPage)
        self.control_layout.addWidget(self.totalPageLabel)
        self.control_layout.addWidget(self.skipLable_0)
        self.control_layout.addWidget(self.skipPage)
        self.control_layout.addWidget(self.skipLabel_1)
        self.control_layout.addWidget(self.confirmSkip)
        self.control_layout.addStretch(1)
        self.__layout.addLayout(self.control_layout)
        self.hasPageController = True

    def setRowCount(self, count):
        self.table.setRowCount(count)

    def setSectionResizeMode(self):
        """表格宽度自适应"""
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 列自适应
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 第一列根据文字宽自适应
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 行自适应

    def setTableTotalPageCount(self, page):
        """改变表格的总页码"""
        self.totalPageLabel.setText("共" + str(page) + "页")

    def setVerticalHeaderVisible(self, flag):
        if not flag:
            self.table.verticalHeader().setVisible(False)

    def totalPage(self):
        """返回当前总页数"""
        return int(self.totalPageLabel.text()[1:-1])


class TableWidgetItem(QTableWidgetItem):
    def __init__(self, id_key, *args):
        super(TableWidgetItem, self).__init__(*args)
        self.id_key = id_key
