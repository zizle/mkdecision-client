# _*_ coding:utf-8 _*_
# company: RuiDa Futures
# author: zizle
from PyQt5.QtWidgets import QWidget, QPushButton, QMessageBox
from PyQt5.QtCore import QPropertyAnimation, QPoint, QParallelAnimationGroup, QTimer, pyqtSignal,Qt
from PyQt5.QtGui import QCursor


class CarouselButton(QPushButton):
    clicked_signal = pyqtSignal(QPushButton)

    def __init__(self, *args):
        super(CarouselButton, self).__init__(*args)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.clicked.connect(self.__button_clicked)

    def __button_clicked(self):
        self.clicked_signal.emit(self)

    def set_attribute(self, each_data):
        self.id = each_data["id"]
        self.name = each_data["name"]
        self.show_type = each_data["show_type"]
        self.image = each_data["image"]
        self.file = each_data["file"]
        self.content = each_data["content"]
        self.redirect = each_data['redirect']


class CarouselWidget(QWidget):
    carousel_clicked = pyqtSignal(dict)

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumWidth(800)
        self.setMaximumWidth(800)
        self.setMinimumHeight(300)
        self.setMaximumHeight(300)
        self.count = len(data) if data else 1
        self.data = data
        self.WIDTH = self.width()
        self.HEIGHT = self.height()
        self.animation_group = QParallelAnimationGroup()
        self.init_ui()

    def init_ui(self):
        carousels = []
        # 创建动画按钮
        for i in range(self.count):
            # 初始化
            button = CarouselButton(self)
            if self.data:
                button.set_attribute(self.data[i])
                button.setStyleSheet("border-image:url(" + str(button.image) + ")")  # 设置背景页
            button.clicked_signal.connect(self.__click_carousel)
            button.resize(self.WIDTH, self.HEIGHT)
            button.move(-self.WIDTH * i, 0)  # 初始化位置
            # 动画
            animation = QPropertyAnimation(button, b'pos')
            button_x = button.pos().x()  # 获得位置
            animation.setStartValue(QPoint(button_x, 0))  # 起始位置
            animation.setEndValue(QPoint(button_x + self.WIDTH, 0))  # 结束位置
            animation.setDuration(300)
            carousels.append((animation, button))
            self.animation_group.addAnimation(animation)  # 加入组
        if self.count > 1:
            # 计时器
            timer = QTimer(self)
            timer.start(5000)
            timer.timeout.connect(self.__time_record)
            # 动画组结束连接处理事件
            self.animation_group.finished.connect(lambda: self.__animation_group_finished(carousels))

    def __animation_group_finished(self, carousels):
        """动画组一次播放结束"""
        for carousel in carousels:
            cur_pos_x = carousel[1].pos().x()
            if cur_pos_x == self.WIDTH:
                target_pos_x = cur_pos_x - self.count * self.WIDTH
                carousel[1].move(target_pos_x, 0)
                carousel[0].setStartValue(QPoint(target_pos_x, 0))
                carousel[0].setEndValue(QPoint(target_pos_x + self.WIDTH, 0))
            else:
                # 重新设置动画的起始结束位置
                carousel[0].setStartValue(QPoint(cur_pos_x, 0))
                carousel[0].setEndValue(QPoint(cur_pos_x + self.WIDTH, 0))

    def __click_carousel(self, button):
        """点击动画,即点击了按钮，传入相应的按钮"""
        # QMessageBox.information(self, "提示", "您点击了" + button.text(), QMessageBox.Yes)
        data = dict()
        data["id"] = button.id
        data["name"] = button.name
        data["show_type"] = button.show_type
        data["image"] = button.image
        data["file"] = button.file
        data["content"] = button.content
        data['redirect'] = button.redirect
        self.carousel_clicked.emit(data)

    def __time_record(self):
        """计时开启动画组"""
        self.animation_group.start()
