import requests

# 接口URL
url = "http://47.238.165.188:8080/api/price/get?chain=sol&address=J341LbyypFvgYxsgK9aEK9qqUzmr2nGZwqXUMsWZpump"

# 发送GET请求
response = requests.get(url)

# 检查请求是否成功
if response.status_code == 200:
    data = response.json()  # 解析JSON响应
    print(data)
else:
    print("请求失败，状态码:", response.status_code)




# 记录每个群组，每个合约，从被发现后，上涨的最大倍数
# 一条喊单记录   群组 喊单人 ca 链  初始市值 最高市值  喊单时间， 最新查询时间，  单次查询到的数据为 供应量 和 价格序列