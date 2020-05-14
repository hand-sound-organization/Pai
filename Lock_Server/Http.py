# 树莓派的HTTP模块 只是测试通过 逻辑还没怎么写（预警信息）
import requests
from datetime import datetime
from Lock_Server.dbconfig import Base, engine, User
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()
data = {
    "name":'Stranger',
    "event":'attack',
    "occur_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "app_username":session.query(User).first().username,
    "lock_id":session.query(User).first().lockid,
    "isSafe":'True'
}


response = requests.post("http://192.168.0.107:5000/app/WarningInfo", data)

print(response)
print(response.content.decode())
print(response.headers)