from wcferry import Wcf
from queue import Empty
from ca.ca_info import is_solca, is_eths, math_price, math_cex_price, math_cex_priceChangePercent, math_km, math_percent, math_bjtime, get_bundles, is_cexToken, is_pump
from httpsss.oke import fetch_oke_latest_info, fetch_oke_overview_info
from httpsss.onchain import get_price_onchain, send_person_ca, get_ca_by_wxid
from common.socialMedia_info import is_x, is_web, is_TG
from common.translate import translate
from datetime import datetime, timedelta, timezone
from common.bjTime import convert_timestamp_to_beijing_time
from ca.exchange import get_exchange_price
from ca.redis_method import get_from_redis_list
# from common.cache import redis
from save_data import get_wx_info, get_wx_info_v2, add_wx_info_v2
from wcwidth import wcswidth

import configparser
import threading
import functools
import re
import requests
import time
import json
import redis
import random
import string
import logging




""" if msg.from_group() and msg.content == "id" :
                # wcf.send_text(msg.roomid,msg.roomid)                
                print(msg.roomid)  """


def command_id(wcf, msg):

    if msg.from_group and msg.content == "id850" :
        wcf.send_text(msg.roomid,msg.roomid)   
        time.sleep(0.2)             
        print(msg.roomid) 
    

def command_cextoken(wcf, msg, groups):
    
    if msg.from_group() and is_cexToken(msg.content) and msg.content!= '/top' and msg.roomid in groups :
                
                token_symble = msg.content[1:]
                token_price, token_priceChangePercent = get_exchange_price(token_symble)
                print(type(token_price))

                if float(token_price) > 0 :
                    token_price = float(token_price)
                    token_price = math_cex_price(token_price)
                    token_priceChangePercent = float(token_priceChangePercent)
                    token_priceChangePercent = math_cex_priceChangePercent(token_priceChangePercent)
                    print('{}当前的price为:{}'.format(token_symble,token_price)) 
                    wcf.send_text('{}: {} ({})'.format(token_symble,token_price,token_priceChangePercent),msg.roomid)


def command_leaderboard_ca(wcf, msg, groups):
            
    r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)        
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
        else:
            wcf.send_text("暂无排行榜数据，群友快快发金狗", roomid)
            print(f"暂无排行榜数据，群友快快发金狗")


def format_leaderboard_entry(prefix, token_symbol, multiple, address, init_value, highest_value, time):
    # 定义固定总长度（以显示宽度为单位）
    total_width = 33

    # 计算当前内容的显示宽度（包括前缀、token_symbol 和 multiple）
    content = f"{prefix} {token_symbol} 🚀{multiple}"
    content_width = wcswidth(content)

    # 计算需要的空格数量
    space_count = max(0, total_width - content_width)

    # 生成空格
    spaces = " " * space_count

    # 格式化字符串
    formatted_text = (
        f"{prefix} {token_symbol}{spaces}🚀{multiple}\n"
        f"#{address}\n"
        f"📈Call: {init_value} >> {highest_value} \n"
        f"🎯发现时间: {time}\n"
        f"━    ━    ━    ━    ━    ━    ━\n"
    )

    return formatted_text


