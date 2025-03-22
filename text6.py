from wcferry import Wcf
from queue import Empty
from ca.ca_info import is_solca, is_eths, math_price, math_cex_price, math_cex_priceChangePercent, math_km, math_percent, math_bjtime, get_bundles, is_cexToken, is_pump
from command.command import command_id, command_cextoken, command_leaderboard_ca, command_person_record
from httpsss.oke import fetch_oke_latest_info, fetch_oke_overview_info
from httpsss.onchain import get_price_onchain, send_person_ca
from common.socialMedia_info import is_x, is_web, is_TG
from common.translate import translate
from datetime import datetime, timedelta, timezone
from common.bjTime import convert_timestamp_to_beijing_time
from ca.exchange import get_exchange_price
from ca.redis_method import get_from_redis_list
# from common.cache import redis
from save_data import get_wx_info, get_wx_info_v2, add_wx_info_v2

import configparser
import threading
import requests
import time
import json
import redis
import random
import string
import logging



# 初始化 Wcf
wcf = Wcf()

# 启用消息接收
wcf.enable_receiving_msg()

# 打印启动信息
print('机器人启动，开始监听群消息...')

# 监听消息
while wcf.is_receiving_msg():
    try:
        # 获取消息
        msg = wcf.get_msg()
        
        # 打印消息内容（调试用）
        print(f"收到消息: {msg}")

        # 判断是否是群消息
        
        print(f"收到群消息 - 群ID: {msg.roomid}, 发送者: {msg.sender}, 内容: {msg.content}")

        # 如果是特定群消息，回复一条消息
        if msg.roomid == "55968294101@chatroom":  # 替换为你的群ID
            reply = f"收到消息: {msg.content}"
            wcf.send_text(reply, msg.roomid)
            print(f"已回复群消息: {reply}")

        # 休眠一段时间，避免 CPU 占用过高
        time.sleep(0.3)

    except Empty:
        # 如果没有消息，继续循环
        continue
    except Exception as e:
        # 打印异常信息
        print(f"处理消息时发生错误: {e}")

# 保持运行
wcf.keep_running()