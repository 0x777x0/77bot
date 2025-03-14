
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



# 将ca_datas 数据以嵌套字典形式存到 redis 的方法
def store_nested_data_to_redis(roomid, ca_ca, tokenSymbol,caller_name, caller_gender, data1, description, find_time_ms):
    # 准备数据
    data = {
    'tokenSymbol':tokenSymbol,
    'caller_name': caller_name,
    'caller_gender':caller_gender,
    'price':float(data1["data"]["price"]),
    'initCap': float(data1["data"]["marketCap"]) , 
    'topCap': float(data1["data"]["marketCap"]) , 
    'circulatingSupply':float(data1["data"]["circulatingSupply"]) if data1["data"]["circulatingSupply"] else 0,
    'description': description,
    'find_time': find_time_ms,
    'query_time': find_time_ms
    }
    # 将 `roomid` 下的 `ca_ca` 字段存储为 Redis 哈希表
    r.hset(roomid, ca_ca, json.dumps(data))
    print(f"数据已存储: {roomid} -> {ca_ca}")


# 从 redis中获取嵌套字典形式的 ca_datas 数据的方法
def get_nested_data_from_redis(roomid, ca_ca):
    # 获取存储的 JSON 数据
    stored_data = r.hget(roomid, ca_ca)
    
    if stored_data:
        # 反序列化 JSON 字符串为字典
        return json.loads(stored_data)
    else:
        return None


# 获取 Redis 中存储的列表数据
def get_data_from_redis(redis_key):
    data = r.lrange(redis_key, 0, -1)  # 获取整个列表
    return data


# 获取数据库中的msgID
def getMyLastestGroupMsgID(keyword) -> dict:

    dbs = wcf.get_dbs()
    db = "MSG0.db"
    for _db in dbs:
        if _db[:3] == "MSG" and _db[-3:] == ".db":
            db = _db

    sql = f"SELECT * FROM MSG WHERE IsSender = 1 and strContent LIKE '%{keyword}%' ORDER BY localId DESC LIMIT 10;"
    msgs = wcf.query_sql(db, sql)
    print(msgs)
    return msgs[0].get("MsgSvrID") if msgs else 0



# 将微信id和昵称以字典的形式存到redis中
def add_wxid_nickname_to_redis_batch(key, data):
    """
    批量将键值对存储到 Redis 的 Hash 中
    :param key: Redis 的 Hash 键名
    :param data: 字典，包含字段名和字段值
    """
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    # 使用 Pipeline 批量操作
    with r.pipeline() as pipe:
        for field, value in data.items():
            # 如果值是字典，转换为 JSON 字符串
            if isinstance(value, dict):
                value = json.dumps(value, ensure_ascii=False)
            pipe.hset(key, field, value)
        pipe.execute()  # 批量执行
    print(f"已批量存储 {len(data)} 条数据到 Redis")



# 将微信id和昵称的字典从redis中取出来
def get_wxid_nickname_from_redis(key):
    """
    从 Redis 的 Hash 中获取整个字典
    :param key: Redis 的 Hash 键名
    :return: 字典（微信 ID -> 微信昵称）
    """
    r = redis.Redis(host='localhost', port=6379, db=0)
    wechat_dict = r.hgetall(key)
    # 将字节字符串解码为普通字符串
    wechat_dict = {k.decode('utf-8'): v.decode('utf-8') for k, v in wechat_dict.items()}
    return wechat_dict


def save_to_redis_list(data, list_name='chatroom_data'):
    """
    将数据存储到 Redis 列表中
    :param data: 要存储的数据（字典格式）
    :param list_name: Redis 列表的名称
    """
    # 将字典转换为 JSON 字符串
   
    data_json = json.dumps(data, ensure_ascii=False)
    # 将 JSON 字符串推入 Redis 列表
    redis_client.lpush(list_name, data_json)
    print(f"数据已存储到 Redis 列表 {list_name} 中")


def save_or_update_to_redis_list(data, list_name='chatroom_data'):
    """
    将数据存储到 Redis 列表中，如果 roomId 已存在则覆盖，否则添加到列表
    :param data: 要存储的数据（字典格式）
    :param list_name: Redis 列表的名称
    """
    # 调用 get_from_redis_list 方法获取 Redis 列表中的数据
    data_list = get_from_redis_list(list_name)
    print('进入redis方法')
    print(data_list)
    # 检查是否存在 roomId 相同的项
    found = False
    
    if data_list :
        for index, item in enumerate(data_list):          
            if item.get('roomId') == data.get('roomId'):
                # 如果找到 roomId 相同的项，覆盖该项
                print('roomid相同')
                data_list[index] = data
                found = True
                break

    # 如果没有找到 roomId 相同的项，调用 save_to_redis_list 方法将新数据添加到列表
    if not found:
        save_to_redis_list(data, list_name)
    else:
        # 清空 Redis 列表
        redis_client.delete(list_name)
        # 将更新后的列表重新存储到 Redis 中
        for item in data_list:
            redis_client.rpush(list_name, json.dumps(item, ensure_ascii=False))
        print(f"数据已更新到 Redis 列表 {list_name} 中")



