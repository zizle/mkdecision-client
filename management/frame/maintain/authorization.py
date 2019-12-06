# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QHeaderView, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from widgets.maintain.base import ManagerAbstractTable
import config


# 客户端权限管理表格
class UserToClientTable(ManagerAbstractTable):
    HEADER_LABELS = [
        ('index', '序号'),
        ('name', '名称'),
        ('machine_code', '机器码'),
        ('is_active', '有效'),
        ('accessed', '可登录'),
        ('category', '类型'),
    ]
    NO_EDIT_COLUMNS = [0]
    CHECKBOX_COLUMNS = [3, 4]
    COMBOBOX_COLUMNS = [
        (5, [('管理端', 'is_manager'), ('普通端', '')]),
    ]

    def __init__(self, customer_id, *args,**kwargs):
        super(UserToClientTable, self).__init__(*args, **kwargs)
        self.customer_id = customer_id

    def setVerticalSectionResizeMode(self):
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(len(self.HEADER_LABELS), QHeaderView.ResizeToContents)

    # 修改有效
    def check_button_changed(self, check_widget):
        row, column = self._get_widget_index(check_widget)
        text = '1' if check_widget.check_button.isChecked() else '0'
        self.item(row, column).setText(text)

    # 表格信息变化，即修改权限或客户端相关信息
    def changed_table_text(self, item):
        current_row = item.row()
        current_column = item.column()
        client_id = self.item(current_row, 0).row_item_id
        print('修改id=%d的客户端%s为:%s' % (client_id, self.HEADER_LABELS[current_column][1], item.text()))
        modify_content = int(item.text()) if current_column in self.CHECKBOX_COLUMNS else item.text()
        fields = {self.HEADER_LABELS[current_column][0]: modify_content}
        if self.HEADER_LABELS[current_column][0] == 'accessed':  # 修改可登录状态，需要加入当前操作的用户id
            fields['current_user_id'] = self.customer_id
        for couple_column in self.COMBOBOX_COLUMNS:
            if current_column == couple_column[0]:
                if item.text():
                    fields = {item.text(): True}
                else:
                    fields = {'is_manager': False}

        modify_result = self._modify_row_content(
            url=config.SERVER_ADDR + 'limit/user-client/' + str(client_id) + '/?mc=' + config.app_dawn.value(
                    'machine'),
            fields=fields
        )
        print('修改结果：', modify_result)
        return
        # 关闭信号再修改单元格内容，防止继续向后端发送请求
        self.blockSignals(True)
        if modify_result:
            # 修改单元格内容
            self.item(current_row, current_column).setText(str(modify_result[self.HEADER_LABELS[current_column][0]]))
        else:
            self.item(current_row, current_column).setText(self.text_ready_to_changed)
        # 恢复信号
        self.blockSignals(False)




# 【权限管理】用户-客户端
class UserToClientAuth(QWidget):
    network_result = pyqtSignal(str)

    def __init__(self, user_id, *args, **kwargs):
        super(UserToClientAuth, self).__init__(*args, **kwargs)
        self.current_user_id = user_id
        layout = QVBoxLayout(margin=0)
        # 下拉框选择
        combo_layout = QHBoxLayout()
        self.client_combo = QComboBox()
        self.client_combo.currentIndexChanged.connect(self.client_combo_changed)
        combo_layout.addWidget(QLabel('类型:'))
        combo_layout.addWidget(self.client_combo)
        combo_layout.addStretch()
        layout.addLayout(combo_layout)
        # 管理表格
        self.client_table = UserToClientTable(customer_id=user_id)
        self.client_table.network_result.connect(self.network_result.emit)  # 直接传出信号
        layout.addWidget(self.client_table)
        self.setLayout(layout)
        # 初始化
        self._combo_selects()

    # 增加客户端类型选择
    def _combo_selects(self):
        for client_item in [
            {'category': '全部', 'flag': 'all'},
            {'category': '管理端', 'flag': 'is_manager'},
            {'category': '普通端', 'flag': None},

        ]:
            self.client_combo.addItem(client_item['category'], client_item['flag'])

    # 客户端类型选择变化
    def client_combo_changed(self):
        self.network_result.emit('')
        current_data = self.client_combo.currentData()
        # 获取相应的客户端
        params = {
            'current_user_id': self.current_user_id
        }
        if current_data == 'all':
            pass
        elif current_data is None:  # 普通端
            params['is_manager'] = False
        else:
            params[current_data] = True
        self._get_clients(params)

    # 根据下拉框变化获取客户端信息
    def _get_clients(self, params):
        try:
            r = requests.get(
                url=config.SERVER_ADDR + 'limit/user-client/?mc=' + config.app_dawn.value('machine'),
                headers={
                    'AUTHORIZATION': config.app_dawn.value('Authorization')
                },
                data=json.dumps(params)
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 200:
                raise ValueError(response['message'])
        except Exception as e:
            self.network_result.emit(str(e))
            return
        else:
            self.client_table.showRowsContent(json_list=response['data'])
            self.network_result.emit(response['message'])
