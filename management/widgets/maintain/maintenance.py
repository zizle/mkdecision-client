# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QStyleOption, QStyle, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QPropertyAnimation, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QPainter
from popup.maintain.base import NewModulePopup
import config


# 功能模块控件
class ModuleBlock(QWidget):
    enter_clicked = pyqtSignal(QPushButton)

    def __init__(self, module_name, *args, **kwargs):
        super(ModuleBlock, self).__init__(*args, **kwargs)
        self.module_name = module_name
        layout = QVBoxLayout()
        self.enter_button = QPushButton('进入', parent=self)
        self.enter_button.clicked.connect(self.enter_button_clicked)
        self.setLayout(layout)
        # 本身样式设置
        self.setObjectName('moduleBlock')
        self.resize(200, 200)
        self.setStyleSheet("""
        #moduleBlock{
            background-color:rgb(200, 200, 200)
        }
        """)
        # 保存点击之间的原始位置
        self.original_x = 0
        self.original_y = 0
        # 保存原始大小
        self.original_width = 0
        self.original_height = 0

    # 记录原始位置
    def set_original_rect(self, x, y, w, h):
        self.original_x = x
        self.original_y = y
        self.original_width = w
        self.original_height = h

    # 重写，可以设置背景颜色
    def paintEvent(self, envent):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    # 设置显示控件
    def set_module_widget(self, widget):
        self.layout().addWidget(widget)
        self.layout().addWidget(self.enter_button)

    # 点击了进入按钮
    def enter_button_clicked(self):
        self.enter_clicked.emit(self.enter_button)


# 模块管理表格
class ModuleMaintainTable(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(ModuleMaintainTable, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()

    # 添加模块数据
    def getModules(self):
        # 获取所有主功能模块列表
        self.clear()
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(['序号', '名称', '开放'])
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'basic/modules-maintain/?mc=' + config.app_dawn.value('machine')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
            print(response)
        except Exception:
            return
        module_list = response['data']
        self.setRowCount(len(module_list))
        for row, module_item in enumerate(module_list):
            item_0 = QTableWidgetItem(str(row + 1))
            item_1 = QTableWidgetItem(str(module_item['name']))
            item_2 = QTableWidgetItem(str(module_item['is_active']))
            item_0.setTextAlignment(Qt.AlignCenter)
            item_1.setTextAlignment(Qt.AlignCenter)
            item_2.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 0, item_0)
            self.setItem(row, 1, item_1)
            self.setItem(row, 2, item_2)

    # 新增模块弹窗
    def addNewModulePopup(self):
        popup = NewModulePopup(parent=self)
        if not popup.exec_():
            popup.deleteLater()
            del popup
            # 刷新模块数据
            self.getModules()



