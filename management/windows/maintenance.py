# _*_ coding:utf-8 _*_
"""
Update: 2019-07-22
Author: zizle
"""
import sys
import json
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, QPushButton, QTabWidget, QStyleOption, QStyle
from PyQt5.QtCore import Qt, QPropertyAnimation, QParallelAnimationGroup, QRect, QPoint, QSize
from PyQt5.QtGui import QPainter

from frame.maintain.base import NoDataWindow
from frame.maintain.home import BulletinMaintain, CarouselMaintain, ReportMaintain, NoticeMaintain, CommodityMaintain, FinanceMaintain
from frame.maintain.pservice import MessageCommMaintain, MarketAnalysisMaintain, TopicalStudyMaintain, ResearchReportMaintain, AdviserMaintain
from frame.maintain.danalysis import VarietyMaintain, UploadDataMaintain
from widgets.maintain import ModuleBlock
from thread.request import RequestThread
import config


# 数据管理主页
class MaintenanceHome(QWidget):
    BLOCK_WIDTH = 200
    BLOCK_HEIGHT = 180

    def __init__(self, *args, **kwargs):
        super(MaintenanceHome, self).__init__(*args, **kwargs)
        # 显示所有可维护的模块
        self.show_maintainers = QWidget(parent=self, objectName='showMaintainers')
        # self.show_maintainers.resize(self.parent().width(), self.parent().height())
        # 主模块名称维护
        module_block = ModuleBlock(parent=self, module_name='main_module')  # module_name用于判断哪个模块
        module_block.set_module_widget(QLabel('主功能模块', styleSheet='min-width:200;min-height:180'))
        module_block.enter_clicked.connect(self.enter_detail_maintainer)
        # ###########品种guan
        variety_block = ModuleBlock(parent=self, module_name='variety_maintain')  # module_name用于判断哪个模块
        variety_block.set_module_widget(QLabel('品种管理', styleSheet='min-width:200;min-height:180'))
        variety_block.enter_clicked.connect(self.enter_detail_maintainer)
        # 数据分析模块维护
        analysis_block = ModuleBlock(parent=self, module_name='danalysis')
        analysis_block.set_module_widget(QLabel('数据分析', styleSheet='min-width:180;min-height:180'))
        analysis_block.enter_clicked.connect(self.enter_detail_maintainer)
        # 可维护模块布局
        maintainers_layout = QGridLayout()
        maintainers_layout.addWidget(module_block, 0, 0)
        maintainers_layout.addWidget(variety_block, 0, 1)
        maintainers_layout.addWidget(analysis_block, 1, 1)
        self.show_maintainers.setLayout(maintainers_layout)
        # 右侧详细维护页面
        self.detail_maintainer = QWidget(parent=self, objectName='detailMaintainer')
        # 详细页面布局
        detail_layout = QVBoxLayout()
        self.detail_maintainer.setLayout(detail_layout)
        self.detail_tab = QTabWidget()
        self.back_button = QPushButton('返回', clicked=self.back_to_maintainers)
        self.back_button.maintain_name = None
        detail_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        detail_layout.addWidget(self.detail_tab)
        # 样式
        self.detail_tab.tabBar().hide()
        self.setObjectName('myself')
        self.setStyleSheet("""
        #showMaintainers{
            background-color: rgb(255,255,255);
        }
        #maintainBlock{
            background-color: rgb(240,240,240);
        }
        #detailMaintainer{
            background-color: rgb(200,200,200);
        }
        """)
        # 详细维护页面动画
        self.detail_maintainer_animation = QPropertyAnimation(self.detail_maintainer, b'geometry')
        self.detail_maintainer_animation.setDuration(500)
        
        # 功能块缩小动画
        self.block_module_animation = QPropertyAnimation()
        self.block_module_animation.setDuration(500)
        
        # 动画组
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.detail_maintainer_animation)
        self.animation_group.addAnimation(self.block_module_animation)
        
        # 窗口层次
        self.detail_maintainer.raise_()
        self.show_maintainers.raise_()

    # 进入维护详情页
    def enter_detail_maintainer(self, button):
        module = button.parent()
        # 详情控件位置移到功能块中心
        self.detail_maintainer.move(module.pos().x() + self.BLOCK_WIDTH / 2,
                                    module.pos().y() + self.BLOCK_HEIGHT / 2)
        # 改变控件层次
        self.show_maintainers.raise_()
        self.detail_maintainer.raise_()
        # 模块记录原始位置大小,供还原使用
        module.set_original_rect(module.pos().x(), module.pos().y(), module.width(), module.height())
        # 设置模块缩小
        self.block_module_animation.setTargetObject(module)
        self.block_module_animation.setPropertyName(b'geometry')
        self.block_module_animation.setStartValue(
            QRect(module.pos().x(), module.pos().y(), self.BLOCK_WIDTH, self.BLOCK_HEIGHT)
        )
        self.block_module_animation.setEndValue(
            QRect(module.pos().x() + self.BLOCK_WIDTH/2, module.pos().y()+self.BLOCK_HEIGHT/2, 0, 0)
        )
        # 设置详情页
        self.back_button.maintain_name = module.module_name
        if module.module_name == 'main_module':
            maintainer = QLabel('主功能维护主功能维护主功能维护主功能维护')
        elif module.module_name == 'danalysis':
            maintainer = UploadDataMaintain()
        elif module.module_name == 'variety_maintain':
            maintainer = VarietyMaintain()
        else:
            self.back_button.maintain_name = None
            maintainer = QLabel('此模块暂不支持维护')
        # 设置详情页进入动画位置和大小
        self.detail_maintainer_animation.setStartValue(
            QRect(self.detail_maintainer.pos().x(), self.detail_maintainer.pos().y(), 0, 0)
        )
        self.detail_maintainer_animation.setEndValue(
            QRect(0, 0, self.parent().width(), self.parent().height())
        )
        # 清除tab，加入页面
        self.detail_tab.clear()
        self.detail_tab.addTab(maintainer, '详细维护界面')
        # 开启动画组
        self.animation_group.start()

    # 退出详情维护界面
    def back_to_maintainers(self):
        maintain_name = self.back_button.maintain_name
        # 找到缩小的那个功能模块
        module_blocks = self.findChildren(ModuleBlock, 'moduleBlock')
        show_block = None
        for module in module_blocks:
            if module.module_name == maintain_name:
                show_block = module
        if not show_block:
            return
        # 设置模块放大
        self.block_module_animation.setTargetObject(show_block)
        self.block_module_animation.setPropertyName(b'geometry')
        self.block_module_animation.setStartValue(
            QRect(show_block.original_x + show_block.original_width / 2, show_block.original_y + show_block.original_height / 2, 0, 0)
        )
        self.block_module_animation.setEndValue(
            QRect(show_block.original_x, show_block.original_y, show_block.original_width, show_block.original_height)
        )
        # 设置详情页退出动画位置和大小
        self.detail_maintainer_animation.setStartValue(
            QRect(0, 0, self.parent().width(), self.parent().height())
        )
        self.detail_maintainer_animation.setEndValue(
            QRect(show_block.original_x + show_block.original_width / 2, show_block.original_y + show_block.original_height / 2, 0, 0)
        )
        self.animation_group.start()
        # 改变控件层次，由于控件最小，无需再改变层次
        # self.detail_maintainer.raise_()
        # self.show_maintainers.raise_()


