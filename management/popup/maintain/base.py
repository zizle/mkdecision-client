# _*_ coding:utf-8 _*_
"""
dialog in clients and users info tab
Update: 2019-07-25
Author: zizle
"""
import re
import json
import requests
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator

import config
from utils import get_desktop_path


# 新增系统主模块
class NewModulePopup(QDialog):

    def __init__(self, *args, **kwargs):
        super(NewModulePopup, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        layout.addWidget(QLabel('名称:', parent=self), 0, 0)
        self.name_edit = QLineEdit(parent=self)
        layout.addWidget(self.name_edit, 0, 1)
        self.name_error_label = QLabel(parent=self, objectName='nameError')
        layout.addWidget(self.name_error_label, 1, 0, 1, 2)
        self.commit_button = QPushButton('确定提交', parent=self, clicked=self.commit_new_module)
        layout.addWidget(self.commit_button, 2, 1)
        self.network_result = QLabel()
        layout.addWidget(self.network_result, 3, 0, 1, 2)
        self.setLayout(layout)
        self.setWindowTitle('增加模块')

    # 提交新增
    def commit_new_module(self):
        name = self.name_edit.text()
        name = re.sub(r'\s+', '', name)
        if not name:
            self.name_error_label.setText('请填入模块名称')
            return
        # 提交
        try:
            r = requests.post(
                url=config.SERVER_ADDR + 'basic/modules-maintain/?mc=' + config.app_dawn.value('machine'),
                headers={
                    'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION'),
                },
                data=json.dumps({
                  'name': name
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.setText(str(e))
        else:
            self.close()


# 新增品种弹窗
class NewVarietyPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(NewVarietyPopup, self).__init__(*args, **kwargs)
        # 左侧分组树
        self.group_tree = QTreeWidget(clicked=self.group_tree_clicked)
        # 新增品种控件
        self.nvwidget = QWidget()  # new variety widget
        # 新增品种控件布局
        nvwlayout = QGridLayout(margin=0)
        nvwlayout.addWidget(QLabel('所属分组：'), 0, 0)
        self.attach_group = QLabel(objectName='attachGroup')
        self.attach_group.gid = None
        nvwlayout.addWidget(self.attach_group, 0, 1)
        nvwlayout.addWidget(QLabel(parent=self, objectName='groupError'), 1, 0, 1, 2)
        nvwlayout.addWidget(QLabel('新的品种：'), 2, 0)
        self.vnedit = QLineEdit(textChanged=self.vn_changed)  # variety name edit
        nvwlayout.addWidget(self.vnedit, 2, 1)
        nvwlayout.addWidget(QLabel(parent=self, objectName='nvnameError'), 3, 0, 1, 2)
        nvwlayout.addWidget(QLabel('英文代码：'), 4, 0)
        self.venedit = QLineEdit(textChanged=self.ven_changed)  # variety english name edit
        nvwlayout.addWidget(self.venedit, 4, 1)
        nvwlayout.addWidget(QLabel(parent=self, objectName='nvenameError'), 5, 0, 1, 2)
        addlayout = QHBoxLayout()
        self.add_variety_btn = QPushButton('确认添加', parent=self, objectName='addVariety', clicked=self.add_new_variety)
        addlayout.addWidget(self.add_variety_btn, alignment=Qt.AlignRight)
        # 布局
        self.nvwidget.setLayout(nvwlayout)
        layout = QHBoxLayout()
        llayout = QVBoxLayout()  # left layout
        rlayout = QVBoxLayout()  # right layout
        llayout.addWidget(self.group_tree)
        llayout.addWidget(QPushButton('新建组别', clicked=self.create_vgroup), alignment=Qt.AlignLeft)
        rlayout.addWidget(self.nvwidget)
        rlayout.addLayout(addlayout)
        rlayout.addStretch()
        layout.addLayout(llayout)
        layout.addLayout(rlayout)
        self.setLayout(layout)
        # 样式
        self.setWindowTitle('新增品种')
        self.setFixedSize(800, 500)
        self.group_tree.header().hide()
        self.group_tree.setMaximumWidth(180)
        self.setObjectName('myself')
        self.setStyleSheet("""

        """)
        # 初始化
        self.get_groups()

    # 获取分组树内容(分组+品种)
    def get_groups(self):
        self.group_tree.clear()
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'basic/groups-varieties/?mc=' + config.app_dawn.value('machine'),
            )
            response = json.loads(r.content.decode('utf-8'))
        except Exception as e:
            return
        # 填充品种树
        for group_item in response['data']:
            group = QTreeWidgetItem(self.group_tree)
            group.setText(0, group_item['name'])
            group.gid = group_item['id']
            # 添加子节点
            for variety_item in group_item['varieties']:
                child = QTreeWidgetItem()
                child.setText(0, variety_item['name'])
                child.vid = variety_item['id']
                group.addChild(child)

    # 点击分组树
    def group_tree_clicked(self):
        item = self.group_tree.currentItem()
        if item.childCount():  # has children open the root
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        text = item.text(0)
        if item.parent():
            # 提示只能在大类下创建品种
            el = self.findChild(QLabel, 'groupError')
            el.setText('只能在分组下新增品种,如需新建,请点击左下角【新建组别】')
            self.add_variety_btn.setEnabled(False)
        else:
            # 该表所属分组
            self.attach_group.setText(text)
            self.attach_group.gid = item.gid
            # 清除提示消息
            el = self.findChild(QLabel, 'groupError')
            el.setText('')
            self.add_variety_btn.setEnabled(True)

    # 新增品种提交
    def add_new_variety(self):
        # 获取当前选择的分组
        if not self.attach_group.gid:
            # 提示只能在大类下创建品种
            el = self.findChild(QLabel, 'groupError')
            el.setText('请选择品种所属的分组,如需新建,请点击左下角【新建组别】')
            self.add_variety_btn.setEnabled(False)
            return
        vname = re.sub(r'\s+', '', self.vnedit.text())
        vname_en = re.sub(r'\s+', '', self.venedit.text())
        vname_en = re.match('[a-z0-9]+', vname_en)
        if not vname:
            el = self.findChild(QLabel, 'nvnameError')
            el.setText('还没输入品种的名称')
            self.add_variety_btn.setEnabled(False)
            return
        if not vname_en:
            el = self.findChild(QLabel, 'nvenameError')
            el.setText('请输入正确的英文代码,小写字母和数字一种或多种组成')
            self.add_variety_btn.setEnabled(False)
            return
        vname_en = vname_en.group()
        # 提交
        try:
            r = requests.post(
                url=config.SERVER_ADDR + 'basic/variety/?mc=' + config.app_dawn.value('machine'),
                headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    "gid": self.attach_group.gid,
                    "name": vname,
                    "name_en": vname_en
                }),
                cookies=config.app_dawn.value('cookies')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            el = self.findChild(QLabel, 'nvenameError')
            el.setText(str(e))
        else:
            self.vnedit.clear()
            self.venedit.clear()
            self.get_groups()

    # 品种中文编辑框的信号函数
    def vn_changed(self):
        el = self.findChild(QLabel, 'nvnameError')
        el.setText('')
        self.add_variety_btn.setEnabled(True)

    # 品种英文编辑框的信号函数
    def ven_changed(self):
        el = self.findChild(QLabel, 'nvenameError')
        el.setText('')
        self.add_variety_btn.setEnabled(True)

    # 新增品种分组
    def create_vgroup(self):
        print('新增品种分组')
        self.vgpopup = QDialog(parent=self)  # variety group popup
        self.vgpopup.deleteLater()
        playout = QGridLayout()  # popup layout
        playout.addWidget(QLabel('组名称：'), 0, 0)
        playout.addWidget(QLineEdit(parent=self.vgpopup, objectName='nvgEdit'), 0, 1)  # nvg = new variety group
        playout.addWidget(QLabel(parent=self.vgpopup, objectName='nvgError'), 1, 0, 1, 2)
        abtlayout = QHBoxLayout()
        abtlayout.addWidget(QPushButton('增加', parent=self.vgpopup, objectName='addNvgbtn',
                                        clicked=self.add_new_vgroup), alignment=Qt.AlignRight)
        playout.addLayout(abtlayout, 1, 1)
        self.vgpopup.setLayout(playout)
        self.vgpopup.resize(300, 120)
        self.vgpopup.setWindowTitle('增加品种组')
        if not self.vgpopup.exec_():
            del self.vgpopup

    # 新增品种大分类
    def add_new_vgroup(self):
        print('新增品种大类')
        edit = self.vgpopup.findChild(QLineEdit, 'nvgEdit')
        group_name = re.sub(r'\s+', '', edit.text())
        if not group_name:
            el = self.vgpopup.findChild(QLabel, 'nvgError')
            el.setText('请输入正确的组名称.')
            return
        # 提交
        commit_btn = self.vgpopup.findChild(QPushButton, 'addNvgbtn')
        commit_btn.setEnabled(False)
        try:
            r = requests.post(
                url=config.SERVER_ADDR + 'basic/variety-groups/?mc=' + config.app_dawn.value('machine'),
                headers={'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    "name": group_name
                }),
                cookies=config.app_dawn.value('cookies')
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            el = self.vgpopup.findChild(QLabel, 'nvgError')
            el.setText(str(e))
        else:
            # 重新刷新目录树
            self.get_groups()
            self.vgpopup.close()
        commit_btn.setEnabled(True)

















class CreateNewClient(QDialog):
    new_data_signal = pyqtSignal(dict)
    def __init__(self, *args):
        super(CreateNewClient, self).__init__(*args)
        self.setMinimumWidth(360)
        self.setWindowTitle('新建')
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignRight)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('为这个客户端起一个名字')
        self.machine = QLineEdit()
        self.machine.setPlaceholderText('输入机器码(小写字母与数字组合)')
        self.bulletin_days = QLineEdit()
        self.bulletin_days.setPlaceholderText("支持输入整数(默认为1)")
        self.bulletin_days.setValidator(QIntValidator())
        self.admin_check = QCheckBox()
        self.active_check = QCheckBox()
        self.active_check.setChecked(True)
        submit_btn = QPushButton("提交")
        submit_btn.clicked.connect(self.new_client_signal)
        layout.addRow('*客户端名称：', self.name_edit)
        layout.addRow('*机器码：', self.machine)
        layout.addRow('公告展示(天)：', self.bulletin_days)
        layout.addRow('管理端：', self.admin_check)
        layout.addRow('有效：', self.active_check)
        layout.addRow('', submit_btn)
        self.setLayout(layout)

    def new_client_signal(self):
        # 收集客户端信息
        bulletin_day = self.bulletin_days.text().strip(' ')
        data = dict()
        data['name'] = self.name_edit.text().strip(' ')
        data['machine_code'] = self.machine.text().strip(' ')
        data['bulletin_days'] = bulletin_day if bulletin_day else 1
        data['is_admin'] = self.admin_check.isChecked()
        data['is_active'] = self.active_check.isChecked()
        data['operation_code'] = config.app_dawn.value('machine')
        if not config.app_dawn.value('cookies'):
            QMessageBox.information(self, '提示', "请先登录再进行操作~", QMessageBox.Yes)
            return
        if not data['name']:
            QMessageBox.information(self, '提示', "请为这个客户端取个名字~", QMessageBox.Yes)
            return
        if not re.match(r'^[0-9a-z]+$', data['machine_code']):
            QMessageBox.information(self, '提示', "机器码格式有误~", QMessageBox.Yes)
            return
        # emit signal
        self.new_data_signal.emit(data)