# 撤回消息和清空排行榜、合约数据的方法
def recover_message():
    global all_rankings
    last_clear_time = None  # 记录上一次清空的时间
    last_send_time = None  # 记录上一次发送排行榜的时间
    send_interval_hours = 1  # 默认发送间隔为1小时，可以根据需要动态调整

    while not stop_event.is_set():
        time.sleep(10)
        print('开始撤回消息')
        try:
            if len(old_news) > 0:
                print(old_news)
                # 反向遍历 old_news，避免删除元素影响索引
                for i in range(len(old_news) - 1, -1, -1):
                    timestamp_ms = int(time.time() * 1000)
                    if timestamp_ms - old_news[i][1] > REVOKE_INTERVAL_MS and old_news[i] != 0 and old_news[i][0]:  # 10000ms = 10秒  停留1分40秒
                        
                        result = wcf.revoke_msg(old_news[i][0]) 
                        print('撤回消息{}'.format(result))
                        if result == 1:
                            del old_news[i]  # 删除已撤回的消息
            
            # 检查是否需要清空排行榜数据
            current_time = datetime.now()
            if current_time.hour == 0 and current_time.minute == 10:
                # 检查上一次清空时间是否超过 1 分钟
                if last_clear_time is None or (current_time - last_clear_time).total_seconds() >= 25:
                    clear_leaderboard()  # 重置内存中的排行榜数据
                    all_rankings = {roomid: [] for roomid in groups}
                    last_clear_time = current_time  # 更新上一次清空时间
                    print("已清空排行榜数据和合约数据")
                
        except Empty:
            continue
        except Exception as e:
            print(f"撤回消息时出错: {e}")


#获取池子创建时间
def get_pool_create_time(chainId,address):
    url = f"https://www.okx.com/priapi/v1/dx/market/pool/list?chainId={chainId}&tokenContractAddress={address}"
    
    # 发送 GET 请求
    response = requests.get(url)
    
    # 获取响应内容
    value = response.text
    # print(value)
    # 如果返回为空，直接返回
    if not value:
        return 0
    
    pool_create_time = 0
    data = json.loads(value)  # 将响应内容转换为字典
    code = data.get("code")
    
    # 如果返回码为 0，表示成功
    if code == 0:
        data = data.get("data")
        list_data = data.get("list")
        
        # 遍历池子列表
        for obj in list_data:
            create_timestamp = obj.get("createTimestamp")
            if pool_create_time == 0:
                pool_create_time = create_timestamp
            else:
                if pool_create_time < create_timestamp:
                    pool_create_time = create_timestamp
    print(pool_create_time)
    return pool_create_time


#获取并处理合约信息
def fetch_and_process_data(roomid, wxId, chainId, ca, data1, data2, time_ms):
    
    try:
            
        # 获取合约基础信息
        #chain_name = data1["data"]["chainName"] if data1["data"]["chainName"] else '暂无数据'            
        try:
            tokenSymbol = data1["data"]["tokenSymbol"] if data1["data"]["tokenSymbol"] else '暂无数据'
        except KeyError:
            tokenSymbol = '暂无数据'

        try:
            tokenName = data1["data"]["tokenName"] if data1["data"]["tokenName"] else '暂无数据'
        except KeyError:
            tokenName = '暂无数据'
        
        try:
            price = math_price(float(data1["data"]["price"])) if data1["data"]["price"] else '暂无数据'
        except KeyError:
            price = '暂无数据'

        try:
            marketCap = math_km(float(data1["data"]["marketCap"])) if data1["data"]["marketCap"] else '暂无数据'
        except KeyError:
            marketCap = '暂无数据'

        try:
            circulatingSupply = data1["data"]["circulatingSupply"] if data1["data"]["circulatingSupply"] else '暂无数据'
        except KeyError:
            circulatingSupply = '暂无数据'
        
        try:
            volume = math_km(float(data1["data"]["volume"])) if data1["data"]["volume"] else '暂无数据'
        except KeyError:
            volume = '暂无数据'

        try:
            holders = data1["data"]["holders"] if data1["data"]["holders"] else '暂无数据'
        except KeyError:
            holders = '暂无数据'

        try:
            top10HoldAmountPercentage = math_percent(float(data1["data"]["top10HoldAmountPercentage"])) if data1["data"]["top10HoldAmountPercentage"] else '暂无数据'
        except KeyError:
            top10HoldAmountPercentage = '暂无数据'

        
        #获取捆绑信息
        total_holding_percentage = '功能优化中'
        # _, total_holding_percentage = get_bundles(address=ca_ca)         
        
        # 获取社交信息
        try:
            twitter = data2["data"]["socialMedia"]["twitter"] if data2["data"]["socialMedia"]["twitter"] else '暂无数据'
        except KeyError:
            twitter = '暂无数据'
            
        try:
            officialWebsite = data2["data"]["socialMedia"]["officialWebsite"] if data2["data"]["socialMedia"]["officialWebsite"] else '暂无数据'
        except KeyError:
            officialWebsite = '暂无数据'

        try:
            telegram = data2["data"]["socialMedia"]["telegram"] if data2["data"]["socialMedia"]["telegram"] else '暂无数据'
        except KeyError:
            telegram = '暂无数据'

        # 对社交信息进行验证
        twitter_info = is_x(twitter) 
        officialWebsite_info = is_web(officialWebsite)
        telegram_info = is_TG(telegram)  
        
        # 获取池子创建时间
        #先从raydium 获取时间
        
        """ find_pool_create_time = '暂未发现'
        
        if chainId == 501:
            pool_create_time = get_pool_create_time(501, ca)
            if(pool_create_time == 0):
                #无法从raydium 就获取代币创建时间表示pump
                pool_create_time = data2["data"]["memeInfo"]["createTime"]
                find_pool_create_time = '暂未发现'
            
            else:
                dt_object = datetime.fromtimestamp(pool_create_time/1000)
                find_pool_create_time = dt_object.strftime('%m-%d %H:%M:%S')  # 格式：年-月-日 时:分:秒 """
        
            
        # 记录哨兵caller信息
        # 先拿到当前caller的昵称                       
        # caller_wxid = sol_ca_jobs[i][0].sender  
        #chatroom_members = wcf.get_chatroom_members(roomid = roomid)
        if price != '暂无数据':
        
            # 返回处理后的数据
            return {
                "ca": ca,
                "roomid": roomid,
                'wxId': wxId,
                "chainId": chainId,
                "tokenSymbol": tokenSymbol,
                "tokenName": tokenName,
                "price": price,
                "marketCap": marketCap,
                "circulatingSupply": circulatingSupply,
                "volume": volume,
                "holders": holders,
                "top10HoldAmountPercentage": top10HoldAmountPercentage,
                "twitter_info": twitter_info,
                "officialWebsite_info": officialWebsite_info,
                "telegram_info": telegram_info,
                #"find_pool_create_time": find_pool_create_time,
                'find_time':time_ms
            }
        else:
            return None
        
    except Exception as e:
        logger.error(f"获取或处理数据时发生错误: {str(e)}", exc_info=True)
        return None


