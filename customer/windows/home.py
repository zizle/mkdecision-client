# _*_ coding:utf-8 _*_
# company: RuiDa Futures
# author: zizle
import os
import re
import webbrowser
import fitz
import json
import xlrd
import datetime
from urllib3 import encode_multipart_formdata
import requests
import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSettings

from .home_wickets import MiddleWindowZero, MiddleWindowOne, MiddleWindowTwo, MiddleWindowThree
from widgets import Bulletin
from widgets.public import ListWidget
from widgets.dialog import PDFReaderDialog, ContentReadDialog, ExportEconomicDialog, AddReportDialog,\
    AddNoticeDialog, SetBulletinDialog, SetCarouselDialog, LoadingDialog
from widgets.carousel import CarouselWidget
from utils import get_desktop_path
from threads import RequestThread
import config


class HomePageScrollWindow(QWidget):
    def __init__(self, menus):
        super(HomePageScrollWindow, self).__init__()
        self.menus = menus
        self.__init_ui()

    def __init_ui(self):
        style = """
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
            background:rgba(0,0,0,25%);
            /*滚动条两端变成椭圆*/
            border-radius:4px;

        }
        QScrollBar::handle:vertical:hover
        {
            width:8px;
            /*鼠标放到滚动条上的时候，颜色变深*/
            background:rgba(0,0,0,50%);
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
        layout = QVBoxLayout(spacing=0, margin=0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)  # 充分利用空间，自动填满
        scroll.verticalScrollBar().setStyleSheet(style)
        home = HomePageWindow(menus=self.menus)
        scroll.setWidget(home)
        layout.addWidget(scroll)
        self.setLayout(layout)


class HomePageWindow(QWidget):
    """首页"""
    def __init__(self, menus, *args, **kwargs):
        super(HomePageWindow, self).__init__(*args, **kwargs)
        self.menus = menus
        self.__init_ui()

    def __init_ui(self):
        bc_option_layout = QHBoxLayout()
        add_carousel = QPushButton("设置广告")
        add_carousel.clicked.connect(self.set_carousel_show)
        bc_option_layout.addWidget(add_carousel)
        bc_option_layout.addStretch()

        # 中间QStack
        self.middle_stack = QStackedWidget()
        # 用传入的menu设置左侧QListWidget
        self.list_menu = ListWidget()
        # 设置左侧菜单栏并根据菜单创建窗口
        self.set_list_menu()
        self.list_menu.setWidth(85)
        # list_menu.setHeight(130)
        # list_menu.addItems(["常规报告", "交易通知", "现货报表", "财经日历"])
        # list_menu.init_style(list_menu.item(0))
        self.list_menu.clicked.connect(self.menu_selected)
        # self.middle_w_0 = MiddleWindowZero()  # 常规报告窗口
        # self.middle_w_1 = MiddleWindowOne()  # 交易通知
        # self.middle_w_2 = MiddleWindowTwo()  # 现货报表
        # self.middle_w_3 = MiddleWindowThree()  # 财经日历

        # self.middle_w_0.func_menu.func_signal.connect(self.middle_w_0_func_clicked)  # 常规报告数据类型选择按钮
        # self.middle_w_0.table.page_control_signal.connect(self.middle_w_0_table_turn_page)  # 常规报告表格控制信号
        # self.middle_w_0.table.cell_clicked_signal.connect(self.middle_w_0_table_clicked)  # 常规报告模块表格点击信号
        # self.middle_w_0.add_report.clicked.connect(self.middle_w_0_add_report)  # 添加报告点击

        # self.middle_w_1.fun_menu.func_signal.connect(self.middle_w_1_func_clicked)  # 交易通知模块数据类型选择
        # self.middle_w_1.table.cell_clicked_signal.connect(self.middle_w_1_table_clicked)  # 交易通知模块表格点击信号
        # self.middle_w_1.table.page_control_signal.connect(self.middle_w_1_table_turn_page)  # 交易通知窗口表格控制信号
        # self.middle_w_1.add_notice.clicked.connect(self.middle_w_1_add_notice)

        # self.middle_w_2.add_new_data_signal.connect(self.middle_w_2_add_new_data)  # 确定添加数据
        # self.middle_w_2.height_change_signal.connect(self.change_size_to_current)
        # self.middle_w_2.date_edit.dateChanged.connect(self.middle_w_2_date_edit_changed)  # 现货报表时间发生改变
        # self.middle_w_2.upload_file_data.clicked.connect(self.middle_w_2_upload_file_data)

        # self.middle_w_3.calendar.click_date.connect(self.date_selected)  # 点击日期的响应事件
        # self.middle_w_3.calendar_export.connect(self.middle_w_3_export_calendar)
        # self.middle_w_3.height_change_signal.connect(self.change_size_to_current)
        # self.middle_w_3.add_new_calendar_signal.connect(self.middle_w_3_add_new_data)
        # self.middle_w_3.upload_file_button.clicked.connect(self.middle_w_3_upload_file_data)

        # self.middle_stack.addWidget(self.middle_w_0)
        # self.middle_stack.addWidget(self.middle_w_1)
        # self.middle_stack.addWidget(self.middle_w_2)
        # self.middle_stack.addWidget(self.middle_w_3)
        # 轮播图参数为个数和对应的url
        carouser_data = self.update_carousel()
        carousel = CarouselWidget(data=carouser_data)
        carousel.carousel_clicked.connect(self.carousel_clicked)
        bc_layout = QHBoxLayout()  # 轮播布局
        self.bulletin = Bulletin()
        self.bulletin.cellClicked.connect(self.bulletin_cell_clicked)
        bc_layout.addWidget(self.bulletin)  # 添加公告栏控件
        bc_layout.addWidget(carousel)  # 添加轮播图控件
        func_layout = QHBoxLayout(spacing=10)  # 功能布局
        func_layout.addWidget(self.list_menu, alignment=Qt.AlignTop)
        func_layout.addWidget(self.middle_stack)
        main_layout = QVBoxLayout(spacing=0)  # 主布局
        main_layout.addLayout(bc_option_layout)
        main_layout.addLayout(bc_layout)
        main_layout.addLayout(func_layout)
        main_layout.addStretch()  # 当中心窗口较小时不会挤在一起
        self.setLayout(main_layout)
        self.fill_bulletin_table()
        self.fill_middle_w_0_table()  # 初始化常规报告表格
        self.fill_middle_w_1_table()  # 初始化交易通知表格
        # self.fill_middle_w_2_table()  # 初始化现货报表表格
        # self.fill_middle_w_3_table()  # 初始化财经日历表格

    def bulletin_cell_clicked(self, row, col):
        """公告栏表点击事件"""
        # 请求文件
        if col == 1:
            # url = settings.SERVER_ADDRESS + "homepage/bulletin/"
            item = self.bulletin.item(row, col)
            name_item = self.bulletin.item(row, 0)
            if item.file:
                self.get_server_file(url=config.SERVER_ADDR + item.file, file=item.file, title=name_item.text())
            elif item.content:
                # print(item.content)
                # 弹窗显示内容
                read_dialog = ContentReadDialog(content=item.content, title=name_item.text())
                if not read_dialog.exec():
                    del read_dialog  # 弹窗生命周期未结束,手动删除
            else:
                pass
            
    def carousel_clicked(self, signal):
        """轮播图被点击"""
        # print(signal)
        if signal["show_type"] == "show_file":
            print("展示文件")
            # 将文件请求下来并弹窗显示
            self.get_server_file(url=config.SERVER_ADDRESS + signal["file"][1:], file=signal["file"], title=signal["name"])
        elif signal["show_type"] == "show_text":
            print("展示文字")
            # 弹窗显示内容
            read_dialog = ContentReadDialog(content=signal['content'], title=signal["name"])
            if not read_dialog.exec():
                del read_dialog  # 弹窗生命周期未结束,手动删除
        elif signal["show_type"] == "redirect":
            print("跳转网址")
            webbrowser.open(signal["redirect"])
        else:
            pass
        
    def change_size_to_current(self):
        """中心窗体容器调整自身的固定高度"""
        self.middle_stack.setFixedHeight(self.middle_stack.currentWidget().height())

    def date_selected(self):
        """财经日历被点击"""
        if not self.middle_w_3.table.isHidden():  # table有显示的时候才请求数据
            # 请求数据
            self.fill_middle_w_3_table()

    def download_pdf_file(self, signal):
        """下载当前pdf相关文件"""
        # print(signal)
        # 弹窗
        desktop_path = get_desktop_path()
        save_path = QFileDialog.getExistingDirectory(self, "选择保存的位置", desktop_path)
        if not save_path:
            return

        # 读取缓存的文件，保存到目标目录
        f_open = open("cache/1a2b3c4d5e.file", 'rb')
        save_path = os.path.join(save_path, signal[0] + ".pdf")
        f_save = open(save_path, 'wb')
        while True:
            content = f_open.read(1024)
            f_save.write(content)
            if not content:
                break
        f_open.close()
        f_save.close()
        QMessageBox.information(self, "完成", "下载完成！", QMessageBox.Yes)

    @staticmethod
    def export_economic_calendar_confirm(signal):
        """导出财经日历对话框确定按钮点击"""
        print(signal)
        # 获取开始时间，结束时间，以及保存的路径

    def fill_bulletin_table(self):
        """公告栏内容"""
        self.bulletin_loading = LoadingDialog(self.bulletin)
        self.bulletin_loading.move(100, 20)
        url = config.SERVER_ADDR + "homepage/bulletin/"
        headers = {"User-Agent": "DAssistant-Client/" + config.VERSION}
        cookies = config.app_dawn.value('cookies')
        print("请求头", )
        self.fill_bulletin_thread = RequestThread(
            url=url,
            method='get',
            headers=headers,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=cookies
        )
        self.fill_bulletin_thread.response_signal.connect(self.fill_bulletin_table_content)
        self.fill_bulletin_thread.finished.connect(self.fill_bulletin_thread.deleteLater)
        self.fill_bulletin_thread.start()

    def fill_bulletin_table_content(self, content):
        """线程返回数据填充表格"""
        self.bulletin_loading.hide()
        if content["error"]:
            # 错误不做处理，直接无数据显示
            pass
        data = content["data"]
        keys = ["name", "file", "create_time"]
        self.bulletin.setDataContents(data, keys=keys, button_col=1)

    def fill_middle_w_0_table(self, data_type="all", current_page=1):
        """常规报告内容初始化(第一页内容,不分类型)"""
        # 检查是否有这个窗口
        for i in range(self.middle_stack.count()):
            frame_window = self.middle_stack.widget(i)
            if frame_window.name == "常规报告":
                # 清除table
                self.middle_w_0.table_hide()
                # 所有按钮不可点
                self.middle_w_0.set_menu_enable(False)
                # 显示加载
                self.middle_0_loading = LoadingDialog(self.middle_w_0)
                self.middle_0_loading.move(400, 50)
                self.middle_0_loading.show()
                # 请求数据
                headers = {"User-Agent": "DAssistant-Client/" + config.VERSION}
                # 设置线程加载
                self.middle_0_thread = RequestThread(
                    url=config.SERVER_ADDR + "homepage/report/{}/?count={}&page={}".format(data_type, config.HOMEPAGE_REPORT_PAGE_COUNT,current_page),
                    method='get',
                    headers=headers
                )
                self.middle_0_thread.response_signal.connect(self.fill_middle_0_table_content)
                self.middle_0_thread.finished.connect(self.middle_0_thread.deleteLater)
                self.middle_0_thread.start()

        # response = requests.get(url=settings.SERVER_ADDRESS + "homepage/report/{}/?count={}&page={}".format(data_type,settings.HOMEPAGE_REPORT_PAGE_COUNT,current_page), headers=headers)
        # data = json.loads(response.content.decode("utf-8"))
        # count = data["count"]  # 数据总长度
        # total_page = math.ceil(count / settings.HOMEPAGE_REPORT_PAGE_COUNT)  # 总页数
        # # 没有数据时总页码为0，加1，方便去除页码控制器
        # if not total_page:
        #     total_page += 1
        # if not data["next"]:
        #     server_current_page = total_page
        # else:
        #     server_current_page = int(re.search(r'page=(.*)', data["next"]).group(1)) - 1
        # data = {
        #     "type": "all",
        #     "total_page": total_page,
        #     "current_page": server_current_page,
        #     "content": data["results"]
        # }
        # # 准备假数据
        # # data = {
        # #     "type": "all",
        # #     "total_page": 1,
        # #     "current_page": 1,
        # #     "content": [
        # #          {
        # #             "id": 8,
        # #             "date": "2019年05月01日",
        # #             "title": "常规报告-年报",
        # #             "type_en": "annual",
        # #             "type_cn": "年报",
        # #             "file": "http://www.yy.com/reports/8",
        # #             "time": "2019-05-06 11:26:47"
        # #         }
        # #     ] * 6
        # # }
        # keys = [("create_time", "日期"), ("name", "标题"), ("type_cn", "类型"), ("update_time", "时间")]
        # total_page = data["total_page"]
        # if current_page != data["current_page"]:
        #     QMessageBox.warning(self, "警告", "数据出现错误", QMessageBox.Yes)
        #     return
        # # 如果总页码为1且有页码控制器就移除
        # # print("总页码", data["total_page"])
        # # print("是否有控制器", self.middle_w_0.table.hasPageController)
        # if data["total_page"] == 1 and self.middle_w_0.table.hasPageController:
        #     self.middle_w_0.table.removePageController()
        # # 如果页码大于1且没有页码控制器就设置页码控制器
        # if total_page > 1 and not self.middle_w_0.table.hasPageController:
        #     self.middle_w_0.table.setPageController(total_page)
        # if self.middle_w_0.table.hasPageController:
        #     self.middle_w_0.table.curPage.setText(str(current_page))
        #     self.middle_w_0.table.setTableTotalPageCount(total_page)
        # # 设置内容
        # self.middle_w_0.table.setDataContents(data["content"], keys=keys, id_col=1, id_key="file")
        # self.change_size_to_current()

    def fill_middle_0_table_content(self, data):
        """线程数据回来填充"""
        self.middle_0_loading.hide()
        self.middle_w_0.table_show()
        self.middle_w_0.set_menu_enable(True)
        if data['error'] is True:
            QMessageBox.information(self, "错误", '请求常规报告数据失败!', QMessageBox.Yes)
            return
        count = data["count"]  # 数据总长度
        total_page = math.ceil(count / config.HOMEPAGE_REPORT_PAGE_COUNT)  # 总页数
        # 没有数据时总页码为0，加1，方便去除页码控制器
        if not total_page:
            total_page += 1
        if not data["next"]:
            server_current_page = total_page
        else:
            server_current_page = int(re.search(r'page=(.*)', data["next"]).group(1)) - 1
        data = {
            "type": "all",
            "total_page": total_page,
            "current_page": server_current_page,
            "content": data["results"]
        }
        keys = [("create_time", "日期"), ("name", "标题"), ("type_cn", "类型"), ("update_time", "时间")]
        total_page = data["total_page"]
        # if current_page != data["current_page"]:
        #     QMessageBox.warning(self, "警告", "数据出现错误", QMessageBox.Yes)
        #     return
        # 如果总页码为1且有页码控制器就移除
        # print("总页码", data["total_page"])
        # print("是否有控制器", self.middle_w_0.table.hasPageController)
        if data["total_page"] == 1 and self.middle_w_0.table.hasPageController:
            self.middle_w_0.table.removePageController()
        # 如果页码大于1且没有页码控制器就设置页码控制器
        if total_page > 1 and not self.middle_w_0.table.hasPageController:
            self.middle_w_0.table.setPageController(total_page)
        if self.middle_w_0.table.hasPageController:
            self.middle_w_0.table.curPage.setText(str(data["current_page"]))
            self.middle_w_0.table.setTableTotalPageCount(total_page)
        # 设置内容
        self.middle_w_0.table.setDataContents(data["content"], keys=keys, id_col=1, id_key="file")
        self.change_size_to_current()

    def fill_middle_w_1_table(self, data_type="all", current_page=1):
        """初始化交易通知内容(第一页内容,不分类型)"""
        for i in range(self.middle_stack.count()):
            frame_window = self.middle_stack.widget(i)
            if frame_window.name == '交易通知':
                # 清除table
                self.middle_w_1.table_hide()
                # 所有按钮不可点
                self.middle_w_1.set_menu_enable(False)
                # 显示加载
                self.middle_1_loading = LoadingDialog(self.middle_w_1)
                self.middle_1_loading.move(400, 50)
                self.middle_1_loading.show()
                # 请求数据
                headers = config.CLIENT_HEADERS
                self.middle_1_thread = RequestThread(
                    url=config.SERVER_ADDR + "homepage/notice/{}/?count={}&page={}".format(data_type, config.HOMEPAGE_NOTICE_PAGE_COUNT, current_page),
                    method='get',
                    headers=headers,
                )
                self.middle_1_thread.response_signal.connect(self.fill_middle_1_table_content)
                self.middle_1_thread.finished.connect(self.middle_1_thread.deleteLater)
                self.middle_1_thread.start()

        # response = requests.get(url=settings.SERVER_ADDRESS + "homepage/notice/{}/?count={}&page={}".format(data_type, settings.HOMEPAGE_NOTICE_PAGE_COUNT, current_page), headers=headers)
        # data = json.loads(response.content.decode("utf-8"))
        # count = data["count"]  # 数据总长度
        # total_page = math.ceil(count / settings.HOMEPAGE_REPORT_PAGE_COUNT)  # 总页数
        # # 没有数据时总页码为0，加1，方便去除页码控制器
        # if not total_page:
        #     total_page += 1
        # if not data["next"]:
        #     server_current_page = total_page
        # else:
        #     server_current_page = int(re.search(r'page=(.*)', data["next"]).group(1)) - 1
        # data = {
        #     "type": "all",
        #     "total_page": total_page,
        #     "current_page": server_current_page,
        #     "content": data["results"]
        # }
        # # print("交易通知初始化数据:\n", data)
        # # 准备假数据
        # # data = {
        # #     "total_page": 1,
        # #     "current_page": 1,
        # #     "type": "choose",
        # #     "content": [
        # #         {
        # #            "id": 1,
        # #            "date": "2019年05月06日",
        # #            "title": "上海期货交易所铜交易通知",
        # #            "type_cn": "交易所",
        # #            "file": "http://www.yy.com/change-noticefile/1",
        # #            "time": "2019-05-06 15:38:19"
        # #         }
        # #     ] * 5
        # # }
        # if current_page != data["current_page"]:
        #     QMessageBox.warning(self, "警告", "数据出现错误", QMessageBox.Yes)
        #     return
        # if data["total_page"] == 1 and self.middle_w_1.table.hasPageController:
        #     self.middle_w_1.table.removePageController()
        #
        # if data["total_page"] > 1 and not self.middle_w_1.table.hasPageController:
        #     self.middle_w_1.table.setPageController(data["total_page"])
        # if self.middle_w_1.table.hasPageController:
        #     self.middle_w_1.table.curPage.setText(str(data["current_page"]))
        #     self.middle_w_1.table.setTableTotalPageCount(data["total_page"])
        # # 设置内容
        # keys = [("create_time", "日期"), ("name", "标题"), ("type_cn", "类型"), ("update_time", "时间")]
        # self.middle_w_1.table.setDataContents(data["content"], keys=keys, id_col=1, id_key="file")
        # self.change_size_to_current()

    def fill_middle_1_table_content(self, data):
        """线程数据返回填充数据"""
        self.middle_1_loading.hide()
        self.middle_w_1.table_show()
        self.middle_w_1.set_menu_enable(True)
        if data['error'] is True:
            # QMessageBox.information(self, "错误", '请求交易通知数据失败!', QMessageBox.Yes)
            return
        count = data["count"]  # 数据总长度
        total_page = math.ceil(count / config.HOMEPAGE_REPORT_PAGE_COUNT)  # 总页数
        # 没有数据时总页码为0，加1，方便去除页码控制器
        if not total_page:
            total_page += 1
        if not data["next"]:
            server_current_page = total_page
        else:
            server_current_page = int(re.search(r'page=(.*)', data["next"]).group(1)) - 1
        data = {
            "type": "all",
            "total_page": total_page,
            "current_page": server_current_page,
            "content": data["results"]
        }
        if data["total_page"] == 1 and self.middle_w_1.table.hasPageController:
            self.middle_w_1.table.removePageController()

        if data["total_page"] > 1 and not self.middle_w_1.table.hasPageController:
            self.middle_w_1.table.setPageController(data["total_page"])
        if self.middle_w_1.table.hasPageController:
            self.middle_w_1.table.curPage.setText(str(data["current_page"]))
            self.middle_w_1.table.setTableTotalPageCount(data["total_page"])
        # 设置内容
        keys = [("create_time", "日期"), ("name", "标题"), ("type_cn", "类型"), ("update_time", "时间")]
        self.middle_w_1.table.setDataContents(data["content"], keys=keys, id_col=1, id_key="file")
        self.change_size_to_current()

    def fill_middle_w_2_table(self, date=None):
        """初始化现货报表表格首页显示"""
        if not date:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
        headers = settings.CLIENT_HEADERS
        response = requests.get(url=settings.SERVER_ADDRESS + "homepage/stock/?date={}".format(date), headers=headers)
        response_data = json.loads(response.content.decode("utf-8"))
        keys = [("variety", "品种"), ("area", "地区"), ("level", "等级"), ("price", "报价"), ("date", "日期"), ("note", "备注")]
        self.middle_w_2.table.setDataContents(response_data["data"], keys=keys)
        self.change_size_to_current()

    def fill_middle_w_3_table(self):
        """初始化财经日历表格"""
        # 获取日期
        current_date = str(self.middle_w_3.calendar.date.toPyDate())
        headers = config.CLIENT_HEADERS
        headers["Content-Type"] = "application/json"  # 请求体参数类型必须带
        data_body = json.dumps({
            "type": "daily",
            "date": current_date
        })
        # 请求数据
        response = requests.get(url=config.SERVER_ADDRESS + "homepage/calendar/", headers=headers, data=data_body)
        response_data = json.loads(response.content.decode("utf-8"))
        # print(response_data)
        data = {
            "date": response_data["message"],
            "content": response_data["data"]
        }
        # 数据
        # data = {
        #     "date": "2019-05-30",
        #     "content": [
        #         {
        #             "time": "2019-05-30 06:00",
        #             "country": "美国",
        #             "event": "美国副总统彭斯将于5月30日前往加拿大渥太华，与加拿大总理特鲁多就尽快推进美墨加协议（USMCA）举行会谈",
        #             "expected": "-"
        #         }
        #     ]
        # }
        keys = [("time", "时间"), ("country", "地区"), ("event", "事件描述"), ("expected", "预期值")]
        self.middle_w_3.table.setDataContents(data=data["content"], keys=keys)
        self.change_size_to_current()

    def fill_set_carousel_table(self, current_page=1):
        """填充设置轮播的的表格"""
        headers = config.CLIENT_HEADERS
        data = json.dumps({"client": config.IDENTIFY_CODE})
        response = requests.get(url=config.SERVER_ADDRESS + "homepage/carousel/list/?count={}&page={}".format(5, current_page), headers=headers, data=data)
        response_data = json.loads(response.content.decode("utf-8"))
        # print(response_data)
        count = response_data["count"]  # 数据总长度
        total_page = math.ceil(count / 5)  # 总页数(一次展示4个)
        # 没有数据时总页码为0，加1，方便去除页码控制器
        if not total_page:
            total_page += 1
        if not response_data["next"]:
            server_current_page = total_page
        else:
            server_current_page = int(re.search(r'page=(.*)', response_data["next"]).group(1)) - 1
        data = {
            "total_page": total_page,
            "current_page": server_current_page,
            "content": response_data["results"]
        }
        total_page = data["total_page"]
        if current_page != data["current_page"]:
            QMessageBox.warning(self, "警告", "数据出现错误", QMessageBox.Yes)
            return
        # 如果总页码为1且有页码控制器就移除
        # print("总页码", data["total_page"])
        # print("是否有控制器", self.set_carousel_dialog.table.hasPageController)
        if data["total_page"] == 1 and self.set_carousel_dialog.table.hasPageController:
            self.set_carousel_dialog.table.removePageController()
        # 如果页码大于1且没有页码控制器就设置页码控制器
        if total_page > 1 and not self.set_carousel_dialog.table.hasPageController:
            self.set_carousel_dialog.table.setPageController(total_page)
        if self.set_carousel_dialog.table.hasPageController:
            self.set_carousel_dialog.table.curPage.setText(str(current_page))
            self.set_carousel_dialog.table.setTableTotalPageCount(total_page)
        # 设置内容
        keys = [("create_time", "创建日期"), ("name", "名称"), ("image", "图片"), ("show_type", "展示方式"), ("is_show", "显示")]
        self.set_carousel_dialog.table.setDataContents(data["content"], keys=keys, id_col=4, id_key="id")
        self.set_carousel_dialog.handle_table_content()

    def get_server_file(self, url, file, title):
        """获取文件"""
        # 请求文件
        headers = {"User-Agent": "DAssistant-Client/" + config.VERSION}
        try:
            response = requests.get(url=url, headers=headers, data={"file": file})
            f = open("cache/1a2b3c4d5e.file", "wb")
            f.write(response.content)
            f.close()
        except Exception as e:
            print(e)
            return
        doc = fitz.open("cache/1a2b3c4d5e.file")
        # 弹窗显示相应文件内容
        read_dialog = PDFReaderDialog(doc, file=file, title=title)
        read_dialog.download_file_signal.connect(self.download_pdf_file)
        if not read_dialog.exec():
            del read_dialog  # 弹窗生命周期未结束,手动删除
        
    def menu_selected(self, index):
        """左侧QListWidgetItem点击事件"""
        item_widget = self.list_menu.currentItem()
        frame_id = list()
        # 遍历窗口
        for index in range(self.middle_stack.count()):
            frame_window = self.middle_stack.widget(index)
            if frame_window.id == item_widget.id:
                # 显示这个窗口
                self.middle_stack.setCurrentWidget(frame_window)
                self.change_size_to_current()
            frame_id.append(frame_window.id)
        if item_widget.id not in frame_id:
            QMessageBox.information(self, "提示", "本功能未开放，敬请期待!", QMessageBox.Yes)

    def middle_w_0_add_report(self):
        """添加报告弹窗"""
        self.add_report_dialog = AddReportDialog()
        self.add_report_dialog.upload_report_signal.connect(self.middle_w_0_upload_report)
        if not self.add_report_dialog.exec():
            del self.add_report_dialog

    def middle_w_0_func_clicked(self, menu):
        """常规窗口类型按钮点击"""
        if menu == "全部":
            self.middle_w_0.data_type = "all"
        elif menu == "日报":
            self.middle_w_0.data_type = "daily"
        elif menu == "周报":
            self.middle_w_0.data_type = "weekly"
        elif menu == "月报":
            self.middle_w_0.data_type = "monthly"
        elif menu == "年报":
            self.middle_w_0.data_type = "annual"
        elif menu == "专题":
            self.middle_w_0.data_type = "special"
        elif menu == "投资报告":
            self.middle_w_0.data_type = "invest"
        elif menu == "其他":
            self.middle_w_0.data_type = "others"
        else:
            return
        self.fill_middle_w_0_table(data_type=self.middle_w_0.data_type, current_page=1)
        self.change_size_to_current()

    def middle_w_0_table_clicked(self, pos):
        """常规报告表格Item点击传出信号处理"""
        if 1 == pos[1]:
            item = self.middle_w_0.table.table.item(pos[0], pos[1])
            url = config.SERVER_ADDRESS + "homepage/report/file/"
            self.get_server_file(url=url, file=item.id_key, title=item.text())

    def middle_w_0_table_turn_page(self, signal):
        """常规窗口页码点击"""
        current_page = self.page_index_controller(self.middle_w_0, signal)  # 需要请求的页数
        if not current_page:
            return
        # 将内容逐条展示在表格中
        data_type = self.middle_w_0.data_type
        self.fill_middle_w_0_table(data_type=data_type, current_page=current_page)

    def middle_w_0_upload_report(self, signal):
        """上传报告"""
        response = self.upload_media_file(
            url=config.SERVER_ADDR + "homepage/report/",
            file_path=signal[0],
            file_type_en=signal[1],
            file_show_name=signal[2]
        )
        if response.status_code == 201:
            QMessageBox.information(self, "成功", "上传成功!", QMessageBox.Yes)
            self.add_report_dialog.close()
        else:
            QMessageBox.warning(self, "失败", "上传失败!", QMessageBox.Yes)

        # if response_data["status"] == 200:
        #     QMessageBox.information(self, "成功", "上传成功!", QMessageBox.Yes)
        #     self.add_report_dialog.close()
        # else:
        #     QMessageBox.warning(self, "失败", "上传失败!", QMessageBox.Yes)

    def middle_w_1_add_notice(self):
        #print("添加通知文件")
        self.add_notice_dialog = AddNoticeDialog()
        self.add_notice_dialog.upload_notice_signal.connect(self.middle_w_1_upload_notice)
        if not self.add_notice_dialog.exec():
            del self.add_notice_dialog

    def middle_w_1_func_clicked(self, menu):
        """交易通知数据类型点击"""
        if menu == "全部":
            self.middle_w_1.data_type = "all"
        elif menu == "公司":
            self.middle_w_1.data_type = "company"
        elif menu == "交易所":
            self.middle_w_1.data_type = "change"
        elif menu == "系统":
            self.middle_w_1.data_type = "system"
        elif menu == "其他":
            self.middle_w_1.data_type = 'others'
        else:
            return
        self.fill_middle_w_1_table(data_type=self.middle_w_1.data_type, current_page=1)
        self.change_size_to_current()

    def middle_w_1_table_clicked(self, pos):
        """交易通知表格Item点击传出信号处理"""
        if 1 == pos[1]:
            item = self.middle_w_1.table.table.item(pos[0], pos[1])
            url = config.SERVER_ADDRESS + "homepage/notice/file/"
            self.get_server_file(url=url, file=item.id_key, title=item.text())

    def middle_w_1_table_turn_page(self, signal):
        """交易通知页码点击"""
        current_page = self.page_index_controller(self.middle_w_1, signal)
        if not current_page:
            return
        data_type = self.middle_w_1.data_type
        self.fill_middle_w_1_table(data_type=data_type, current_page=current_page)

    def middle_w_1_upload_notice(self, signal):
        print(signal)
        response_data = self.upload_media_file(
            url=config.SERVER_ADDRESS + "homepage/notice/",
            file_path=signal[0],
            file_type_en=signal[1],
            file_show_name=signal[2]
        )
        if response_data["status"] == 200:
            QMessageBox.information(self, "成功", "上传成功!", QMessageBox.Yes)
            self.add_notice_dialog.close()
        else:
            QMessageBox.warning(self, "失败", "上传失败!\n" + response_data["message"], QMessageBox.Yes)

    def middle_w_2_add_new_data(self):
        """现货报表添加数据"""
        data_set = []
        # 获取表格, 获取数据整理为json
        table = self.middle_w_2.add_data_table
        header_labels = ["variety", "area", "level", "price", "date", "note"]
        for row in range(table.rowCount()):
            item = dict()
            for col in range(table.columnCount()):
                col_item = table.item(row, col)
                if not col_item or not col_item.text():
                    continue
                item[header_labels[col]] = col_item.text()
            # 验证信息
            print(item)
            for key in header_labels:
                if key == "note":
                    continue
                if len(item) > 1 and not item.get(key):
                    QMessageBox.warning(self, "错误", "请将信息填写完整!", QMessageBox.Yes)
                    return
            if len(item) >= 5:
                data_set.append(item)
        if not data_set:
            QMessageBox.warning(self, "错误", "您未填写任何信息!", QMessageBox.Yes)
            return
        table.clear()
        table.setHorizontalHeaderLabels(["品种", "地区", "等级", "报价", "时间", "备注"])
        data = json.dumps(data_set)
        # 上传数据
        headers = config.CLIENT_HEADERS
        headers["Content-Type"] = "application/json"
        response = requests.post(url=config.SERVER_ADDRESS + "homepage/stock/", headers=headers, data=data)
        response_data = json.loads(response.content.decode("utf-8"))
        if response_data["status"] == 200:
            QMessageBox.information(self, "成功", response_data["message"] + "\n返回查看数据。", QMessageBox.Yes)
        if response_data["status"] == 400:
            QMessageBox.information(self, "成功", response_data["message"], QMessageBox.Yes)

    def middle_w_2_date_edit_changed(self, date):
        """时间选择发生改变"""
        self.fill_middle_w_2_table(date=str(date.toPyDate()))

    def middle_w_2_upload_file_data(self):
        """现货报表上传文件数据"""
        # 弹窗选择文件
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.xlsx *.xls)")
        if not file_path:
            return
        rf = xlrd.open_workbook(filename=file_path)
        sheet1 = rf.sheet_by_index(0)
        row_header = sheet1.row_values(0)
        # 表头错误即就不能读取
        header_labels = ["品种", "地区", "等级", "报价", "日期", "备注"]
        if row_header != header_labels:
            return
        # 对表格设置行数，列数
        self.middle_w_2.add_data_table.set_rc_labels(row=sheet1.nrows - 1, col=len(header_labels), labels=header_labels)  # 不用表头
        # 遍历行
        for row in range(1, sheet1.nrows):
            row_content = sheet1.row_values(row)
            row_content[4] = datetime.datetime.strftime(xlrd.xldate_as_datetime(row_content[4], rf.datemode), "%Y-%m-%d")
            # 填入表格
            self.middle_w_2.add_data_table.set_row_content(row - 1, row_content)
        self.change_size_to_current()

    def middle_w_3_add_new_data(self):
        """确定提交新的财经日历按钮点击"""
        data_set = []
        table = self.middle_w_3.add_data_table
        header_labels = ["date", "time", "country", "event", "expected"]
        for row in range(table.rowCount()):
            item = dict()
            for col in range(table.columnCount()):
                col_item = table.item(row, col)
                if not col_item:
                    continue
                item[header_labels[col]] = col_item.text()
            # 验证信息
            for key in header_labels:
                if not item.get(key):
                    QMessageBox.warning(self, "错误", "请将信息填写完整!", QMessageBox.Yes)
            # 验证过关加入data
            data_set.append(item)
        if not data_set:
            QMessageBox.warning(self, "错误", "您未填写任何信息!", QMessageBox.Yes)
            return
        data = json.dumps(data_set)
        # 上传数据
        headers = config.CLIENT_HEADERS
        headers["Content-Type"] = "application/json"
        response = requests.post(url=config.SERVER_ADDRESS + "homepage/calendar/", headers=headers, data=data)
        response_data = json.loads(response.content.decode("utf-8"))
        # print(response_data)
        if response_data["status"] == 200:
            table.clear()
            table.setHorizontalHeaderLabels(["日期", "时间", "地区", "事件描述", "预期值"])
            QMessageBox.information(self, "成功", response_data["message"] + "\n返回查看数据。", QMessageBox.Yes)
        if response_data["status"] == 400:
            QMessageBox.information(self, "失败", response_data["message"], QMessageBox.Yes)

    def middle_w_3_export_calendar(self):
        """导出财经日历按钮被点击"""
        #print("导出财经日历")
        dialog = ExportEconomicDialog()
        dialog.export_data_signal.connect(self.export_economic_calendar_confirm)
        if not dialog.exec():
            del dialog

    def middle_w_3_upload_file_data(self):
        """上传文件财经日历"""
        # 弹窗选择文件
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.xlsx *.xls)")
        if not file_path:
            return
        rf = xlrd.open_workbook(filename=file_path)
        sheet1 = rf.sheet_by_index(0)
        row_header = sheet1.row_values(0)
        # 表头错误即就不能读取
        header_labels = ["日期", "时间", "地区", "事件描述", "预期值"]
        if row_header != header_labels:
            return
        # 对表格设置行数，列数
        self.middle_w_3.add_data_table.set_rc_labels(row=sheet1.nrows - 1, col=len(header_labels), labels=header_labels)  # 不用表头
        # 遍历行
        for row in range(1, sheet1.nrows):
            row_content = sheet1.row_values(row)
            # 处理日期与事件
            row_content[0] = datetime.datetime.strftime(xlrd.xldate_as_datetime(row_content[0], rf.datemode), "%Y-%m-%d")
            row_content[1] = datetime.datetime.strftime(xlrd.xldate_as_datetime(row_content[1], rf.datemode), "%H:%M")
            # 填入表格
            self.middle_w_3.add_data_table.set_row_content(row - 1, row_content)
        self.change_size_to_current()

    def page_index_controller(self, window, signal):
        """页码控制器"""
        total_page = window.table.totalPage()
        if "home" == signal[0]:
            window.table.curPage.setText("1")
        elif "pre" == signal[0]:
            window.table.curPage.setText(str(int(signal[1]) - 1))
        elif "next" == signal[0]:
            window.table.curPage.setText(str(int(signal[1]) + 1))
        elif "final" == signal[0]:
            window.table.curPage.setText(str(total_page))
        elif "confirm" == signal[0]:
            if total_page < int(signal[1]) or int(signal[1]) < 0:
                QMessageBox.information(self, "提示", "跳转页码超出范围", QMessageBox.Yes)
                return None
            window.table.curPage.setText(signal[1])
        return int(window.table.curPage.text())

    def set_bulletin_data(self, signal):
        """设置好的公告内容上传"""
        headers = config.CLIENT_HEADERS
        cookies = config.app_dawn.value('cookies')
        client = config.app_dawn.value("machine")
        if signal["set_option"] == "new_bulletin":
            data = dict()
            data["name"] = signal["name"]
            data["show_type"] = signal["show_type"]
            data['machine_code'] = client
            if signal["show_type"] == "show_file":
                file_raw_name = signal["file"].rsplit("/", 1)
                file = open(signal["file"], "rb")
                file_content = file.read()
                file.close()
                data["file"] = (file_raw_name[1], file_content)
            elif signal["show_type"] == "show_text":
                data["content"] = signal["content"]
            encode_data = encode_multipart_formdata(data)
            data = encode_data[0]
            headers['Content-Type'] = encode_data[1]
            # response = requests.post(url=config.SERVER_ADDRESS + "homepage/bulletin/", headers=headers, data=data)
            response = requests.post(
                url=config.SERVER_ADDR + "homepage/bulletin/",
                headers=headers,
                data=data,
                cookies=cookies
            )
            response_data = json.loads(response.content.decode("utf-8"))
            self.set_bulletin_dialog.close()
            QMessageBox.information(self, "提示", response_data["message"], QMessageBox.Yes)
            self.fill_bulletin_table()
        elif signal["set_option"] == "days":
            # 发起请求
            headers = config.CLIENT_HEADERS
            client = config.app_dawn.value("machine")
            # url = config.SERVER_ADDRESS + 'system/bulletin_days/?days={}'.format(signal["days"])
            url = config.SERVER_ADDR + "limits/client/"
            response = requests.put(
                url=url,
                headers=headers,
                data=json.dumps({
                    "bulletin_days": signal["days"],
                    "machine_code": client
                }),
                cookies=cookies
            )
            response_data = json.loads(response.content.decode('utf-8'))
            if response.status_code == 200:
                self.set_bulletin_dialog.close()
                QMessageBox.information(self, "成功", response_data["message"], QMessageBox.Yes)
            else:
                QMessageBox.warning(self, "失败", response_data["message"], QMessageBox.Yes)
        else:
            pass
        
    def set_carousel_image(self, signal):
        """设置广告轮播图信息"""
        # print(signal)
        headers = config.CLIENT_HEADERS
        # 处理信号信息
        data = dict()
        data["name"] = signal["name"]
        data["show_type"] = signal["show_type"]
        image_raw_name = signal["image"].rsplit("/", 1)
        image = open(signal["image"], "rb")
        image_content = image.read()
        image.close()
        data["image"] = (image_raw_name[1], image_content)
        if signal["show_type"] == "show_file":
            file_raw_name = signal["file"].rsplit("/", 1)
            file = open(signal["file"], "rb")
            file_content = file.read()
            file.close()
            data["file"] = (file_raw_name[1], file_content)
        data["redirect"] = signal["redirect"]
        data["content"] = signal["content"]
        encode_data = encode_multipart_formdata(data)
        data = encode_data[0]
        headers['Content-Type'] = encode_data[1]
        response = requests.post(url=config.SERVER_ADDRESS + "homepage/carousel/", headers=headers, data=data)
        response_data = json.loads(response.content.decode("utf-8"))
        self.set_carousel_dialog.close()
        QMessageBox.information(self, "提示", response_data["message"], QMessageBox.Yes)
    
    def set_carousel_show(self):
        """设置广告"""
        self.set_carousel_dialog = SetCarouselDialog()
        self.set_carousel_dialog.carousel_show_signal.connect(self.show_carousel_or_not)
        self.set_carousel_dialog.add_widget.upload_carousel_signal.connect(self.set_carousel_image)
        self.set_carousel_dialog.upload_carousel_signal.connect(self.set_carousel_image)
        self.set_carousel_dialog.table.page_control_signal.connect(self.set_carousel_turn_page)
        self.fill_set_carousel_table()
        _exec = self.set_carousel_dialog.exec()
        if not _exec:
            del self.set_carousel_dialog

    def set_carousel_turn_page(self, signal):
        """广告展示弹窗页码点击"""
        current_page = self.page_index_controller(self.set_carousel_dialog, signal)  # 需要请求的页数
        if not current_page:
            return
        self.fill_set_carousel_table(current_page=current_page)

    def set_list_menu(self):
        """设置左侧菜单栏"""
        self.list_menu.setHeight(32.5 * len(self.menus))
        if self.menus:
            print(self.menus)
            for item in self.menus:
                # 创建list元素实例
                list_menu = QListWidgetItem(item["name"])
                list_menu.id = item["id"]
                list_menu.name = item["name"]
                self.list_menu.addItem(list_menu)
                # 创建窗口实例,并赋予属性
                if item["name"] == "常规报告":
                    self.middle_w_0 = MiddleWindowZero()
                    self.middle_w_0.id = item["id"]
                    self.middle_w_0.name = item["name"]
                    # 绑定事件
                    self.middle_w_0.func_menu.func_signal.connect(self.middle_w_0_func_clicked)  # 常规报告数据类型选择按钮
                    self.middle_w_0.table.page_control_signal.connect(self.middle_w_0_table_turn_page)  # 常规报告表格控制信号
                    self.middle_w_0.table.cell_clicked_signal.connect(self.middle_w_0_table_clicked)  # 常规报告模块表格点击信号
                    self.middle_w_0.add_report.clicked.connect(self.middle_w_0_add_report)  # 添加报告点击
                    # 加入中间堆栈
                    self.middle_stack.addWidget(self.middle_w_0)
                elif item["name"] == "交易通知":
                    self.middle_w_1 = MiddleWindowOne()
                    self.middle_w_1.id = item["id"]
                    self.middle_w_1.name = item["name"]
                    self.middle_w_1.fun_menu.func_signal.connect(self.middle_w_1_func_clicked)  # 交易通知模块数据类型选择
                    self.middle_w_1.table.cell_clicked_signal.connect(self.middle_w_1_table_clicked)  # 交易通知模块表格点击信号
                    self.middle_w_1.table.page_control_signal.connect(self.middle_w_1_table_turn_page)  # 交易通知窗口表格控制信号
                    self.middle_w_1.add_notice.clicked.connect(self.middle_w_1_add_notice)
                    self.middle_stack.addWidget(self.middle_w_1)
                elif item["name"] == "现货报表":
                    self.middle_w_2 = MiddleWindowTwo(menus=item['subs'])
                    self.middle_w_2.id = item["id"]
                    self.middle_w_2.name = item["name"]
                    self.middle_w_2.add_new_data_signal.connect(self.middle_w_2_add_new_data)  # 确定添加数据
                    self.middle_w_2.height_change_signal.connect(self.change_size_to_current)
                    self.middle_w_2.date_edit.dateChanged.connect(self.middle_w_2_date_edit_changed)  # 现货报表时间发生改变
                    self.middle_w_2.upload_file_data.clicked.connect(self.middle_w_2_upload_file_data)
                    self.middle_stack.addWidget(self.middle_w_2)
                elif item["name"] == "财经日历":
                    self.middle_w_3 = MiddleWindowThree(menus=item["subs"])
                    self.middle_w_3.id = item["id"]
                    self.middle_w_3.name = item["name"]
                    self.middle_w_3.calendar.click_date.connect(self.date_selected)  # 点击日期的响应事件
                    self.middle_w_3.calendar_export.connect(self.middle_w_3_export_calendar)
                    self.middle_w_3.height_change_signal.connect(self.change_size_to_current)
                    self.middle_w_3.add_new_calendar_signal.connect(self.middle_w_3_add_new_data)
                    self.middle_w_3.upload_file_button.clicked.connect(self.middle_w_3_upload_file_data)
                    self.middle_stack.addWidget(self.middle_w_3)
                else:
                    pass

    def show_carousel_or_not(self, signal):
        """设置某个广告的显示与否"""
        # 网络请求更改轮播图显示与否
        headers = config.CLIENT_HEADERS
        data = json.dumps({
            "client": config.IDENTIFY_CODE,
            "id": signal[0],
            "show": signal[1]
        })
        response = requests.put(url=config.SERVER_ADDRESS + "homepage/carousel/", headers=headers, data=data)
        response_data = json.loads(response.content.decode("utf-8"))
        if response_data["status"] == 205:
            option = QMessageBox.information(self.set_carousel_dialog, "提示", "修改成功.重启生效!\n继续设置？", QMessageBox.Yes | QMessageBox.No)
            if option == QMessageBox.Yes:
                pass
            else:
                self.set_carousel_dialog.close()
        elif response_data["status"] == 403:
            QMessageBox.warning(self.set_carousel_dialog, "警告", "这是仅存可以见光的广告!\n此修改无效。", QMessageBox.Yes)
            self.set_carousel_dialog.close()
        else:
            QMessageBox.information(self.set_carousel_dialog, "提示", "修改失败!", QMessageBox.Yes)

    @staticmethod
    def update_carousel():
        """是否更新轮播"""
        # 请求查询数据库
        headers = {"User-Agent": "DAssistant-Client/" + config.VERSION}
        machine_code = config.app_dawn.value('machine')
        url = config.SERVER_ADDR + "homepage/carousel/"
        try:
            response = requests.get(url=url, headers=headers, data={"client": machine_code})
            data = json.loads(response.content.decode("utf-8"))
        except Exception as e:
            print('轮播图信息请求失败')
            return
        # print(data)
        if data["update"]:
            print("本客户端需要更新")
            carousel_data = list()
            url = config.SERVER_ADDR + "homepage/carousel/"
            for index, image_data in enumerate(data["data"]):
                each_carousel = dict()
                response = requests.get(url=url, headers=headers, data={"image": image_data["image"], "client": client})
                f = open("media/carousel/ad-{}.png".format(index), "wb")
                f.write(response.content)
                f.close()
                each_carousel["image"] = "media/carousel/ad-{}.png".format(index)
                each_carousel["name"] = image_data["name"]
                each_carousel["file"] = image_data["file"]
                each_carousel["content"] = image_data['content']
                each_carousel['redirect'] = image_data["redirect"]
                each_carousel["show_type"] = image_data["show_type"]
                each_carousel["id"] = image_data["id"]
                carousel_data.append(each_carousel)
            with open("conf/carousel.dat", 'w', encoding="utf-8") as f:
                f.write(str(carousel_data))
        else:
            print("本客户端轮播无需更新")
            with open("conf/carousel.dat", "r", encoding="utf-8") as f:
                carousel_data = eval(f.read())
        return carousel_data

    @staticmethod
    def upload_media_file(url, file_path, file_type_en, file_show_name=None):
        """
        上传文件
        :param url: 服务器地址API
        :param file_path: 文件本地路径
        :param file_type_en: 文件类型英文
        :param file_show_name: 文件显示的名称
        :return:
        """
        headers = config.CLIENT_HEADERS
        file = open(file_path, "rb")
        file_content = file.read()
        file.close()
        data = dict()
        # 处理文件名字
        file_raw_name = file_path.rsplit("/", 1)
        data['file'] = (file_raw_name[1], file_content)
        if file_type_en:
            data["type_en"] = file_type_en
        if not file_show_name:
            file_name_list = file_raw_name[1].rsplit(".", 1)
            data["name"] = file_name_list[0]
        encode_data = encode_multipart_formdata(data)
        data = encode_data[0]
        headers['Content-Type'] = encode_data[1]
        response = requests.post(url=url, headers=headers, data=data)
        # response_data = json.loads(response.content.decode("utf-8"))
        return response
