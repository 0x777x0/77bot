import json
import redis


redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_from_redis_list(list_name='chatroom_data'):
    """
    从 Redis 列表中取出数据并转换为 Python 字典
    :param list_name: Redis 列表的名称
    :return: 包含所有数据的列表（每个元素是一个字典）
    """
    # 从 Redis 列表中获取所有数据

    data_list = redis_client.lrange(list_name, 0, -1)
    # 将 JSON 字符串转换为 Python 字典
    result = [json.loads(item.decode('utf-8')) for item in data_list]
    return result