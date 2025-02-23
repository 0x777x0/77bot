import requests
import json

def get_pool_create_time(symbol):
    upper_symbol = symbol.upper()

    url = f"https://api.binance.com/api/v3/ticker/price?symbol={upper_symbol}USDT"
    
    # 发送 GET 请求
    response = requests.get(url)
    print(response)
    # 获取响应内容
    value = response.text
    print(value)

    # print(value)
    # 如果返回为空，直接返回
    if not value:
        return 0
    
    data = json.loads(value)  # 将响应内容转换为字典
    price = data.get("price")

    print(price)
    

get_pool_create_time("btc");    