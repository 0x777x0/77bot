
from wcferry import Wcf
from queue import Empty
from ca.ca_info import is_solca, is_eths, math_price, math_cex_price, math_km, math_percent, math_bjtime, get_bundles, is_cexToken, is_pump
from command.command import command_id
from httpsss.oke import fetch_oke_latest_info, fetch_oke_overview_info
from common.socialMedia_info import is_x, is_web, is_TG
from common.translate import translate
from datetime import datetime, timedelta, timezone
from common.bjTime import convert_timestamp_to_beijing_time
from ca.binance import get_binance_price
# from common.cache import redis
from ca.binance import get_binance_price
from save_data import get_wx_info

import threading
import functools
import re
import requests
import time
import json
import redis
import random
import string



# 将ca_datas 数据以嵌套字典形式存到 redis 的方法
def store_nested_data_to_redis(roomid, ca_ca, tokenSymbol,caller_name, data1, description, find_time_ms):
    # 准备数据
    data = {
    'tokenSymbol':tokenSymbol,
    'caller_name': caller_name,
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


# 启动微信消息监听的线程
def start_wcf_listener():
    global message_number
    wcf.enable_receiving_msg()
    print('机器人启动')
    
    while wcf.is_receiving_msg():
        try:
            msg = wcf.get_msg()
            # 处理消息的逻辑...
            time.sleep(1)
            print('222222')
            if msg.content == "滚kkkkkkkkkkk":
                wcf.send_text("好的，小瓜瓜，爱你爱你哦,周末一起玩",msg.sender)
            
            if msg.content == "时间1":
                wcf.send_text("你好，宇哥，现在时间是："+ math_bjtime(),msg.sender)

            if msg.from_group() and msg.content == "id850" :
            
                               
                # wcf.send_text(info,msg.roomid)  
                timestamp_ms = int(time.time() * 1000)
                time.sleep(1)
                old_news_id =  getMyLastestGroupMsgID(keyword=info)  
                print(old_news_id)
                old_news.append([old_news_id,timestamp_ms])          
                print(msg.roomid)       
                
            """ wcf.send_text("fgfdgh223441","58224083481@chatroom")
            timestamp_ms = int(time.time() * 1000)
            time.sleep(1)
            old_news_id =  getMyLastestGroupMsgID(keyword="fgfdgh223441")  
            print(old_news_id)
            old_news.append([old_news_id,timestamp_ms]) """

            # 获取主流代币价格
            if msg.from_group() and is_cexToken(msg.content) and msg.content!= '/top' and msg.roomid in groups :
                
                token_symble = msg.content[1:]
                token_price = get_binance_price(token_symble)
                print(type(token_price))

                if float(token_price) > 0 :
                    token_price = float(token_price)
                    token_price = math_cex_price(token_price)
                    print('{}当前的price为:{}'.format(token_symble,token_price)) 
                    wcf.send_text('{}当前的price为:{}'.format(token_symble,token_price),msg.roomid)
            
            # 记录用户发言次数（使用昵称）
            if msg.from_group() and msg.roomid in groups:
                user_wxid = msg.sender

                # 检查 sender 是否是群 roomid
                if user_wxid == msg.roomid:
                    continue  # 跳过群 roomid，不记录

                # 获取用户昵称
                chatroom_members = wcf.get_chatroom_members(roomid=msg.roomid) or {}
                user_name = chatroom_members.get(user_wxid, user_wxid)  # 如果没有昵称，使用微信ID
                
                # 使用 Redis 记录用户发言次数（以昵称为键）
                redis_key = f"activity_{msg.roomid}"
                r.hincrby(redis_key, user_wxid, 1)  # 每次发言增加1 

       
            if msg.from_group() and msg.content.startswith("/活跃") and msg.roomid in groups:
                # 获取页码（例如 /huo1 会得到页码 1）
                try:
                    page_number = int(msg.content[3:])  # 获取页码（从/huo后面的数字提取）
                except ValueError:
                    wcf.send_text("请输入正确的页码，例如 /huo1、/huo2 等", msg.roomid)
                    continue

                # 获取活跃度数据
                redis_key = f"activity_{msg.roomid}"
                activity_data = r.hgetall(redis_key)  # 获取活跃度数据

                # 获取群成员昵称映射
                chatroom_members = wcf.get_chatroom_members(roomid=msg.roomid) or {}

                # 处理活跃度数据：把 wxid 转换为昵称
                user_activity = [
                    (chatroom_members.get(user, user), int(count))  # 如果找不到昵称，就显示 wxid
                    for user, count in activity_data.items()
                ]

                # 按照发言次数降序排序
                user_activity.sort(key=lambda x: x[1], reverse=True)

                # 每页显示10条数据
                items_per_page = 10
                start_index = (page_number - 1) * items_per_page
                end_index = start_index + items_per_page

                # 截取当前页面的数据
                page_data = user_activity[start_index:end_index]

                if not page_data:
                    wcf.send_text(f"第 {page_number} 页没有数据，请确认页码是否正确", msg.roomid)
                    continue

                # 生成排行榜信息
                leaderboard_msg = f"🎉   🏅   🎉   🏅   🎉   🏅   🎉\n"
                leaderboard_msg += f"🏆🌟     活跃度排行榜     🌟🏆\n"
                leaderboard_msg += "━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"

                # 修改：从 start_index + 1 开始，确保排名连续
                for idx, (user_name, count) in enumerate(page_data, start=start_index + 1):
                    rank_emoji = {1: "🥇👤", 2: "🥈👤", 3: "🥉👤"}.get(idx, f"{idx}.👤")
                    leaderboard_msg += f"{rank_emoji} {user_name}  : {count} 次\n"
                    leaderboard_msg += "━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"

                leaderboard_msg += "🎉🏅  恭喜活跃群友上榜  🏅🎉\n"
                leaderboard_msg += "🎉   🏅   🎉   🏅   🎉   🏅   🎉"

                # 发送排行榜
                wcf.send_text(leaderboard_msg, msg.roomid)
                print(f"已发送活跃度排行榜第 {page_number} 页到分组 {msg.roomid}:\n{leaderboard_msg}")


            # 获取群排行榜数据  
            if msg.from_group() and msg.content == "/top" and msg.roomid in groups:
                roomid = msg.roomid
                leaderboard_data = r.get(f"leaderboard_{roomid}")

                if leaderboard_data:
                    rankings = json.loads(leaderboard_data)
                    
                    # 检查排行榜数据是否为空
                    if not rankings:
                        wcf.send_text("暂无排行榜数据，群友快快发金狗", roomid)
                        print(f"分组 {roomid} 的排行榜数据为空")
                        return  # 直接返回，避免后续逻辑
                    
                    # 只取前 10 名
                    top_10_rankings = rankings[:10]
                    
                    # 排行榜标题
                    leaderboard_msg = "🎉   🏅   🎉   🏅   🎉   🏅   🎉\n"
                    leaderboard_msg += "🏆🌟     Top10  排行榜    🌟🏆\n"
                    leaderboard_msg += "━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"
                    
                    for idx, entry in enumerate(top_10_rankings, start=1):
                        if idx == 1:
                            rank_emoji = "🥇👤"  # 第一名
                        elif idx == 2:
                            rank_emoji = "🥈👤"  # 第二名
                        elif idx == 3:
                            rank_emoji = "🥉👤"  # 第三名
                        else:
                            rank_emoji = f"{idx}.👤"  # 其他名次
                        
                        leaderboard_msg += (
                            f"{rank_emoji} {entry['caller_name']}\n"
                            f"   💰  {entry['tokenSymbol']}   🚀 {entry['ratio']:.2f}X\n"
                            f"━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"
                        )
                    # ━━━━━━━━━━━━━━
                    # 如果数据不足 10 条，添加提示信息
                    if len(top_10_rankings) < 10:
                        leaderboard_msg += "\n⚠️ 当前排行榜数据不足 10 条\n"
                    
                    # 排行榜底部装饰
                    leaderboard_msg += "🎉🏅   恭喜老板上榜   🏅🎉\n"
                    leaderboard_msg += "🎉   🏅   🎉   🏅   🎉   🏅   🎉"
                    
                    wcf.send_text(leaderboard_msg, roomid)
                    print(f"已发送排行榜到分组 {roomid}:\n{leaderboard_msg}")
                else:
                    wcf.send_text("暂无排行榜数据，群友快快发金狗", roomid)
                    print(f"暂无排行榜数据，群友快快发金狗")
                
            
            # 判断消息中是否包含ca信息
            sol_id, sol_ca = is_solca(msg.content)
            eths_id, eths_ca = is_eths(msg.content)
            print('zoudaozheli')
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
                    find_time_ms = int(time.time()*1000)
                    
                    url1 = "https://www.okx.com/priapi/v1/dx/market/v2/latest/info?chainId={}&tokenContractAddress={}".format(chain_id, ca_ca)
                    url2= "https://www.okx.com/priapi/v1/dx/market/v2/token/overview/?chainId={}&tokenContractAddress={}".format(chain_id, ca_ca)

                    # 发送GET请求
                    response1 = requests.get(url1)
                    response2 = requests.get(url2)

                    # 检查请求是否成功
                    if response1.status_code == 200 and response2.status_code == 200:
                        data1 = response1.json()  # 解析JSON响应
                        data2 = response2.json()  
                        # 获取合约基础信息
                        
                        chain_name = data1["data"]["chainName"]            
                        tokenSymbol = data1["data"]["tokenSymbol"]
                        tokenName = data1["data"]["tokenName"]
                        price = math_price(float(data1["data"]["price"])) if data1["data"]["price"] else '数据异常'
                        marketCap = math_km(float(data1["data"]["marketCap"])) if data1["data"]["price"] else '数据异常'
                        #circulatingSupply = data1["data"]["circulatingSupply"]
                        volume = math_km(float(data1["data"]["volume"])) if data1["data"]["price"] else '数据异常'
                        holders = data1["data"]["holders"] if data1["data"]["price"] else '数据异常'
                        top10HoldAmountPercentage = math_percent(float(data1["data"]["top10HoldAmountPercentage"]))             
                        total_holding_percentage  = '功能优化中'
                        roomid = msg.roomid
                        
                        #获取社交信息
                        twitter = data2["data"]["socialMedia"]["twitter"]                  
                        officialWebsite = data2["data"]["socialMedia"]["officialWebsite"]
                        telegram = data2["data"]["socialMedia"]["telegram"]
                        # 对社交信息进行验证
                        twitter_info = is_x(twitter) 
                        officialWebsite_info = is_web(officialWebsite)
                        telegram_info = is_TG(telegram)  


                        caller_wxid = msg.sender
                        chatroom_members = wcf.get_chatroom_members(roomid=roomid)
                        caller_simulate_name = chatroom_members[caller_wxid] if (chatroom_members and len(chatroom_members) > 1 )  else '数据暂时异常'
                        # 将caller喊单信息组装成模拟数据
                        ca_group_simulate_datas = [roomid,ca_ca]
                        redis_key = 'ca_group_simulate_datas'
                        ca_group_datas = get_data_from_redis(redis_key)
                        data_save = get_nested_data_from_redis(roomid = roomid,ca_ca = ca_ca)
                        # 判断该ca在当前群组是不是首次出现
                        if data_save :
                            # 如果是再次出现，则需要找到哨兵数据
                            print('该合约重复出现')
                            query_time = int(time.time()*1000)
                            ca_datas = get_nested_data_from_redis(roomid, ca_ca)
                            
                            caller_name = data_save["caller_name"]
                            find_time = data_save["find_time"]

                            timestamp_seconds = find_time / 1000
                            # 转换为 UTC 时间
                            utc_time = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
                            # 转换为北京时间（UTC+8）
                            beijing_time = utc_time + timedelta(hours=8)
                            # 格式化输出
                            find_time = beijing_time.strftime("%m-%d %H:%M:%S")

                            description = translate(data2["data"]['socialMedia']['description']) if data_save["description"] == '暂无叙事' else data_save["description"]                           
                            nowCap = float(data1["data"]["price"])*float(data1["data"]["circulatingSupply"])
                        
                            print(data_save)
                            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=14))
                            info = (
                            f"{ca_ca}\n"
                            f"简写：{tokenSymbol}\n"
                            f"名称：{tokenName}\n"
                            f"💰价格: {price}\n"
                            f"💹流通市值：{marketCap}\n"
                            f"📊交易量：{volume}\n"
                            f"🦸持有人: {holders}\n"
                            f"🐋top10持仓: {top10HoldAmountPercentage}\n"
                            f"🍭捆绑比例：{total_holding_percentage}\n\n"
                            f"{twitter_info[0]}{twitter_info[1]}{officialWebsite_info[0]}{officialWebsite_info[1]}{telegram_info[0]}{telegram_info[1]}\n"
                            f"🕵️哨兵：{caller_name}\n"
                            f"📈Call: {math_km(data_save['initCap'])} -> {math_km(data_save['topCap'])}\n"
                            f"🚀最大倍数: {str(round(data_save['topCap'] / data_save['initCap'], 2)) + 'X'}\n"
                            f"🔥当前倍数: {str(round(nowCap / float(data_save['initCap']), 2)) + 'X'}\n\n"
                            f"💬大致叙事: {description} {random_string}\n"
                            f"🎯发现时间：{find_time}"
                            )                            
                            wcf.send_text(info,msg.roomid)

                            timestamp_ms = int(time.time() * 1000)
                            time.sleep(1)
                            old_news_id =  getMyLastestGroupMsgID(keyword=random_string)  
                            print(old_news_id)
                            old_news.append([old_news_id,timestamp_ms])
                            print(info)
                        # 首次出现    
                        else:
                            description = translate(data2["data"]['socialMedia']['description']) if data2["data"]['socialMedia']['description'] else '暂无叙事'
                            caller_name = caller_simulate_name
                            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=14))
                            info = (
                            f"{ca_ca}\n"
                            f"链: {chain_name}\n"
                            f"简写：{tokenSymbol}\n"
                            f"名称：{tokenName}\n"
                            f"💰价格: {price}\n"
                            f"💹流通市值：{marketCap}\n"
                            f"📊交易量：{volume}\n"
                            f"🦸持有人: {holders}\n"
                            f"🐋top10持仓: {top10HoldAmountPercentage}\n\n"
                            f"{twitter_info[0]}{twitter_info[1]}{officialWebsite_info[0]}{officialWebsite_info[1]}{telegram_info[0]}{telegram_info[1]}\n"
                            f"🕵️哨兵：{caller_name}\n"
                            f"📈Call: {marketCap} -> {marketCap}\n"
                            f"🚀最大倍数: 1.00X\n"
                            f"🔥当前倍数: 1.00X\n\n"
                            f"💬大致叙事: {description if description else '暂无叙事'} {random_string}\n"
                            f"🎯发现时间：{find_time}"
                        )                   
                            wcf.send_text(info,msg.roomid)

                            timestamp_ms = int(time.time() * 1000)
                            time.sleep(1)
                            old_news_id =  getMyLastestGroupMsgID(keyword=random_string)  
                            print(old_news_id)
                            old_news.append([old_news_id,timestamp_ms])

                            store_nested_data_to_redis(roomid, ca_ca, tokenSymbol,caller_name, data1, description, find_time_ms)
                            data_save = get_nested_data_from_redis(roomid = roomid,ca_ca = ca_ca)
                            print(data_save)                          
                            print(info)      
                    
                    else:
                        print("请求失败，状态码:", response1.status_code)
                        print("请求失败，状态码:", response2.status_code)
                
            else:
                chain_id = None
                ca_ca = None      

        except Empty:
            continue
        except Exception as e:
            print(e)

    wcf.keep_running()



