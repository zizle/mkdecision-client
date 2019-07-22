# _*_ coding:utf-8 _*_
# author: zizle
# Date: 20190510
"""首页公示栏"""
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView, QPushButton, QTableWidgetItem, QHeaderView
from widgets.public import TableWidgetItem
from PyQt5.QtGui import QMouseEvent, QBrush, QColor, QCursor, QFont
from PyQt5.QtCore import Qt


class Bulletin(QTableWidget):
    def __init__(self, *args):
        super(Bulletin, self).__init__(*args)
        self.__init_ui()

    def __init_ui(self):
        style = """
        QTableWidget{
            background-color:rgb(240,240,240);
            border: 1px solid rgb(220,220,220);
        }
        QTableWidget::item{
            border-bottom: 1px solid rgb(200,200,200);
            cursor:hand;
        }
        QScrollBar:vertical
        {
            width:8px;
            background:rgba(0,0,0,0%);
            margin:0px,0px,0px,0px;
            /*留出8px给上面和下面的箭头*/
            padding-top:8px;
            padding-bottom:8px;
        }
        QScrollBar::handle:vertical
        {
            width:8px;
            background:rgba(0,0,0,8%);
            /*滚动条两端变成椭圆*/
            border-radius:4px;

        }
        QScrollBar::handle:vertical:hover
        {
            width:8px;
            /*鼠标放到滚动条上的时候，颜色变深*/
            background:rgba(0,0,0,40%);
            border-radius:4px;
            min-height:20;
        }
        QScrollBar::add-line:vertical
        {
            height:9px;width:8px;
            /*设置下箭头*/
            border-image:url(media/scroll/3.png);
            subcontrol-position:bottom;
        }
        QScrollBar::sub-line:vertical 
        {
            height:9px;width:8px;
            /*设置上箭头*/
            border-image:url(media/scroll/1.png);
            subcontrol-position:top;
        }
        QScrollBar::add-line:vertical:hover
        /*当鼠标放到下箭头上的时候*/
        {
            height:9px;width:8px;
            border-image:url(media/scroll/4.png);
            subcontrol-position:bottom;
        }
        QScrollBar::sub-line:vertical:hover
        /*当鼠标放到下箭头上的时候*/
        {
            height:9px;
            width:8px;
            border-image:url(media/scroll/2.png);
            subcontrol-position:top;
        }
        """
        self.setMouseTracking(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
        self.setFocusPolicy(Qt.NoFocus)
        self.setColumnCount(2)  # 列数
        self.setShowGrid(False)  # 不显示网格
        # self.setSelectionBehavior(1)  # 一次选中一行
        self.setFocusPolicy(0)  # 选中不出现虚框
        self.horizontalHeader().setVisible(False)  # 横向表头不可见
        self.verticalHeader().setVisible(False)  # 纵向表头不可见
        self.setStyleSheet(style)

    def leaveEvent(self, *args, **kwargs):
        """鼠标离开控件"""
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                self.item(row, col).setForeground(QBrush(QColor(0, 0, 0)))  # 改变了其他的item字体色

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        # 获取当前这个item
        current_item = self.itemAt(event.pos())
        if current_item:
            row = current_item.row()
            for item in [self.item(row, col) for col in range(self.columnCount())]:
                # item.setBackground(QBrush(QColor(200, 200, 200)))  # 改变了当前的item背景色
                item.setForeground(QBrush(QColor(255, 10, 20)))  # 改变了当前的item字体色
            for other_row in range(self.rowCount()):
                if other_row == row:
                    continue
                for other_item in [self.item(other_row, col) for col in range(self.columnCount())]:
                    # other_item.setBackground(QBrush(QColor(240, 240, 240)))  # 改变了其他的item背景色
                    other_item.setForeground(QBrush(QColor(0, 0, 0)))  # 改变了其他的item字体色

    def setDataContents(self, data, keys, button_col=-1):
        """设置内容"""
        if not data:
            return
        self.setRowCount(len(data))
        self.setColumnCount(len(keys))
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if col == button_col:
                    item = QTableWidgetItem("查看")
                    item.file = data[row]["file"]
                    item.content = data[row]["content"]
                else:
                    item = QTableWidgetItem(str(data[row][keys[col]]))
                    if col == self.columnCount() - 1:
                        font = QFont()
                        font.setPointSize(8)
                        item.setFont(QFont(font))
                    else:
                        font = QFont()
                        font.setPointSize(10)
                        item.setFont(QFont(font))
                # if not col:
                #     item = TableWidgetItem(data[row]["file"], str(data[row]["name"]))
                # else:
                #     item = TableWidgetItem(data[row]["file"], str(data[row]["create_time"]))
                self.setItem(row, col, item)
        self.setRiseMode()

    def setRiseMode(self):
        self.horizontalHeader().setSectionResizeMode(1)  # 自适应大小
        self.horizontalHeader().setSectionResizeMode(1, 3)  # 第1列随文字宽度
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 第1列随文字宽度


