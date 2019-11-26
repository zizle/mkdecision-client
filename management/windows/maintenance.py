# _*_ coding:utf-8 _*_
"""
Update: 2019-07-22
Author: zizle
"""
import re
import sys
import json
import requests
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout,QHBoxLayout, QLabel, QPushButton, QTabWidget, QLineEdit,\
    QListWidget
from PyQt5.QtCore import Qt, QPropertyAnimation, QParallelAnimationGroup, QRect, QPoint

from frame.maintain.base import NoDataWindow
from frame.maintain.home import BulletinMaintain, CarouselMaintain, ReportMaintain, NoticeMaintain, CommodityMaintain, FinanceMaintain
from frame.maintain.pservice import MessageCommMaintain, MarketAnalysisMaintain, TopicalStudyMaintain, ResearchReportMaintain, AdviserMaintain
from frame.maintain.danalysis import VarietyMaintain, UploadDataMaintain
from widgets.maintain.maintenance import ModuleBlock, ModuleMaintainTable
from widgets.maintain.authorization import UserTable
from thread.request import RequestThread
import config
from utils.maintain import change_user_information


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
        # 品种管理维护
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
        # 详细维护页面
        self.detail_maintainer = QWidget(parent=self, objectName='detailMaintainer')
        # 详细页面布局
        detail_layout = QVBoxLayout()
        self.detail_maintainer.setLayout(detail_layout)
        self.detail_tab = QTabWidget()
        self.back_button = QPushButton('返回', clicked=self.back_to_maintainers)
        self.back_button.maintain_name = None
        self.detail_tab.setDocumentMode(True)
        # 返回按钮和信息提示布局和增加按钮
        back_message_layout = QHBoxLayout()
        # 信息提示
        self.network_message = QLabel(parent=self.detail_maintainer)
        # 增加按钮
        self.new_module_button = QPushButton('新增模块', parent=self.detail_maintainer)
        self.new_module_button.is_clicked_connected = False
        back_message_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        back_message_layout.addWidget(self.network_message, alignment=Qt.AlignLeft)
        back_message_layout.addWidget(self.new_module_button, alignment=Qt.AlignRight)
        detail_layout.addLayout(back_message_layout)
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
            maintainer = ModuleMaintainTable(parent=self)
            if not self.new_module_button.is_clicked_connected:  # 未连接信号才连接
                self.new_module_button.clicked.connect(maintainer.addNewModulePopup)  # 新增模块信号
                self.new_module_button.is_clicked_connected = True
            maintainer.getModules()


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
class AuthorityHome(QWidget):
    def __init__(self, *args, **kwargs):
        super(AuthorityHome, self).__init__(*args, **kwargs)
        self.show_users = QWidget(parent=self, objectName='showUsers')
        self.show_users.resize(self.parent().width(), self.parent().height())  # 窗口大小(与一级主容器等大)用于承载显示的表格
        # 显示用户布局
        show_users_layout = QVBoxLayout(margin=2)
        # 显示用户表格
        self.user_table = UserTable()
        self.user_table.enter_detail.connect(self.enter_authority)
        show_users_layout.addWidget(self.user_table)
        self.show_users.setLayout(show_users_layout)
        # 右侧用户详情控件
        self.user_detail = QWidget(parent=self, objectName='userDetail')
        self.user_detail.user_id = None
        self.user_detail.resize(self.parent().width(), self.parent().height())
        # 右侧详情页布局
        detail_layout = QVBoxLayout()
        # 详情页返回按钮
        back_show_users = QPushButton('←返回', clicked=self.back_users_list)
        # 详情页信息头
        detail_header_layout = QHBoxLayout(spacing=0)
        self.detail_user_phone = QLabel(parent=self.user_detail, objectName='textLabel')
        self.detail_user_role = QLabel(parent=self.user_detail, objectName='textLabel')
        self.detail_user_note = QLineEdit(parent=self.user_detail, objectName='noteEdit')
        detail_header_layout.addWidget(QLabel('手机:', parent=self.user_detail, objectName='tipsLabel'), alignment=Qt.AlignLeft)
        detail_header_layout.addWidget(self.detail_user_phone, alignment=Qt.AlignLeft)
        detail_header_layout.addWidget(QLabel('角色:', parent=self.user_detail, objectName='tipsLabel'), alignment=Qt.AlignLeft)
        detail_header_layout.addWidget(self.detail_user_role, alignment=Qt.AlignLeft)
        detail_header_layout.addWidget(QLabel('备注名:', parent=self.user_detail, objectName='tipsLabel'), alignment=Qt.AlignLeft)
        detail_header_layout.addWidget(self.detail_user_note, alignment=Qt.AlignLeft)
        detail_header_layout.addWidget(QPushButton('设置', parent=self.user_detail, objectName='noteButton',
                                                   cursor=Qt.PointingHandCursor, clicked=self.set_note_name))
        self.note_name_error = QLabel(parent=self.user_detail, objectName='noteError')
        self.detail_user_note.textChanged.connect(lambda: self.note_name_error.setText(''))
        detail_header_layout.addWidget(self.note_name_error)
        detail_header_layout.addStretch()
        # 详情页权限设置布局
        detail_authority_layout = QHBoxLayout()
        self.authority_list = QListWidget()
        self.authority_list.addItems(['客户端权限', '模块权限', ])  # 添加左侧权限管理菜单
        self.authority_list.clicked.connect(self.authority_list_clicked)
        detail_authority_layout.addWidget(self.authority_list, alignment=Qt.AlignLeft)
        # 详情权限右侧容器
        self.detail_tab = QTabWidget(parent=self)
        self.detail_tab.setDocumentMode(True)
        self.detail_tab.tabBar().hide()
        detail_authority_layout.addWidget(self.detail_tab)

        detail_layout.addWidget(back_show_users, alignment=Qt.AlignTop|Qt.AlignLeft)
        detail_layout.addLayout(detail_header_layout)
        detail_layout.addLayout(detail_authority_layout)
        self.user_detail.setLayout(detail_layout)
        # 详情页移动到右侧窗口外
        self.user_detail.move(self.parent().width(), 0)
        # 样式
        self.setStyleSheet("""
        #showUsers{
            background-color: rgb(80,150,89);  
        }
        #userDetail{
            background-color: rgb(160,150,189);
        }
        #tipsLabel{
            margin-left: 10px;
            font-weight: bold;
            font-size:12px;
        }
        #textLabel,#noteEdit{
            color: rgb(100,130,200);
            font-size:12px;
        }
        #noteEdit{
            max-width:70px;
            min-width:70px;
        }
        #noteError{
            color: rgb(200,100,110)
        }
        #noteButton{
            margin-left:5px;
            min-width:40px;
            min-height:22px;
            max-width:40px;
            max-height:22px;
        }
        """)
        # 获取用户
        self.get_users()
        # 进入详情管理动画
        self.detail_authority_animation = QPropertyAnimation(self.user_detail, b'pos')
        self.detail_authority_animation.setDuration(300)
        # 当前用户列表页退出动画
        self.show_users_animation = QPropertyAnimation(self.show_users, b'pos')
        self.show_users_animation.setDuration(300)
        # 串行动画组
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.detail_authority_animation)
        self.animation_group.addAnimation(self.show_users_animation)

    # 获取所有用户信息
    def get_users(self):
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'user/users-management/?mc=' + config.app_dawn.value('machine'),
                headers={
                  'AUTHORIZATION': config.app_dawn.value('Authorization')
                },
            )
            response = json.loads(r.content.decode('utf-8'))
        except Exception:
            return
        self.user_table.addUsers(json_list=response['data'])

    # 进入详情权限管理页
    def enter_authority(self, uid):
        print('权限管理用户id', uid)
        self.user_detail.user_id = uid  # 设置用户id
        self.note_name_error.setText('')  # 清空提示
        # 获取当前用户的基础信息
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'user/' + str(uid) + '/?mc=' + config.app_dawn.value('machine'),
                headers={"AUTHORIZATION": config.app_dawn.value('AUTHORIZATION')},
            )
            response = json.loads(r.content.decode('utf-8'))
        except Exception:
            return
        user_data = response['data']
        self.detail_user_phone.setText(user_data['phone'])
        if user_data['is_superuser']:
            role = '超级管理员'
        elif user_data['is_maintainer']:
            role = '数据搜集员'
        elif user_data['is_researcher']:
            role = '研究员'
        else:
            role = '普通用户'
        self.detail_user_role.setText(role)
        note = user_data['note'] if user_data['note'] else ''
        self.detail_user_note.setText(note)
        # 设置权限列表的项目
        self.authority_list.setCurrentRow(0)
        self.authority_list_clicked()  # 点中第一个
        # 进入详情页动画设置
        self.detail_authority_animation.setStartValue(QPoint(self.parent().width(), 0))
        self.detail_authority_animation.setEndValue(QPoint(0, 0))
        # 列表页退出动画设置
        self.show_users_animation.setStartValue(QPoint(0, 0))
        self.show_users_animation.setEndValue(QPoint(-self.parent().width(), 0))
        # 开启动画组动画
        self.animation_group.start()

    # 设置用户的备注名
    def set_note_name(self):
        note_name = self.detail_user_note.text()
        note_name = re.sub(r'\s+', '', note_name)
        note_name = re.match(r'^[\u4e00-\u9fa5a-z]{2,20}', note_name)
        if not note_name:
            self.note_name_error.setText('备注名只能由中文、英文且2-20个字符组成')
            return
        note_name = note_name.group()
        # 发起设置请求
        result = change_user_information(
            uid=self.user_detail.user_id,
            data_dict={
                'note': note_name
            }
        )
        self.note_name_error.setText(result)

    # 返回用户列表页
    def back_users_list(self):
        # 刷新用户列表页
        self.get_users()
        # 详情页退出动画设置
        self.detail_authority_animation.setStartValue(QPoint(0, 0))
        self.detail_authority_animation.setEndValue(QPoint(self.parent().width(), 0))
        # 列表页退出动画设置
        self.show_users_animation.setStartValue(QPoint(-self.parent().width(), 0))
        self.show_users_animation.setEndValue(QPoint(0, 0))
        # 开启动画组动画
        self.animation_group.start()

    # 使用备注名后面的错误显示框显示网络错误信息
    def network_error(self, error_message):
        self.note_name_error.setText(error_message)

    # 详情页权限设置列表点击
    def authority_list_clicked(self):
        item = self.authority_list.currentItem()
        if item.text() == u'客户端权限':
            from widgets.maintain.authorization import UserClientTable
            auth_tab = UserClientTable(uid=self.user_detail.user_id, parent=self.detail_tab)
            auth_tab.network_result.connect(self.network_error)
            # 获取客户端信息
            try:
                r = requests.get(
                    url=config.SERVER_ADDR + 'basic/clients/?mc=' + config.app_dawn.value('machine'),
                    data=json.dumps({'uid': self.user_detail.user_id})
                )
                response = json.loads(r.content.decode('utf-8'))
            except Exception:
                return
            print('请求可登录客户端成功', response)
            # 展示信息
            auth_tab.addClients(response['data'])
        else:
            return
        self.detail_tab.clear()
        self.detail_tab.addTab(auth_tab, item.text())










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
