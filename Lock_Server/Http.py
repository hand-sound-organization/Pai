# 树莓派的HTTP模块 只是测试通过 逻辑还没怎么写（预警信息）
import requests
from datetime import datetime
data = {
    "name":'陌生人',
    "event":'攻击',
    "occur_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "app_username":'lsd',
    "lock_id":'2020',
    "isSafe":'True'
}


response = requests.post("http://127.0.0.1:5000/app/WarningInfo", data)

print(response)
print(response.content.decode())
print(response.headers)