# _*_ coding:utf-8 _*_
# Author: zizle  QQ:462894999

import re
import json
import requests
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout,QHBoxLayout, QLabel, QPushButton, QTabWidget, QLineEdit,\
    QListWidget, QComboBox
from PyQt5.QtCore import Qt, QPropertyAnimation, QParallelAnimationGroup, QRect, QPoint, QMetaMethod

import config
from frame.maintain.danalysis import UploadDataMaintain
from widgets.maintain.maintenance import ModuleBlock
from widgets.maintain.authorization import UserTable
from utils.maintain import change_user_information


# 数据管理主页
class MaintenanceHome(QWidget):
    BLOCK_WIDTH = 200
    BLOCK_HEIGHT = 180

    def __init__(self, *args, **kwargs):
        super(MaintenanceHome, self).__init__(*args, **kwargs)
        # 显示所有可维护的模块
        self.show_maintainers = QWidget(parent=self, objectName='showMaintainers')
        # 客户端管理
        client_block = ModuleBlock(parent=self, module_name='client_manager')
        client_block.set_module_widget(QLabel('客户端管理', styleSheet='min-width:200;min-height:180', alignment=Qt.AlignCenter))
        client_block.enter_clicked.connect(self.enter_detail_maintainer)
        # 主模块名称维护
        module_block = ModuleBlock(parent=self, module_name='main_module')  # module_name用于判断哪个模块
        module_block.set_module_widget(QLabel('主功能模块', styleSheet='min-width:200;min-height:180', alignment=Qt.AlignCenter))
        module_block.enter_clicked.connect(self.enter_detail_maintainer)
        # 品种管理维护
        variety_block = ModuleBlock(parent=self, module_name='variety_maintain')  # module_name用于判断哪个模块
        variety_block.set_module_widget(QLabel('品种管理', styleSheet='min-width:200;min-height:180', alignment=Qt.AlignCenter))
        variety_block.enter_clicked.connect(self.enter_detail_maintainer)
        # 首页数据管理
        homepage_block = ModuleBlock(parent=self, module_name='homepage')
        homepage_block.set_module_widget(QLabel('首页管理',  styleSheet='min-width:200;min-height:180', alignment=Qt.AlignCenter))
        homepage_block.enter_clicked.connect(self.enter_detail_maintainer)
        # 数据分析模块维护
        analysis_block = ModuleBlock(parent=self, module_name='trend_analysis')
        analysis_block.set_module_widget(QLabel('数据分析', styleSheet='min-width:180;min-height:180', alignment=Qt.AlignCenter))
        analysis_block.enter_clicked.connect(self.enter_detail_maintainer)
        # 可维护模块布局
        maintainers_layout = QGridLayout()
        maintainers_layout.addWidget(client_block, 0, 0)
        maintainers_layout.addWidget(module_block, 0, 1)
        maintainers_layout.addWidget(variety_block, 0, 2)
        maintainers_layout.addWidget(homepage_block, 0, 3)
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
        self.back_msg_create_layout = QHBoxLayout()
        # 信息提示
        self.network_message = QLabel(parent=self.detail_maintainer, objectName='networkMessage')
        self.back_msg_create_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        self.back_msg_create_layout.addWidget(self.network_message, alignment=Qt.AlignLeft)
        self.back_msg_create_layout.addStretch()
        # self.back_msg_create_layout.addWidget(self.new_module_button, alignment=Qt.AlignRight)
        detail_layout.addLayout(self.back_msg_create_layout)
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
        #networkMessage{
            color:rgb(200,130,100)
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
        self.network_message.setText('')  # 网络提示置空
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
        # 客户端管理
        if module.module_name == 'client_manager':
            from frame.maintain.base import ClientMaintain
            maintainer = ClientMaintain(parent=self)
            maintainer.network_result.connect(self.network_message_show_message)
            maintainer.getClients()  # 获取所有客户端
        # 主模块管理
        elif module.module_name == 'main_module':
            from widgets.maintain.maintenance import ModuleMaintainTable
            maintainer = ModuleMaintainTable(parent=self)
            maintainer.network_result.connect(self.network_message_show_message)  # 网络请求结果信号
            self.add_create_button(maintainer.create_button)  # 加入新增button
            maintainer.getModules()
        # 品种管理
        elif module.module_name == 'variety_maintain':
            from frame.maintain.base import VarietyMaintain
            maintainer = VarietyMaintain(parent=self)
            maintainer.network_result.connect(self.network_message_show_message)  # 网络请求结果信号
            self.add_create_button(maintainer.create_button)  # 加入新增button
            maintainer.getVarietyGroups()  # 获取品种组别
        # 首页管理
        elif module.module_name == 'homepage':
            from frame.maintain.home import HomepageMaintain
            maintainer = HomepageMaintain(parent=self)
            maintainer.network_result.connect(self.network_message_show_message)  # 网络请求结果信号
            self.add_create_button(maintainer.create_button)  # 加入新增button
        # 数据分析管理
        elif module.module_name == 'trend_analysis':
            from frame.maintain.trend import TrendMaintain
            maintainer = TrendMaintain(parent=self)
            maintainer.network_result.connect(self.network_message_show_message)  # 网络请求结果信号
            self.add_create_button(maintainer.create_button)  # 加入新增button
            # maintainer = UploadDataMaintain()

        else:
            # self.back_button.maintain_name = None
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
        # 去除新增按钮
        self.remove_create_button()

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

    # 显示提示信息
    def network_message_show_message(self, text):
        self.network_message.setText(text)

    # 去除新增数据的按钮
    def remove_create_button(self):
        # 获取最后一个控件
        count = self.back_msg_create_layout.count()
        widget = self.back_msg_create_layout.itemAt(count - 1).widget()
        if isinstance(widget, QPushButton):
            # 去除布局中最后一个控件
            widget.deleteLater()
            del widget

    # 增加新增数据按钮
    def add_create_button(self, button):
        self.back_msg_create_layout.addWidget(button, alignment=Qt.AlignRight)


