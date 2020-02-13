# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
from urllib3 import encode_multipart_formdata
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from widgets.CAvatar import CAvatar
import settings


# 修改头像
class EditUserAvatar(QDialog):
    new_avatar_url = pyqtSignal(str)

    def __init__(self, user_id, current_url, *args, **kwargs):
        super(EditUserAvatar, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.new_image_path = None
        self.setFixedWidth(300)
        self.setWindowTitle('我的头像')
        layout = QVBoxLayout(spacing=10)
        self.avatar_show = CAvatar(url=current_url, size=QSize(180, 180))
        layout.addWidget(self.avatar_show, alignment=Qt.AlignCenter)
        # 上传
        self.select_btn = QPushButton('更改头像', objectName='selectBtn', clicked=self.browser_image, cursor=Qt.PointingHandCursor)
        # 确定
        self.confirm_btn = QPushButton('确认设置', objectName='confirmBtn', clicked=self.confirm_avatar)
        layout.addWidget(self.select_btn)
        layout.addWidget(self.confirm_btn)
        self.setLayout(layout)
        self.setStyleSheet("""
        #selectBtn{
            border:none;
            min-width: 200px;
            font-size: 14px;
        }
        #selectBtn:hover{
            color:rgb(50,160, 180)
        }
        #confirmBtn{
            border:none;
            min-width: 200px;
            font-size: 16px;
            border: none;
            background-color: rgb(20, 150, 200);
            color: rgb(255, 255, 255);
            padding: 10px 0;
            border-radius: 5px;
        }
        #confirmBtn:pressed{
            background-color: rgb(20, 120, 170);
        }
        """)

    def browser_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, '打开图片', '', "png file(*.png)")
        if image_path:
            self.avatar_show.setUrl(image_path)
            self.new_image_path = image_path

        # if image_path:
        #     # 对文件的大小进行限制
        #     img = Image.open(image_path)
        #     print(img.size[0], img.size[1])
        #     if 520 <= img.size[0] <= 660 and 260 <= img.size[1] <= 330:
        #         self.advertisement_image_edit.setText(image_path)
        #     else:
        #         self.error_message_label.setText('宽:520~660像素;高:260~330像素')

    # 确定更改头像
    def confirm_avatar(self):
        data = dict()
        if self.new_image_path:
            image_name = self.new_image_path.rsplit('/', 1)[1]
            image = open(self.new_image_path, 'rb')
            image_content = image.read()
            image.close()
            data['image'] = (image_name, image_content)
            encode_data = encode_multipart_formdata(data)
            try:
                # 发起上传请求
                r = requests.post(
                    url=settings.SERVER_ADDR + 'user/'+ str(self.user_id) +'/avatar/?mc=' + settings.app_dawn.value('machine'),
                    headers={
                        'AUTHORIZATION': settings.app_dawn.value('AUTHORIZATION'),
                        'Content-Type': encode_data[1]
                    },
                    data=encode_data[0]
                )
                response = json.loads(r.content.decode('utf-8'))
                if r.status_code != 201:
                    raise ValueError(response['message'])
            except Exception as e:
                pass
            else:
                # 关闭弹窗，修改头像
                new_avatar = response['data']
                self.new_avatar_url.emit(new_avatar)
                self.close()



