# _*_ coding:utf-8 _*_
# __Author__： zizle
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout,QGridLayout, QListWidget, QLabel, QComboBox, QLineEdit, \
    QTextEdit, QPushButton, QFileDialog
from PyQt5.Qt import Qt, pyqtSignal
from widgets.base import LoadedPage

""" 【首页】数据管理相关 """


# 新闻公告
class NewsBulletin(QWidget):
    def __init__(self, *args, **kwargs):
        super(NewsBulletin, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        category_select_layout = QHBoxLayout()
        category_select_layout.addWidget(QLabel('显示类型:'), alignment=Qt.AlignLeft)
        self.category_combo = QComboBox(currentIndexChanged=self.category_combo_selected)
        category_select_layout.addWidget(self.category_combo)
        # 错误提示
        self.error_message_label = QLabel()
        category_select_layout.addWidget(self.error_message_label)
        category_select_layout.addStretch()
        layout.addLayout(category_select_layout)
        # 文件选择
        self.file_widget = QWidget(parent=self)
        file_widget_layout = QHBoxLayout(margin=0)
        self.file_path_edit = QLineEdit()
        file_widget_layout.addWidget(QLabel('文件:'), alignment=Qt.AlignLeft)
        file_widget_layout.addWidget(self.file_path_edit)
        file_widget_layout.addWidget(QPushButton('浏览', clicked=self.browser_file))
        self.file_widget.setLayout(file_widget_layout)
        layout.addWidget(self.file_widget)
        # 文字输入
        self.text_widget = QWidget(parent=self)
        text_widget_layout = QHBoxLayout(margin=0)
        self.text_edit = QTextEdit()
        text_widget_layout.addWidget(QLabel('内容:'), alignment=Qt.AlignLeft)
        text_widget_layout.addWidget(self.text_edit)
        self.text_widget.setLayout(text_widget_layout)
        layout.addWidget(self.text_widget)
        # 提交按钮
        self.commit_button = QPushButton('确认提交', clicked=self.commit_news_bulletin)
        layout.addWidget(self.commit_button)
        layout.addStretch()
        self.setLayout(layout)
        self._addCategoryCombo()

    # 类型选择的内容
    def _addCategoryCombo(self):
        for item in [u'上传文件', u'上传内容']:
            self.category_combo.addItem(item)

    # 选择了显示的样式
    def category_combo_selected(self):
        current_text = self.category_combo.currentText()
        if current_text == u'上传文件':
            self.text_widget.hide()
            self.file_widget.show()
        elif current_text == u'上传内容':
            self.text_widget.show()
            self.file_widget.hide()
        else:
            pass

    # 选择上传的文件
    def browser_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files(*.pdf)")
        print(file_path)

    # 确认上传新闻公告
    def commit_news_bulletin(self):
        print('上传新闻公告')

# 广告设置
class AdvertisementPage(QWidget):
    def __init__(self, *args, **kwargs):
        super(AdvertisementPage, self).__init__(*args, **kwargs)

# 首页管理主页
class HomePageCollector(QWidget):
    network_result = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(HomePageCollector, self).__init__(*args, **kwargs)
        layout = QHBoxLayout(margin=0)
        # 左侧菜单列表
        self.left_list = QListWidget(parent=self, clicked=self.left_menu_clicked)
        layout.addWidget(self.left_list, alignment=Qt.AlignLeft)
        # 右侧显示具体操作窗体
        self.operate_frame = LoadedPage()
        layout.addWidget(self.operate_frame)
        self.setLayout(layout)
        self._addListMenu()

    # 添加菜单按钮
    def _addListMenu(self):
        for item in [u'新闻公告', u'广告设置', u'常规报告', u'交易通知', u'现货报表', u'财经日历']:
            self.left_list.addItem(item)

    # 点击左侧按钮
    def left_menu_clicked(self):
        text = self.left_list.currentItem().text()
        if text == u'新闻公告':
            frame_page = NewsBulletin(parent=self.operate_frame)
        elif text == u'广告设置':
            frame_page = AdvertisementPage(parent=self.operate_frame)
        else:
            frame_page = QLabel('【' + text + '】正在加紧开发中...')
        self.operate_frame.clear()
        self.operate_frame.addWidget(frame_page)





