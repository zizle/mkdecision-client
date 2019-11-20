# _*_ config _*_
# Update: 2019-11-20
# Author: zizle
import json
import requests
import config
from .machine import get_machine_code


# 启动检查客户端是否存在
def check_client_existed():
    exist_mc = config.app_dawn.value('machine')
    if exist_mc:  # 原来就存在则不发起请求
        print('windows.base.Base.check_client_existed 客户端没卸载')
        return
    # 获取机器码
    print('windows.base.Base.check_client_existed 客户端已卸载重装,鉴定是否已注册过的')
    machine_code = get_machine_code()
    # 查询机器是否存在
    try:
        r = requests.get(
            url=config.SERVER_ADDR + 'basic/client-existed/?mc=' + machine_code
        )
        response = json.loads(r.content.decode('utf-8'))
    except Exception:
        return
    if response['data']['existed']:
        # 存在,写入配置
        print('注册过的客户端,写入配置')
        config.app_dawn.setValue('machine', machine_code)