


def is_x(text):
     
    text2 = text
    
    if bool(text2) == False :
        return ["🐦","✖"]
    elif "https://x.com" not in text2 and "https://twitter.com" not in text2:
        return ["🐦","✖"]        
    else:
        # 统计 '/' 的数量
        slash_count = text2.count('/')

        # 判断是否超过 3 个
        if slash_count > 3:
            return ["蹭推文","✔"]
        elif "?q=" in text2:
            return ["蹭推文","✔"]
        else:
            return ["🐦","✔"]
        
        
def is_web(text):
    
    text2 = text
    
    if bool(text2) == False :
        return ["🌏","✖"]
         
    else:
        return ["🌏","✔"]
    
def is_TG(text):    
    text2 = text
    
    if bool(text2) == False :
        return ["✈","✖"]
    elif "https://t.me/" in text2 :
        return ["✈","✔"]        
    else:
        return ["✈","✖"]

       