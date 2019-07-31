# _*_ coding:utf-8 _*_
# author: zizle
# Date: 20190515
import requests
import json
import hashlib
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QCursor, QPixmap
from PyQt5.QtCore import pyqtSignal, QDate, Qt, QSettings
from widgets.frame_less_window import TitleBar
from widgets.public import TableWidget
from utils import get_desktop_path
from utils.machine import machine
from utils.pdf_page import render_pdf_page

import config


class AddCarouselDataWidget(QWidget):
    """添加轮播内容的控件"""
    upload_carousel_signal = pyqtSignal(dict)

    def __init__(self):
        super(AddCarouselDataWidget, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        """初始化界面"""
        self.setFixedWidth(320)
        self.show_style_items = ["显示文件", "显示文字", "跳转网址"]
        main_layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        image_select_layout = QHBoxLayout()
        self.show_style_layout = QHBoxLayout()
        self.form_layout.setLabelAlignment(Qt.AlignRight)
        self.edit_0 = QLineEdit()  # 图片本地路径
        self.edit_0.setEnabled(False)
        self.edit_3 = QLineEdit()  # 广告的名称
        button_0 = QPushButton("…")  # 选择图片按钮
        button_1 = QPushButton("…")  # 选择文件按钮
        button_0.clicked.connect(self.select_image)
        button_1.clicked.connect(self.select_file)
        self.combo = QComboBox()
        self.combo.addItems(self.show_style_items)
        self.combo.currentTextChanged.connect(self.show_style_changed)
        self.edit_1 = QLineEdit()  # 文件本地路径
        self.edit_1.setEnabled(False)
        self.edit_2 = QLineEdit()
        self.edit_2.hide()
        self.text_edit = QTextEdit()
        self.text_edit.hide()
        # 大小控制
        self.edit_0.setFixedSize(200, 25)
        self.edit_3.setFixedSize(200, 25)
        button_0.setFixedSize(30, 25)
        button_1.setFixedSize(30, 25)
        self.combo.setFixedSize(200, 25)
        self.edit_1.setFixedSize(200, 25)
        image_select_layout.addWidget(self.edit_0)
        image_select_layout.addWidget(button_0)
        self.show_style_layout.addWidget(self.edit_1)
        self.show_style_layout.addWidget(button_1)
        self.form_layout.addRow("广告命名：", self.edit_3)
        self.form_layout.addRow("选择图片：", image_select_layout)
        self.form_layout.addRow("展示方式：", self.combo)
        self.form_layout.addRow("选择文件：", self.show_style_layout)
        main_layout.addLayout(self.form_layout)
        # 上传按钮
        button_upload = QPushButton("确认提交")
        button_upload.setCursor(QCursor(Qt.PointingHandCursor))
        button_upload.setStyleSheet("min-width:250px;min-height:30px;max-width:200px;max-height:30px;border:none; background-color:rgb(100,182,220)")
        button_upload.clicked.connect(self.upload_carousel)
        main_layout.addWidget(button_upload, alignment=Qt.AlignCenter)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def select_file(self):
        # 弹窗
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        self.edit_1.setText(file_path)

    def select_image(self):
        # 弹窗
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "Image files (*.png *.jpg)")
        if not file_path:
            return
        self.edit_0.setText(file_path)

    def show_style_changed(self, signal):
        # 创建控件
        # 文件展示所需
        show_style_layout = QHBoxLayout()
        self.edit_1 = QLineEdit()
        self.edit_1.setFixedSize(200, 25)
        self.edit_1.setEnabled(False)
        button = QPushButton("…")
        button.setFixedSize(30, 25)
        show_style_layout.addWidget(self.edit_1)
        show_style_layout.addWidget(button)
        # 文字展示所需
        self.text_edit = QTextEdit()
        # 跳转网址所需
        self.edit_2 = QLineEdit()
        self.text_edit.setFixedSize(200, 100)
        self.edit_2.setFixedSize(200,25)
        self.form_layout.removeRow(self.form_layout.rowCount() - 1)
        if signal == self.show_style_items[0]:
            # print("文件展示")
            self.form_layout.addRow("选择文件：", show_style_layout)
        elif signal == self.show_style_items[1]:
            # print('文字展示')
            self.form_layout.addRow("内容：", self.text_edit)
        elif signal == self.show_style_items[2]:
            # print("跳转网址")
            self.form_layout.addRow("网址：", self.edit_2)
        else:
            pass

    def upload_carousel(self):
        """上传广告"""
        data = dict()
        show_dict = {
            "显示文件": "show_file",
            "显示文字": "show_text",
            "跳转网址": "redirect"
        }
        name = self.edit_3.text().strip(' ')
        if not name:
            QMessageBox.warning(self, "错误", "请起一个名字!", QMessageBox.Yes)
            return
        image_path = self.edit_0.text()
        if not image_path:
            QMessageBox.warning(self, "错误", "请上传展示的图片!", QMessageBox.Yes)
            return
        show_style = show_dict.get(self.combo.currentText(), None)
        if not show_style:
            QMessageBox.warning(self, "错误", "程序发生未知错误!", QMessageBox.Yes)
            return
        if show_style == "show_file" and not self.edit_1.text():
            QMessageBox.warning(self, "错误", "要显示文件需上传pdf文件!", QMessageBox.Yes)
            return
        if show_style == "redirect" and not self.edit_2.text().strip(' '):
            QMessageBox.warning(self, "错误", "跳转网址需填写网址!", QMessageBox.Yes)
            return
        file_path = self.edit_1.text()
        content_list = self.text_edit.toPlainText().split('\n')
        # 处理文本内容
        text_content = ""
        if content_list[0]:
            for p in content_list:
                text_content += "<p style='margin:0;'><span>&nbsp;&nbsp;</span>" + p + "</p>"
        redirect_url = self.edit_2.text().strip(' ')
        data["name"] = name
        data["image"] = image_path
        data["show_type"] = show_style
        data["file"] = file_path
        data["content"] = text_content
        data["redirect"] = redirect_url
        self.upload_carousel_signal.emit(data)
        self.edit_0.clear()
        self.edit_1.clear()
        self.edit_2.clear()
        self.text_edit.clear()