# 权限管理主页
class AuthorityHome(QWidget):
    def __init__(self, *args, **kwargs):
        super(AuthorityHome, self).__init__(*args, **kwargs)
        """ 显示用户列表页 """
        self.show_users = QWidget(parent=self, objectName='showUsers')
        self.show_users.resize(self.parent().width(), self.parent().height())  # 窗口大小(与一级主容器等大)用于承载显示的表格
        # 显示用户布局
        show_users_layout = QVBoxLayout(margin=2)
        # 下拉框和网络信息提示布局
        combo_message_layout = QHBoxLayout()
        # 下拉框显示当前角色下的所有用户
        self.user_role_combo = QComboBox(parent=self)
        self.user_role_combo.activated.connect(self.role_combo_changed)
        combo_message_layout.addWidget(self.user_role_combo)
        self.show_users_network_message = QLabel(parent=self.show_users)
        combo_message_layout.addWidget(self.show_users_network_message)
        combo_message_layout.addStretch()
        # 显示用户表格
        self.user_table = UserTable()
        self.user_table.network_result.connect(self.set_show_users_network_message)
        self.user_table.enter_detail_authenticated.connect(self.enter_user_authenticated)
        show_users_layout.addLayout(combo_message_layout)
        show_users_layout.addWidget(self.user_table)
        self.show_users.setLayout(show_users_layout)
        """ 权限详情控制页 """
        self.user_detail = QWidget(parent=self, objectName='userDetail')
        self.user_detail.user_id = None
        # self.user_detail.resize(self.parent().width(), self.parent().height())  # 点击进入改变详情页的大小(利用动画改变)
        # 详情页布局
        detail_layout = QVBoxLayout()
        # 详情页用户信息和网络信息显示和返回按钮
        detail_msgbtn_layout = QHBoxLayout()
        # 用户信息（手机）
        detail_msgbtn_layout.addWidget(QLabel('手机:', parent=self.user_detail))
        self.detail_user_phone = QLabel(parent=self.user_detail)
        detail_msgbtn_layout.addWidget(self.detail_user_phone)
        # 用户信息（角色）
        detail_msgbtn_layout.addWidget(QLabel('角色:', parent=self.user_detail))
        self.detail_user_role = QLabel(parent=self.user_detail)
        detail_msgbtn_layout.addWidget(self.detail_user_role)
        # 用户信息（备注）
        detail_msgbtn_layout.addWidget(QLabel('备注名:', parent=self.user_detail))
        self.detail_user_note = QLabel(parent=self.user_detail)
        detail_msgbtn_layout.addWidget(self.detail_user_role)
        # 显示网络请求的结果
        self.user_detail.network_message_show = QLabel('显示网络请求的信息')
        detail_msgbtn_layout.addWidget(self.user_detail.network_message_show)
        detail_msgbtn_layout.addStretch()  # 伸缩
        # 关闭按钮
        back_show_users = QPushButton('关闭', clicked=self._animation_detail_out)
        detail_msgbtn_layout.addWidget(back_show_users, alignment=Qt.AlignRight)
        detail_layout.addLayout(detail_msgbtn_layout)
        # 详情页权限设置布局
        detail_authority_layout = QHBoxLayout()
        self.authority_list = QListWidget()
        self.authority_list.addItems(['客户端权限', '模块权限', '品种权限'])  # 添加左侧权限管理菜单
        self.authority_list.clicked.connect(self.authority_list_clicked)
        detail_authority_layout.addWidget(self.authority_list, alignment=Qt.AlignLeft)
        # 详情权限右侧容器
        self.detail_tab = QTabWidget(parent=self.user_detail)
        self.detail_tab.setDocumentMode(True)
        self.detail_tab.tabBar().hide()
        detail_authority_layout.addWidget(self.detail_tab)
        detail_layout.addLayout(detail_authority_layout)
        self.user_detail.setLayout(detail_layout)
        self.user_detail.resize(0, 0)  # 初始没有大小，即不可见
        self.setStyleSheet("""
        #userDetail{
            background-color: rgb(180, 210, 210);   
        }
        """)
        # 记录原始权限按钮的位置
        self.detail_origin_x = None
        self.detail_origin_y = None
        # 详情页进入退出动画
        self.authority_animation = QPropertyAnimation(self.user_detail, b'geometry')
        self.authority_animation.setDuration(300)

    # 下拉框添加数据
    def addComboItem(self):
        for role_item in [
            {'role': '全部', 'flag': 'all'},
            {'role': '运营管理员', 'flag': 'is_operator'},
            {'role': '信息管理员', 'flag': 'is_collector'},
            {'role': '研究员', 'flag': 'is_researcher'},
            {'role': '普通用户', 'flag': None},
        ]:
            self.user_role_combo.addItem(role_item['role'], role_item['flag'])
        # 默认点击了第一个
        self.role_combo_changed()

    # 角色选择框变化
    def role_combo_changed(self):
        self.show_users_network_message.setText('')
        current_data = self.user_role_combo.currentData()
        # 获取相应用户
        params = dict()
        if current_data == 'all':
            pass
        elif current_data is None:  # 普通用户
            params['is_operator'] = False
            params['is_collector'] = False
            params['is_researcher'] = False
        else:
            params[current_data] = True
        self._get_users(params)

    # 获取用户
    def _get_users(self, params):
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'user/authenticated/?mc=' + config.app_dawn.value('machine'),
                headers={
                  'AUTHORIZATION': config.app_dawn.value('Authorization')
                },
                data=json.dumps(params)
            )
            response = json.loads(r.content.decode('utf-8'))
        except Exception:
            return
        self.user_table.showUsers(json_list=response['data'])

    # 设置主页出现的网络请求信息显示
    def set_show_users_network_message(self, message):
        self.show_users_network_message.setText(message)

    # 设置详情页网络请求信息提示
    def set_user_detail_network_message(self, message):
        self.user_detail.network_message_show.setText(message)

    # 进入用户权限管理
    def enter_user_authenticated(self, user_id, origin_center):
        self.user_detail.network_message_show.setText('')  # 网络信息置空
        print('进入用户id=%d的详情权限管理' % user_id)
        # 获取当前用户信息
        user_detail_data = self._get_current_user(user_id)
        if not user_detail_data:
            self.show_users_network_message.setText('获取当前用户信息失败')
            return
        self.user_detail.user_id = user_detail_data['id']  # 设置当前管理的用户id
        # 初始化好详情管理页
        role_dict = {
            'is_operator': '运营管理员',
            'is_collector': '信息管理员',
            'is_researcher': '研究员',
            '': '普通用户'
        }
        print(user_detail_data)
        # 设置权限列表的项目
        self.authority_list.setCurrentRow(0)
        self.authority_list_clicked()  # 点中第一个
        # 设置用户基本信息
        self.detail_user_phone.setText(user_detail_data['phone'])
        self.detail_user_role.setText(role_dict.get(user_detail_data['role'], ''))
        self.detail_user_note.setText(user_detail_data['note'])
        # 动画显示出来
        self._animation_detail_in(origin_center)

    # 获取当前用户详情信息
    @staticmethod
    def _get_current_user(user_id):
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'user/' + str(user_id) + '/?mc=' + config.app_dawn.value('machine'),
                headers={"AUTHORIZATION": config.app_dawn.value('AUTHORIZATION')},
            )
            response = json.loads(r.content.decode('utf-8'))
        except Exception:
            return {}
        else:
            return response['data']

    # 动画显示详情页
    def _animation_detail_in(self, origin_center):
        print('按钮中心位置', origin_center)  # 记录按钮原始位置
        self.detail_origin_x = origin_center['center_x']
        self.detail_origin_y = origin_center['center_y']
        # 设置详情页放大
        self.authority_animation.setStartValue(
            QRect(self.detail_origin_x, self.detail_origin_y, 0, 0)
        )
        self.authority_animation.setEndValue(
            QRect(0, 0, self.parent().width(), self.parent().height())
        )
        self.authority_animation.start()

    # 动画关闭详情页
    def _animation_detail_out(self):
        # 设置详情页缩小
        self.authority_animation.setStartValue(
            QRect(0, 0, self.parent().width(), self.parent().height())
        )
        self.authority_animation.setEndValue(
            QRect(self.detail_origin_x, self.detail_origin_y, 0, 0)
        )
        self.authority_animation.start()
        self.detail_origin_x = None
        self.detail_origin_y = None  # 原始位置置空
        self.user_detail.user_id = None  # 用户id置空

    # 详情页权限设置列表点击
    def authority_list_clicked(self):
        item = self.authority_list.currentItem()
        print(item)
        if item.text() == u'客户端权限':
            from frame.maintain.authorization import UserToClientAuth
            auth_tab = UserToClientAuth(user_id=self.user_detail.user_id)
            auth_tab.network_result.connect(self.set_user_detail_network_message)
        else:
            auth_tab = QLabel('【' + item.text() + '】还不能进行管理.', alignment=Qt.AlignCenter)
        self.detail_tab.clear()
        self.detail_tab.addTab(auth_tab, item.text())
        return



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
        elif item.text() == u'模块权限':
            from widgets.maintain.authorization import UserModuleTable
            auth_tab = UserModuleTable(uid=self.user_detail.user_id, parent=self.detail_tab)
            auth_tab.network_result.connect(self.network_error)
            # 获取与展示信息
            auth_tab.getModules()
        elif item.text() == u'品种权限':
            from piece.maintain.authorization import UserVarietyAuth
            auth_tab = UserVarietyAuth(uid=self.user_detail.user_id, parent=self.detail_tab)
            auth_tab.network_result.connect(self.network_error)
            auth_tab.getVarietyGroup()
        else:
            return

