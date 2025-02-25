import logging
from wcferry import Wcf
from queue import Empty
import time

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 初始化 WeChatFerry
wcf = Wcf()
wcf.enable_receiving_msg()
logging.info('机器人启动')

# 消息监听循环
while wcf.is_receiving_msg():
    try:
        msg = wcf.get_msg()
        logging.info(f"收到消息: {msg.content}")  # 记录消息内容
        
        if msg.from_self:
            print(msg)
            id = msg.id
            time.sleep(5)
            print(id)
            jg = wcf.revoke_msg(id)
            print(jg)

    except Empty:
        logging.warning("消息队列为空")  # 记录空队列警告
        continue
    except Exception as e:
        logging.error(f"处理消息时发生错误: {e}")  # 记录错误信息

# 保持运行
wcf.keep_running()