# _*_ coding:utf-8 _*_
# company: RuiDa Futures
# author: zizle
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDateEdit, QPushButton, QFrame
from PyQt5.QtCore import QRect, QDate, pyqtSignal, Qt
from PyQt5.QtGui import QCursor


class Calendar(QWidget):
    controller = pyqtSignal(list)
    click_date = pyqtSignal(QDate)

    def __init__(self):
        super(Calendar, self).__init__()
        self.__dateItems = []
        self.__init_ui()

    def __init_ui(self):
        layout = QVBoxLayout(spacing=10, margin=0)
        # 头布局
        self.headers_layout = QHBoxLayout()
        self.date = QDate.currentDate()  # 整个日历的date属性,获取日历当前的date
        self.date_edit = QDateEdit(self.date)
        self.date_edit.setStyleSheet("""
        QDateEdit{
            border:none;
            height:22px;
            background-color:rgb(240,240,240);
        }
        QDateEdit::drop-down{
           image:url(media/drop-down.png);
        }""")
        self.date_edit.setDisplayFormat("yyyy年MM月dd日")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.dateChanged.connect(self.date_edit_changed)
        self.date_edit.setCursor(QCursor(Qt.PointingHandCursor))
        back_today = QPushButton("回到今日")
        back_today.setCursor(QCursor(Qt.PointingHandCursor))
        back_today.setStyleSheet("border:1px solid rgb(208,177,133);padding:5px 15px;margin-left:15px;")
        back_today.clicked.connect(self.back_today_clicked)
        self.headers_layout.addWidget(self.date_edit)
        self.headers_layout.addWidget(back_today)
        self.headers_layout.addStretch()
        # 内容布局
        contents_layout = QHBoxLayout()
        last_week = QPushButton("< 上周")
        last_week.setCursor(QCursor(Qt.PointingHandCursor))
        last_week.setStyleSheet("border: none;font-size: 12px;font-weight:bold")
        last_week.clicked.connect(self.last_week_clicked)
        # 分割线1
        splitter_line_0 = QFrame()
        splitter_line_0.setEnabled(True)
        splitter_line_0.setGeometry(QRect(110, 170, 3, 61))
        splitter_line_0.setFrameShape(QFrame.VLine)
        splitter_line_0.setFrameShadow(QFrame.Sunken)
        # 分割线2
        splitter_line_1 = QFrame()
        splitter_line_1.setEnabled(True)
        splitter_line_1.setGeometry(QRect(110, 170, 3, 61))
        splitter_line_1.setFrameShape(QFrame.VLine)
        splitter_line_1.setFrameShadow(QFrame.Sunken)
        next_week = QPushButton("下周 >")
        next_week.setCursor(QCursor(Qt.PointingHandCursor))
        next_week.setStyleSheet("border: none;font-size: 12px;font-weight:bold")
        next_week.clicked.connect(self.next_week_clicked)
        contents_layout.addWidget(last_week)
        contents_layout.addWidget(splitter_line_0)
        current_day = QDate.currentDate()  # 当前时间
        sunday = self.__get_sunday(current_day)  # 获取前日期所在周的周日
        monday = sunday.addDays(1)
        tuesday = sunday.addDays(2)
        wednesday = sunday.addDays(3)
        thursday = sunday.addDays(4)
        friday = sunday.addDays(5)
        saturday = sunday.addDays(6)
        self.date_btn_7 = DatePushButtonItem(sunday, str(sunday.day()) + "\n周日")
        self.date_btn_1 = DatePushButtonItem(monday, str(monday.day()) + "\n周一")
        self.date_btn_2 = DatePushButtonItem(tuesday, str(tuesday.day()) + "\n周二")
        self.date_btn_3 = DatePushButtonItem(wednesday, str(wednesday.day()) + "\n周三")
        self.date_btn_4 = DatePushButtonItem(thursday, str(thursday.day()) + "\n周四")
        self.date_btn_5 = DatePushButtonItem(friday, str(friday.day()) + "\n周五")
        self.date_btn_6 = DatePushButtonItem(saturday, str(saturday.day()) + "\n周六")
        self.__dateItems.append(self.date_btn_7)
        self.__dateItems.append(self.date_btn_1)
        self.__dateItems.append(self.date_btn_2)
        self.__dateItems.append(self.date_btn_3)
        self.__dateItems.append(self.date_btn_4)
        self.__dateItems.append(self.date_btn_5)
        self.__dateItems.append(self.date_btn_6)
        # 改变今日的样式
        self.__today_style_change()
        contents_layout.addWidget(self.date_btn_7)
        contents_layout.addWidget(self.date_btn_1)
        contents_layout.addWidget(self.date_btn_2)
        contents_layout.addWidget(self.date_btn_3)
        contents_layout.addWidget(self.date_btn_4)
        contents_layout.addWidget(self.date_btn_5)
        contents_layout.addWidget(self.date_btn_6)
        contents_layout.addWidget(splitter_line_1)
        contents_layout.addWidget(next_week)
        layout.addLayout(self.headers_layout)
        layout.addLayout(contents_layout)
        layout.addStretch()
        # 点击事件
        self.date_btn_7.clicked.connect(lambda: self.date_clicked(self.date_btn_7))
        self.date_btn_1.clicked.connect(lambda: self.date_clicked(self.date_btn_1))
        self.date_btn_2.clicked.connect(lambda: self.date_clicked(self.date_btn_2))
        self.date_btn_3.clicked.connect(lambda: self.date_clicked(self.date_btn_3))
        self.date_btn_4.clicked.connect(lambda: self.date_clicked(self.date_btn_4))
        self.date_btn_5.clicked.connect(lambda: self.date_clicked(self.date_btn_5))
        self.date_btn_6.clicked.connect(lambda: self.date_clicked(self.date_btn_6))
        self.setFixedHeight(100)
        self.setLayout(layout)

    def __change_date(self, sunday):
        """改变7个按钮的显示及date属性"""
        # 获得当周的每一天
        monday = sunday.addDays(1)
        tuesday = sunday.addDays(2)
        wednesday = sunday.addDays(3)
        thursday = sunday.addDays(4)
        friday = sunday.addDays(5)
        saturday = sunday.addDays(6)
        # 修改各按钮的相关属性及显示字样
        self.date_btn_7.date = sunday
        self.date_btn_7.setText(str(sunday.day()) + "\n周日")
        self.date_btn_1.date = monday
        self.date_btn_1.setText(str(monday.day()) + "\n周一")
        self.date_btn_2.date = tuesday
        self.date_btn_2.setText(str(tuesday.day()) + "\n周二")
        self.date_btn_3.date = wednesday
        self.date_btn_3.setText(str(wednesday.day()) + "\n周三")
        self.date_btn_4.date = thursday
        self.date_btn_4.setText(str(thursday.day()) + "\n周四")
        self.date_btn_5.date = friday
        self.date_btn_5.setText(str(friday.day()) + "\n周五")
        self.date_btn_6.date = saturday
        self.date_btn_6.setText(str(saturday.day()) + "\n周六")

    def __date_btn_style_changed(self, change_btn=None):
        for btn in self.__dateItems:
            if change_btn:
                if btn == change_btn:
                    btn.turn_style(btn)
                else:
                    btn.init_style(btn)
            else:
                btn.init_style(btn)

    @staticmethod
    def __get_sunday(date):
        """获取参数date所在周的周日"""
        pre_days_count = -(date.dayOfWeek())
        if date.dayOfWeek() == 7:
            pre_days_count = 0
        return date.addDays(pre_days_count)

    def __today_style_change(self):
        """改变今日(当前时间)的显示样式"""
        today = QDate.currentDate()
        for btn in self.__dateItems:
            if btn.date == today:
                btn.setStyleSheet("""
                QPushButton{
                    border: none;
                    font-size: 17px;
                    font-weight:bold;
                    border-radius: 25px;
                    background-color:rgb(180,180,180)
                }
                QPushButton:hover{
                    font-size:16px;
                    color:rgb(66,111,153);
                    cursor:pointer;
                    font-weight:bold
                }
                """)
            else:
                btn.init_style(btn)

    def back_today_clicked(self):
        """点击回到今日按钮"""
        # 获取今日日期
        self.date = QDate.currentDate()
        # 改变日期编辑框
        self.date_edit.setDate(self.date)
        # 得到今日所在周的周日
        sunday = self.__get_sunday(self.date)
        # 改变按钮date属性与显示
        self.__change_date(sunday)
        # 改变今日样式
        self.__today_style_change()

    def date_clicked(self, date_btn):
        """点击的时间通过信号传出"""
        self.date = date_btn.date
        self.__date_btn_style_changed(date_btn)
        self.click_date.emit(date_btn.date)

    def date_edit_changed(self):
        """时间输入框的时间改变"""
        self.__date_btn_style_changed()
        # 获取改变后的时间
        edit_date = self.date_edit.date()
        # 改变后的时间所在周的周日
        sunday = self.__get_sunday(edit_date)
        # 改变按钮及date属性
        self.__change_date(sunday)
        # 改变今日(当前时间)样式
        self.__today_style_change()

    def last_week_clicked(self):
        """点击上周, 改变按钮的显示与date属性"""
        self.__date_btn_style_changed()
        # 获取当前的sunday
        cur_sunday = self.date_btn_7.date
        # 得到上周的sunday
        last_sunday = cur_sunday.addDays(-7)
        # 改变时间输入框
        self.date_edit.setDate(last_sunday)
        # 改变按钮的date属性和显示
        self.__change_date(last_sunday)

    def next_week_clicked(self):
        """点击下周, 改变按钮的显示与date属性"""
        self.__date_btn_style_changed()
        # 获取当前的sunday
        cur_sunday = self.date_btn_7.date
        # 得到下周的sunday
        next_sunday = cur_sunday.addDays(7)
        # 改变时间输入框
        self.date_edit.setDate(next_sunday)
        # 改变按钮的date属性与显示
        self.__change_date(next_sunday)


class DatePushButtonItem(QPushButton):
    def __init__(self, date, *args):
        super(DatePushButtonItem, self).__init__(*args)
        self.date = date
        self.__init_ui()

    def __init_ui(self):
        style = """
        QPushButton{
            border: none;
            font-size: 14px;
        }
        QPushButton:hover{
            font-size:16px;
            color:rgb(66,111,153);
            font-weight:bold
        }
        """
        self.setMinimumHeight(50)
        self.setMinimumWidth(50)
        self.setStyleSheet(style)

    def init_style(self, btn):
        btn.setStyleSheet("""
        QPushButton{
            border: none;
            font-size: 14px;
        }
        QPushButton:hover{
            font-size:16px;
            color:rgb(66,111,153);
            cursor:pointer;
            font-weight:bold
        }
        """)

    def turn_style(self, btn):
        btn.setStyleSheet("""
        QPushButton{
            border:none;
            font-size:17px;
            font-weight:bold;
            color: rgb(255,255,255);
            background-color: rgb(91,140,185);
            border-radius: 25px;
        }
        QPushButton:hover{
            font-size:16px;
            color:rgb(66,111,153);
            cursor:pointer;
            font-weight:bold
        }        
        """)


