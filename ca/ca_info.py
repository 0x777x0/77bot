import re
import math
import pytz
import logging
import json
from common.cache import redis
import requests

from decimal import Decimal, getcontext
from datetime import datetime
from base58 import b58decode
from util.date_util import get_timestamp




def is_solca(content):
    # 合并多行文本为单行（去除所有换行符）
    #content = content.replace('\n', '')
    
    # Solana address regex, ensuring it's not prefixed with "0x" and not containing unwanted characters
    regex_sol = r"(?<!0x)(?<![a-zA-Z0-9])[1-9A-HJ-NP-Za-z]{32,44}(?![a-zA-Z0-9])"
    
    if content:
        matcher_sol = re.search(regex_sol, content)
        if matcher_sol:
            try:
                # Try decoding the address to check if it's a valid base58 encoded public key
                decoded_address = b58decode(matcher_sol.group())
                if len(decoded_address) == 32:
                    return 501, matcher_sol.group()  # Return Solana chain ID and address
            except ValueError as e:
                logging.error("get address error, content:%s, err:%s", content, e)
    
    return None, None

def is_eths(content):
    # 合并多行文本为单行（去除所有换行符）
    #content = content.replace('\n', '')
    # Ethereum address regex, matches "0x" followed by exactly 40 hexadecimal characters
    regex_sol = r"0x[a-fA-F0-9]{40}"
    
    if content:
        matcher = re.search(regex_sol, content)
        if matcher:
            try:
                return 56, matcher.group()  # Return Ethereum chain ID and address
            except ValueError as e:
                logging.error("get address error, content:%s, err:%s", content, e)
    
    return None, None
    
    
    
def math_price(content):
    
    if content < 1 :
        return f"{content:.8f}"
    else :
        return round(content, 8 - int(math.floor(math.log10(abs(content)))) - 1)
    
def math_cex_price(content):
    
    if content < 1 :
        return f"{content:.6f}"
    else :
        return round(content, 8 - int(math.floor(math.log10(abs(content)))) - 1)
        
def math_km(content):
    
    if  content < 1000:
        return content
    elif  1000 <=  content < 1000000:
        texted = content/1000
        return str(f"{texted:.2f}")+"K"
    else:
        texted = content/1000000
        return str(f"{texted:.2f}")+"M"
    
def math_percent(content):
   
    return str(f"{content:.2f}")+"%"
    

def math_bjtime():
    
    now_utc = datetime.now(pytz.utc)

    # 转换为北京时间（东八区）
    beijing_time = now_utc.astimezone(pytz.timezone("Asia/Shanghai"))

    # 格式化为 "02-18 23:33:08" 的格式
    formatted_time = beijing_time.strftime("%m-%d %H:%M:%S")   
    
    return formatted_time


def is_cexToken(text):
    """
    检查文本是否是 /+字母或数字的组合（不区分大小写），且总长度不超过 15 位。

    :param text: 要检查的文本
    :return: 如果匹配返回 True,否则返回 False
    """
    pattern = r'^/[a-zA-Z0-9]{1,14}$'  # 正则表达式模式
    return bool(re.match(pattern, text))
    
def is_pump(address):
    # true 就是在内盘 false 外盘
    url = f"https://api.quickcar.io/sol/api/getPump?address={address}"
    
    # 发送 GET 请求
    response = requests.get(url)

    # 获取响应内容
    value = response.text

    # 如果返回为空，直接返回
    if not value:
        return False
    
    data = json.loads(value)  # 将响应内容转换为字典
    externalMarket = data.get("data").get("externalMarket")
    return externalMarket


def get_bundles(address):
    """
    获取指定 address 的 bundle 信息。

    :param address: 要查询的地址
    :return: 如果成功，返回 (total_percentage_bundled, total_holding_percentage)；如果失败，返回 None。
    """
    url = f"https://trench.bot/api/bundle/bundle_advanced/{address}"
    redis_key = f"sol:bundles:{address}"
    data = redis.get(redis_key)

    # 检查 Redis 缓存
    if data:
        cached_values = data.split(",")
        total_percentage_bundled = cached_values[0]
        total_holding_percentage = cached_values[1]
        return float(total_percentage_bundled), float(total_holding_percentage)

    try:
        # 发送 API 请求
        start = get_timestamp()
        logging.debug("获取 bundle 信息,address: %s", address)
        response = requests.get(url, timeout=7)  # 设置超时时间
        logging.debug("监控 ===> get_bundles, 耗时: %s", get_timestamp() - start)

        if response.status_code == 200:
            data = response.json()
            total_percentage_bundled = round(data['total_percentage_bundled'], 2)
            total_holding_percentage = round(data['total_holding_percentage'], 2)
            logging.debug("获取 bundle 信息成功,address: %s, data: %s", address, data)

            # 缓存结果到 Redis
            redis.set(redis_key, f"{total_percentage_bundled},{total_holding_percentage}", ex=60 * 5)
            return total_percentage_bundled, total_holding_percentage
        else:
            logging.error("请求 bundles 失败,address: %s, status_code: %s, response: %s", address, response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        logging.error("API 请求失败,address: %s, 错误信息: %s", address, str(e))
    except ValueError as e:
        logging.error("JSON 解析失败,address: %s, 错误信息: %s", address, str(e))
    except Exception as e:
        logging.error("请求 bundles 过程中发生未知错误,address: %s, 错误信息: %s", address, str(e), exc_info=True)

    return None




