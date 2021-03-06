# _*_ coding:utf-8 _*_
# __Author__： zizle
import re
import json
import requests
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import QDialog, QDateEdit, QTimeEdit,QMessageBox, QVBoxLayout, QTextEdit, QHBoxLayout,QGridLayout, QLabel, \
    QPushButton, QLineEdit, QFileDialog
from PyQt5.QtCore import Qt, QDate, QTime
import settings


""" 培训服务-品种介绍 """

# 修改部门组建文件
class ModifyVarietyIntroPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(ModifyVarietyIntroPopup, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        layout.addWidget(QLabel('文件:'), 0, 0)
        self.file_edit = QLineEdit()
        self.file_edit.setEnabled(False)
        layout.addWidget(self.file_edit, 0, 1)
        layout.addWidget(QPushButton('浏览', clicked=self.select_file), 0, 2)
        layout.addWidget(QLabel(objectName='fileError'), 1, 0, 1, 3)
        layout.addWidget(QPushButton('确定', clicked=self.commit_upload), 2, 1, 1, 2)
        self.setMinimumWidth(400)
        self.setWindowTitle('修改文件')
        self.setLayout(layout)

    # 选择文件
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files(*.pdf)")
        if file_path:
            # file_name = file_path.rsplit('/', 1)[1]
            # file_name = file_name.rsplit('.', 1)[0]
            # self.name_edit.setText(file_name)
            self.file_edit.setText(file_path)

    # 修改人才培养显示文件内容
    def commit_upload(self):
        # name = re.sub(r'\s+', '', self.name_edit.text())
        # if not name:
        #     self.findChild(QLabel, 'nameError').setText('请输入名称!')
        #     return
        file_path = self.file_edit.text()
        file_name = file_path.rsplit('/', 1)[1]
        data_file = dict()
        # # 增加其他字段
        data_file['utoken'] = settings.app_dawn.value('AUTHORIZATION')
        # data_file['name'] = name
        # 读取文件
        file = open(file_path, "rb")
        file_content = file.read()
        file.close()
        # 文件内容字段
        data_file["variety_file"] = (file_name, file_content)
        encode_data = encode_multipart_formdata(data_file)
        data_file = encode_data[0]
        # 发起上传请求
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'train/varietyintro/',
                headers={'Content-Type': encode_data[1]},
                data=data_file
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])

        except Exception as e:
            QMessageBox.information(self, '错误', str(e))
        else:
            QMessageBox.information(self, '成功', response['message'])
            self.close()



""" 策略服务-套保方案 """


# 上传套保方案
class CreateNewHedgePlanPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateNewHedgePlanPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QGridLayout()
        layout.addWidget(QLabel('名称:'), 0, 0)
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit, 0, 1, 1, 2)
        layout.addWidget(QLabel(), 1, 0, 1, 3)
        layout.addWidget(QLabel('文件:'), 2, 0)
        self.file_edit = QLineEdit()
        self.file_edit.setEnabled(False)
        layout.addWidget(self.file_edit, 2, 1)
        layout.addWidget(QPushButton('浏览', clicked=self.select_file), 2, 2)
        layout.addWidget(QLabel(objectName='fileError'), 3, 0, 1, 3)
        layout.addWidget(QPushButton('确定', clicked=self.commit_upload), 4, 1, 1, 2)
        self.setMinimumWidth(400)
        self.setWindowTitle('新增方案')
        self.setLayout(layout)

    # 选择文件
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files(*.pdf)")
        if file_path:
            file_name = file_path.rsplit('/', 1)[1]
            file_name = file_name.rsplit('.', 1)[0]
            self.name_edit.setText(file_name)
            self.file_edit.setText(file_path)

    # 上传方案文件
    def commit_upload(self):
        name = re.sub(r'\s+', '', self.name_edit.text())
        if not name:
            self.findChild(QLabel, 'nameError').setText('请输入名称!')
            return
        file_path = self.file_edit.text()
        file_name = file_path.rsplit('/', 1)[1]
        data_file = dict()
        # 增加其他字段
        data_file['utoken'] = settings.app_dawn.value('AUTHORIZATION')
        data_file['title'] = name
        # 读取文件
        file = open(file_path, "rb")
        file_content = file.read()
        file.close()
        # 文件内容字段
        data_file["hedge_file"] = (file_name, file_content)
        encode_data = encode_multipart_formdata(data_file)
        data_file = encode_data[0]
        # 发起上传请求
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'strategy/hedgeplan/',
                headers={'Content-Type': encode_data[1]},
                data=data_file
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])

        except Exception as e:
            QMessageBox.information(self, '错误', str(e))
        else:
            QMessageBox.information(self, '成功', response['message'])
            self.close()


