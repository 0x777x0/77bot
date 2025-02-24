import logging
import requests
import time
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别为 DEBUG
    format="%(asctime)s - %(levelname)s - %(message)s",  # 日志格式
    handlers=[
        logging.FileHandler("api_request.log"),  # 输出到文件
        logging.StreamHandler()  # 输出到控制台
    ]
)

# 获取日志记录器
logger = logging.getLogger("api_request_logger")

def fetch_oke_latest_info(ca_ca, max_retries=3, retry_delay=0.5):
    """
    访问指定 URL 并获取市场信息。如果请求失败，会尝试重试。

    :param ca_ca: tokenContractAddress 参数
    :param max_retries: 最大重试次数（默认 3 次）
    :param retry_delay: 重试间隔时间（默认 500 毫秒）
    :return: 返回 API 响应数据JSON 格式），如果请求失败则返回 None。
    """
    url = "https://www.okx.com/priapi/v1/dx/market/v2/latest/info"
    params = {
        "chainId": 501,
        "tokenContractAddress": ca_ca
    }

    for attempt in range(max_retries):
        try:
            # 记录调试信息
            logger.debug(f"开始请求 URL: {url}, 参数: {params}, 尝试次数: {attempt + 1}")

            # 发送 GET 请求
            start_time = datetime.now()
            response = requests.get(url, params=params, timeout=10)  # 设置超时时间为 10 秒
            elapsed_time = (datetime.now() - start_time).total_seconds()

            # 记录请求耗时
            logger.debug(f"请求完成，耗时: {elapsed_time:.2f} 秒")

            # 检查响应状态码
            if response.status_code == 200:
                # 记录成功日志
                logger.info(f"请求成功，响应数据: {response.json()}")
                return response.json()
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

    # 如果所有尝试都失败，记录错误日志并返回 None
    logger.error(f"所有 {max_retries} 次尝试均失败，停止重试。")
    return None



def fetch_oke_overview_info(ca_ca, max_retries=3, retry_delay=0.5):
    """
    访问指定 URL 并获取市场信息。如果请求失败，会尝试重试。

    :param ca_ca: tokenContractAddress 参数
    :param max_retries: 最大重试次数（默认 3 次）
    :param retry_delay: 重试间隔时间（默认 500 毫秒）
    :return: 返回 API 响应数据JSON 格式），如果请求失败则返回 None。
    """
    url = "https://www.okx.com/priapi/v1/dx/market/v2/token/overview/"
    params = {
        "chainId": 501,
        "tokenContractAddress": ca_ca
    }

    for attempt in range(max_retries):
        try:
            # 记录调试信息
            logger.debug(f"开始请求 URL: {url}, 参数: {params}, 尝试次数: {attempt + 1}")

            # 发送 GET 请求
            start_time = datetime.now()
            response = requests.get(url, params=params, timeout=10)  # 设置超时时间为 10 秒
            elapsed_time = (datetime.now() - start_time).total_seconds()

            # 记录请求耗时
            logger.debug(f"请求完成，耗时: {elapsed_time:.2f} 秒")

            # 检查响应状态码
            if response.status_code == 200:
                # 记录成功日志
                logger.info(f"请求成功，响应数据: {response.json()}")
                return response.json()
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

    # 如果所有尝试都失败，记录错误日志并返回 None
    logger.error(f"所有 {max_retries} 次尝试均失败，停止重试。")
    return None





""" # 示例调用
if __name__ == "__main__":
    ca_ca = "E9PyaRvisPewpq1QCp6PGuwLERfWxRRB5qaPgpJqpump"  # 替换为实际的 tokenContractAddress
    market_info = fetch_overview_info(ca_ca)

    if market_info:
        print("请求成功，返回数据:")
        print(market_info)
    else:
        print("请求失败，请检查日志。") """