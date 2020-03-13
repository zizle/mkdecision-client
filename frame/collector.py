# _*_ coding:utf-8 _*_
# __Author__： zizle

from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont, QPixmap
import settings
from widgets.base import LoadedPage
from frame.homepage.homeCollector import HomePageCollector
from frame.basetrend.trendCollector import TrendPageCollector
from frame.proservice.infoServiceCollector import InfoServicePageCollector
from frame.hedging.deliveryCollector import DeliveryPageCollector


# 管理的功能块
class CollectorBlockIcon(QWidget):
    clicked_block = pyqtSignal(QWidget)

    def __init__(self, text, icon_path, *args, **kwargs):
        super(CollectorBlockIcon, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QPixmap(icon_path))
        self.icon_label.setScaledContents(True)
        layout.addWidget(self.icon_label)
        self.block_button = QPushButton(text, objectName='nameBtn')
        self.block_button.clicked.connect(lambda: self.clicked_block.emit(self))
        layout.addWidget(self.block_button, alignment=Qt.AlignBottom)
        self.setLayout(layout)
        self.setAutoFillBackground(True)  # 受父窗口影响(父窗口已设置透明)会透明,填充默认颜色
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        self.setFixedSize(250, 220)
        # 保存点击之间的原始位置
        self.original_x = 0
        self.original_y = 0
        # 保存原始大小
        self.original_width = 0
        self.original_height = 0
        self.setObjectName('blockIcon')
        self.setStyleSheet("""
        #blockIcon{
            background:rgb(189,255,245)
        }
        #nameBtn{
            border:none;
            font-size:13px;
        }
        """)

    # 记录原始位置
    def set_original_rect(self, x, y, w, h):
        self.original_x = x
        self.original_y = y
        self.original_width = w
        self.original_height = h

    # 鼠标进入
    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
        #blockIcon{
            background:rgb(170,243,217)
        }
        #nameBtn{
            border:none;
            font-size:13px;
        }
        """)

    # 鼠标退出
    def leaveEvent(self, event):
        self.setStyleSheet("""
        #blockIcon{
            background:rgb(189,255,245)
        }
        #nameBtn{
            border:none;
            font-size:13px;
        }
        """)

    # 鼠标点击
    def mousePressEvent(self, event):
        self.block_button.click()


# 详情管理页容器
class DetailCollector(QWidget):
    def __init__(self, *args, **kwargs):
        super(DetailCollector, self).__init__(*args, **kwargs)
        # 详细页布局
        layout = QVBoxLayout(margin=2, spacing=2)
        message_button_layout = QHBoxLayout(margin=0)
        font = QFont()
        font.setFamily('Webdings')
        self.back_collector_button = QPushButton('r', parent=self, font=font, objectName='closeButton', cursor=Qt.PointingHandCursor)
        message_button_layout.addWidget(self.back_collector_button, alignment=Qt.AlignLeft)
        self.network_message_label = QLabel('', parent=self)
        message_button_layout.addWidget(self.network_message_label)
        layout.addLayout(message_button_layout)
        # 下方容器控件
        self.collector_container = LoadedPage(parent=self)
        layout.addWidget(self.collector_container)
        self.setLayout(layout)
        self.setAttribute(Qt.WA_StyledBackground, True)  # 支持qss设置背景颜色(受父窗口透明影响qss会透明)
        self.setStyleSheet("""
        #closeButton{
            border:none;
            min-width: 20px;
            max-width: 20px;
            min-height: 20px;
            max-height: 20px;
            background-color: rgb(220, 220, 220)
        }
        #closeButton:hover{
            background-color: rgb(220, 120, 100)
        }
        """)


# 数据管理主页
class CollectorMaintain(QWidget):
    def __init__(self, *args, **kwargs):
        super(CollectorMaintain, self).__init__(*args, **kwargs)
        layout = QGridLayout(margin=2)
        self.setLayout(layout)
        self._addMaintainBlock()
        # 缓存功能块引用
        self.cache_block_widget = None
        # 详情管理页
        self.detail_collector = DetailCollector(parent=self, objectName='detailCollector')
        self.detail_collector.back_collector_button.clicked.connect(self.out_detail_collector)
        self.detail_collector.resize(self.parent().width(), self.parent().height())
        # 详细维护页面动画
        self.detail_collector_animation = QPropertyAnimation(self.detail_collector, b'geometry')
        self.detail_collector_animation.setDuration(500)
        self.setStyleSheet("""
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
        for block_item in [
            {'text': u'首页管理', 'icon': 'media/collector_icon/home.png'},
            {'text': u'产品服务', 'icon': 'media/collector_icon/service.png'},
            {'text': u'数据分析', 'icon': 'media/collector_icon/trend.png'},
            {'text': u'交割服务', 'icon': 'media/collector_icon/service.png'},
        ]:
            block = CollectorBlockIcon(text=block_item['text'], icon_path=block_item['icon'], parent=self)
            block.clicked_block.connect(self.enter_detail_collector)
            self.layout().addWidget(block, row_index, col_index)
            col_index += 1
            if col_index == horizontal_count:  # 因为col_index先+1,此处应相等
                row_index += 1
                col_index = 0

    def resizeEvent(self, event):
        super(CollectorMaintain, self).resizeEvent(event)
        if self.detail_collector.width() != 0:
            self.detail_collector.resize(self.parent().width(), self.parent().height())

    # 设置进入详情页动画
    def setEnterCollertorPageAnimation(self, collector_block):
        # 详情控件位置移到功能块中心
        self.detail_collector.move(collector_block.pos().x() + collector_block.width() / 2,
                                   collector_block.pos().y() + collector_block.width() / 2)

        # 设置详情页放大
        self.detail_collector_animation.setStartValue(
            QRect(self.detail_collector.pos().x(), self.detail_collector.pos().y(), 0, 0)
        )
        self.detail_collector_animation.setEndValue(
            QRect(0, 0, self.parent().width(), self.parent().height())
        )
        # 开启动画
        self.detail_collector_animation.start()
        # 缓存功能块引用
        self.cache_block_widget = collector_block

    # 设置退出详情页
    def setOuterCollertorPageAnimation(self):
        self.detail_collector_animation.setStartValue(
            QRect(0, 0, self.parent().width(), self.parent().height())
        )
        self.detail_collector_animation.setEndValue(
            QRect(self.cache_block_widget.pos().x() + self.cache_block_widget.width() / 2,
                  self.cache_block_widget.pos().y() + self.cache_block_widget.height() / 2, 0, 0)
        )
        self.detail_collector_animation.start()

    # 进入维护详情页
    def enter_detail_collector(self, collector_block):
        current_block = collector_block.block_button.text()
        # 初始化详情页显示控件
        if current_block == u'首页管理':
            detail_widget = HomePageCollector(parent=self.detail_collector)
        elif current_block == u'产品服务':
            detail_widget = InfoServicePageCollector(parent=self.detail_collector)
        elif current_block == u'数据分析':
            detail_widget = TrendPageCollector(parent=self.detail_collector)
        elif current_block == u'交割服务':

            detail_widget = DeliveryPageCollector(parent=self.detail_collector)
        else:
            detail_widget = QLabel('【' + current_block + '】暂不支持数据管理...',
                                   styleSheet='font-size:16px;color:rgb(200, 120, 100);', alignment=Qt.AlignCenter)
        # 设置详情页展示页面
        self.detail_collector.collector_container.clear()
        self.detail_collector.collector_container.addWidget(detail_widget)
        self.detail_collector.show()
        # 设置进入动画
        self.setEnterCollertorPageAnimation(collector_block)

    # 退出维护详情页
    def out_detail_collector(self):
        if self.cache_block_widget is None:
            return
        self.setOuterCollertorPageAnimation()