# 每5分钟更新top数据和最高倍数数据
def start_top_update():
    
    # 初始化全局 rankings 字典，用于存储每个群组的排行榜数据
    global_rankings = {roomid: [] for roomid in groups}

    while not stop_event.is_set():
        updata_time = math_bjtime()

        print('----{}----开始更新排行榜数据'.format(updata_time))
        time.sleep(3000)  # 300 秒 = 5 分钟
        for roomid in groups:
            # 获取该分组下的所有合约代币
            ca_data = r.hgetall(roomid)
            # print(ca_data)
            if not ca_data:
                continue

            # 获取上一次的排行榜数据
            rankings = global_rankings.get(roomid, [])

            for ca_ca, data_json in ca_data.items():
                data1 = json.loads(data_json)
                time.sleep(2)
                # 监测topcap数据是否创新高
                # 接口URL
                sol_id, sol_ca = is_solca(ca_ca)
                eths_id, eths_ca = is_eths(ca_ca)

                if sol_id :               
                    url = "https://www.okx.com/priapi/v1/dx/market/v2/latest/info?chainId={}&tokenContractAddress={}".format(sol_id,ca_ca)
                    # 发送GET请求
                    response = requests.get(url)

                else:
                    url = "https://www.okx.com/priapi/v1/dx/market/v2/latest/info?chainId={}&tokenContractAddress={}".format(eths_id,ca_ca)
                    response = requests.get(url)

                
               # 检查请求是否成功
                if response.status_code == 200:
                    print('开始检测----{}----的---{}----'.format(roomid,data1['tokenSymbol']))
                    data2 = response.json()  # 解析JSON响应
                    newCap = float(data2["data"]["price"]) * data1['circulatingSupply']
                    random_number = round(random.uniform(1.10, 1.20), 2)
                    if random_number * newCap > data1['topCap']:
                        ath_time = math_bjtime()
                        print('{}创新高,市值突破{}新高时间为{}'.format(data1['tokenSymbol'], random_number * newCap, ath_time))
                        data1['topCap'] = random_number * newCap
                        # 计算 topCap / initCap
                        ratio = data1['topCap'] / data1['initCap']
                        # 更新 Redis 中的数据
                        r.hset(roomid, ca_ca, json.dumps(data1))

                        # 更新 rankings 中的数据
                        # 查找是否已经存在该代币的数据
                        existing_entry = next((entry for entry in rankings if entry['tokenSymbol'] == data1['tokenSymbol']), None)
                        if existing_entry:
                            # 如果存在，更新 ratio
                            existing_entry['ratio'] = ratio
                        else:
                            # 如果不存在，添加新数据
                            rankings.append({
                                'tokenSymbol': data1['tokenSymbol'],
                                'caller_name': data1['caller_name'],
                                'ratio': ratio
                            })
                    else:
                        # 如果未创新高，直接使用已有的 ratio
                        ratio = data1['topCap'] / data1['initCap']
                        # 查找是否已经存在该代币的数据
                        existing_entry = next((entry for entry in rankings if entry['tokenSymbol'] == data1['tokenSymbol']), None)
                        if not existing_entry:
                            # 如果不存在，添加新数据
                            rankings.append({
                                'tokenSymbol': data1['tokenSymbol'],
                                'caller_name': data1['caller_name'],
                                'ratio': ratio
                            })
                else:
                    print("请求失败，状态码:", response.status_code)

            # 按 ratio 从高到低排序
            rankings.sort(key=lambda x: x['ratio'], reverse=True)

            # 更新全局 rankings 数据
            global_rankings[roomid] = rankings

            # 将排行榜数据存储到 Redis 中
            r.set(f"leaderboard_{roomid}", json.dumps(rankings))
            print(f"已更新分组 {roomid} 的排行榜数据")

            '''
                for i in range(len(data_list)):
                    if data1['query_time'] >= data_list[i]['times']:
                        pass
                    else:
                        print(ca_ca)
                        print(data_list[i]['price'])
                        print(data1['circulatingSupply'])
                        print(data_list[i]['price']*data1['circulatingSupply'])
                        
                        if data1['topCap'] >= data_list[i]['price']*data1['circulatingSupply']:
                            pass
                        else:
                            print('{}更新最高价,新高时间为｛｝'.format(data1['tokenSymbol'],convert_timestamp_to_beijing_time(data_list[i]['times'])))
                            data1['topCap'] = data_list[i]['price']*data1['circulatingSupply']  
                            # 计算 topCap / initCap
                            ratio = data1['topCap'] / data1['initCap']
                            rankings.append({
                            'tokenSymbol': data1['tokenSymbol'],
                            'caller_name': data1['caller_name'],
                            'ratio': ratio
                                })
                                # 更新 Redis 中的数据
                            r.hset(roomid, ca_ca, json.dumps(data1))
                            
                # 更新最新的查询时间            
                data1['query_time'] = data_list[-1]['times']  
                '''


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





    sql = """
    select * from MSG 
    where StrTalker = {} 
    and StrContent like {} 
    order by Sequence desc limit 1
    """.format(room_id, "%" + keyword + "%")
    msgs = wcf.query_sql("MSG0.db", sql)
    return msgs[0].get("MsgSvrID") if msgs else 0