# 处理合约信息
def generate_info_message(data, data_save, data1, data2, is_first_time, time_ms):
    """
    生成信息消息。
    :param data: 处理后的数据
    :param is_first_time: 是否是首次出现
    :param timestamp: 时间戳
    :return: 生成的消息内容
    """
    try:
        find_time = data["find_time"]
        print('1122222222')

        timestamp_seconds = find_time / 1000
        # 转换为 UTC 时间
        utc_time = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
        # 转换为北京时间（UTC+8）
        beijing_time = utc_time + timedelta(hours=8)
        # 格式化输出
        find_time = beijing_time.strftime("%m-%d %H:%M:%S")
        
        #跨账号拿取wxid
        caller_simulate_name = None
        caller_gender ='未知'
        wxId = data["wxId"]
        
        # 从监听服务器拿取群成员信息，wxid和昵称
        # 在业务逻辑中使用批量存储
        print('1122222222')
        results = get_wx_info_v2(data['roomid'])
        print('~~~~~~~~~~~~~~~~~~~~~~~')
        print(results)
        # 将群组成员信息进行更新或添加
        if results != '{}' :
            print('为空为什么还进来')
            save_or_update_to_redis_list(results)
             
            member_dict = results['chatroomMembers']
            all_member_dict = get_wxid_nickname_from_redis(REDIS_WX_KEY)

            if not all_member_dict and not member_dict:
                caller_simulate_name = '数据暂时异常'
            elif not all_member_dict and member_dict:
                add_wxid_nickname_to_redis_batch(key=REDIS_WX_KEY, data=member_dict)
                caller_simulate_name = member_dict.get(wxId, '数据暂时异常')
            elif all_member_dict and member_dict:
                # 合并 member_dict 和 all_member_dict
                merged_dict = {**all_member_dict, **member_dict}
                add_wxid_nickname_to_redis_batch(key=REDIS_WX_KEY, data=member_dict)
                caller_simulate_name = merged_dict.get(wxId, '数据暂时异常')
        else:
            member_dict = None
            all_member_dict = get_wxid_nickname_from_redis(REDIS_WX_KEY)
            if not all_member_dict :
                caller_simulate_name = '数据暂时异常'
            elif all_member_dict :                   
                caller_simulate_name = merged_dict.get(wxId, '数据暂时异常')

            
        """ for i in range(len(caller_list)):
            diff = abs(caller_list[i]['times']- time_ms )
            diff_seconds = diff/1000.0
            if diff_seconds <= 8 :
                caller_simulate_name = caller_list[i]['wxNick']
                wxId = caller_list[i]['wxId']
                data3 = wcf.get_info_by_wxid(caller_list[i]['wxId'])
                #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                #print(data3)
                caller_gender = data3['gender'] if data3['gender'] else '未知'
                break  
        caller_simulate_name = caller_simulate_name if caller_simulate_name  else '数据暂时异常'
        wxId = wxId if wxId else '数据暂时异常' """
        
        if is_first_time:
            
            #cp_time = '发射时间' if is_pump(data["ca"]) else '创建时间'
            try:
                description = translate(data2["data"]['socialMedia']['description']) if data2["data"]['socialMedia']['description'] else '暂无叙事'
            except KeyError:
                description = '暂无数据'
            
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=14))
            info = (
                f"{data['ca']}\n"
                f"简写：{data['tokenSymbol']}\n"
                f"名称：{data['tokenName']}\n"
                f"💰价格: {data['price']}\n"
                f"💹流通市值：{data['marketCap']}\n"
                f"📊交易量：{data['volume']}\n"
                f"🦸持有人: {data['holders']}\n"
                f"🐋top10持仓: {data['top10HoldAmountPercentage']}\n"
                f"🍭捆绑比例：功能优化中\n\n"
                f"{data['twitter_info'][0]}{data['twitter_info'][1]}{data['officialWebsite_info'][0]}{data['officialWebsite_info'][1]}{data['telegram_info'][0]}{data['telegram_info'][1]}\n"
                f"🕵️哨兵：{caller_simulate_name}\n"
                f"📈Call: {data['marketCap']} -> {data['marketCap']}\n"
                f"🚀最大倍数: 1.00X\n"
                f"🔥当前倍数: 1.00X\n\n"
                f"💬大致叙事: {description if description else '暂无叙事'} {random_string}\n"
                f"🎯发现时间：{find_time}"
                #f"🎯{cp_time}:{data['find_pool_create_time']}"
            )
            wcf.send_text(info, data['roomid'])
            
            
            """ timestamp_2 = int(time.time() * 1000)
            hs = (timestamp_2 - timestamp_1)/1000
            print('总耗时{}'.format(hs)) """

            store_nested_data_to_redis(data['roomid'],data['ca'], data['tokenSymbol'],caller_simulate_name, caller_gender,data1, description, data['find_time'])
        else:
            description = translate(data2["data"]['socialMedia']['description']) if data_save["description"] == '暂无叙事' else data_save["description"]
            nowCap = float(data1["data"]["price"]) * float(data1["data"]["circulatingSupply"])
            #如果发现创新高，则更新最大市值
            if nowCap > data_save['topCap']:
                data_save['topCap'] = nowCap
                store_nested_data_to_redis(data['roomid'],data['ca'], data['tokenSymbol'],caller_simulate_name, caller_gender,data1, description, data['find_time'])

            if data_save['caller_name'] == '数据暂时异常':
                print('哨兵数据异常，重新获取')
                         
                if caller_simulate_name != '数据暂时异常':
                    store_nested_data_to_redis(data['roomid'],data['ca'], data['tokenSymbol'],caller_simulate_name, caller_gender,data1, description, data['find_time'])
                    data_save = get_nested_data_from_redis(roomid=data['roomid'], ca_ca=data['ca'])
            
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=14))
            info = (
                f"{data['ca']}\n"
                f"简写：{data['tokenSymbol']}\n"
                f"名称：{data['tokenName']}\n"
                f"💰价格: {data['price']}\n"
                f"💹流通市值：{data['marketCap']}\n"
                f"📊交易量：{data['volume']}\n"
                f"🦸持有人: {data['holders']}\n"
                f"🐋top10持仓: {data['top10HoldAmountPercentage']}\n"
                f"🍭捆绑比例：功能优化中\n\n"
                f"{data['twitter_info'][0]}{data['twitter_info'][1]}{data['officialWebsite_info'][0]}{data['officialWebsite_info'][1]}{data['telegram_info'][0]}{data['telegram_info'][1]}\n"
                f"🕵️哨兵：{data_save['caller_name']}\n"
                f"📈Call: {math_km(data_save['initCap'])} -> {math_km(data_save['topCap'])}\n"
                f"🚀最大倍数: {str(round(data_save['topCap'] / data_save['initCap'], 2)) + 'X'}\n"
                f"🔥当前倍数: {str(round(nowCap / float(data_save['initCap']), 2)) + 'X'}\n\n"
                f"💬大致叙事: {description} {random_string} \n"
                f"🎯发现时间：{find_time}"
                #f"🎯创建时间：{data['find_pool_create_time']}"
            )
            wcf.send_text(info, data['roomid'])
        
        #将用户的首次喊单数据进行存储    
        if caller_simulate_name != '数据暂时异常' and wxId!= '数据暂时异常':
            
            # 构造需要存储的列表数据
            new_data = [[
                wxId,
                caller_simulate_name,
                data['chainId'],
                data['ca'],
                float(data['circulatingSupply']) * float(data['price']),
                float(data['circulatingSupply']) * float(data['price']),
                data['circulatingSupply'],
                data['price'],
                data["find_time"],
                data['tokenSymbol']
            ]]
            send_person_ca(payload=new_data)

                


            """ if len(person_ca) > 0:
                for i in range(len(person_ca)):
                    if wxId == person_ca[i][0] and data['ca'] == person_ca[i][3]:
                        pass
                    else:
                        person_ca.append([
                            wxId,
                            caller_simulate_name,
                            data['chainId'],
                            data['ca'],
                            float(data['circulatingSupply'])*float(data['price']),
                            float(data['circulatingSupply'])*float(data['price']),
                            data['circulatingSupply'],
                            data['price'],
                            data["find_time"]
                        ])

                        
            else:
                person_ca.append([
                    wxId,
                    caller_simulate_name,
                    data['chainId'],
                    data['ca'],
                    float(data['circulatingSupply'])*float(data['price']),
                    float(data['circulatingSupply'])*float(data['price']),
                    data['circulatingSupply'],
                    data['price'],
                    data["find_time"]
                ]) """

        
        return info,random_string


    except Exception as e:
        logger.error(f'生成消息时发生错误：{str(e)}',exc_info = True)
        return None, None


