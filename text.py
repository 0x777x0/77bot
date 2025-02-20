import re



def is_solca(text):
    # 合并多行文本为单行（去除所有换行符）
    text = text.replace('\n', '')
    
    # 定义正则表达式：匹配长度为45的由数字和大小写字母组成的子串
    pattern = r'[a-zA-Z0-9]{44}'
    
    # 使用findall方法从文本中找到所有匹配的字符串
    matches = re.findall(pattern, text)
    
    # 返回第一个匹配的结果（如果有的话）
    if matches:
        return matches[0]
    else:
        return None
    
    
print(bool(501))

a = "BNB Chain"

print(a)