""" 策略服务-投资方案 """


# 上传投资方案
class CreateNewInvestPlanPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateNewInvestPlanPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QGridLayout()
        layout.addWidget(QLabel('名称:'), 0, 0)
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit, 0, 1, 1, 2)
        layout.addWidget(QLabel(), 1, 0, 1, 3)
        layout.addWidget(QLabel('文件:'), 2, 0)
        self.file_edit = QLineEdit()
        self.file_edit.setEnabled(False)
        layout.addWidget(self.file_edit, 2, 1)
        layout.addWidget(QPushButton('浏览', clicked=self.select_file), 2, 2)
        layout.addWidget(QLabel(objectName='fileError'), 3, 0, 1, 3)
        layout.addWidget(QPushButton('确定', clicked=self.commit_upload), 4, 1, 1, 2)
        self.setMinimumWidth(400)
        self.setWindowTitle('新增方案')
        self.setLayout(layout)

    # 选择文件
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files(*.pdf)")
        if file_path:
            file_name = file_path.rsplit('/', 1)[1]
            file_name = file_name.rsplit('.', 1)[0]
            self.name_edit.setText(file_name)
            self.file_edit.setText(file_path)

    # 上传方案文件
    def commit_upload(self):
        name = re.sub(r'\s+', '', self.name_edit.text())
        if not name:
            self.findChild(QLabel, 'nameError').setText('请输入名称!')
            return
        file_path = self.file_edit.text()
        file_name = file_path.rsplit('/', 1)[1]
        data_file = dict()
        # 增加其他字段
        data_file['title'] = name
        data_file['utoken'] = settings.app_dawn.value('AUTHORIZATION')
        # 读取文件
        file = open(file_path, "rb")
        file_content = file.read()
        file.close()
        # 文件内容字段
        data_file["invest_file"] = (file_name, file_content)
        encode_data = encode_multipart_formdata(data_file)
        data_file = encode_data[0]
        # 发起上传请求
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'strategy/investmentplan/',
                headers={'Content-Type': encode_data[1]},
                data=data_file
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])

        except Exception as e:
            QMessageBox.information(self, '错误', str(e))
        else:
            QMessageBox.information(self, '成功', response['message'])
            self.close()


""" 策略服务-交易策略 """


# 创建交易策略弹窗
class CreateNewTradePolicyPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateNewTradePolicyPopup, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        # 时间布局
        date_time_layout = QHBoxLayout()
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        date_time_layout.addWidget(QLabel('日期:'))
        date_time_layout.addWidget(self.date_edit)
        date_time_layout.addWidget(QLabel('时间:'))
        self.time_edit = QTimeEdit(QTime.currentTime())
        self.time_edit.setDisplayFormat('HH:mm:ss')
        date_time_layout.addWidget(self.time_edit)
        date_time_layout.addStretch()
        layout.addLayout(date_time_layout)
        self.text_edit = QTextEdit(textChanged=self.set_show_tips_null)
        layout.addWidget(self.text_edit)
        self.show_tips = QLabel()
        layout.addWidget(self.show_tips)
        layout.addWidget(QPushButton('确定', clicked=self.commit_trade_policy), alignment=Qt.AlignRight)
        self.setLayout(layout)
        self.resize(400, 200)
        self.setWindowTitle('新建短信通')

    def set_show_tips_null(self):
        self.show_tips.setText('')

    # 确定增加
    def commit_trade_policy(self):
        text = self.text_edit.toPlainText().strip(' ')
        if not text:
            self.show_tips.setText('请输入内容。')
            return
        # 提交
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'info/trade-policy/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'date': self.date_edit.text(),
                    'time': self.time_edit.text(),
                    'content': text
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            self.show_tips.setText(str(e))
        else:
            self.show_tips.setText(response['message'])