def recover_message():
    while not stop_event.is_set():
        time.sleep(10)
        print('开始撤回消息')
        try:
            print(old_news)
            if len(old_news) > 0:
                # 反向遍历 old_news，避免删除元素影响索引
                for i in range(len(old_news) - 1, -1, -1):
                    timestamp_ms = int(time.time() * 1000)
                    if timestamp_ms - old_news[i][1] > 4000 and old_news[i] != 0 :  # 10000ms = 10秒  停留1分40秒
                        result = wcf.revoke_msg(old_news[i][0])
                        print('撤回消息{}'.format(result))
                        if result == 1:
                            del old_news[i]  # 删除已撤回的消息
        except Empty:
            continue
        except Exception as e:
            print(f"撤回消息时出错: {e}")





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

def sol_ca_job():
    while not stop_event.is_set():
        print('开始sol任务') 
        if len(sol_ca_jobs) > 0:
                # 反向遍历 sol_ca_jobs，避免删除元素影响索引
                for i in range(len(sol_ca_jobs) - 1, -1, -1):
                    time.sleep(1)
                    roomid = sol_ca_jobs[i][0].roomid
                    ca = sol_ca_jobs[i][1]

                    data1 = fetch_oke_latest_info(ca_ca = ca)
                    data2 = fetch_oke_overview_info(ca_ca = ca)
                    print('来到了这里1111')
                    print(data1)
                    print(data2)
                    # 检查请求是否成功
                    if data1 and data2 :
                        print('来到了这里2222')
                        # 获取合约基础信息
                        chain_name = data1["data"]["chainName"]            
                        tokenSymbol = data1["data"]["tokenSymbol"]
                        tokenName = data1["data"]["tokenName"]
                        price = math_price(float(data1["data"]["price"]))
                        marketCap = math_km(float(data1["data"]["marketCap"]))
                        circulatingSupply = data1["data"]["circulatingSupply"]
                        volume = math_km(float(data1["data"]["volume"]))
                        holders = data1["data"]["holders"]
                        top10HoldAmountPercentage = math_percent(float(data1["data"]["top10HoldAmountPercentage"]))  
                        
                        #获取捆绑信息
                        total_holding_percentage = '功能优化中'
                        # _, total_holding_percentage = get_bundles(address=ca_ca)         
                        
                        # 获取社交信息
                        twitter = data2["data"]["socialMedia"]["twitter"]                  
                        officialWebsite = data2["data"]["socialMedia"]["officialWebsite"]
                        telegram = data2["data"]["socialMedia"]["telegram"]
                        # 对社交信息进行验证
                        twitter_info = is_x(twitter) 
                        officialWebsite_info = is_web(officialWebsite)
                        telegram_info = is_TG(telegram)  
                        
                        # 获取池子创建时间
                        #先从raydium 获取时间
                        pool_create_time = get_pool_create_time(501, ca)
                        
                        if(pool_create_time == 0):
                            #无法从raydium 就获取代币创建时间表示pump
                            pool_create_time = data2["data"]["memeInfo"]["createTime"]
                            find_pool_create_time = '暂未发现'
                        
                        else:
                            dt_object = datetime.fromtimestamp(pool_create_time/1000)
                            find_pool_create_time = dt_object.strftime('%m-%d %H:%M:%S')  # 格式：年-月-日 时:分:秒
                         
                        print('拿到数据了1')
                        # 记录哨兵caller信息
                        # 先拿到当前caller的昵称                       
                        print(roomid)
                        # caller_wxid = sol_ca_jobs[i][0].sender
                        
                        chatroom_members = wcf.get_chatroom_members(roomid = roomid)
                        print('拿到数据了2')
                        print(chatroom_members)
                        """ caller_list = get_wx_info(roomid,ca)
                        for i in range(len(caller_list)):
                            diff = abs(caller_list[i]['times']- sol_ca_jobs[i][2] )
                            diff_seconds = diff/1000.0
                            if diff_seconds <=4 :
                               caller_simulate_name = caller_list[i]['wxNick']
                               break """
 
                        caller_simulate_name = caller_simulate_name if caller_simulate_name  else '数据暂时异常'
                        print('拿到数据了3')
                        # 将caller喊单信息组装成模拟数据
                        ca_group_simulate_datas = [roomid,sol_ca_jobs[i][1]]
                        redis_key = 'ca_group_simulate_datas'
                        ca_group_datas = get_data_from_redis(redis_key)
                        data_save = get_nested_data_from_redis(roomid = roomid,ca_ca = sol_ca_jobs[i][1])
                        
                        
                        # 判断该ca在当前群组是不是首次出现
                        if data_save :
                            # 如果是再次出现，则需要找到哨兵数据
                            print('该合约重复出现')
                            query_time = int(time.time()*1000)
                            ca_datas = get_nested_data_from_redis(roomid, sol_ca_jobs[i][1])
                            
                            caller_name = data_save["caller_name"]
                            find_time = data_save["find_time"]

                            timestamp_seconds = find_time / 1000
                            # 转换为 UTC 时间
                            utc_time = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
                            # 转换为北京时间（UTC+8）
                            beijing_time = utc_time + timedelta(hours=8)
                            # 格式化输出
                            find_time = beijing_time.strftime("%m-%d %H:%M:%S")

                            description = translate(data2["data"]['socialMedia']['description']) if data_save["description"] == '暂无叙事' else data_save["description"]                           
                            nowCap = float(data1["data"]["price"])*float(data1["data"]["circulatingSupply"])
                        
                            print(data_save)
                            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=14))

                            info = (
                            f"{sol_ca_jobs[i][1]}\n"
                            f"简写：{tokenSymbol}\n"
                            f"名称：{tokenName}\n"
                            f"💰价格: {price}\n"
                            f"💹流通市值：{marketCap}\n"
                            f"📊交易量：{volume}\n"
                            f"🦸持有人: {holders}\n"
                            f"🐋top10持仓: {top10HoldAmountPercentage}\n"
                            f"🍭捆绑比例：{total_holding_percentage}\n\n"
                            f"{twitter_info[0]}{twitter_info[1]}{officialWebsite_info[0]}{officialWebsite_info[1]}{telegram_info[0]}{telegram_info[1]}\n"
                            f"🕵️哨兵：{caller_name}\n"
                            f"📈Call: {math_km(data_save['initCap'])} -> {math_km(data_save['topCap'])}\n"
                            f"🚀最大倍数: {str(round(data_save['topCap'] / data_save['initCap'], 2)) + 'X'}\n"
                            f"🔥当前倍数: {str(round(nowCap / float(data_save['initCap']), 2)) + 'X'}\n\n"
                            f"💬大致叙事: {description} {random_string} \n"
                            f"🎯发现时间：{find_time}\n"
                            f"🎯创建时间：{find_pool_create_time}"
                            #f"{message_number}"
                            ) 
                                                       
                            wcf.send_text(info,sol_ca_jobs[i][0].roomid)
                            timestamp_ms = int(time.time() * 1000)
                            time.sleep(1)
                            old_news_id =  getMyLastestGroupMsgID(keyword=random_string)  
                            print(old_news_id)
                            old_news.append([old_news_id,timestamp_ms])
                            print(info)
                            
                            
                        # 首次出现    
                        else:
                            cp_time = '发射时间' if is_pump(sol_ca_jobs[i][1]) else '创建时间'
                            description = translate(data2["data"]['socialMedia']['description']) if data2["data"]['socialMedia']['description'] else '暂无叙事'
                            caller_name = caller_simulate_name
                            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=14))
                            info = (
                            f"{sol_ca_jobs[i][1]}\n"
                            f"简写：{tokenSymbol}\n"
                            f"名称：{tokenName}\n"
                            f"💰价格: {price}\n"
                            f"💹流通市值：{marketCap}\n"
                            f"📊交易量：{volume}\n"
                            f"🦸持有人: {holders}\n"
                            f"🐋top10持仓: {top10HoldAmountPercentage}\n"
                            f"🍭捆绑比例：{total_holding_percentage}\n\n"
                            f"{twitter_info[0]}{twitter_info[1]}{officialWebsite_info[0]}{officialWebsite_info[1]}{telegram_info[0]}{telegram_info[1]}\n"
                            f"🕵️哨兵：{caller_name}\n"
                            f"📈Call: {marketCap} -> {marketCap}\n"
                            f"🚀最大倍数: 1.00X\n"
                            f"🔥当前倍数: 1.00X\n\n"
                            f"💬大致叙事: {description if description else '暂无叙事'} {random_string}\n"
                            f"🎯发现时间：{sol_ca_jobs[i][2]}\n"
                            f"🎯{cp_time}:{find_pool_create_time}"
                            )                   
                            wcf.send_text(info,sol_ca_jobs[i][0].roomid)
                            timestamp_ms = int(time.time() * 1000)
                            time.sleep(1)
                            old_news_id =  getMyLastestGroupMsgID(keyword=random_string)  
                            print(old_news_id)
                            old_news.append([old_news_id,timestamp_ms])
                        
                            # 记录每个群组，每个合约，从被发现后，上涨的最大倍数
                            # 一条喊单记录   群组 ca 简写 喊单人 链 初始市值 最高市值 叙事 喊单时间， 最新查询时间，  单次查询到的数据为 供应量 和 价格序列                           
                            store_nested_data_to_redis(roomid, sol_ca_jobs[i][1], tokenSymbol,caller_name, data1, description, timestamp_ms)
                            data_save = get_nested_data_from_redis(roomid = roomid,ca_ca = sol_ca_jobs[i][1])
                            print(data_save)
                            #redis_key = "ca_group_simulate_datas_list"
                            #r.rpush(redis_key, *ca_group_simulate_datas)

                            #ca_datas[roomid][ca_ca] = {
                                #'caller_name':caller_name,
                                #'initCap':float(data1["data"]["marketCap"]),
                                #'topCap':float(data1["data"]["marketCap"]),
                                #'description':description,
                                #'find_time':find_time_ms,
                                #'query_time':find_time_ms}                                                       
                            print(info)
                                    
                        del sol_ca_jobs[i]
                    
        pass



