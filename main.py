import functools

from wcferry import Wcf
from queue import Empty
from ca.ca_info import is_solca, is_eths, math_price,math_km,math_percent,math_bjtime
from common.socialMedia_info import is_x, is_web, is_TG
from common.translate import translate

import re
import requests

groups = ["47836900220@chatroom","43449134530@chatroom","50189478867@chatroom",
"43394429151@chatroom","47598301997@chatroom","45591905909@chatroom","57408201119@chatroom",
"48020994456@chatroom","43420738257@chatroom","49280501224@chatroom","58026200405@chatroom",
"52643323891@chatroom","57683690853@chatroom","56941492148@chatroom","53229125057@chatroom"]
ca_datas = {}
ca_group_datas = []

wcf = Wcf()

wcf.enable_receiving_msg()

while wcf.is_receiving_msg():
    try:
        print('机器人启动')
        msg = wcf.get_msg()
        
        # 判断消息中是否包含ca信息
        sol_id, sol_ca = is_solca(msg.content)
        eths_id, eths_ca = is_eths(msg.content)
        
        # 判断ca属于哪条链
        if bool(sol_id):
            chain_id = sol_id
            ca_ca = sol_ca
            print('发现sol合约')
        elif bool(eths_id):
            chain_id = eths_id
            ca_ca = eths_ca
            print('发现eths合约')
        else:
            chain_id = None
            ca_ca = None
            
               
        if msg.content == "滚kkkkkkkkkkk":
            wcf.send_text("好的，小瓜瓜，爱你爱你哦,周末一起玩",msg.sender)
            
        if msg.content == "时间llllllllll":
            wcf.send_text("你好，宇哥，现在时间是："+ math_bjtime(),msg.sender)
            
        if msg.from_group() and msg.content == "id":
            # wcf.send_text(msg.roomid,msg.roomid)
            groups.append()
            print(msg.roomid) 
        
        # 判断是否在监听的指定群组中接收到sol合约信息，并进行操作   
        if msg.from_group() and chain_id and msg.roomid in groups:   
            
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
    
                # 如何是sol链ca，则获取社交信息
                
                if sol_id : 
                    twitter = data2["data"]["socialMedia"]["twitter"]                  
                    officialWebsite = data2["data"]["socialMedia"]["officialWebsite"]
                    telegram = data2["data"]["socialMedia"]["telegram"]
                    # 对社交信息进行验证
                    twitter_info = is_x(twitter) 
                    officialWebsite_info = is_web(officialWebsite)
                    telegram_info = is_TG(telegram)                   
                    description = translate(data2["data"]['socialMedia']['description']) if data2["data"]['socialMedia']['description'] else '暂无叙事'

                    # 记录哨兵caller信息
                    # 先拿到当前caller的昵称
                    roomid = msg.roomid
                    caller_wxid = msg.sender
                    chatroom_members = wcf.get_chatroom_members(roomid = roomid)
                    caller_simulate_name = chatroom_members[caller_wxid]
                    # 将caller喊单信息组装成模拟数据
                    ca_group_simulate_datas = [ca_ca,roomid]
                    # 判断该ca在当前群组是不是首次出现
                
                    if ca_group_simulate_datas in ca_group_datas:
                        # 如果不是首次出现，则需要找到哨兵数据
                        
                        caller_name = ca_datas[roomid][ca_ca]["caller_name"]
                        find_time = ca_datas[roomid][ca_ca]["find_time"]

                        





                        info = f"""
                        {ca_ca}
                        链: {chain_name}
                        简写：{tokenSymbol}
                        名称：{tokenName}
                        💰价格: {price}
                        💹流通市值：{marketCap}
                        📊交易量：{volume}
                        🦸持有人: {holders}
                        🐋top10持仓:{top10HoldAmountPercentage}

                        {twitter_info[0]}{twitter_info[1]}{officialWebsite_info[0]}{officialWebsite_info[1]}{telegram_info[0]}{telegram_info[1]}
                        🕵️哨兵：{caller_name}
                        📈Call: {ca_datas[roomid][ca_ca]["initCap"]} -> {ca_datas[roomid][ca_ca]["topCap"]}
                        🚀最大倍数:{str(round(ca_datas[roomid][ca_ca]["topCap"]/ca_datas[roomid][ca_ca]["initCap"],2))+'X'}
                        🔥当前倍数:{str((round(price*circulatingSupply)/ca_datas[roomid][ca_ca]["initCap"],2))+'X'}

                        💬大致叙事: {description if description else "暂无叙事"}

                        🎯发现时间：{find_time}
"""                             
                        wcf.send_text(info,msg.roomid)
                        print(info)
                    # 首次出现    

                    else:
                        caller_name = caller_simulate_name
                        info = f"""
                        {ca_ca}
                        链: {chain_name}
                        简写：{tokenSymbol}
                        名称：{tokenName}
                        💰价格: {price}
                        💹流通市值：{marketCap}
                        📊交易量：{volume}
                        🦸持有人: {holders}
                        🐋top10持仓:{top10HoldAmountPercentage}

                        {twitter_info[0]}{twitter_info[1]}{officialWebsite_info[0]}{officialWebsite_info[1]}{telegram_info[0]}{telegram_info[1]}

                        🕵️哨兵：{caller_name}
                        📈Call: {marketCap} -> {marketCap}
                        🚀最大倍数:1.00X
                        🔥当前倍数:1.00X

                        💬大致叙事: {description if description else "暂无叙事"}
                        🎯发现时间：{find_time}
"""                    
                        wcf.send_text(info,msg.roomid)
                        # 记录每个群组，每个合约，从被发现后，上涨的最大倍数
                        # 一条喊单记录   群组 ca 喊单人 链 初始市值 最高市值  喊单时间， 最新查询时间，  单次查询到的数据为 供应量 和 价格序列

                        ca_datas[roomid][ca_ca] = {
                            'caller_name':caller_name,
                            'initCap':float(data1["data"]["marketCap"]),
                            'topCap':float(data1["data"]["marketCap"]),
                            'find_time':find_time,
                            'query_time':find_time}     
                                     
                        ca_group_datas.append(ca_group_simulate_datas)
                        print(info)
                else:
                    
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
                                info = f"""
                                {ca_ca}
                                链: {chain_name}
                                简写：{tokenSymbol}
                                名称：{tokenName}
                                💰价格: {price}
                                💹流通市值：{marketCap}
                                📊交易量：{volume}
                                🦸持有人: {holders}
                                🐋top10持仓：{top10HoldAmountPercentage}

                                {twitter_info[0]}{twitter_info[1]}{officialWebsite_info[0]}{officialWebsite_info[1]}{telegram_info[0]}{telegram_info[1]}

                                🕵️哨兵：{caller_name}

                                💬大致叙事: {description if description else "暂无叙事"}

                                🎯发现时间：{find_time}
                                """                                
                                wcf.send_text(info,msg.roomid)
                                print(info)
                    # 首次出现    
                    else:
                        caller_name = caller_simulate_name
                        info = f"""
                        {ca_ca}
                        链: {chain_name}
                        简写：{tokenSymbol}
                        名称：{tokenName}
                        💰价格: {price}
                        💹流通市值：{marketCap}
                        📊交易量：{volume}
                        🦸持有人: {holders}
                        🐋top10持仓:{top10HoldAmountPercentage}

                        {twitter_info[0]}{twitter_info[1]}{officialWebsite_info[0]}{officialWebsite_info[1]}{telegram_info[0]}{telegram_info[1]}

                        🕵️哨兵：{caller_name}
                        📈Call: {marketCap} -> {marketCap}
                        🚀最大倍数:1.00X
                        🔥当前倍数:1.00X

                        💬大致叙事: {description if description else "暂无叙事"}
                        🎯发现时间：{find_time}
                        """                    
                        wcf.send_text(info,msg.roomid)
                        caller_simulate_data = [ca_ca,roomid,caller_simulate_name,float(data1["data"]["marketCap"]),find_time]
                        ca_datas.append(caller_simulate_data)
                        ca_group_datas.append(ca_group_simulate_datas)
                        print(info)      
            
            else:
                print("请求失败，状态码:", response1.status_code)
                print("请求失败，状态码:", response2.status_code)

        
                
    except Empty:
        continue
    except Exception as e:
        print(e)
        
wcf.keep_running()