#存个人ca数据
def store_person_ca(new_data):
    """
    将 new_data 存储到 Redis 中，确保没有重复数据。
    
    参数:
        new_data (list): 需要存储的数据，格式为 [wxId, caller_simulate_name, chainId, ca, total_value1, total_value2, circulatingSupply, price, find_time]
    """
    try:
        # 解析 new_data
        wxId = new_data[0]
        ca = new_data[3]

        # 检查 Redis 中是否存在该键
        if r.exists(REDIS_KEY):
            # 如果 Redis 中的列表不为空，获取列表中的所有数据
            person_ca_list = r.lrange(REDIS_KEY, 0, -1)
            should_store = True  # 默认需要存储数据

            # 遍历列表中的每条数据
            for item in person_ca_list:
                # 如果 item 是字节类型，解码为字符串
                if isinstance(item, bytes):
                    item = item.decode()
                # 将字符串拆分为列表
                item_data = item.split(',')
                # 检查是否满足条件
                if wxId == item_data[0] and ca == item_data[3]:
                    should_store = False  # 如果条件满足，则不存储
                    break  # 发现重复数据，直接退出循环

            # 如果满足条件，存储数据
            if should_store:
                r.rpush(REDIS_KEY, ','.join(map(str, new_data)))
                print("数据已存储到 Redis 中。")
            else:
                print("数据已存在，未存储。")
        else:
            # 如果 Redis 中的列表为空，直接存储数据
            r.rpush(REDIS_KEY, ','.join(map(str, new_data)))
            print("数据已存储到 Redis 中。")
    except Exception as e:
        print(f"存储数据时出错: {e}")


