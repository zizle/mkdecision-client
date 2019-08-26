# _*_ coding:utf-8 _*_
"""
Update: 2019-07-22
Author: zizle
"""
import sys
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

from frame.maintain.base import NoDataWindow
from frame.maintain.home import BulletinMaintain, CarouselMaintain, ReportMaintain, NoticeMaintain, CommodityMaintain, FinanceMaintain
from frame.maintain.pservice import MessageCommMaintain, MarketAnalysisMaintain, TopicalStudyMaintain, ResearchReportMaintain
from thread.request import RequestThread
import config


class Maintenance(QWidget):
    def __init__(self):
        super(Maintenance, self).__init__()
        hor_layout = QHBoxLayout()
        self.left_tree = QTreeWidget()
        self.left_tree.setExpandsOnDoubleClick(False)
        self.left_tree.clicked.connect(self.left_tree_clicked)
        # self.left_tree.setRootIsDecorated(False)  # remove root icon
        self.left_tree.setHeaderHidden(True)
        # a tab show windows
        self.right_tab = QTabWidget()
        self.right_tab.setTabsClosable(True)
        # self.right_tab.setTabBarAutoHide(True)  # hide tabBar when only one tab
        self.right_tab.tabCloseRequested.connect(self.close_tab)
        hor_layout.addWidget(self.left_tree, alignment=Qt.AlignLeft)
        hor_layout.addWidget(self.right_tab)
        layout = QVBoxLayout()
        layout.addLayout(hor_layout)
        self.setLayout(layout)
        # 线程请求菜单
        self.get_list_menu()

    def close_tab(self, index):
        if self.right_tab.count() > 1:
            self.right_tab.removeTab(index)
        else:
            # self.close()  # 当只有1个tab时，关闭主窗口
            return

    def get_list_menu(self):
        """ get menus """
        headers = config.CLIENT_HEADERS
        self.left_tree_thread = RequestThread(
            url=config.SERVER_ADDR + 'basic/maintenance/',
            method='get',
            headers=headers,
            data=json.dumps({"machine_code": config.app_dawn.value("machine")}),
            cookies=config.app_dawn.value('cookies')
        )
        self.left_tree_thread.finished.connect(self.left_tree_thread.deleteLater)
        self.left_tree_thread.response_signal.connect(self.set_tree_menu)
        self.left_tree_thread.start()

    def set_tree_menu(self, content):
        """ set the left list navigate"""
        print('windows.maintenance.py {} : '.format(str(sys._getframe().f_lineno)), content)
        if content['error']:
            return
        for module in content['data']:
            menu = QTreeWidgetItem(self.left_tree)
            menu.setText(0, module['name'])
            # menu.setTextAlignment(0, Qt.AlignCenter)
            menu.name_en = module['name_en']
            sub_menus = module['subs']
            # 添加子节点
            for sub_module in sub_menus:
                child = QTreeWidgetItem()
                child.name_en = sub_module['name_en']
                child.setText(0, sub_module['name'])
                menu.addChild(child)
                # 添加孙节点
                grandson_menus = sub_module['subs']
                for grand_module in grandson_menus:
                    grand_son = QTreeWidgetItem()
                    grand_son.name_en = grand_module['name_en']
                    grand_son.setText(0, grand_module['name'])
                    child.addChild(grand_son)

    def left_tree_clicked(self):
        """ click action """
        item = self.left_tree.currentItem()
        if item.childCount():  # has children open the root
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        else:
            parent = item.parent()
            name_text = item.text(0)
            name_en = item.name_en
            parent_text = parent.parent().text(0) if parent.parent() else parent.text(0)  # has grandpa parent text is grandpa
            parent_en = parent.parent().name_en if parent.parent() else parent.name_en  # has grandpa parent text is grandpa
            tab_name = parent_text + '·' + name_text
            if parent_en == 'home_page':
                if name_en == 'bulletin':
                    tab = BulletinMaintain()
                elif name_en == 'carousel':
                    tab = CarouselMaintain()
                elif name_en == 'routine_report':
                    tab = ReportMaintain()
                elif name_en == 'transact_notice':
                    tab = NoticeMaintain()
                elif name_en == 'spot_statement':
                    tab = CommodityMaintain()
                elif name_en == 'economic_calendar':
                    tab = FinanceMaintain()
                else:
                    tab = NoDataWindow(name=tab_name)
            elif parent_en == 'product_service':
                if name_en == 'message_comm':
                    tab = MessageCommMaintain()
                elif name_en == 'market_analysis':
                    tab = MarketAnalysisMaintain()
                elif name_en == 'topical_study':
                    tab = TopicalStudyMaintain()
                elif name_en == 'research':
                    tab = ResearchReportMaintain()
                # elif text == '人才培养':
                #     tab = PersonTrain()

                else:
                    tab = NoDataWindow(name=tab_name)
            # elif parent_text == '系统信息':
            #     if text == '客户端':
            #         tab = ClientInfo()
            #     elif text == '用户':
            #         tab = UserInfo()
            #     else:
            #         tab = NoDataWindow(name=text)
            else:
                tab = NoDataWindow(name=tab_name)
            self.right_tab.addTab(tab, tab_name)
            self.right_tab.setCurrentWidget(tab)