# 修改交易策略弹窗
class EditTradePolicy(QDialog):
    def __init__(self, sms_data, *args, **kwargs):
        super(EditTradePolicy, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        print(sms_data)
        self.sms_id = sms_data['id']
        # 时间布局
        date_time_layout = QHBoxLayout()
        self.date_edit = QDateEdit(QDate.fromString(sms_data['date'], 'yyyy-MM-dd'))
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        date_time_layout.addWidget(QLabel('日期:'))
        date_time_layout.addWidget(self.date_edit)
        date_time_layout.addWidget(QLabel('时间:'))
        self.time_edit = QTimeEdit(QTime.fromString(sms_data['time'], 'HH:mm:ss'))
        self.time_edit.setDisplayFormat('HH:mm:ss')
        date_time_layout.addWidget(self.time_edit)
        date_time_layout.addStretch()
        layout.addLayout(date_time_layout)
        self.show_tips = QLabel()
        self.text_edit = QTextEdit(textChanged=self.set_show_tips_null)
        self.text_edit.setPlainText(sms_data['content'])
        layout.addWidget(self.text_edit)
        layout.addWidget(self.show_tips)
        layout.addWidget(QPushButton('确定', clicked=self.commit_policy_edited), alignment=Qt.AlignRight)
        self.setLayout(layout)
        self.resize(420, 240)
        self.setWindowTitle('编辑短信通')

    def set_show_tips_null(self):
        self.show_tips.setText('')

    # 确定提交修改
    def commit_policy_edited(self):
        text = self.text_edit.toPlainText().strip(' ')
        if not text:
            self.show_tips.setText('请输入内容。')
            return
        # 提交
        try:
            r = requests.put(
                url=settings.SERVER_ADDR + 'info/trade-policy/' + str(self.sms_id) + '/?mc=' + settings.app_dawn.value(
                    'machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'date': self.date_edit.text(),
                    'time': self.time_edit.text(),
                    'content': text
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            self.show_tips.setText(str(e))
        else:
            self.show_tips.setText(response['message'])


""" 顾问服务-制度考核 """


# 制度考核文件修改
class ModifyInstExaminePopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(ModifyInstExaminePopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QGridLayout()
        # layout.addWidget(QLabel('名称:'), 0, 0)
        # self.name_edit = QLineEdit()
        # layout.addWidget(self.name_edit, 0, 1, 1, 2)
        # layout.addWidget(QLabel(), 1, 0, 1, 3)
        layout.addWidget(QLabel('文件:'), 0, 0)
        self.file_edit = QLineEdit()
        self.file_edit.setEnabled(False)
        layout.addWidget(self.file_edit, 0, 1)
        layout.addWidget(QPushButton('浏览', clicked=self.select_file), 0, 2)
        layout.addWidget(QLabel(objectName='fileError'), 1, 0, 1, 3)
        layout.addWidget(QPushButton('确定', clicked=self.commit_upload), 2, 1, 1, 2)
        self.setMinimumWidth(400)
        self.setWindowTitle('修改文件')
        self.setLayout(layout)

    # 选择文件
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files(*.pdf)")
        if file_path:
            # file_name = file_path.rsplit('/', 1)[1]
            # file_name = file_name.rsplit('.', 1)[0]
            # self.name_edit.setText(file_name)
            self.file_edit.setText(file_path)

    # 修改人才培养显示文件内容
    def commit_upload(self):
        # name = re.sub(r'\s+', '', self.name_edit.text())
        # if not name:
        #     self.findChild(QLabel, 'nameError').setText('请输入名称!')
        #     return
        file_path = self.file_edit.text()
        file_name = file_path.rsplit('/', 1)[1]
        data_file = dict()
        # # 增加其他字段
        data_file['utoken'] = settings.app_dawn.value('AUTHORIZATION')
        # data_file['name'] = name
        # 读取文件
        file = open(file_path, "rb")
        file_content = file.read()
        file.close()
        # 文件内容字段
        data_file["rxm_file"] = (file_name, file_content)
        encode_data = encode_multipart_formdata(data_file)
        data_file = encode_data[0]
        # 发起上传请求
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'consult/rulexamine/',
                headers={'Content-Type': encode_data[1]},
                data=data_file
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])

        except Exception as e:
            QMessageBox.information(self, '错误', str(e))
        else:
            QMessageBox.information(self, '错误', response['message'])
            self.close()


""" 顾问服务-部门组建相关 """


# 修改部门组建文件
class ModifyDeptBuildPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(ModifyDeptBuildPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QGridLayout()
        # layout.addWidget(QLabel('名称:'), 0, 0)
        # self.name_edit = QLineEdit()
        # layout.addWidget(self.name_edit, 0, 1, 1, 2)
        # layout.addWidget(QLabel(), 1, 0, 1, 3)
        layout.addWidget(QLabel('文件:'), 0, 0)
        self.file_edit = QLineEdit()
        self.file_edit.setEnabled(False)
        layout.addWidget(self.file_edit, 0, 1)
        layout.addWidget(QPushButton('浏览', clicked=self.select_file), 0, 2)
        layout.addWidget(QLabel(objectName='fileError'), 1, 0, 1, 3)
        layout.addWidget(QPushButton('确定', clicked=self.commit_upload), 2, 1, 1, 2)
        self.setMinimumWidth(400)
        self.setWindowTitle('修改文件')
        self.setLayout(layout)

    # 选择文件
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files(*.pdf)")
        if file_path:
            # file_name = file_path.rsplit('/', 1)[1]
            # file_name = file_name.rsplit('.', 1)[0]
            # self.name_edit.setText(file_name)
            self.file_edit.setText(file_path)

    # 修改人才培养显示文件内容
    def commit_upload(self):
        # name = re.sub(r'\s+', '', self.name_edit.text())
        # if not name:
        #     self.findChild(QLabel, 'nameError').setText('请输入名称!')
        #     return
        file_path = self.file_edit.text()
        file_name = file_path.rsplit('/', 1)[1]
        data_file = dict()
        data_file['utoken'] = settings.app_dawn.value('AUTHORIZATION')
        file = open(file_path, "rb")
        file_content = file.read()
        file.close()
        # 文件内容字段
        data_file["depb_file"] = (file_name, file_content)
        encode_data = encode_multipart_formdata(data_file)
        data_file = encode_data[0]
        # 发起上传请求
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'consult/deptbuild/',
                headers={'Content-Type': encode_data[1]},
                data=data_file
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])

        except Exception as e:
            QMessageBox.information(self, '错误', str(e))
        else:
            QMessageBox.information(self, '错误', response['message'])
            self.close()


""" 顾问服务-人才培养相关 """


# 修改人才培养显示的文件
class ModifyPersonnelTrainPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(ModifyPersonnelTrainPopup, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        # layout.addWidget(QLabel('名称:'), 0, 0)
        # self.name_edit = QLineEdit()
        # layout.addWidget(self.name_edit, 0, 1, 1, 2)
        # layout.addWidget(QLabel(), 1, 0, 1, 3)
        layout.addWidget(QLabel('文件:'), 0, 0)
        self.file_edit = QLineEdit()
        self.file_edit.setEnabled(False)
        layout.addWidget(self.file_edit, 0, 1)
        layout.addWidget(QPushButton('浏览', clicked=self.select_file), 0, 2)
        layout.addWidget(QLabel(objectName='fileError'), 1, 0, 1, 3)
        layout.addWidget(QPushButton('确定', clicked=self.commit_upload), 2, 1, 1, 2)
        self.setMinimumWidth(400)
        self.setWindowTitle('修改文件')
        self.setLayout(layout)

        # 选择文件

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files(*.pdf)")
        if file_path:
            # file_name = file_path.rsplit('/', 1)[1]
            # file_name = file_name.rsplit('.', 1)[0]
            # self.name_edit.setText(file_name)
            self.file_edit.setText(file_path)

    # 修改人才培养显示文件内容
    def commit_upload(self):
        file_path = self.file_edit.text()
        file_name = file_path.rsplit('/', 1)[1]
        data_file = dict()
        # 增加其他字段
        data_file['utoken'] = settings.app_dawn.value('AUTHORIZATION')
        # data_file['name'] = name
        # 读取文件
        file = open(file_path, "rb")
        file_content = file.read()
        file.close()
        # 文件内容字段
        data_file["pt_file"] = (file_name, file_content)
        encode_data = encode_multipart_formdata(data_file)
        data_file = encode_data[0]
        # 发起上传请求
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'consult/persontrain/',
                headers={'Content-Type': encode_data[1]},
                data=data_file
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, '错误', str(e))
        else:
            QMessageBox.information(self, '成功', response['message'])
            self.close()


""" 专题研究相关 """


# 上传新专题研究文件
class CreateNewTopicSearchPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateNewTopicSearchPopup, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        layout.addWidget(QLabel('名称:'), 0, 0)
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit, 0, 1, 1, 2)
        layout.addWidget(QLabel(), 1, 0, 1, 3)
        layout.addWidget(QLabel('文件:'), 2, 0)
        self.file_edit = QLineEdit()
        self.file_edit.setEnabled(False)
        layout.addWidget(self.file_edit, 2, 1)
        layout.addWidget(QPushButton('浏览', clicked=self.select_file), 2, 2)
        layout.addWidget(QLabel(objectName='fileError'), 3, 0, 1, 3)
        layout.addWidget(QPushButton('确定', clicked=self.commit_upload), 4, 1, 1, 2)
        self.setMinimumWidth(400)
        self.setWindowTitle('新增文件')
        self.setLayout(layout)
        self.setAttribute(Qt.WA_DeleteOnClose)

    # 选择文件
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files(*.pdf)")
        if file_path:
            file_name = file_path.rsplit('/', 1)[1]
            file_name = file_name.rsplit('.', 1)[0]
            self.name_edit.setText(file_name)
            self.file_edit.setText(file_path)

    # 上传专题研究
    def commit_upload(self):
        name = re.sub(r'\s+', '', self.name_edit.text())
        if not name:
            self.findChild(QLabel, 'nameError').setText('请输入名称!')
            return
        file_path = self.file_edit.text()
        file_name = file_path.rsplit('/', 1)[1]
        data_file = dict()
        # 增加其他字段
        data_file['utoken'] = settings.app_dawn.value('AUTHORIZATION')
        data_file['title'] = name
        # 读取文件
        file = open(file_path, "rb")
        file_content = file.read()
        file.close()
        # 文件内容字段
        data_file["topic_file"] = (file_name, file_content)
        encode_data = encode_multipart_formdata(data_file)
        data_file = encode_data[0]
        # 发起上传请求
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'advise/topicsearch/',
                headers={'Content-Type': encode_data[1]},
                data=data_file
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])

        except Exception as e:
            QMessageBox.information(self, '错误', str(e))
        else:
            QMessageBox.information(self, '成功', '上传成功!')
            self.close()


