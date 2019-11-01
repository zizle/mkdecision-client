# _*_ coding:utf-8 _*_
# __Author__： zizle
"""
data analysis 数据分析
"""
import sys
from PyQt5.QtWidgets import QTabWidget, QTabBar
from piece.danalysis import VarietyHome, VarietyDetail


class DAnalysis(QTabWidget):
    def __init__(self, *args, **kwargs):
        super(DAnalysis, self).__init__(*args, **kwargs)
        # 索引为0的tab，即首页
        self.tab_0 = VarietyHome()
        # 索引1为点击品种后产生
        self.addTab(self.tab_0, '品种')
        # signal
        self.tab_0.variety_menu.menu_clicked.connect(self.variety_selected)
        self.tabCloseRequested.connect(self.click_tab_closed)
        self.tabBarClicked.connect(self.click_tab_bar)
        # style
        self.setTabsClosable(True)
        self.tabBar().setTabButton(0, QTabBar.RightSide, None)
        self.setStyleSheet("""
           QTabBar::pane{
               border: 0.5px solid rgb(180,180,180);
           }
           QTabBar::tab{
               min-height: 25px
           }
           QTabBar::tab:selected {
           
           }
           QTabBar::tab:!selected {
               background-color:rgb(180,180,180)
           }
           QTabBar::tab:hover {
               color: rgb(20,100,230);
               background: rgb(220,220,220)
           }
           """
        )

    # 选择品种后的详情tab
    def variety_selected(self, menu):
        print('windows.danalysis.py {} 选择品种菜单：'.format(sys._getframe().f_lineno), menu.parent, menu.name_en)
        parent = menu.parent
        parent_en = menu.parent_en
        name = menu.text()
        name_en = menu.name_en
        self.removeTab(1)
        tab_1 = VarietyDetail(variety=name_en, width=self.tab_0.variety_menu.width())
        self.addTab(tab_1, name + '数据')
        self.setCurrentIndex(1)

    def click_tab_closed(self, index):
        self.removeTab(index)

    def click_tab_bar(self, index):
        self.setCurrentIndex(index)
        if index == 1:  # 品种详情页面
            current = self.currentWidget()
            current.vd_right.show()
            if current.layout().itemAt(1).widget() != current.vd_right:
                current.layout().itemAt(1).widget().close()
                current.layout().removeWidget(current.layout().itemAt(1).widget())
                current.layout().addWidget(current.vd_right)


