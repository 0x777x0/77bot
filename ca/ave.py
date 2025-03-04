import requests
import json  # 需要导入 json 库

def get_ave_token(chain: str, address: str) -> int:

    if chain == "sol":
        chain = "solana"
    elif chain == "bsc":
        chain = "bsc"

    url = f"https://febweb002.com/v1api/v3/tokens/{address}-{chain}"
    headers = {
        "x-auth": "8905c1ff44194cf246698870730056e21740896456053685294"
    }

    try:
        response = requests.get(url, headers=headers)
        response_text = response.text.strip()

        # 检查是否为空
        if not response_text:
            print("Error: Empty response from API")
            return 0

        # 解析 JSON
        try:
            result = response.json()
        except ValueError:
            print("Error: Invalid JSON response")
            print("Response content:", response_text)
            return 0

        # 确保 result 是一个字典
        if not isinstance(result, dict):
            print("Error: JSON response is not a dictionary")
            return 0

        # 获取 status
        status = result.get("status")
        if status != 1:
            return 0

        # 解析 `data`（如果是字符串，则再解析一次）
        data = result.get("data", "{}")  # 这里可能是 JSON 字符串
        if isinstance(data, str):
            try:
                data = json.loads(data)  # 再次解析
            except json.JSONDecodeError:
                print("Error: Failed to parse 'data' as JSON")
                print("data content:", data)
                return 0

        # 获取 pairs 数据
        pairs = data.get("pairs", [])

        pool_time = 0
        for pair in pairs:
            amm = pair.get("amm", "")
            created_at = pair.get("created_at", 0)
            reserve0 = pair.get("reserve0", 0)

            if amm == "pump":
                if reserve0 > 0:
                    pool_time = created_at
                    break
            else:
                pool_time = min(pool_time or created_at, created_at)

        return pool_time * 1000

    except requests.RequestException as e:
        print(f"Network Error: {e}")
        return 0

# 示例调用
# print(get_ave_token("sol", "7tmrdpNQ19GanoVK4Mq5GY2gKBWyn1oQeYYDP5zApump"))