""" 调研报告相关 """


# 新增上传调研报告文件
class CreateNewSearchReportPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateNewSearchReportPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QGridLayout()
        layout.addWidget(QLabel('名称:'), 0, 0)
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit, 0, 1, 1, 2)
        layout.addWidget(QLabel(), 1, 0, 1, 3)
        layout.addWidget(QLabel('文件:'), 2, 0)
        self.file_edit = QLineEdit()
        self.file_edit.setEnabled(False)
        layout.addWidget(self.file_edit, 2, 1)
        layout.addWidget(QPushButton('浏览', clicked=self.select_file), 2, 2)
        layout.addWidget(QLabel(objectName='fileError'), 3, 0, 1, 3)
        layout.addWidget(QPushButton('确定', clicked=self.commit_upload), 4, 1, 1, 2)
        self.setMinimumWidth(400)
        self.setWindowTitle('新增报告')
        self.setLayout(layout)

    # 选择文件
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files(*.pdf)")
        if file_path:
            file_name = file_path.rsplit('/', 1)[1]
            file_name = file_name.rsplit('.', 1)[0]
            self.name_edit.setText(file_name)
            self.file_edit.setText(file_path)

    # 上传调研报告
    def commit_upload(self):
        name = re.sub(r'\s+', '', self.name_edit.text())
        if not name:
            self.findChild(QLabel, 'nameError').setText('请输入名称!')
            return
        file_path = self.file_edit.text()
        file_name = file_path.rsplit('/', 1)[1]
        data_file = dict()
        # 增加其他字段
        data_file['utoken'] = settings.app_dawn.value('AUTHORIZATION')
        data_file['title'] = name
        # 读取文件
        file = open(file_path, "rb")
        file_content = file.read()
        file.close()
        # 文件内容字段
        data_file["sreport_file"] = (file_name, file_content)
        encode_data = encode_multipart_formdata(data_file)
        data_file = encode_data[0]
        # 发起上传请求
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'advise/searchreport/',
                headers={'Content-Type': encode_data[1]},
                data=data_file
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])

        except Exception as e:
            QMessageBox.information(self, '错误', str(e))
        else:
            QMessageBox.information(self, '成功', response['message'])
            self.close()


