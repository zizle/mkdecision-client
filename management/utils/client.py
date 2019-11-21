# _*_ config _*_
# Update: 2019-11-20
# Author: zizle
import json
import requests
import config
from .machine import get_machine_code


# 启动使客户端存在
def make_client_existed():
    machine_code = get_machine_code()  # 获取机器码
    # 查询机器是否存在
    try:
        r = requests.post(
            url=config.SERVER_ADDR + 'basic/client/',
            data=json.dumps({
                'machine_code': machine_code,
                'is_manager': config.ADMINISTRATOR
            })
        )
        response = json.loads(r.content.decode('utf-8'))
        if r.status_code != 200:
            raise ValueError(response['message'])
    except Exception:
        return
    else:
        # 写入配置
        print('utils.client.make_client_existed写入配置')
        config.app_dawn.setValue('machine', response['data']['machine_code'])