def command_person_record(wcf, msg, groups):
    
    if msg.from_group() and msg.roomid in groups:
        text = msg.content

        if text.startswith('战绩'):
            # 使用 split 方法分割文本，取 @ 之后的部分
            content = text.split('绩', 1)[1].strip()  # 去除空白字符
            print(f"content: {content}, type: {type(content)}, length: {len(content)}")
            roomid = msg.roomid
            chatrooms_member = get_from_redis_list()
            print(chatrooms_member)
            for index, item in enumerate(chatrooms_member):
                if item.get('roomId') == roomid:
                    print('发现相同')
                    members = item.get('chatroomMembers')
                    print(members)
                    for key, value in members.items():
                        value = value.strip()  # 去除空白字符
                        print(f"value: {value}, type: {type(value)}, length: {len(value)}")
                        if value == content:
                            print('发现相同昵称')
                            wxid = key
                            print(wxid)
                            nickname = content
                            data = get_ca_by_wxid(wxid)
                            data = data['data']
                            keys_to_remove = ['wxId', 'chain', 'initPrice', 'highestPrice', 'circulation']
                            # 遍历列表中的每个字典
                            for item in data:
                                for key in keys_to_remove:
                                    item.pop(key, None)  # 使用 pop() 移除键，如果键不存在则忽略
             
                            # 遍历数据列表
                            for item in data:
                                # 格式化 initMarketValue 和 highestMarketValue
                                item['initMarketValue'] = math_km(item['initMarketValue'])
                                item['highestMarketValue'] = math_km(item['highestMarketValue'])
                                
                                # 格式化 findTime
                                timestamp_seconds = item['findTime'] / 1000
                                # 转换为 UTC 时间
                                utc_time = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
                                # 转换为北京时间（UTC+8）
                                beijing_time = utc_time + timedelta(hours=8)
                                # 格式化输出
                                item['findTime'] = beijing_time.strftime("%m-%d %H:%M:%S")
                            
                            # 只取前 10 条数据
                            top_10_data = data[:7]

                            # 生成排行榜文本
                            def generate_leaderboard(data):
                                leaderboard_text = "🏅        🎉        🏅        🎉        🏅\n"
                                leaderboard_text += data[0]['wxNick'] + " 个人战绩\n"
                                leaderboard_text +=  "\n"
                                leaderboard_text += "━    ━    ━    ━    ━    ━    ━\n"

                                if len(data) == 0:
                                    leaderboard_text += "当前排行榜数据不足 7 条\n"
                                    #leaderboard_text += "🏅   恭喜老板上榜   🏅\n"
                                    leaderboard_text += "🏅   🎉    🏅    🎉   🏅\n"
                                    return leaderboard_text

                                # 奖牌和序号
                                medals = ["🥇", "🥈", "🥉"]  # 前 3 名
                                numbers = ['4.', '5.', "6.", "7.", "8.", "9.", "10."]  # 第 4-10 名

                                for index, item in enumerate(data):
                                    if index < 3:
                                        prefix = medals[index]  # 前 3 名使用奖牌
                                    elif index < 7:
                                        prefix = numbers[index - 3]  # 第 4-10 名使用数字序号
                                    else:
                                        break  # 只处理前 10 条数据

                                    token_symbol = item['symbol'] 
                                    init_value = item['initMarketValue']
                                    highest_value = item['highestMarketValue']
                                    multiple = f"{item['highestMultiple']:.2f}X"
                                    time = item['findTime']

                                    # 格式化每一行
                                    formatted_text = format_leaderboard_entry(
                                        prefix=prefix,
                                        token_symbol=token_symbol,
                                        multiple=multiple,
                                        address=item['address'],
                                        init_value=init_value,
                                        highest_value=highest_value,
                                        time=time
                                    )


                                    leaderboard_text += formatted_text 

                                if len(data) < 7:
                                    leaderboard_text += "当前排行榜数据不足 7 条\n"
                                    
                                
                                # 排行榜底部装饰
                                leaderboard_text += "🎉🏅   恭喜老板拿大结果   🏅🎉\n"
                                leaderboard_text += "🎉   🏅   🎉   🏅   🎉   🏅   🎉"

                                return leaderboard_text

                            # 生成排行榜
                            leaderboard = generate_leaderboard(top_10_data)

                            # 打印排行榜
                            print(leaderboard)

                            # 发送到群组的逻辑（假设有一个 send_to_group 函数）
                            wcf.send_text(leaderboard, roomid)






""" def talk_times(wcf, msg, groups):

    r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)        

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
        r.hincrby(redis_key, user_wxid, 1)  # 每次发言增加1 """


""" if msg.from_group() and msg.content.startswith("/活跃") and msg.roomid in groups:
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
                print(f"已发送活跃度排行榜第 {page_number} 页到分组 {msg.roomid}:\n{leaderboard_msg}") """