#取个人ca数据
def get_person_ca_from_redis():
    """
    从 Redis 中获取数据并还原成二维数组。

    返回:
        list: 二维数组，格式为 [[wxId, caller_simulate_name, chainId, ca, ...], ...]
    """
    try:
        # 检查 Redis 中是否存在该键
        if r.exists(REDIS_KEY):
            # 获取 Redis 列表中的所有数据
            person_ca_list = r.lrange(REDIS_KEY, 0, -1)
            result = []

            # 遍历列表中的每条数据
            for item in person_ca_list:
                # 如果 item 是字节类型，解码为字符串
                if isinstance(item, bytes):
                    item = item.decode()
                # 将字符串按逗号分割成列表
                item_data = item.split(',')
                # 将列表添加到结果中
                result.append(item_data)

            return result
        else:
            print("Redis 中不存在该键。")
            return []  # 返回空列表
    except Exception as e:
        print(f"从 Redis 获取数据时出错: {e}")
        return []  # 返回空列表



#sol合约的任务
def sol_ca_job():
    
    while not stop_event.is_set():
        try:
            if len(sol_ca_jobs) > 0:
                print('开始sol任务') 
                # 反向遍历 sol_ca_jobs，避免删除元素影响索引
                for i in range(len(sol_ca_jobs) - 1, -1, -1):
                    time.sleep(0.2)
                    roomid = sol_ca_jobs[i][0].roomid
                    wxId = sol_ca_jobs[i][0].sender
                    ca = sol_ca_jobs[i][1]
                    time_ms = sol_ca_jobs[i][2]
                    # 获取并处理信息
                    data1 = fetch_oke_latest_info(chainId=501, ca_ca = ca)
                    data2 = fetch_oke_overview_info(chainId=501, ca_ca = ca)
                    if data1 and data2 :
                        data =  fetch_and_process_data(roomid=roomid, wxId=wxId, chainId=501, ca=ca, data1=data1, data2=data2, time_ms=time_ms)
                        if not data:
                            del sol_ca_jobs[i]
                            continue

                        # 判断该 ca 在当前群组是不是首次出现
                        data_save = get_nested_data_from_redis(roomid=roomid, ca_ca=ca)
                                    
                        # 判断该ca在当前群组是不是首次出现
                        if data_save :
                            # 如果是再次出现，则需要找到哨兵数据
                            logger.info('该合约重复出现')
                            info, random_string = generate_info_message(data,data_save=data_save,data1=data1, data2=data2, is_first_time=False, time_ms=time_ms)
                        else:
                            # 首次出现
                            info, random_string = generate_info_message(data,data_save=data_save,data1=data1, data2=data2, is_first_time=True, time_ms=time_ms)

                        if info:
                            
                            timestamp_ms = int(time.time() * 1000)
                            time.sleep(1)
                            old_news_id = getMyLastestGroupMsgID(keyword=random_string)
                            old_news.append([old_news_id, timestamp_ms])
                            del sol_ca_jobs[i]

        except Exception as e:
            logger.error(f"主循环发生错误: {str(e)}", exc_info=True)
            continue


#ETHS合约的任务
def eths_ca_job():
    while not stop_event.is_set():
        try:
            if len(eths_ca_jobs) > 0:
                print('开始eths任务') 
                # 反向遍历 sol_ca_jobs，避免删除元素影响索引
                for i in range(len(eths_ca_jobs) - 1, -1, -1):
                    time.sleep(0.2)
                    roomid = eths_ca_jobs[i][0].roomid
                    wxId = eths_ca_jobs[i][0].sender
                    ca = eths_ca_jobs[i][1]
                    time_ms = eths_ca_jobs[i][2]
                    # 获取并处理信息
                    data1 = fetch_oke_latest_info(chainId=56, ca_ca = ca)
                    data2 = fetch_oke_overview_info(chainId=56, ca_ca = ca)
                    if data1 and data2 :
                        data =  fetch_and_process_data(roomid=roomid, wxId=wxId, chainId=56, ca=ca, data1=data1, data2=data2, time_ms=time_ms)
                        if not data:
                            del eths_ca_jobs[i]
                            continue

                        # 判断该 ca 在当前群组是不是首次出现
                        data_save = get_nested_data_from_redis(roomid=roomid, ca_ca=ca)
                                    
                        # 判断该ca在当前群组是不是首次出现
                        if data_save :
                            # 如果是再次出现，则需要找到哨兵数据
                            logger.info('该合约重复出现')
                            info, random_string = generate_info_message(data,data_save=data_save,data1=data1, data2=data2, is_first_time=False, time_ms=time_ms)
                        else:
                            # 首次出现
                            info, random_string = generate_info_message(data,data_save=data_save,data1=data1, data2=data2, is_first_time=True, time_ms=time_ms)

                        if info:
                            # wcf.send_text(info, roomid)
                            timestamp_ms = int(time.time() * 1000)
                            time.sleep(1)
                            old_news_id = getMyLastestGroupMsgID(keyword=random_string)
                            old_news.append([old_news_id, timestamp_ms])
                            del eths_ca_jobs[i]

        except Exception as e:
            logger.error(f"主循环发生错误: {str(e)}", exc_info=True)
            continue    
                     

