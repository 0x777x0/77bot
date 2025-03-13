import logging
import requests
import time
from datetime import datetime
import json
import sys
import io


# 修改标准输出的编码为 utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别为 DEBUG
    format="%(asctime)s - %(levelname)s - %(message)s",  # 日志格式
    handlers=[
        logging.FileHandler("api_request.log", encoding='utf-8'),  # 输出到文件，并设置编码为 utf-8
        logging.StreamHandler(sys.stdout)  # 输出到控制台
    ]
)


# 获取日志记录器
logger = logging.getLogger("api_request_logger")

def get_price_onchain(payload, max_retries=3, retry_delay=0.5):
    """
    访问指定 URL 并获取链上价格信息。如果请求失败，会尝试重试。

    :param payload: 请求参数（JSON 格式）
    :param max_retries: 最大重试次数（默认 3 次）
    :param retry_delay: 重试间隔时间（默认 500 毫秒）
    :return: 返回 API 响应数据（JSON 格式），如果请求失败则返回空字典。
    """
    url = "http://47.238.165.188:8080/api/price/getList"

    # 设置请求头
    headers = {
        'Content-Type': 'application/json'
    }

    for attempt in range(max_retries):
        try:
            # 记录调试信息
            logger.debug(f"开始请求 URL: {url}, 参数: {payload}, 尝试次数: {attempt + 1}")

            # 发送 POST 请求
            start_time = datetime.now()
            response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=7)  # 设置超时时间为 7 秒
            elapsed_time = (datetime.now() - start_time).total_seconds()

            # 记录请求耗时
            logger.debug(f"请求完成，耗时: {elapsed_time:.2f} 秒")

            # 检查响应状态码
            if response.status_code == 200:
                result = response.json()
                if 'data' in result:
                    # 记录成功日志
                    logger.info(f"请求成功，响应数据: {result['data']}")
                    return result
                else:
                    # 记录警告日志
                    logger.warning(f"返回的数据中没有 'data' 字段，完整返回数据: {result}")
                    return {}  # 返回空字典，表示请求失败但不影响主流程
            else:
                # 记录警告日志
                logger.warning(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
                if attempt < max_retries - 1:  # 如果不是最后一次尝试，则等待后重试
                    time.sleep(retry_delay)
                continue

        except requests.exceptions.RequestException as e:
            # 记录错误日志
            logger.error(f"请求过程中发生错误: {str(e)}", exc_info=True)
            if attempt < max_retries - 1:  # 如果不是最后一次尝试，则等待后重试
                time.sleep(retry_delay)
            continue

    # 如果所有尝试都失败，记录错误日志并返回空字典
    logger.error(f"所有 {max_retries} 次尝试均失败，停止重试。")
    return {}  # 返回空字典，表示请求失败但不影响主流程



def send_person_ca(payload, max_retries=3, retry_delay=0.5, timeout=7):
    """
    发送 POST 请求到指定 URL，支持重试机制和超时判断。

    :param url: 请求的 URL
    :param payload: 请求参数（JSON 格式）
    :param max_retries: 最大重试次数（默认 3 次）
    :param retry_delay: 重试间隔时间（默认 500 毫秒）
    :param timeout: 请求超时时间（默认 7 秒）
    :return: 返回 API 响应数据（JSON 格式），如果请求失败则返回空字典。
    """
    # 设置请求头
    headers = {
        'Content-Type': 'application/json'
    }
    url = "http://47.238.165.188:8080/api/ca/add"

    for attempt in range(max_retries):
        try:
            # 记录调试信息
            logger.debug(f"开始请求 URL: {url}, 参数: {payload}, 尝试次数: {attempt + 1}")

            # 发送 POST 请求
            start_time = datetime.now()
            response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=timeout)
            elapsed_time = (datetime.now() - start_time).total_seconds()

            # 记录请求耗时
            logger.debug(f"请求完成，耗时: {elapsed_time:.2f} 秒")

            # 检查响应状态码
            if response.status_code == 200:
                result = response.json()
                # 记录成功日志
                logger.info(f"请求成功，响应数据: {result}")
                return result
            else:
                # 记录警告日志
                logger.warning(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
                if attempt < max_retries - 1:  # 如果不是最后一次尝试，则等待后重试
                    time.sleep(retry_delay)
                continue

        except requests.exceptions.RequestException as e:
            # 记录错误日志
            logger.error(f"请求过程中发生错误: {str(e)}", exc_info=True)
            if attempt < max_retries - 1:  # 如果不是最后一次尝试，则等待后重试
                time.sleep(retry_delay)
            continue

    # 如果所有尝试都失败，记录错误日志并返回空字典
    logger.error(f"所有 {max_retries} 次尝试均失败，停止重试。")
    return {}  # 返回空字典，表示请求失败但不影响主流程


def get_ca_by_wxid(wxid, max_retries=3, retry_delay=0.5, timeout=7):
    """
    根据微信 ID 查询数据，支持重试机制和超时判断。

    :param wxid: 微信 ID
    :param max_retries: 最大重试次数（默认 3 次）
    :param retry_delay: 重试间隔时间（默认 500 毫秒）
    :param timeout: 请求超时时间（默认 7 秒）
    :return: 返回 API 响应数据（JSON 格式），如果请求失败则返回空字典。
    """
    url = f"http://47.238.165.188:8080/api/ca/get?wxId={wxid}"

    for attempt in range(max_retries):
        try:
            # 记录调试信息
            logger.debug(f"开始请求 URL: {url}, 尝试次数: {attempt + 1}")

            # 发送 GET 请求
            start_time = datetime.now()
            response = requests.get(url, timeout=timeout)
            elapsed_time = (datetime.now() - start_time).total_seconds()

            # 记录请求耗时
            logger.debug(f"请求完成，耗时: {elapsed_time:.2f} 秒")

            # 检查响应状态码
            if response.status_code == 200:
                result = response.json()
                # 记录成功日志
                logger.info(f"请求成功，响应数据: {result}")
                return result
            else:
                # 记录警告日志
                logger.warning(f"请求失败，状态码: {response.status_code}, 响应内容: {response.text}")
                if attempt < max_retries - 1:  # 如果不是最后一次尝试，则等待后重试
                    time.sleep(retry_delay)
                continue

        except requests.exceptions.RequestException as e:
            # 记录错误日志
            logger.error(f"请求过程中发生错误: {str(e)}", exc_info=True)
            if attempt < max_retries - 1:  # 如果不是最后一次尝试，则等待后重试
                time.sleep(retry_delay)
            continue

    # 如果所有尝试都失败，记录错误日志并返回空字典
    logger.error(f"所有 {max_retries} 次尝试均失败，停止重试。")
    return {}  # 返回空字典，表示请求失败但不影响主流程





# 示例调用
if __name__ == "__main__":
    payload = [{'chain': 'sol', 'address': '4GxCee457d4zfw8NPnBbqFuVpRjZtsiQg9P2C4Bcpump'},
                {'chain': 'sol', 'address': '47u37R4w5VSh7YXSCpiB9mogQjFA9JW7A25sHWxfpump'}, 
                {'chain': 'sol', 'address': 'DjgujfEv2u2qz7PNuS6Ct7bctnxPFihfWE2zBpKZpump'},
                  {'chain': 'bsc', 'address': '0xd2a55e015C8Aa074De8b3bffefdb926B262884F1'},
                    {'chain': 'sol', 'address': '9L1SWjsBFaCeUP9sh9s7wty7n69vTrTPCJx41DcPpump'}]
    result = get_price_onchain(payload)
    if result:
        print("请求成功，返回数据:", result)
    else:
        print("请求失败，返回空数据。")