# 启动更新top10的 的线程
# 启动所有线程
def start_all_tasks():
    
    # 启动微信监听线程
    wcf_listener_thread = threading.Thread(target=start_wcf_listener)
    wcf_listener_thread.start()

    # 启动sol合约查询任务的线程
    #sol_job_thread = threading.Thread(target=sol_ca_job)
    #sol_job_thread.start()

    # 启动排行榜更新线程
    #top_update_thread = threading.Thread(target=start_top_update)
    #top_update_thread.start()

    # 启动撤回消息的线程
    #recover_message_thread = threading.Thread(target=recover_message)
    #recover_message_thread.start()

    


    # 等待线程结束（如果需要的话）
    try:
        while True:
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        stop_event.set()
        wcf_listener_thread.join()
        #top_update_thread.join()
        #sol_job_thread.join()
        #recover_message_thread.join()
        print("已停止所有任务")






stop_event = threading.Event()  # 控制线程停止的事件
sol_ca_jobs = []

message_number = 1000000
wcf = Wcf()
old_news = []

r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# '53951514521@chatroom'
groups = ["58224083481@chatroom"]


start_all_tasks()

""" T = is_pump('FiUGrUV1mq2pyGjxMK3jpRed5CsuqX1QPzqZJpvJpump')
L = is_pump('XgJcy1kER1tLgM4mskd7UG3feJvTqtdDSkV3EXxpump')

print(T)
print(L) """