def person_ca_max():
    while not stop_event.is_set():
        try:
            if len(person_ca_jobs) > 0:
                print('开始计算个人最高倍数任务')

                # 反向遍历 person_ca_jobs，避免删除元素影响索引
                for i in range(len(person_ca_jobs) - 1, -1, -1):
                    job_data = person_ca_jobs[i]
                    
                    job_ca = job_data[0]  # 任务中的合约地址
                    job_price = float(job_data[1])  # 任务中的价格

                    # 遍历 Redis 中的 person_ca 数据
                    person_ca_length = r.llen(REDIS_KEY)
                    print(person_ca_length)
                    for j in range(person_ca_length):
                        # 获取 person_ca 中的数据
                        person_data = r.lindex(REDIS_KEY, j)
                        # 如果 person_data 是字节类型，解码为字符串
                        if isinstance(person_data, bytes):
                            person_data = person_data.decode()
                        # 将字符串拆分为列表
                        person_data = person_data.split(',')
                        print(person_data)
                        person_ca = person_data[3]  # person_ca 中的合约地址
                        person_circulatingSupply = float(person_data[-3])  # person_ca 中的流通量

                        # 如果任务中的合约地址与 person_ca 中的合约地址匹配
                        if job_ca == person_ca:
                            now_cap = job_price * person_circulatingSupply  # 计算当前市值
                            max_cap = float(person_data[5])  # 获取历史最高市值
                            print(now_cap)
                            print(max_cap)
                            # 如果当前市值大于历史最高市值
                            if now_cap > max_cap:
                                # 更新历史最高市值
                                person_data[5] = str(now_cap)
                                # 将更新后的数据重新存储到 Redis
                                r.lset(REDIS_KEY, j, ','.join(person_data))
                                print('---------------------------')
                                print('{}喊单的{}已创新高{}'.format(person_data[1], person_data[3], now_cap))

                    # 删除已处理的任务
                    del person_ca_jobs[i]

            # 休眠一段时间，避免频繁轮询
            time.sleep(1)
        except Exception as e:
            print(f"计算个人最高倍数任务出错: {e}")



""" #定时计算个人ca最高倍数的任务
def person_ca_max():
    while not stop_event.is_set():
        try:
            if len(person_ca_jobs) > 0:
                
                # 反向遍历 sol_ca_jobs避免删除元素影响索引
                for i in range(len(person_ca_jobs) - 1, -1, -1):
                    print('开始计算个人最高倍数任务') 
                    print(person_ca)
                    for j in range(len(person_ca)):
                        if person_ca_jobs[i][0] ==  person_ca[j][3]:
                            now_cap = float(person_ca_jobs[i][1])*float(person_ca[j][-3])
                            print(now_cap)
                            print(person_ca[j][5])
                            # 币价产生了新高
                            if now_cap > person_ca[j][5]:
                                person_ca[j][5] = now_cap
                                print('---------------------------')
                                print('{}喊单的{}已创新高{}'.format(person_ca[j][1],person_ca[j][3],person_ca[j][5]))
                    del person_ca_jobs[i]           
                        
                           

#person_ca.append([wxId, caller_simulate_name, data['chainId'], data['ca'], data['circulatingSupply']*data['price'], data['circulatingSupply']*data['price'], data['circulatingSupply'], data['price'], data["find_time"]])
        
        except Exception as e:
            logger.error(f"主循环发生错误: {str(e)}", exc_info=True)
            continue """


#根据 input_data 的顺序，重新排列 response_data['data']
def sort_response_by_input(input_data, response_data):
    """
    根据 input_data 的顺序，重新排列 response_data['data']
    
    :param input_data: list,包含请求的合约地址列表
    :param response_data: dict,包含 API 返回的数据
    :return: dict,返回和原始 response_data 格式相同，但顺序匹配 input_data
    """
    if 'data' not in response_data:
        return {'msg': '错误: API 返回数据格式不正确', 'code': 400, 'data': []}

    # 创建一个地址 -> 价格的映射表
    price_dict = {item['address']: item['price'] for item in response_data['data']}

    # 按照 input_data 的顺序重新排序返回数据
    sorted_data = [{'address': item['address'], 'price': price_dict.get(item['address'], None)} for item in input_data]

    # 生成最终的返回数据，格式和原始 response_data 一致
    sorted_response = {
        'msg': response_data.get('msg', '操作成功'),
        'code': response_data.get('code', 200),
        'data': sorted_data
    }

    return sorted_response


#定时发送排行榜信息。
def send_leaderboard_periodically(send_interval_hours:int):
    """
    独立线程：定时发送排行榜信息。
    
    :param send_interval_hours: 发送间隔（小时）
    """
    last_send_time = None  # 记录上一次发送的时间

    while not stop_event.is_set():
        current_time = datetime.now()
        
        # 检查是否到达整点
        if current_time.minute == 0 and current_time.second == 0:
            # 检查是否满足时间间隔
            if last_send_time is None or (current_time - last_send_time).total_seconds() >= 4 * 3600:
                for roomid in groups:
                    rankings = all_rankings.get(roomid, [])
                    if rankings:
                        send_leaderboard_to_group(roomid, rankings)
                        time.sleep(1)  # 每次发送间隔2秒
                last_send_time = current_time  # 更新上一次发送时间
                print(f"已发送排行榜信息，当前时间: {current_time}，发送间隔: {4}小时")
                result = get_person_ca_from_redis()
                send_person_ca(payload=result)

        time.sleep(1)  # 每秒检查一次时间


