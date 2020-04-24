# Pai
树莓派端
###Socket交互过程
1. Server监听UDP广播端口
2. Client发送UDP广播，里面包含关键字段用于给Server确认协议类型
3. Server确认收到的广播消息中的关键字段，协议确认通过，可以开始交互
4. Server开启新的TCP端口并监听
5. Server确认后向Client的UDP端口发送确认响应（包含开启的TCP端口和自己的IP地址）
6. Client收到TCP端口和IP地址后与Server新建的TCP端口建立连接
7. Client通过新建的TCP连接发送token给Server
8. Server验证token后确认本次会话，至此Client与Server可以开始正式通信

#####PS：Client是APP，Server是树莓派，广播在同一个WiFi的局域网下广播，模式有点像FTP的主动模式