class UploadFile(QDialog):
    def __init__(self, url):
        super(UploadFile, self).__init__()
        self.url = url
        layout = QGridLayout()
        # widgets
        title_label = QLabel('标题')
        file_label = QLabel('文件')
        self.title_edit = QLineEdit()
        self.file_edit = QLineEdit()
        select_btn = QPushButton('选择')
        submit_btn = QPushButton('提交')
        # signal
        select_btn.clicked.connect(self.select_file)
        submit_btn.clicked.connect(self.submit_file)
        # style
        self.setMinimumWidth(300)
        select_btn.setMaximumWidth(30)
        self.title_edit.setPlaceholderText('默认文件名')
        self.file_edit.setEnabled(False)
        # add layout
        layout.addWidget(title_label, 0, 0)
        layout.addWidget(self.title_edit, 0, 1, 1, 2)
        layout.addWidget(file_label, 1, 0)
        layout.addWidget(self.file_edit, 1,1)
        layout.addWidget(select_btn, 1,2)
        layout.addWidget(submit_btn, 2, 1, 1,2)
        self.setLayout(layout)

    def select_file(self):
        # select file
        desktop_path = get_desktop_path()
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', desktop_path, "PDF files (*.pdf)")
        if not file_path:
            return
        file_name_list = file_path.rsplit('/', 1)
        if not self.title_edit.text().strip(' '):
            self.title_edit.setText((file_name_list[1].rsplit('.', 1))[0])
        self.file_edit.setText(file_path)

    def submit_file(self):
        # submit file to server
        title = self.title_edit.text().strip(' ')
        if not title:
            self.title_edit.setPlaceholderText('您还未填写标题.')
            return
        data = dict()
        file_path = self.file_edit.text().strip(' ')
        file_raw_name = file_path.rsplit("/", 1)
        file = open(file_path, "rb")
        file_content = file.read()
        file.close()
        data['title'] = title
        data["file"] = (file_raw_name[1], file_content)
        data['machine_code'] = config.app_dawn.value('machine')
        encode_data = encode_multipart_formdata(data)
        data = encode_data[0]
        headers = config.CLIENT_HEADERS
        headers['Content-Type'] = encode_data[1]
        try:
            response = requests.post(
                url=self.url,
                headers=headers,
                data=data,
                cookies=config.app_dawn.value('cookies')
            )
        except Exception as error:
            QMessageBox.information(self, '提示', "发生了个错误!\n{}".format(error), QMessageBox.Yes)
            return
        response_data = json.loads(response.content.decode('utf-8'))
        if response.status_code != 201:
            QMessageBox.information(self, '提示', response_data['message'], QMessageBox.Yes)
            return
        else:
            QMessageBox.information(self, '成功', '添加成功, 赶紧刷新看看吧.', QMessageBox.Yes)
            self.close()  # close the dialog
