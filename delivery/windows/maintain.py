# _*_ coding:utf-8 _*_
# __Author__： zizle
"""管理端数据维护"""
import requests
from delivery import config
import json
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem
from PyQt5.QtCore import Qt
from delivery.piece import maintain


class DataMaintain(QWidget):
    def __init__(self):
        super(DataMaintain, self).__init__()
        layout = QHBoxLayout(spacing=0, margin=0)
        self.left_menu = QListWidget()
        self.right_stack = QStackedWidget()
        layout.addWidget(self.left_menu)
        layout.addWidget(self.right_stack)
        self.setLayout(layout)
        # style
        self.left_menu.setMaximumWidth(130)
        # signal
        self.left_menu.clicked.connect(self.menu_clicked)
        # 请求菜单
        self.get_left_menu()
        # 样式
        self.left_menu.setFocusPolicy(Qt.NoFocus)
        self.left_menu.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
        QListWidget{
            background-color: rgb(240,240,240);
            border: none;
            font-size: 13px;
        }
        QListWidget::item{
            min-height: 30px;
            border: none;
            padding-left: 5px;
        }
        QListWidget::item:selected {
            border:none;
            background-color: rgb(255,255,255);
        }
        QListWidget::item:!selected{
            
        }
        QListWidget::item:hover {
            background-color: rgb(230,230,230);
            cursor: pointer;
        }
        QStackedWidget{
            
        }
        QPushButton{
            border:none;
            min-height: 23px;
            min-width: 50px;
        }
        QPushButton:hover{
            color: rgb(80, 100, 200);
            background-color: rgb(240,240,240)
        }
        #submitButton{
            background-color: rgb(121,205,205);
            margin: 5px 0;
            border-radius: 5px; 
        }
        QMessageBox::QPushButton{
            border: 1px solid rgb(80,80,80)
        }
        """)

    def get_left_menu(self):
        # 请求菜单
        try:
            response = requests.get(url=config.SERVER + 'maintain-menu/')
            menu_list = json.loads(response.content.decode('utf-8'))
        except Exception:
            menu_list = []
        if not menu_list:
            return
        for menu_dict in menu_list:
            menu_item = QListWidgetItem(menu_dict['name'])
            menu_item.en_code = menu_dict['en_code']
            self.left_menu.addItem(menu_item)
            # 添加stack堆栈窗口
            if menu_item.en_code == 'area':
                stack_widget = maintain.AreaMaintain()
                stack_widget.en_code = 'area'
            elif menu_item.en_code == 'exchange':
                stack_widget = maintain.ExchangeMaintain()
                stack_widget.en_code = 'exchange'
            elif menu_item.en_code == 'variety':
                stack_widget = maintain.VarietyMaintain()
                stack_widget.en_code = 'variety'
            elif menu_item.en_code == 'storehouse':
                stack_widget = maintain.StorehouseMaintain()
                stack_widget.en_code = 'storehouse'
            elif menu_item.en_code == 'housereport':
                stack_widget = maintain.HouseReportMaintain()
                stack_widget.en_code = 'housereport'
            elif menu_item.en_code == 'news':
                stack_widget = maintain.NewsMaintain()
                stack_widget.en_code = 'news'
            elif menu_item.en_code == 'bulletin':
                stack_widget = maintain.BulletinMaintain()
                stack_widget.en_code = 'bulletin'
            else:
                stack_widget = maintain.NotFoundMaintain()
                stack_widget.en_code = 'notFound'
            self.right_stack.addWidget(stack_widget)
        self.left_menu.setCurrentRow(0)  # 默认选择第一个

    def menu_clicked(self, index):
        en_code = self.left_menu.currentItem().en_code
        # print(en_code)
        for index in range(self.right_stack.count()):
            win_frame = self.right_stack.widget(index)
            if win_frame.en_code == en_code:
                self.right_stack.setCurrentWidget(win_frame)
