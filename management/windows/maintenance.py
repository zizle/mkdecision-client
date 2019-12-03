# _*_ coding:utf-8 _*_
# Author: zizle  QQ:462894999

import re
import json
import requests
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout,QHBoxLayout, QLabel, QPushButton, QTabWidget, QLineEdit,\
    QListWidget
from PyQt5.QtCore import Qt, QPropertyAnimation, QParallelAnimationGroup, QRect, QPoint

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
        self.authority_list.addItems(['客户端权限', '模块权限', '品种权限'])  # 添加左侧权限管理菜单
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
        self.detail_tab.clear()
        self.detail_tab.addTab(auth_tab, item.text())