#发送排行榜数据的方法
def send_leaderboard_to_group(roomid, rankings):
    """将排行榜数据发送到指定群组"""
    try:
        # 检查排行榜数据是否为空
        if not rankings:
            wcf.send_text("暂无排行榜数据，群友快快发金狗", roomid)
            print(f"分组 {roomid} 的排行榜数据为空")
            return

        # 只取前 10 名
        top_10_rankings = rankings[:10]

        # 排行榜标题
        leaderboard_msg = "🎉   🏅   🎉   🏅   🎉   🏅   🎉\n"
        leaderboard_msg += "🏆🌟     Top10  排行榜    🌟🏆\n"
        leaderboard_msg += "━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"

        for idx, entry in enumerate(top_10_rankings, start=1):
            # 根据性别选择头像
            if entry.get('caller_gender') == '女':
                avatar = "👩"  # 女性头像
            else:
                avatar = "👨"  # 男性头像或默认头像

            # 根据排名选择奖牌
            if idx == 1:
                rank_emoji = "🥇" + avatar  # 第一名
            elif idx == 2:
                rank_emoji = "🥈" + avatar  # 第二名
            elif idx == 3:
                rank_emoji = "🥉" + avatar  # 第三名
            else:
                rank_emoji = f"{idx}." + avatar  # 其他名次

            leaderboard_msg += (
                f"{rank_emoji} {entry['caller_name']}\n"
                f"   💰  {entry['tokenSymbol']}   🚀 {entry['ratio']:.2f}X\n"
                f"━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"
            )

        # 如果数据不足 10 条，添加提示信息
        if len(top_10_rankings) < 10:
            leaderboard_msg += "\n⚠️ 当前排行榜数据不足 10 条\n"

        # 排行榜底部装饰
        leaderboard_msg += "🎉🏅   恭喜老板上榜   🏅🎉\n"
        leaderboard_msg += "🎉   🏅   🎉   🏅   🎉   🏅   🎉"

        wcf.send_text(leaderboard_msg, roomid)
        print(f"已发送排行榜到分组 {roomid}:\n{leaderboard_msg}")
    except Exception as e:
        logger.error(f"发送排行榜数据到群组 {roomid} 时发生错误: {str(e)}", exc_info=True)


#清空排行榜数据
def clear_leaderboard():
    """清空排行榜数据"""
    try:
        for roomid in groups:
            r.delete(f"leaderboard_{roomid}")
            logger.info(f"已清空群组 {roomid} 的排行榜数据")

            # 清空合约代币数据
            r.delete(roomid)
            logger.info(f"已清空群组 {roomid} 的合约代币数据")
    except Exception as e:
        logger.error(f"清空排行榜数据时发生错误: {str(e)}", exc_info=True)


#定时更新排行榜数据，并实现整点发送和每日清空功能
def start_top_update():
    """定时更新排行榜数据，并实现整点发送和每日清空功能"""
    global all_rankings 
    all_rankings = {roomid: [] for roomid in groups}
   
    # 上一次发送排行榜数据的时间
    last_send_time = None

    while not stop_event.is_set():
        try:
            # 获取当前时间
            update_time = math_bjtime()
            logger.info(f"----{update_time}----开始更新排行榜数据")

            # 遍历每个群组
            for roomid in groups:
                try:
                    # 获取该分组下的所有合约代币数据
                    ca_data = r.hgetall(roomid)
                    if not ca_data:
                        logger.warning(f"群组 {roomid} 没有合约代币数据")
                        continue

                    # 获取上一次的排行榜数据
                    print('________________________')
                    
                    rankings = all_rankings.get(roomid, [])

                    # 将合约地址分成每 10 个一组
                    ca_list = list(ca_data.items())
                    for i in range(0, len(ca_list), 10):
                        batch = ca_list[i:i + 10]  # 每 10 个合约为一组
                        payload = []

                        # 构建批量查询的 payload
                        for ca_ca, data_json in batch:
                            data1 = json.loads(data_json)
                            sol_id, sol_ca = is_solca(ca_ca)
                            eths_id, eths_ca = is_eths(ca_ca)

                            if sol_id:
                                payload.append({"chain": "sol", "address": sol_ca})
                            else:
                                payload.append({"chain": "bsc", "address": eths_ca})

                        # 批量查询价格
                        result1 = get_price_onchain(payload)
                        result2 = sort_response_by_input(payload, result1)
                        if not result2 or 'data' not in result2:
                            logger.warning(f"批量查询价格失败: {result2}")
                            continue

                        # 处理每个合约的最新价格
                        for idx, (ca_ca, data_json) in enumerate(batch):
                            data1 = json.loads(data_json)
                            price_data = result2['data'][idx] if idx < len(result2['data']) else None

                            if not price_data:
                                logger.warning(f"未获取到合约 {data1['tokenSymbol']} 的价格数据")
                                continue

                            # 获取最新价格
                            price = float(price_data['price'])
                            #person_ca_jobs.append([ca_ca, price])
                            newCap = price * data1['circulatingSupply'] if price else (data1['topCap'] / 1.15)

                            # 检查是否创新高
                            random_number = round(random.uniform(1.10, 1.20), 2)
                            if random_number * newCap > data1['topCap']:
                                ath_time = math_bjtime()
                                print('{}创新高,市值突破{}新高时间为{}'.format(data1['tokenSymbol'], random_number * newCap, ath_time))
                                data1['topCap'] = random_number * newCap
                                ratio = data1['topCap'] / data1['initCap']
                                r.hset(roomid, ca_ca, json.dumps(data1))

                                # 更新 rankings 中的数据
                                existing_entry = next((entry for entry in rankings if entry['tokenSymbol'] == data1['tokenSymbol']), None)
                                if existing_entry:
                                    existing_entry['ratio'] = ratio
                                else:
                                    rankings.append({
                                        'tokenSymbol': data1['tokenSymbol'],
                                        'caller_name': data1['caller_name'],
                                        'ratio': ratio
                                    })
                            else:
                                ratio = data1['topCap'] / data1['initCap']
                                existing_entry = next((entry for entry in rankings if entry['tokenSymbol'] == data1['tokenSymbol']), None)
                                if not existing_entry:
                                    rankings.append({
                                        'tokenSymbol': data1['tokenSymbol'],
                                        'caller_name': data1['caller_name'],
                                        'caller_gender': data1['caller_gender'],
                                        'ratio': ratio
                                    })

                    # 按 ratio 从高到低排序
                    rankings.sort(key=lambda x: x['ratio'], reverse=True)

                    # 更新总 rankings 数据
                    all_rankings[roomid] = rankings

                    # 将排行榜数据存储到 Redis 中
                    r.set(f"leaderboard_{roomid}", json.dumps(rankings))
                    logger.info(f"已更新分组 {roomid} 的排行榜数据")

                except Exception as e:
                    logger.error(f"更新群组 {roomid} 的排行榜数据时发生错误: {str(e)}", exc_info=True)
                    continue
   

            # 休眠 180 秒
            time.sleep(TOP_UPDATA_S)

        except Exception as e:
            logger.error(f"更新排行榜数据时发生错误: {str(e)}", exc_info=True)
            continue


