from datetime import datetime, timedelta, timezone

def convert_timestamp_to_beijing_time(millisecond_timestamp):
    """
    将毫秒级时间戳转换为北京时间，并格式化为 "02-18 23:33:08" 格式。

    :param millisecond_timestamp: 毫秒级时间戳（例如 1740152409710
    :return: 格式化后的北京时间字符串（例如 "02-18 23:33:08"
    """
    # 将毫秒级时间戳转换为秒级
    timestamp_seconds = millisecond_timestamp / 1000

    # 使用 datetime.fromtimestamp() 并指定时区为 UTC
    utc_time = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)

    # 转换为北京时间（UTC+8）
    beijing_time = utc_time + timedelta(hours=8)

    # 格式化输出
    formatted_time = beijing_time.strftime("%m-%d %H:%M:%S")
    return formatted_time