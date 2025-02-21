import redis
import time

'''

ca_datas = {
    '47836900220@chatroom':{
        'VaEDXcwMC3xef56e1D4xEDTMy4LyGbw6zt95KHspump':{
            'caller_name':'张三',
            'initCap':'11.21M',
            'topCap':'11.21M',
            'find_time':'02-20 15:30',
            'query_time':'02-20 15:30' 
        }   
    },
    '99936900220@chatroom':{
        'VaEDXcwMC3xef56e1D4xEDTMy4LyGbw6zt95KHspump':{
            'caller_name':'李四',
            'initCap':'1.21M',
            'topCap':'111.21M',
            'find_time':'02-20 15:30',
            'query_time':'02-20 15:30' 
        }   
    }          
}



# 连接到本地的 Redis 服务
r = redis.StrictRedis(host='localhost', port=6379, db=0)

# 尝试从 Redis 获取保存的 k 值，如果不存在则设置为 0
k = r.get('k')
if k is None:
    k = 0
else:
    k = int(k)

try:
    while True:
        print(f'当前 k 的值: {k}')
        k += 1  # 每秒钟 k 增加 1
        r.set('k', k)  # 将 k 的值保存到 Redis
        time.sleep(1)  # 每秒更新一次
except KeyboardInterrupt:
    print("程序被手动停止")
'''

# 初始化 Redis 客户端
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# 清除所有数据库
redis_client.flushall()
print("所有数据库已清除")