import re
import math
import pytz
import logging

from decimal import Decimal, getcontext
from datetime import datetime
from base58 import b58decode




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

    # 格式化为 "2025-02-18 23:33:08" 的格式
    formatted_time = beijing_time.strftime("%m-%d %H:%M:%S")   
    
    return formatted_time
    
  





