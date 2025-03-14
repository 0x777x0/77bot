import time
import logging
import redis
from wcferry import Wcf
from queue import Empty

""" # 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 初始化 wcferry
logging.info("开始初始化 wcferry")
wcf = Wcf()
wcf.enable_receiving_msg()
logging.info('机器人启动')

# 连接 Redis
logging.info("开始连接 Redis")
redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=0, decode_responses=True)
redis_client = redis.Redis(connection_pool=redis_pool)

# 群组列表
groups = ["58224083481@chatroom", '52173635194@chatroom']

def command_id(msg):
    # 处理消息的逻辑...
    logging.info(f"处理消息: {msg}")

# 消息处理循环
while wcf.is_receiving_msg():
    try:
        msg = wcf.get_msg()
        command_id(msg=msg)
        time.sleep(0.3)
    except Empty:
        time.sleep(1)  # 增加 sleep 时间，减少空轮询
    except Exception as e:
        logging.error(f"处理消息时发生错误: {e}")

wcf.keep_running() """
A = ['{}']
B = A[0]

print(B)

print(len(B))
