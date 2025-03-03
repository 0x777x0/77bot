import requests
import json
import time
from common.cache import redis

#这里添加代理 不然请求redis 很慢
proxies = {
    'http': 'http://localhost:10010',
}

binance_symbols_set_key = 'binance_symbols_set'


def get_binance_price(symbol):
    start_time = time.time()  # 记录开始时间
    upper_symbol = symbol.upper()

    print(f"开始获取价格: {upper_symbol}")
    
    # 判断是否存在，如果不存在直接返回0
    if not is_binance_symbol(upper_symbol):
        print(f"{upper_symbol} 不在缓存中，返回 0")
        return 0
    
    # 获取价格之前，先记录时间
    exchange_info_end_time = time.time()
    # https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT
    # url = f"https://api.binance.com/api/v3/ticker/price?symbol={upper_symbol}USDT"
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={upper_symbol}USDT"

    # 发送 GET 请求
    response = requests.get(url, proxies=proxies)
    print(f"请求 {url} 耗时: {time.time() - exchange_info_end_time:.2f} 秒")
    
    # 获取响应内容
    value = response.text
    print(f"返回数据：{value[:100]}...")  # 仅输出前100个字符，防止过长

    # 如果返回为空，直接返回
    if not value:
        print("返回数据为空，返回 0")
        return 0
    
    data = json.loads(value)  # 将响应内容转换为字典
    priceChangePercent = data.get("priceChangePercent");
    price = data.get("lastPrice")
    print(f"获取到价格: {price}")

    end_time = time.time()  # 记录结束时间
    print(f"获取获取BINANCE {upper_symbol} 的价格总耗时: {end_time - start_time:.2f} 秒")
    return {price,priceChangePercent}


def is_binance_symbol(symbol):
    check_start_time = time.time()  # 检查符号的时间
   
    # 首先检查集合是否存在
    if not redis.exists(binance_symbols_set_key):
        # 如果集合不存在，则去获取
        get_exchange_info()
    
    is_member = redis.sismember(binance_symbols_set_key, symbol)
    print(f"检查 {symbol} 是否在集合中的耗时: {time.time() - check_start_time:.2f} 秒")
    return is_member


def get_exchange_info():
    get_exchange_info_start_time = time.time()
    url = "https://api.binance.com/api/v3/exchangeInfo"
    
    try:
        # 发送 GET 请求
        response = requests.get(url, proxies=proxies)
        response.raise_for_status()
        
        # 获取响应内容
        value = response.text

        # 如果返回为空，直接返回
        if not value:
            print("没有返回数据")
            return 0

        data = json.loads(value)
        symbols = data.get("symbols", [])

        # 创建一个待添加的元素列表
        base_assets_to_add = []

        # 遍历所有符号并将符合条件的 baseAsset 收集到待添加列表中
        for item in symbols:
            if item.get("quoteAsset") == "USDT":
                base_asset = item.get("baseAsset")
                base_assets_to_add.append(base_asset)

        # 记录批量添加到 Redis 前的时间
        batch_add_start_time = time.time()

        # 使用 Redis pipeline 批量添加
        if base_assets_to_add:
            with redis.pipeline() as pipe:
                for base_asset in base_assets_to_add:
                    pipe.sadd(binance_symbols_set_key, base_asset)
                pipe.execute()

        # 记录批量添加到 Redis 后的时间
        batch_add_end_time = time.time()

        # 输出批量添加 Redis 操作的耗时
        print(f"批量添加到 Redis 耗时: {batch_add_end_time - batch_add_start_time:.5f} 秒")

        # 设置集合的过期时间为 5 分钟
        redis.expire(binance_symbols_set_key, 300)  # 300 秒即 5 分钟
        print("Binance 交易对信息已更新并缓存。")
    
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
    
    print(f"获取 Binance 交易对信息耗时: {time.time() - get_exchange_info_start_time:.2f} 秒")