class AddNoticeDialog(QDialog):
    upload_notice_signal = pyqtSignal(list)

    def __init__(self):
        super(AddNoticeDialog, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        self.setWindowTitle("添加通知")
        self.setWindowIcon(QIcon("media/notice.png"))
        label_0 = QLabel("文件：", self)
        self.edit_0 = QLineEdit(self)
        self.edit_0.setEnabled(False)
        button_0 = QPushButton("...", self)
        label_0.setGeometry(50, 20, 35, 25)
        self.edit_0.setGeometry(90, 20, 200, 25)
        button_0.setGeometry(290, 22.5, 25, 20)
        label_1 = QLabel("类型：", self)
        self.combo = QComboBox(self)
        self.combo.addItems(["公司", "交易所", "系统", "其他"])
        label_1.setGeometry(50, 55, 35, 25)
        self.combo.setGeometry(90, 55, 200, 25)
        label_2 = QLabel("名字：", self)
        self.edit_1 = QLineEdit(self)
        self.edit_1.setPlaceholderText("默认文件名称")
        label_2.setGeometry(50, 90, 35, 25)
        self.edit_1.setGeometry(90, 90, 200, 25)
        button_1 = QPushButton("上传", self)
        button_1.setGeometry(240, 125, 50, 25)
        button_0.clicked.connect(self.select_file)
        button_1.clicked.connect(self.upload_notice)

    def select_file(self):
        # 弹窗
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        self.edit_0.setText(file_path)

    def upload_notice(self):
        type_dict = {
            "公司": "company",
            "交易所": "change",
            "系统": "system",
            "其他": "others"
        }
        file_type = type_dict.get(self.combo.currentText(), None)
        if not file_type:
            QMessageBox.warning(self, "错误", "请选择通知类型!", QMessageBox.Yes)
            return

        self.upload_notice_signal.emit([self.edit_0.text(), file_type, self.edit_1.text().strip(' ')])


class AddReportDialog(QDialog):
    upload_report_signal = pyqtSignal(list)

    def __init__(self):
        super(AddReportDialog, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        self.setWindowTitle("添加报告")
        self.setWindowIcon(QIcon("media/report.png"))
        label_0 = QLabel("报告：", self)
        self.edit_0 = QLineEdit(self)
        self.edit_0.setEnabled(False)
        button_0 = QPushButton("...", self)
        label_0.setGeometry(50, 20, 35, 25)
        self.edit_0.setGeometry(90, 20, 200, 25)
        button_0.setGeometry(290, 22.5, 25, 20)
        label_1 = QLabel("类型：", self)
        self.combo = QComboBox(self)
        self.combo.addItems(["日报", "周报", "月报", "年报", "专题", "投资报告", "其他"])
        label_1.setGeometry(50, 55, 35, 25)
        self.combo.setGeometry(90, 55, 200, 25)
        label_2 = QLabel("名字：", self)
        self.edit_1 = QLineEdit(self)
        self.edit_1.setPlaceholderText("默认文件名称")
        label_2.setGeometry(50, 90, 35, 25)
        self.edit_1.setGeometry(90, 90, 200, 25)
        button_1 = QPushButton("上传", self)
        button_1.setGeometry(240, 125, 50, 25)
        button_0.clicked.connect(self.select_file)
        button_1.clicked.connect(self.upload_report)

    def select_file(self):
        # 弹窗
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        self.edit_0.setText(file_path)

    def upload_report(self):
        type_dict = {
            "日报": "daily",
            "周报": "weekly",
            "月报": "monthly",
            "年报": "annual",
            "专题": "special",
            "投资报告": "invest",
            "其他": "others"
        }
        file_type = type_dict.get(self.combo.currentText(), None)
        if not file_type:
            QMessageBox.warning(self, "错误", "请选择报告类型!", QMessageBox.Yes)
            return

        self.upload_report_signal.emit([self.edit_0.text(), file_type, self.edit_1.text().strip(' ')])


class ContentReadDialog(QDialog):
    """显示文本信息"""
    def __init__(self, content, title="查看内容", *args):
        super(ContentReadDialog, self).__init__(*args)
        self.content = content
        self.title = title
        self.__init_ui()

    def __init_ui(self):
        layout = QVBoxLayout()
        text_browser = QTextBrowser()
        text_browser.setStyleSheet("font-size:14px;")
        text_browser.setHtml(self.content)
        layout.addWidget(text_browser)
        self.setWindowTitle(self.title)
        self.setLayout(layout)


class ExportEconomicDialog(QDialog):
    """导出财经日历对话框"""
    export_data_signal = pyqtSignal(list)

    def __init__(self):
        super(ExportEconomicDialog, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        self.setWindowTitle("导出财经日历")
        self.setWindowIcon(QIcon("media/calendar.png"))
        hbox_layout_0 = QHBoxLayout()
        hbox_layout_1 = QHBoxLayout()
        hbox_layout_2 = QHBoxLayout()
        self.start_time = QDateEdit(QDate.currentDate())
        self.start_time.setCalendarPopup(True)
        self.start_time.setDisplayFormat("yyyy年MM月dd日")
        self.end_time = QDateEdit(QDate.currentDate().addDays(1))
        self.end_time.setCalendarPopup(True)
        self.end_time.setDisplayFormat("yyyy年MM月dd日")
        commit_button = QPushButton("确定")
        commit_button.clicked.connect(self.confirm_export_calendar)
        hbox_layout_0.addWidget(QLabel("选择要导出的时间区间:"))
        hbox_layout_0.addWidget(self.start_time)
        hbox_layout_0.addWidget(QLabel("至"))
        hbox_layout_0.addWidget(self.end_time)
        hbox_layout_0.addStretch()
        hbox_layout_1.addWidget(QLabel("选择要保存的路径:"))
        self.desktop_path = get_desktop_path()
        self.path = QLineEdit(self.desktop_path)
        self.path.setMinimumWidth(300)
        hbox_layout_1.addWidget(self.path)
        browser = QPushButton("浏览")
        browser.clicked.connect(self.browser_path)
        hbox_layout_1.addWidget(browser)
        hbox_layout_2.addWidget(commit_button, alignment=Qt.AlignRight)
        layout = QVBoxLayout()
        layout.addLayout(hbox_layout_0)
        layout.addLayout(hbox_layout_1)
        layout.addLayout(hbox_layout_2)
        self.setLayout(layout)

    def browser_path(self):
        """选择保存路径"""
        save_path = QFileDialog.getExistingDirectory(self, "选择保存的位置", self.desktop_path)
        if save_path:
            self.path.setText(save_path)

    def confirm_export_calendar(self):
        """确定导出财经日历"""
        self.export_data_signal.emit([self.start_time.date(), self.end_time.date(), self.path.text()])


class LoadingDialog(QWidget):
    def __init__(self, *args):
        super(LoadingDialog, self).__init__(*args)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.__init_ui()

    def __init_ui(self):
        self.setFixedSize(180, 50)
        self.setStyleSheet('background-color: #CDE345')
        layout = QHBoxLayout()
        label = QLabel("数据加载中...请稍候...")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)


class LoginDialog(QDialog):
    """登录弹窗"""
    button_clicked_signal = pyqtSignal(str)

    def __init__(self):
        super(LoginDialog, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        register_forget_style = """
        QPushButton {
           font-size:11px;
           color:rgb(0,0,200);
           border:none;
        } 
        """
        style_sheet = """
        LoginDialog {
            border:1px solid rgb(54, 157, 180)
            }
        QLineEdit {
            font-size:13px;
            border-width:0;
            border-style:outset;
            border-top:1px solid rgb(150,150,150);
            border-bottom:1px solid rgb(150,150,150)
        }
        """
        self.resize(480, 300)
        # 设置无边框
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 添加个head
        title_bar = TitleBar(self)
        self.setWindowTitle("登录")
        title_bar.setTitle("登录瑞达期货分析决策系统")
        title_bar.setGeometry(0, 0, 480, 50)
        # 按钮处理
        title_bar.buttonMinimum.hide()
        title_bar.buttonMaximum.hide()
        title_bar.buttonClose.setCursor(QCursor(Qt.PointingHandCursor))
        title_bar.windowClosed.connect(lambda: self.button_clicked("cancel"))
        title_bar.windowMoved.connect(self.move)
        account_label = QLabel(self)
        account_label.setStyleSheet("image:url(media/user_icon.jpg)")
        account_label.setGeometry(75, 100, 36, 35)
        password_label = QLabel(self)
        password_label.setStyleSheet("image:url(media/mima_icon.jpg)")
        password_label.setGeometry(75, 150, 36, 35)
        # 用户名输入
        self.account_edit = QLineEdit(self)
        self.account_edit.setGeometry(111, 100, 250, 35)
        self.account_edit.setPlaceholderText("用户名/手机号")
        # 无用户名注册账号
        register_account = QPushButton("还没账号?", self)
        register_account.setGeometry(365, 100, 60, 35)
        register_account.setStyleSheet(register_forget_style)
        register_account.setCursor(QCursor(Qt.PointingHandCursor))
        register_account.clicked.connect(lambda: self.button_clicked("register"))
        # 密码输入
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setGeometry(111, 150, 250, 35)
        self.password_edit.setPlaceholderText("请输入密码")
        # 忘记密码
        forget_password = QPushButton("忘记密码?", self)
        forget_password.setGeometry(365, 150, 60, 35)
        forget_password.setStyleSheet(register_forget_style)
        forget_password.setCursor(QCursor(Qt.PointingHandCursor))
        forget_password.clicked.connect(lambda: self.button_clicked("forget"))
        # 记住密码
        self.remember_check = QCheckBox("记住密码",self)
        self.remember_check.setGeometry(75, 190, 80, 30)
        # 自动登录
        self.automatic = QCheckBox("自动登录", self)
        self.automatic.setGeometry(155, 190, 80, 30)
        self.automatic.stateChanged.connect(self.automatic_state_change)
        # 登录
        login_button = QPushButton("登录", self)
        login_button.setGeometry(75, 220, 286, 35)
        login_button.setStyleSheet("color:#FFFFFF;font-size:15px;border:none;background-color:rgb(30,50,190);")
        login_button.setCursor(QCursor(Qt.PointingHandCursor))
        login_button.clicked.connect(lambda: self.button_clicked("login"))
        self.windowIconChanged.connect(title_bar.setIcon)
        self.setWindowIcon(QIcon("media/logo.png"))
        self.setStyleSheet(style_sheet)
        self.set_config()

    def set_config(self):
        config = QSettings('conf/config.ini', QSettings.IniFormat)
        username = config.value('username')
        if username:
            self.account_edit.setText(username)

    def automatic_state_change(self):
        """自动登录选框状态发生改变"""
        if self.automatic.isChecked():
            self.remember_check.setChecked(True)

    def button_clicked(self, signal):
        """"取消或登录"""
        self.button_clicked_signal.emit(signal)


class PDFReaderContent(QWidget):
    """显示PDF内容控件"""
    def __init__(self):
        super(PDFReaderContent, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        self.page_layout = QVBoxLayout()  # 每一页内容展示在一个竖向布局中
        self.setLayout(self.page_layout)

    def add_page(self, page):
        """添加页码"""
        page_label = QLabel()
        page_label.setMinimumSize(self.width()+200, self.height())  # 设置label大小
        page_map = render_pdf_page(page)
        # page_map.scaled()
        # 按弹窗大小缩放标签
        page_label.setPixmap(page_map)
        page_label.setScaledContents(True)  # 图片自适应大小
        self.page_layout.addWidget(page_label, alignment=Qt.AlignRight)


class PDFReaderDialog(QDialog):
    """显示PDF内容对话框"""
    download_file_signal = pyqtSignal(list)

    def __init__(self, doc, file=None, title="查看PDF"):
        super(PDFReaderDialog, self).__init__()
        self.title = title
        self.doc = doc
        self.file = file
        self.__init_ui()

    def __init_ui(self):
        layout = QVBoxLayout()
        self.setWindowIcon(QIcon("media/reader.png"))
        self.download = QPushButton("下载PDF")
        self.download.setIcon(QIcon("media/download-file.png"))
        self.download.clicked.connect(self.download_file)
        scroll_area = QScrollArea()
        self.content = PDFReaderContent()
        for page in range(self.doc.pageCount):
            self.content.add_page(self.doc.loadPage(page))
        scroll_area.setWidget(self.content)
        layout.addWidget(self.download, alignment=Qt.AlignLeft)
        layout.addWidget(scroll_area)
        self.setMinimumSize(config.PDF_READER_DIALOG_WIDTH, config.PDF_READER_DIALOG_HEIGHT)
        self.setWindowTitle(self.title)
        self.setLayout(layout)

    def download_file(self):
        """下载文档"""
        self.download_file_signal.emit([self.title, self.file])


class RegisterDialog(QDialog):
    """注册弹窗"""
    button_click_signal = pyqtSignal(str)

    def __init__(self):
        super(RegisterDialog, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        self.resize(490, 400)
        # 设置无边框
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 添加个head
        title_bar = TitleBar(self)
        self.setWindowTitle("注册")
        title_bar.setTitle("注册账号")
        title_bar.setGeometry(0, 0, 490, 50)
        # 按钮处理
        title_bar.buttonMinimum.hide()
        title_bar.buttonMaximum.hide()
        title_bar.buttonClose.setCursor(QCursor(Qt.PointingHandCursor))
        title_bar.windowClosed.connect(lambda: self.button_clicked("cancel"))
        title_bar.windowMoved.connect(self.move)
        self.windowIconChanged.connect(title_bar.setIcon)
        self.setWindowIcon(QIcon("media/logo.png"))
        # 获取机器码
        get_machine = QLabel('机器码：', self)
        self.machine_code = QLineEdit(self)
        get_machine.setGeometry(88, 45, 60, 35)
        self.machine_code.setGeometry(145, 50, 220, 25)
        # 手机号
        account_label = QLabel("手机：", self)
        account_label.setGeometry(75, 100, 60, 36)
        account_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        self.account_edit = QLineEdit(self)
        self.account_edit.setPlaceholderText("请输入手机号")
        self.account_edit.setCursor(QCursor(Qt.PointingHandCursor))
        self.account_edit.setGeometry(145, 100, 220, 35)
        # 昵称
        nick_label = QLabel("昵称：", self)
        nick_label.setGeometry(75, 150, 60, 35)
        nick_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        self.nick_edit = QLineEdit(self)
        self.nick_edit.setPlaceholderText("请输入昵称,不填为空")
        self.nick_edit.setCursor(QCursor(Qt.PointingHandCursor))
        self.nick_edit.setGeometry(145, 150, 220, 35)
        # 密码
        password_label = QLabel("密码：", self)
        password_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        password_label.setGeometry(75, 200, 60, 35)
        self.password_edit = QLineEdit(self)
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setCursor(QCursor(Qt.PointingHandCursor))
        self.password_edit.setGeometry(145, 200, 220, 35)
        # 确认密码
        confirm_password = QLabel("确认密码：", self)
        confirm_password.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        confirm_password.setGeometry(75, 250, 60, 35)
        self.confirm_edit = QLineEdit(self)
        self.confirm_edit.setPlaceholderText("请再次输入密码")
        self.confirm_edit.setCursor(QCursor(Qt.PointingHandCursor))
        self.confirm_edit.setGeometry(145, 250, 220, 35)
        # 协议
        self.agreement = QCheckBox("我已阅读并同意", self)
        self.agreement.setStyleSheet("font-size:11px;color:rgb(100,100,100)")
        self.agreement.setChecked(True)
        self.agreement.setGeometry(145, 295, 110, 25)
        self.agreement.stateChanged.connect(self.agreement_state_changed)
        agreement_button = QPushButton("《决策分析系统最终用户许可协议》", self)
        agreement_button.setStyleSheet("font-size:11px;border:none; color:rgb(0,0,255)")
        agreement_button.setCursor(QCursor(Qt.PointingHandCursor))
        agreement_button.setGeometry(240, 295, 165, 25)
        agreement_button.clicked.connect(lambda: self.button_clicked("agreement"))
        # 注册
        self.register_button = QPushButton("注册", self)
        self.register_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.register_button.setStyleSheet("color:#FFFFFF;font-size:15px;background-color:rgb(30,50,190);")
        self.register_button.setGeometry(145, 330, 220, 35)
        self.register_button.clicked.connect(lambda: self.button_clicked("register"))
        # 已有账号
        has_account = QLabel("已有账号?", self)
        has_account.setStyleSheet("font-size:11px;")
        has_account.setGeometry(145, 370, 60, 20)
        # 登录
        self.login_button = QPushButton("登录", self)
        self.login_button.setStyleSheet("font-size:11px;border:none;color:rgb(30,50,190)")
        self.login_button.setGeometry(195, 370, 30, 20)
        self.login_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.login_button.clicked.connect(lambda: self.button_clicked("login"))
        self.setStyleSheet("RegisterDialog {border:1px solid rgb(54, 157, 180)}")
        conf_machine = config.app_dawn.value("machine")
        # 没有机器码再获取
        if conf_machine is None:
            self.get_machine_code()
        else:
            self.machine_code.setText(conf_machine)

    def get_machine_code(self):
        """获取机器码"""
        md = hashlib.md5()
        main_board = machine.main_board()
        disk = machine.disk()
        md.update(main_board.encode('utf-8'))
        md.update(disk.encode('utf-8'))
        machine_code = md.hexdigest()
        # 在配置里保存
        config.app_dawn.setValue("machine", machine_code)
        self.machine_code.setText(machine_code)

    def agreement_state_changed(self):
        """同意协议状态发生改变"""
        if not self.agreement.isChecked():
            self.register_button.setEnabled(False)
            self.register_button.setStyleSheet("color:#FFFFFF;font-size:15px;background-color:rgb(200,200,200);")
        else:
            self.register_button.setStyleSheet("color:#FFFFFF;font-size:15px;background-color:rgb(30,50,190);")
            self.register_button.setEnabled(True)

    def button_clicked(self, signal):
        """按钮点击"""
        self.button_click_signal.emit(signal)


class SelectParentModuleDialog(QDialog):
    def __init__(self):
        super(SelectParentModuleDialog, self).__init__()
        # self.__init_ui()

    def __init_ui(self):
        # 请求数据
        response = requests.get(
            url=config.SERVER_ADDR + "limits/module/",
            headers=config.CLIENT_HEADERS,
            data=json.dumps({"machine_code": app_conf["machine_code"]})
        )
        response_content = json.loads(response.content.decode("utf-8"))
        # 设置目录树
        select_tree = QTreeWidget()
        select_tree.setHeaderLabel('')
        layout = QVBoxLayout()
        for item in response_content["data"]:
            # 设置根节点
            root = SelectParentModuleItem(select_tree)
            root.setText(0, item["fields"]["name"])
            root.setId(item["pk"])
        layout.addWidget(select_tree)
        self.setLayout(layout)


class SelectParentModuleItem(QTreeWidgetItem):
    def setId(self, id):
        self.id = id


class SetBulletinDialog(QDialog):
    """有关公告栏设置弹窗"""
    set_bulletin_signal = pyqtSignal(dict)

    def __init__(self):
        super(SetBulletinDialog, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        self.setFixedWidth(340)
        self.setWindowTitle("设置公告栏")
        self.setWindowIcon(QIcon("media/bulletin.png"))
        layout = QVBoxLayout(margin=0, spacing=0)
        # 添加一个tab
        tabs = QTabWidget()
        self.tab_0 = QWidget()
        self.tab_1 = QWidget()
        tabs.addTab(self.tab_0, "添加公告")
        tabs.addTab(self.tab_1, "显示天数")
        # 初始化tab_0
        self.init_tab_0()
        self.init_tab_1()
        layout.addWidget(tabs)

        self.setLayout(layout)

    def init_tab_0(self):
        self.show_type_list = ["文件展示", "显示文字"]
        layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.form_layout.setLabelAlignment(Qt.AlignRight)
        self.tab_0_edit_0 = QLineEdit()
        self.tab_0_edit_0.setPlaceholderText("输入条目展示的名称(默认文件名)")
        self.tab_0_edit_1 = QComboBox()
        self.tab_0_edit_1.addItems(self.show_type_list)
        self.tab_0_edit_1.currentTextChanged.connect(self.tab_0_show_type_changed)
        self.tab_0_edit_2 = QLineEdit()
        self.tab_0_edit_2.setEnabled(False)
        select_file_button = QPushButton("…")
        select_file_button.setFixedSize(30, 25)
        select_file_button.clicked.connect(self.tab_0_file_selected)
        show_type_layout = QHBoxLayout()
        show_type_layout.addWidget(self.tab_0_edit_2)
        show_type_layout.addWidget(select_file_button)
        # 固定大小
        self.tab_0_edit_0.setFixedSize(220, 25)
        self.tab_0_edit_1.setFixedSize(220, 25)
        self.tab_0_edit_2.setFixedSize(220, 25)
        # 填写文字的框
        self.text_edit = QTextEdit()
        self.text_edit.hide()
        self.form_layout.addRow("展示方式：", self.tab_0_edit_1)
        self.form_layout.addRow("公告名称：", self.tab_0_edit_0)
        self.form_layout.addRow("选择文件：", show_type_layout)
        # 上传按钮
        upload_button = QPushButton("确认")
        upload_button.setStyleSheet('border:none; background-color:rgb(100,182,220);height:30px; width:80px')
        upload_button.setCursor(QCursor(Qt.PointingHandCursor))
        upload_button.clicked.connect(self.tab_0_upload_data)
        upload_button_layout = QHBoxLayout()
        upload_button_layout.addWidget(upload_button, alignment=Qt.AlignRight)
        layout.addLayout(self.form_layout)
        layout.addLayout(upload_button_layout)
        layout.addStretch()
        self.tab_0.setLayout(layout)

    def init_tab_1(self):
        """初始化显示天数tab"""
        layout = QVBoxLayout()
        tip_label = QLabel("* 设置公告栏展示距今日几天前的内容")
        tip_label.setStyleSheet("color: rgb(84,182,230);font-size:12px;")
        form_layout = QFormLayout()
        self.tab_1_edit_1 = QLineEdit()
        self.tab_1_edit_1.setFixedHeight(28)
        self.tab_1_edit_1.setPlaceholderText("请输入正整数.")
        form_layout.addRow("设置天数：", self.tab_1_edit_1)
        self.set_button = QPushButton("确认设置")
        self.set_button.clicked.connect(self.tab_1_upload_data)
        self.set_button.setStyleSheet('border:none; background-color:rgb(100,182,220);height:30px; width:80px')
        self.set_button.setCursor(QCursor(Qt.PointingHandCursor))
        form_layout.addRow('', self.set_button)
        layout.addWidget(tip_label)
        layout.addLayout(form_layout)
        layout.addStretch()
        self.tab_1.setLayout(layout)


    def tab_0_show_type_changed(self, signal):
        """添加公告展示方式改变"""
        self.tab_0_edit_0.clear()
        self.text_edit.clear()
        self.tab_0_edit_2.clear()
        show_type_layout = QHBoxLayout()
        self.tab_0_edit_2 = QLineEdit()
        self.tab_0_edit_2.setFixedSize(220, 25)
        self.tab_0_edit_2.setEnabled(False)
        select_file_button = QPushButton("…")
        select_file_button.setFixedSize(30, 25)
        show_type_layout.addWidget(self.tab_0_edit_2)
        show_type_layout.addWidget(select_file_button)
        # 文字展示所需
        self.text_edit = QTextEdit()
        self.text_edit.setFixedSize(220, 100)
        self.form_layout.removeRow(self.form_layout.rowCount() - 1)
        if signal == self.show_type_list[0]:
            self.tab_0_edit_0.setPlaceholderText("输入条目展示的名称(默认文件名)")
            self.form_layout.addRow("选择文件：", show_type_layout)
        elif signal == self.show_type_list[1]:
            self.tab_0_edit_0.setPlaceholderText("输入条目展示的名称(必填)")
            self.form_layout.addRow("内容：", self.text_edit)
        else:
            pass

    def tab_0_file_selected(self):
        """选择文件"""
        # 弹窗
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        if not self.tab_0_edit_0.text().strip(' '):
            file_raw_name = file_path.rsplit("/", 1)
            file_name_list = file_raw_name[1].rsplit(".", 1)
            self.tab_0_edit_0.setText(file_name_list[0])
        self.tab_0_edit_2.setText(file_path)

    def tab_0_upload_data(self):
        """设置公告上传"""
        data = dict()
        show_dict = {
            "文件展示": "show_file",
            "显示文字": "show_text",
        }
        show_type = show_dict.get(self.tab_0_edit_1.currentText(), None)
        file_path = self.tab_0_edit_2.text()
        if not show_type:
            QMessageBox.warning(self, "错误", "未选择展示方式!", QMessageBox.Yes)
            return
        if show_type == "show_file" and not file_path:
            QMessageBox.warning(self, "错误", "请选择文件!", QMessageBox.Yes)
            return
        if show_type == "show_file" and not self.tab_0_edit_0.text().strip(' '):
            # 处理文件名称
            file_raw_name = file_path.rsplit("/", 1)
            file_name_list = file_raw_name.rsplit(".", 1)
            self.tab_0_edit_0.setText(file_name_list[0])
        if show_type == "show_text" and not self.tab_0_edit_0.text().strip(' '):
            QMessageBox.warning(self, "错误", "展示内容需输入条目名称!", QMessageBox.Yes)
            return
        content_list = self.text_edit.toPlainText().strip(' ').split('\n') # 去除前后空格和分出换行
        if show_type == "show_text" and not content_list[0]:
            QMessageBox.warning(self, "错误", "展示内容请填写文本内容!", QMessageBox.Yes)
            return
        # 处理文本内容
        text_content = ""
        if show_type == "show_text":
            for p in content_list:
                text_content += "<p style='margin:0;'><span>&nbsp;&nbsp;</span>" + p + "</p>"
        data["name"] = self.tab_0_edit_0.text().strip(' ')
        data["show_type"] = show_type
        data["file"] = file_path
        data["content"] = text_content
        data["set_option"] = "new_bulletin"
        self.set_bulletin_signal.emit(data)
        self.tab_0_edit_0.clear()
        self.tab_0_edit_2.clear()
        self.text_edit.clear()

    def tab_1_upload_data(self):
        try:
            days = int(self.tab_1_edit_1.text())
        except Exception as e:
            QMessageBox.warning(self, "错误", "请输入一个正整数!\n{}".format(e), QMessageBox.Yes)
            return
        if days <= 0:
            QMessageBox.warning(self, "错误", "请输入大于0的正整数!", QMessageBox.Yes)
            return
        data = dict()
        data["set_option"] = "days"
        data["days"] = days
        self.set_bulletin_signal.emit(data)
        self.tab_1_edit_1.clear()


class SetCarouselCheckBox(QCheckBox):
    """"设置轮播图显示与否的表格内复选框控件"""
    check_change_signal = pyqtSignal(QCheckBox)

    def __init__(self, row, col, *args):
        super(SetCarouselCheckBox, self).__init__(*args)
        self.rowIndex = row
        self.colIndex = col
        self.stateChanged.connect(self.check_state_changed)

    def check_state_changed(self):
        self.check_change_signal.emit(self)

    def column(self):
        return self.colIndex

    def row(self):
        return self.rowIndex


class SetCarouselDialog(QDialog):
    """有关轮播广告设置弹窗"""
    upload_carousel_signal = pyqtSignal(list)
    carousel_show_signal = pyqtSignal(list)

    def __init__(self):
        super(SetCarouselDialog, self).__init__()
        self.resize(840, 500)
        self.__init_ui()

    def __init_ui(self):
        layout = QVBoxLayout(margin=0, spacing=0)
        option_layout = QHBoxLayout()
        self.setWindowTitle("设置广告")
        self.setWindowIcon(QIcon("media/carousel.png"))
        self.show_carousel_tab = QPushButton("设置广告")
        self.show_carousel_tab.clicked.connect(self.add_tab_hide)
        self.add_carousel_tab = QPushButton("添加广告")
        self.add_carousel_tab.clicked.connect(self.add_tab_show)
        self.table = TableWidget(self)
        self.table.move(0, 35)
        self.table.setVerticalHeaderVisible(False)
        self.table.setMouseTracking(False)
        self.add_widget = AddCarouselDataWidget()
        option_layout.addWidget(self.show_carousel_tab)
        option_layout.addWidget(self.add_carousel_tab)
        option_layout.addStretch()
        layout.addLayout(option_layout)
        layout.addWidget(self.add_widget, alignment=Qt.AlignCenter)
        layout.addWidget(self.table)
        self.add_widget.hide()
        self.setLayout(layout)

    def add_tab_hide(self):
        self.resize(840, 500)
        self.show_carousel_tab.setEnabled(False)
        self.add_carousel_tab.setEnabled(True)
        self.table.show()
        self.add_widget.hide()

    def add_tab_show(self):
        self.resize(320, 210)
        self.add_carousel_tab.setEnabled(False)
        self.show_carousel_tab.setEnabled(True)
        self.table.hide()
        self.add_widget.show()

    def carousel_is_show_changed(self, checkbox):
        """改变是否显示"""
        carousel_id = int(self.table.item(checkbox.rowIndex, checkbox.colIndex).id_key)
        # option = QMessageBox.warning(self, "提示", "将更改本广告状态！", QMessageBox.Yes)
        self.carousel_show_signal.emit([carousel_id, checkbox.isChecked()])

    def handle_table_content(self):
        """处理表格信息"""
        for row in range(self.table.rowCount()):
            is_show = int(self.table.item(row, 4).text())
            check_show = SetCarouselCheckBox(row=row, col=4)
            check_show.setChecked(is_show)
            check_show.setStyleSheet("padding-left:80px; background-color:rgb(240,240,240)")  # 左边间距，看起来居中
            check_show.check_change_signal.connect(self.carousel_is_show_changed)
            self.table.setCellWidget(row, 4, check_show)
            # 请求图片显示在表格中
            image_show = QLabel()
            response = requests.get(SERVER_ADDRESS + self.table.item(row, 2).text()[1:])
            image = QPixmap()
            image.loadFromData(response.content)
            image_show.setPixmap(image)
            image_show.setScaledContents(True)  # 图片缩放，适应大小
            self.table.setCellWidget(row, 2, image_show)