# 权限管理主页
class AuthenticationHome(QWidget):
    def __init__(self, *args, **kwargs):
        super(AuthenticationHome, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.addWidget(QLabel('权限管理'))
        self.setLayout(layout)

















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
        # self.right_tab.setTabsClosable(True)
        self.right_tab.tabBar().hide()
        # self.right_tab.setTabBarAutoHide(True)  # hide tabBar when only one tab
        self.right_tab.tabCloseRequested.connect(self.close_tab)
        hor_layout.addWidget(self.left_tree, alignment=Qt.AlignLeft)
        hor_layout.addWidget(self.right_tab)
        layout = QVBoxLayout()
        layout.addLayout(hor_layout)
        self.setLayout(layout)
        # 线程请求菜单
        self.left_tree_thread = None
        self.get_list_menu()
        self.left_tree.setStyleSheet("""
        QTreeWidget{
            font-size: 13px;
        }
        QTreeWidget::item{
            min-height: 30px;
        }
        QTreeWidget::item:selected {
            border:none;
            color: rgb(0,0,0)

        }
        QTreeWidget::item:!selected{

        }
        QTreeWidget::item:hover {
            background-color: rgb(230,230,230);
            cursor: pointer;
        }
        """)

    def close_tab(self, index):
        if self.right_tab.count() > 1:
            self.right_tab.removeTab(index)
        else:
            # self.close()  # 当只有1个tab时，关闭主窗口
            return

    def get_list_menu(self):
        """ get menus """
        if self.left_tree_thread:
            del self.left_tree_thread
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
                elif name_en == 'adviser':
                    tab = AdviserMaintain()
                else:
                    tab = NoDataWindow(name=tab_name)
            elif parent_en == 'data_analysis':
                if name_en == 'variety_manager':
                    tab = VarietyMaintain()
                elif name_en == 'upload_data':
                    tab = UploadDataMaintain()

                # elif name_en == 'variety_detail_menu':
                #     tab = VarietyDetailMenuMaintain()
                # elif name_en == 'dahchart':
                #     tab = DAHomeChartMaintain()
                # elif name_en == 'davchart':
                #     tab = DAVarietyChartMaintain()
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
