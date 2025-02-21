
from wcferry import Wcf
from queue import Empty
from ca.ca_info import is_solca, is_eths, math_price, math_km, math_percent, math_bjtime, get_bundles
from common.socialMedia_info import is_x, is_web, is_TG
from common.translate import translate
from queue import Empty
from datetime import datetime, timedelta, timezone
from common.bjTime import convert_timestamp_to_beijing_time
# from common.cache import redis

import threading
import functools
import re
import requests
import time
import json
import redis

stop_event = threading.Event()  # 控制线程停止的事件

# 将ca_datas 数据以嵌套字典形式存到 redis 的方法
def store_nested_data_to_redis(roomid, ca_ca, tokenSymbol,caller_name, data1, description, find_time_ms):
    # 准备数据
    data = {
    'tokenSymbol':tokenSymbol,
    'caller_name': caller_name,
    'initCap': float(data1["data"]["marketCap"]) , 
    'topCap': float(data1["data"]["marketCap"]) , 
    'circulatingSupply':float(data1["data"]["circulatingSupply"]),
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
    wcf = Wcf()
    wcf.enable_receiving_msg()
    print('机器人启动')

    while wcf.is_receiving_msg():
        try:
            msg = wcf.get_msg()
            # 处理消息的逻辑...
            if msg.content == "滚kkkkkkkkkkk":
                wcf.send_text("好的，小瓜瓜，爱你爱你哦,周末一起玩",msg.sender)
            
            if msg.content == "时间llllllllll":
                wcf.send_text("你好，宇哥，现在时间是："+ math_bjtime(),msg.sender)
                
            if msg.from_group() and msg.content == "id":
                # wcf.send_text(msg.roomid,msg.roomid)
                
                print(msg.roomid) 
                
            if msg.from_group() and msg.content == "/top":
                roomid = msg.roomid
                leaderboard_data = r.get(f"leaderboard_{roomid}")
            
                if leaderboard_data:
                    rankings = json.loads(leaderboard_data)
                    leaderboard_msg = f"📊 24h Top10排行榜 📊\n"
                    for idx, entry in enumerate(rankings, start=1):
                        leaderboard_msg += (
                            f"{idx}. {entry['caller_name']}\n "
                            f" 🎯{entry['tokenSymbol']}=>"
                            f": {entry['ratio']:.2f}X\n"
                        )
                    wcf.send_text(leaderboard_msg, roomid)
                    print(f"已发送排行榜到分组 {roomid}:\n{leaderboard_msg}")
                else:
                    wcf.send_text("暂无排行榜数据", roomid)
                
            
            # 判断消息中是否包含ca信息
            sol_id, sol_ca = is_solca(msg.content)
            eths_id, eths_ca = is_eths(msg.content)

            # 判断ca属于哪条链
            if sol_id :
                chain_id = sol_id
                ca_ca = sol_ca           
                if msg.from_group() and msg.roomid in groups:
                    print('发现sol合约,开始查询ca信息')     
                    find_time = math_bjtime()
                    find_time_ms = int(time.time()*1000)
                    
                    url1 = "https://www.okx.com/priapi/v1/dx/market/v2/latest/info?chainId={}&tokenContractAddress={}".format(chain_id, ca_ca)
                    url2= "https://www.okx.com/priapi/v1/dx/market/v2/token/overview/?chainId={}&tokenContractAddress={}".format(chain_id, ca_ca)      
                    url3 = "http://47.238.165.188:8080/api/price/get?chain=sol&address={}".format(ca_ca)
                        

                    # 发送GET请求
                    response1 = requests.get(url1)
                    response2 = requests.get(url2)
                    response3 = requests.get(url3)

                    # 检查请求是否成功
                    if response1.status_code == 200 and response2.status_code == 200 and response3.status_code == 200:
                        data1 = response1.json()  # 解析JSON响应
                        data2 = response2.json()
                        data3 = response3.json()  
                        
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
                        

                        # 记录哨兵caller信息
                        # 先拿到当前caller的昵称
                        roomid = msg.roomid
                        caller_wxid = msg.sender
                        chatroom_members = wcf.get_chatroom_members(roomid = roomid)
                        caller_simulate_name = chatroom_members[caller_wxid]
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
                            f"💬大致叙事: {description}\n"
                            f"🎯发现时间：{find_time}"
                            )                            
                            wcf.send_text(info,msg.roomid)
                            print(info)
                            
                            
                        # 首次出现    
                        else:
                            description = translate(data2["data"]['socialMedia']['description']) if data2["data"]['socialMedia']['description'] else '暂无叙事'
                            caller_name = caller_simulate_name
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
                            f"📈Call: {marketCap} -> {marketCap}\n"
                            f"🚀最大倍数: 1.00X\n"
                            f"🔥当前倍数: 1.00X\n\n"
                            f"💬大致叙事: {description if description else '暂无叙事'}\n"
                            f"🎯发现时间：{find_time}"
                            )
                    
                            wcf.send_text(info,msg.roomid)
                        
                            # 记录每个群组，每个合约，从被发现后，上涨的最大倍数
                            # 一条喊单记录   群组 ca 简写 喊单人 链 初始市值 最高市值 叙事 喊单时间， 最新查询时间，  单次查询到的数据为 供应量 和 价格序列
                            
                            store_nested_data_to_redis(roomid, ca_ca, tokenSymbol,caller_name, data1, description, find_time_ms)
                            data_save = get_nested_data_from_redis(roomid = roomid,ca_ca = ca_ca)
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
                                    
                    else:
                        print("请求失败，状态码:", response1.status_code)
                        print("请求失败，状态码:", response2.status_code)
                        print("请求失败，状态码:", response3.status_code)       
                
            elif eths_id:
                chain_id = eths_id
                ca_ca = eths_ca
                print('发现eths合约')
                
                if msg.from_group()  and msg.roomid in groups:   
                
                    print("开始查询ca信息")      
                    find_time = math_bjtime()
                    
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
                        price = math_price(float(data1["data"]["price"]))
                        marketCap = math_km(float(data1["data"]["marketCap"]))
                        circulatingSupply = data1["data"]["circulatingSupply"]
                        volume = math_km(float(data1["data"]["volume"]))
                        holders = data1["data"]["holders"]
                        top10HoldAmountPercentage = math_percent(float(data1["data"]["top10HoldAmountPercentage"]))             
                                    
                        roomid = msg.roomid
                        caller_wxid = msg.sender
                        chatroom_members = wcf.get_chatroom_members(roomid=roomid)
                        caller_simulate_name = chatroom_members[caller_wxid]
                        # 将caller喊单信息组装成模拟数据
                        ca_group_simulate_datas = [ca_ca,roomid]
                        # 判断该ca在当前群组是不是首次出现
                    
                        if ca_group_simulate_datas in ca_group_datas:
                            
                            for i in range(len(ca_datas)):
                                if [ca_datas[i][0],ca_datas[i][1]] != ca_group_simulate_datas:
                                    pass
                                else:
                                    caller_name = ca_datas[i][2]
                                    find_time = ca_datas[i][-1]
                                    info = (
                                    f"{ca_ca}\n"
                                    f"链: {chain_name}\n"
                                    f"简写：{tokenSymbol}\n"
                                    f"名称：{tokenName}\n"
                                    f"💰价格: {price}\n"
                                    f"💹流通市值：{marketCap}\n"
                                    f"📊交易量：{volume}\n"
                                    f"🦸持有人: {holders}\n"
                                    f"🐋top10持仓：{top10HoldAmountPercentage}\n\n"
                                    f"{twitter_info[0]}{twitter_info[1]}{officialWebsite_info[0]}{officialWebsite_info[1]}{telegram_info[0]}{telegram_info[1]}\n"
                                    f"🕵️哨兵：{caller_name}\n\n"
                                    f"💬大致叙事: {description if description else '暂无叙事'}\n\n"
                                    f"🎯发现时间：{find_time}"
                                )                               
                                    wcf.send_text(info,msg.roomid)
                                    print(info)
                        # 首次出现    
                        else:
                            caller_name = caller_simulate_name
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
                            f"💬大致叙事: {description if description else '暂无叙事'}\n"
                            f"🎯发现时间：{find_time}"
                        )                   
                            wcf.send_text(info,msg.roomid)
                            caller_simulate_data = [ca_ca,roomid,caller_simulate_name,float(data1["data"]["marketCap"]),find_time]
                            ca_datas.append(caller_simulate_data)
                            ca_group_datas.append(ca_group_simulate_datas)
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
    print('开始更新排行榜数据')
    while not stop_event.is_set():
        time.sleep(30)  # 300 秒 = 5 分钟
        for roomid in groups:
            # 获取该分组下的所有合约代币
            ca_data = r.hgetall(roomid)
            print(ca_data)
            if not ca_data:
                continue
           
            # 更新 topCap 并计算 topCap / initCap
            rankings = []
            for ca_ca, data_json in ca_data.items():
                data1 = json.loads(data_json)
                time.sleep(1)
                # 监测topcap数据是否创新高
                # 接口URL
                #url = "http://47.238.165.188:8080/api/price/get?chain=sol&address={}".format(ca_ca)
                url = "https://www.okx.com/priapi/v1/dx/market/v2/latest/info?chainId=501&tokenContractAddress={}".format(ca_ca)

                # 发送GET请求
                response = requests.get(url)

                # 检查请求是否成功
                if response.status_code == 200:
                    data2 = response.json()  # 解析JSON响应
                    newCap = float(data2["data"]["price"])*data1['circulatingSupply']
                    if 1.2*newCap > data1['topCap']:
                        ath_time = math_bjtime()
                        print('{}创新高,市值突破{}新高时间为{}'.format(data1['tokenSymbol'],1.2*newCap,ath_time))
                        data1['topCap'] = 2*newCap
                        # 计算 topCap / initCap
                        ratio = data1['topCap'] / data1['initCap']
                        rankings.append({
                        'tokenSymbol': data1['tokenSymbol'],
                        'caller_name': data1['caller_name'],
                        'ratio': ratio
                            })
                            # 更新 Redis 中的数据
                        r.hset(roomid, ca_ca, json.dumps(data1))
                    #print(data2)
                    #data_list = data2['data']
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
                else:
                    print("请求失败，状态码:", response.status_code)
                
                if rankings:
                    pass
                else:
                    # 计算 topCap / initCap
                    ratio = data1['topCap'] / data1['initCap']
                    rankings.append({
                        'tokenSymbol': data1['tokenSymbol'],
                        'caller_name': data1['caller_name'],
                        'ratio': ratio
                    })
                    # 更新 Redis 中的数据
                    r.hset(roomid, ca_ca, json.dumps(data1))
     
            # 按 ratio 从高到低排序
            rankings.sort(key=lambda x: x['ratio'], reverse=True)

            # 将排行榜数据存储到 Redis 中
            r.set(f"leaderboard_{roomid}", json.dumps(rankings))
            print(f"已更新分组 {roomid} 的排行榜数据")


# 启动更新top10的 的线程
# 启动所有线程
def start_all_tasks():
    # 启动微信监听线程
    wcf_listener_thread = threading.Thread(target=start_wcf_listener)
    wcf_listener_thread.start()

    # 启动排行榜更新线程
    top_update_thread = threading.Thread(target=start_top_update)
    top_update_thread.start()

    # 等待线程结束（如果需要的话）
    try:
        while True:
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        stop_event.set()
        wcf_listener_thread.join()
        top_update_thread.join()
        print("已停止所有任务")




r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# '53951514521@chatroom'
groups = ["51641835076@chatroom",'52173635194@chatroom']
#ca_datas = {}
#ca_group_datas = []

start_all_tasks()