""" 市场分析相关 """


# 上传市场分析文件
class CreateNewMarketAnalysisPopup(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateNewMarketAnalysisPopup, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QGridLayout()
        layout.addWidget(QLabel('名称:'), 0, 0)
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit, 0, 1, 1, 2)
        layout.addWidget(QLabel(), 1, 0, 1, 3)
        layout.addWidget(QLabel('文件:'), 2, 0)
        self.file_edit = QLineEdit()
        self.file_edit.setEnabled(False)
        layout.addWidget(self.file_edit, 2, 1)
        layout.addWidget(QPushButton('浏览', clicked=self.select_file), 2, 2)
        layout.addWidget(QLabel(objectName='fileError'), 3, 0, 1, 3)
        layout.addWidget(QPushButton('确定', clicked=self.commit_upload), 4, 1, 1, 2)
        self.setMinimumWidth(400)
        self.setWindowTitle('新增文件')
        self.setLayout(layout)

    # 选择文件
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', "PDF files(*.pdf)")
        if file_path:
            file_name = file_path.rsplit('/', 1)[1]
            file_name = file_name.rsplit('.', 1)[0]
            self.name_edit.setText(file_name)
            self.file_edit.setText(file_path)

    # 上传市场分析
    def commit_upload(self):
        name = re.sub(r'\s+', '', self.name_edit.text())
        if not name:
            self.findChild(QLabel, 'nameError').setText('请输入名称!')
            return
        file_path = self.file_edit.text()
        file_name = file_path.rsplit('/', 1)[1]
        data_file = dict()
        data_file['utoken'] = settings.app_dawn.value('AUTHORIZATION')
        # 增加其他字段
        data_file['title'] = name
        # 读取文件
        file = open(file_path, "rb")
        file_content = file.read()
        file.close()
        # 文件内容字段
        data_file["market_file"] = (file_name, file_content)
        encode_data = encode_multipart_formdata(data_file)
        data_file = encode_data[0]
        # 发起上传请求
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'advise/marketanalysis/',
                headers={
                    'Content-Type': encode_data[1]
                },
                data=data_file
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])

        except Exception as e:
            QMessageBox.information(self, '错误', '失败:{}'.format(e))
        else:
            QMessageBox.information(self, '成功', '添加数据成功.')
            self.close()


