from wcferry import Wcf
from queue import Empty
from ca.ca_info import is_solca, is_eths, math_price, math_cex_price, math_km, math_percent, math_bjtime, get_bundles, is_cexToken, is_pump
from datetime import datetime


import time
import requests
import json
import logging


""" wcf = Wcf()
groups = ["58224083481@chatroom"]
wcf.enable_receiving_msg() """
# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别为 DEBUG
    format="%(asctime)s - %(levelname)s - %(message)s",  # 日志格式
    handlers=[
        logging.FileHandler("api_request.log"),  # 输出到文件
        logging.StreamHandler()  # 输出到控制台
    ]
)

# 获取日志记录器
logger = logging.getLogger("api_request_logger")

print('机器人启动')


def add_wx_info(roomid, wxId, wxNick, address, times, max_retries=3, retry_delay=0.5):
    """
    访问指定 URL 并添加微信信息。如果请求失败，会尝试重试。

    :param roomid: 群组 ID
    :param wxId: 微信 ID
    :param wxNick: 微信昵称
    :param address: 地址参数
    :param times: 时间参数
    :param max_retries: 最大重试次数（默认 3 次）
    :param retry_delay: 重试间隔时间（默认 500 毫秒）
    :return: 返回 API 响应数据，如果请求失败则返回 None。
    """
    url = "http://47.238.165.188:8080/api/wxInfo/add"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "roomId": roomid,
        "wxId": wxId,
        "wxNick": wxNick,
        "address": address,
        "times": times
    }

    for attempt in range(max_retries):
        try:
            # 记录调试信息
            logger.debug(f"开始请求 URL: {url}, 参数: {data}, 尝试次数: {attempt + 1}")

            # 发送 POST 请求
            start_time = datetime.now()
            response = requests.post(url, json=data, headers=headers, timeout=7)  # 设置超时时间为 7 秒
            elapsed_time = (datetime.now() - start_time).total_seconds()

            # 记录请求耗时
            logger.debug(f"请求完成，耗时: {elapsed_time:.2f} 秒")

            # 检查响应状态码
            if response.status_code == 200:
                # 记录成功日志
                logger.info(f"请求成功，响应数据: {response.json()}")
                return response.json()
            else:
                # 记录警告日志
                logger.warning(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
                if attempt < max_retries - 1:  # 如果不是最后一次尝试，则等待后重试
                    time.sleep(retry_delay)
                continue

        except requests.exceptions.RequestException as e:
            # 记录错误日志
            logger.error(f"请求过程中发生错误: {str(e)}", exc_info=True)
            if attempt < max_retries - 1:  # 如果不是最后一次尝试，则等待后重试
                time.sleep(retry_delay)
            continue

    # 如果所有尝试都失败，记录错误日志并返回 None
    logger.error(f"所有 {max_retries} 次尝试均失败，停止重试。")
    return None   




def get_wx_info(roomid, ca, max_retries=3, retry_delay=0.5):
    """
    访问指定 URL 并获取微信信息。如果请求失败，会尝试重试。

    :param roomid: 群组 ID
    :param ca: 地址参数
    :param max_retries: 最大重试次数（默认 3 次）
    :param retry_delay: 重试间隔时间（默认 500 毫秒）
    :return: 返回 API 响应数据中的 data 列表，如果请求失败则返回空列表。
    """
    url = "http://47.238.165.188:8080/api/wxInfo/get"
    params = {
        "roomId": roomid,
        "address": ca
    }

    for attempt in range(max_retries):
        try:
            # 记录调试信息
            logger.debug(f"开始请求 URL: {url}, 参数: {params}, 尝试次数: {attempt + 1}")

            # 发送 GET 请求
            start_time = datetime.now()
            response = requests.get(url, params=params, timeout=7)  # 设置超时时间为 7 秒
            elapsed_time = (datetime.now() - start_time).total_seconds()

            # 记录请求耗时
            logger.debug(f"请求完成，耗时: {elapsed_time:.2f} 秒")

            # 检查响应状态码
            if response.status_code == 200:
                value = response.text
                logger.info(f"请求成功，响应数据: {value[:100]}...")  # 仅输出前100个字符，防止过长

                # 如果返回为空，直接返回空列表
                if not value:
                    logger.warning("返回数据为空，返回空列表")
                    return []

                # 将响应内容转换为字典
                data = json.loads(value)
                data_list = data.get("data", [])
                logger.info(f"解析后的数据: {data_list}")
                return data_list
            else:
                # 记录警告日志
                logger.warning(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
                if attempt < max_retries - 1:  # 如果不是最后一次尝试，则等待后重试
                    time.sleep(retry_delay)
                continue

        except requests.exceptions.RequestException as e:
            # 记录错误日志
            logger.error(f"请求过程中发生错误: {str(e)}", exc_info=True)
            if attempt < max_retries - 1:  # 如果不是最后一次尝试，则等待后重试
                time.sleep(retry_delay)
            continue

    # 如果所有尝试都失败，记录错误日志并返回空列表
    logger.error(f"所有 {max_retries} 次尝试均失败，停止重试。")
    return []

""" ca_datas = [] 
while wcf.is_receiving_msg():
        # print('启动了吗？？？？')
        try: 
            msg = wcf.get_msg()
            # 处理消息的逻辑...
            time.sleep(1)
            if msg.from_group() and msg.roomid in groups:
                
                sol_id, sol_ca = is_solca(msg.content)
                eths_id, eths_ca = is_eths(msg.content)
                
                # 如果是sol和eth合约，就把你要把 群id  wxid 昵称 合约 时间戳    存下来
                if sol_id or eths_id:
                    roomid = msg.roomid
                    caller_wxid = msg.sender      
                    chatroom_members = wcf.get_chatroom_members(roomid = roomid)
                    caller_simulate_name = chatroom_members[caller_wxid]
                    ca = sol_ca if sol_ca else eths_ca
                    query_time = int(time.time()*1000)
                    
                    ca_data = [msg.roomid, caller_wxid, caller_simulate_name, ca, query_time]
                    ca_datas.append(ca_data) 
                    print(ca_datas)   
                    add_wx_info(roomid,caller_wxid,caller_simulate_name,ca,query_time)
                    
        except Empty:
            continue
        except Exception as e:
            print(e) """


# add_wx_info("111","123","xx","ca",time.time()*1000)
# get_wx_info("111","ca")
#wcf.keep_running()   
