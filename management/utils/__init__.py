# _*_ coding:utf-8 _*_
"""
Create: 2019-08-09
Author: zizle
"""
from win32com.shell import shell, shellcon

def text_content_handler(content):
    # handler content
    content_list = content.strip(' ').split('\n')  # 去除前后空格和分出换行
    # 处理文本内容
    text_content = ""
    for line in content_list:
        if line.startswith('<image') and line.endswith('</image>'):
            text_content += line
        else:
            text_content += "<p>" + line + "</p>"
    return text_content

def get_desktop_path():
    """获取用户桌面路径"""
    ilist = shell.SHGetSpecialFolderLocation(0, shellcon.CSIDL_DESKTOP)
    return shell.SHGetPathFromIDList(ilist).decode("utf-8")