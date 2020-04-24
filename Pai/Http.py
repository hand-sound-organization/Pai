# 树莓派的HTTP模块 只是测试通过 逻辑还没怎么写（预警信息）
import requests

response = requests.get("http://127.0.0.1:5000/app/login")
print(response.headers)
print(response.request)
print(response.json()['isTrue'])
