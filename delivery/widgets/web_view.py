# _*_ coding:utf-8 _*_
# __Author__： zizle

from PyQt5.QtWebEngineWidgets import QWebEngineView


class WebView(QWebEngineView):
    def contextMenuEvent(self, event):
        # 禁止右击菜单行为
        pass