# 启动微信消息监听的线程
def start_wcf_listener():
    wcf.enable_receiving_msg()
    print('机器人启动')
    
    while wcf.is_receiving_msg():
        try:
            msg = wcf.get_msg()
            # 处理消息的逻辑...
            time.sleep(0.3)
            # print('222222')
            '''if msg.content == "滚kkkkkkkkkkk":
                wcf.send_text("好的，小瓜瓜，爱你爱你哦,周末一起玩",msg.sender)
            '''
            # 判断是否是id指令，查询打印roomid
            command_id(msg = msg)
      
            # 判断是否是cextoken指令，查询发送交易所代币价格
            command_cextoken(wcf = wcf, msg= msg, groups= groups)
            
            # 判断是否是ca排行榜指令，查询发送群组排行榜信息
            command_leaderboard_ca(wcf = wcf, msg= msg, groups= groups)
            
            # 判断是否是个人战绩指令
            command_person_record(wcf = wcf, msg= msg, groups= groups)
            
       
                   
            # 判断消息中是否包含ca信息
            #timestamp_1 = int(time.time() * 1000)
            sol_id, sol_ca = is_solca(msg.content)
            eths_id, eths_ca = is_eths(msg.content)
           
            # 判断ca属于哪条链
            if sol_id :
                chain_id = sol_id
                ca_ca = sol_ca           
                if msg.from_group() and msg.roomid in groups:
                    print('发现sol合约,开始查询ca信息')     
                    find_time = math_bjtime()
                    timestamp_ms = int(time.time() * 1000)
                    #将查询sol合约任务添加到任务列表中,并进行去重，相同合约在任务列表中只能存在一个
                    if any(ca_ca in row for row in sol_ca_jobs):
                        pass
                    else:
                        sol_ca_jobs.append([msg, sol_ca, timestamp_ms])              
             
            elif eths_id:
                chain_id = eths_id
                ca_ca = eths_ca
                        
                if msg.from_group()  and msg.roomid in groups:   
                    print('发现eths合约,开始查询ca信息') 
                    find_time = math_bjtime()
                    timestamp_ms = int(time.time()*1000)
                    if any(ca_ca in row for row in eths_ca_jobs):
                        pass
                    else:
                        eths_ca_jobs.append([msg, eths_ca, timestamp_ms]) 
                                               
            else:
                chain_id = None
                ca_ca = None      

        except Empty:
            continue
        except Exception as e:
            print(e)

    wcf.keep_running()




# 启动所有线程
def start_all_tasks():
    
    # 启动微信监听线程
    wcf_listener_thread = threading.Thread(target=start_wcf_listener)
    wcf_listener_thread.start()

    # 启动sol合约查询任务的线程
    sol_job_thread = threading.Thread(target=sol_ca_job)
    sol_job_thread.start()

    # 启动eths合约查询任务的线程
    eths_job_thread = threading.Thread(target=eths_ca_job)
    eths_job_thread.start()


    # 启动撤回消息\00:10情况排行榜数据的的线程
    recover_message_thread = threading.Thread(target=recover_message)
    recover_message_thread.start()

    # 启动定时发送排行榜的线程
    send_leaderboard_periodically_thread = threading.Thread(target=send_leaderboard_periodically, args=(4,))
    send_leaderboard_periodically_thread.start()

    # 启动排行榜更新线程
    top_update_thread = threading.Thread(target=start_top_update)
    top_update_thread.start()



    # 等待线程结束（如果需要的话）
    try:
        while True:
            time.sleep(30)  # 每分钟检查一次
    except KeyboardInterrupt:
        stop_event.set()
        wcf_listener_thread.join()
        top_update_thread.join()
        sol_job_thread.join()
        eths_job_thread.join()
        recover_message_thread.join()
        send_leaderboard_periodically_thread.join()
        
        print("已停止所有任务")


# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别为 DEBUG
    format="%(asctime)s - %(levelname)s - %(message)s",  # 日志格式
    handlers=[
        logging.FileHandler("sol_ca_job.log"),  # 输出到文件
        logging.StreamHandler()  # 输出到控制台
    ]
)


# 获取日志记录器
logger = logging.getLogger("sol_ca_job_logger")

logger = logging.getLogger("top_update_logger")




config = configparser.ConfigParser()
try:
    with open('config.ini', 'r', encoding='utf-8') as f:
        config.read_file(f)
    REVOKE_INTERVAL_MS = int(config['Settings']['revoke_interval_ms'])
    TOP_UPDATA_S =  int(config['Settings']['top_updata_s'])

except Exception as e:
    print(f"读取配置文件失败，使用默认值: {e}")

print(f"撤回时间间隔配置: {REVOKE_INTERVAL_MS} ms")


stop_event = threading.Event()  # 控制线程停止的事件
all_rankings = {}
sol_ca_jobs = []
eths_ca_jobs = []
person_ca_jobs = []
old_news = []


REDIS_KEY = "person_ca_list"
REDIS_WX_KEY = 'wxid_nickname_dict'

wcf = Wcf()

r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# '53951514521@chatroom'
groups = ["58224083481@chatroom",'52173635194@chatroom']

print(12311111111111111111)
start_all_tasks()