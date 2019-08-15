# _*_ coding:utf-8 _*_
"""
Create: 2019-08-15
Author: zizle
"""
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont

class BulletinTable(QTableWidget):
    def __init__(self, *args):
        super(BulletinTable, self).__init__(*args)
        # table style
        self.setMouseTracking(True)
        self.setShowGrid(False)  # no grid
        self.setFocusPolicy(0)  # No empty box appears in the selection
        self.setSelectionMode(QAbstractItemView.NoSelection)  # hold the style(exp:font color)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # no edit
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setStyleSheet("""
        QTableWidget{
            background-color:rgb(255,255,255);
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
        """)

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

    def show_content(self, contents, header_couple):
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
        self.horizontalHeader().setSectionResizeMode(1, 3)  # 第1列随文字宽度
        self.horizontalHeader().setSectionResizeMode(self.columnCount() - 1, 3)  # 最后1列随文字宽度
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                label_key = set_keys[col]
                if label_key == 'to_look':
                    item = QTableWidgetItem('查看')
                    item.title = contents[row]['title']
                    item.file = contents[row]['file']
                    item.content = contents[row]["content"]
                else:
                    item = QTableWidgetItem(str(contents[row][label_key]))
                font = QFont()
                if col == self.columnCount()-1:
                    size = 8
                    item.setFont(QFont(font))
                else:
                    size = 10
                font.setPointSize(size)
                item.setFont(QFont(font))
                if col == 0:
                    pass
                else:
                    item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, item)