""" 短信通相关 """


# 创建短信通弹窗
class CreateNewSMSLink(QDialog):
    def __init__(self, *args, **kwargs):
        super(CreateNewSMSLink, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QVBoxLayout()
        # 时间布局
        date_time_layout = QHBoxLayout()
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        date_time_layout.addWidget(QLabel('日期:'))
        date_time_layout.addWidget(self.date_edit)
        date_time_layout.addWidget(QLabel('时间:'))
        self.time_edit = QTimeEdit(QTime.currentTime())
        self.time_edit.setDisplayFormat('HH:mm:ss')
        date_time_layout.addWidget(self.time_edit)
        date_time_layout.addStretch()
        layout.addLayout(date_time_layout)
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)
        layout.addWidget(QPushButton('确定', clicked=self.commit_sms), alignment=Qt.AlignRight)
        self.setLayout(layout)
        self.setFixedSize(400, 200)
        self.setWindowTitle('新建短信通')


    # 确定增加
    def commit_sms(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.information(self,'错误', '请输入内容。')
            return
        # 提交
        try:
            r = requests.post(
                url=settings.SERVER_ADDR + 'advise/shortmessage/',
                headers={'Content-Type': 'application/json;charset=utf8'},
                data=json.dumps({
                    'utoken':settings.app_dawn.value('AUTHORIZATION'),
                    'custom_time': self.date_edit.text() + ' ' + self.time_edit.text(),
                    'content': text
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self,'错误', str(e))
        else:
            QMessageBox.information(self,'成功', "新增成功")
            self.close()


# 修改短信通弹窗
class EditSMSLink(QDialog):
    def __init__(self, sms_data, *args, **kwargs):
        super(EditSMSLink, self).__init__(*args, **kwargs)
        layout = QVBoxLayout(margin=0)
        print(sms_data)
        self.sms_id = sms_data['id']
        # 时间布局
        date_time_layout = QHBoxLayout()
        self.date_edit = QDateEdit(QDate.fromString(sms_data['date'], 'yyyy-MM-dd'))
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        date_time_layout.addWidget(QLabel('日期:'))
        date_time_layout.addWidget(self.date_edit)
        date_time_layout.addWidget(QLabel('时间:'))
        self.time_edit = QTimeEdit(QTime.fromString(sms_data['time'], 'HH:mm:ss'))
        self.time_edit.setDisplayFormat('HH:mm:ss')
        date_time_layout.addWidget(self.time_edit)
        date_time_layout.addStretch()
        layout.addLayout(date_time_layout)
        self.show_tips = QLabel()
        self.text_edit = QTextEdit(textChanged=self.set_show_tips_null)
        self.text_edit.setPlainText(sms_data['content'])
        layout.addWidget(self.text_edit)
        layout.addWidget(self.show_tips)
        layout.addWidget(QPushButton('确定', clicked=self.commit_sms_edited), alignment=Qt.AlignRight)
        self.setLayout(layout)
        self.resize(420, 240)
        self.setWindowTitle('编辑短信通')

    def set_show_tips_null(self):
        self.show_tips.setText('')

    # 确定提交修改
    def commit_sms_edited(self):
        text = self.text_edit.toPlainText().strip(' ')
        if not text:
            self.show_tips.setText('请输入内容。')
            return
        # 提交
        try:
            r = requests.put(
                url=settings.SERVER_ADDR + 'info/sms/' + str(self.sms_id) + '/?mc=' + settings.app_dawn.value('machine'),
                headers={'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION')},
                data=json.dumps({
                    'date': self.date_edit.text(),
                    'time': self.time_edit.text(),
                    'content': text
                })
            )
            response = json.loads(r.content.decode('utf-8'))
            if r.status_code != 201:
                raise ValueError(response['message'])
        except Exception as e:
            QMessageBox.information(self, '错误', str(e))
        else:
            QMessageBox.information(self,'成功', '修改成功!')
            self.close()


