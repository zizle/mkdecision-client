# _*_ coding:utf-8 _*_
# __Author__： zizle
import json
import requests
import config


# 设置用户的某项数据
def change_user_information(uid, data_dict):
    # 发起设置请求
    try:
        r = requests.patch(
            url=config.SERVER_ADDR + 'user/' + str(uid) + '/?mc=' + config.app_dawn.value(
                'machine'),
            headers={
                'AUTHORIZATION': config.app_dawn.value('AUTHORIZATION')
            },
            data=json.dumps(data_dict)
        )
        response = json.loads(r.content.decode('utf-8'))
        if r.status_code != 200:
            raise ValueError(response['message'])
    except Exception as e:
        return str(e)
    else:
        return response['message']
