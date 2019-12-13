# _*_ coding:utf-8 _*_
# __Author__： zizle

from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QParallelAnimationGroup, QRect
import settings
from widgets.base import LoadedPage

""" 首页管理页 """


# 管理的功能块
class CollectorBlockIcon(QWidget):
    clicked_block = pyqtSignal(QWidget)

    def __init__(self, text, *args, **kwargs):
        super(CollectorBlockIcon, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        self.icon_label = QLabel()
        layout.addWidget(self.icon_label)
        self.block_button = QPushButton(text)
        self.block_button.clicked.connect(lambda: self.clicked_block.emit(self))
        layout.addWidget(self.block_button, alignment=Qt.AlignBottom)
        self.setLayout(layout)
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        # self.setFixedSize(250, 220)
        # 保存点击之间的原始位置
        self.original_x = 0
        self.original_y = 0
        # 保存原始大小
        self.original_width = 0
        self.original_height = 0

    # 记录原始位置
    def set_original_rect(self, x, y, w, h):
        self.original_x = x
        self.original_y = y
        self.original_width = w
        self.original_height = h


# 详情管理页容器
class DetailCollector(QWidget):
    def __init__(self, *args, **kwargs):
        super(DetailCollector, self).__init__(*args, **kwargs)
        # 详细页面布局
        layout = QVBoxLayout(margin=2)
        message_button_layout = QHBoxLayout()
        self.network_message_label = QLabel('网络信息提示', parent=self)
        message_button_layout.addWidget(self.network_message_label)
        self.back_collector_button = QPushButton('X')
        message_button_layout.addWidget(self.back_collector_button, alignment=Qt.AlignRight)
        layout.addLayout(message_button_layout)
        # 下方容器控件
        self.collector_container = LoadedPage(parent=self)
        layout.addWidget(self.collector_container)
        self.setLayout(layout)
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)


# 数据管理主页
class CollectorMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(CollectorMaintain, self).__init__(*args, **kwargs)
        layout = QGridLayout(margin=2)
        self.setLayout(layout)
        self._addMaintainBlock()

        # 详情管理页
        self.detail_collector = DetailCollector(parent=self, objectName='detailCollector')
        self.detail_collector.back_collector_button.clicked.connect(self.out_detail_collector)
        self.detail_collector.resize(self.parent().width(), self.parent().height())
        # 详细维护页面动画
        self.detail_collector_animation = QPropertyAnimation(self.detail_collector, b'geometry')
        self.detail_collector_animation.setDuration(500)
        # 功能块动画
        self.block_widget_animation = QPropertyAnimation()
        self.block_widget_animation.setDuration(500)
        # 动画组
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.detail_collector_animation)
        self.animation_group.addAnimation(self.block_widget_animation)
        self.setStyleSheet("""
        #blockIcon{
            background:rgb(100,200,160)
        }
        #detailCollector{
            background:rgb(230, 235, 230)
        }
        """)
        self.detail_collector.hide()


    # 设置管理的功能
    def _addMaintainBlock(self):
        horizontal_count = settings.COLLECTOR_BLOCK_ROWCOUNT
        row_index = 0
        col_index = 0
        for block_item in [u'首页管理', u'模块1', u'模块2', u'模块2', u'模块2', u'模块2']:
            block = CollectorBlockIcon(text=block_item, parent=self, objectName='blockIcon')
            block.clicked_block.connect(self.enter_detail_collector)
            self.layout().addWidget(block, row_index, col_index)
            col_index += 1
            if col_index == horizontal_count:  # 因为col_index先+1,此处应相等
                row_index += 1
                col_index = 0

    def resizeEvent(self, event):
        super(CollectorMaintain, self).resizeEvent(event)
        self.detail_collector.resize(self.parent().width(), self.parent().height())


    # 设置进入详情页动画
    def setEnterCollertorPageAnimation(self, collector_block):
        # 详情控件位置移到功能块中心
        self.detail_collector.move(collector_block.pos().x() + collector_block.width() / 2,
                                   collector_block.pos().y() + collector_block.width() / 2)

        # 模块记录原始位置大小,供还原使用
        collector_block.set_original_rect(collector_block.pos().x(), collector_block.pos().y(), collector_block.width(),
                                          collector_block.height())
        # 设置模块缩小
        self.block_widget_animation.setTargetObject(collector_block)
        self.block_widget_animation.setPropertyName(b'geometry')
        self.block_widget_animation.setStartValue(
            QRect(collector_block.pos().x(), collector_block.pos().y(), collector_block.width(),
                  collector_block.height())
        )
        self.block_widget_animation.setEndValue(
            QRect(collector_block.pos().x() + collector_block.width() / 2,
                  collector_block.pos().y() + collector_block.height() / 2, 0, 0)
        )
        # 设置详情页放大
        self.detail_collector_animation.setStartValue(
            QRect(self.detail_collector.pos().x(), self.detail_collector.pos().y(), 0, 0)
        )
        self.detail_collector_animation.setEndValue(
            QRect(0, 0, self.parent().width(), self.parent().height())
        )

        self.animation_group.addAnimation(self.detail_collector_animation)
        self.animation_group.addAnimation(self.block_widget_animation)
        # 开启动画组
        self.animation_group.start()

    # 进入维护详情页
    def enter_detail_collector(self, collector_block):
        current_block = collector_block.block_button.text()
        self.detail_collector.collector_container.clear()
        # 设置详情页展示页面
        self.detail_collector.collector_container.addWidget(QLabel(current_block))
        self.detail_collector.show()
        # 设置进入动画
        self.setEnterCollertorPageAnimation(collector_block)

    # 退出维护详情页
    def out_detail_collector(self):
        print('退出详情页')
        return

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
            QRect(show_block.original_x + show_block.original_width / 2,
                  show_block.original_y + show_block.original_height / 2, 0, 0)
        )
        self.block_module_animation.setEndValue(
            QRect(show_block.original_x, show_block.original_y, show_block.original_width,
                  show_block.original_height)
        )
        # 设置详情页退出动画位置和大小
        self.detail_maintainer_animation.setStartValue(
            QRect(0, 0, self.parent().width(), self.parent().height())
        )
        self.detail_maintainer_animation.setEndValue(
            QRect(show_block.original_x + show_block.original_width / 2,
                  show_block.original_y + show_block.original_height / 2, 0, 0)
        )
        self.animation_group.start()
        # 改变控件层次，由于控件最小，无需再改变层次
        # self.detail_maintainer.raise_()
        # self.show_maintainers.raise_()

