from pymem import Pymem

#登录复制
def fix_version(pm: Pymem):
    WeChatWindll_base =0 
    for m in list(pm.list_modules()):
        path =m.filename
        if path.endswith("WeChatWin.dll"):
            WeChatWindll_base = m.lpBaseOfDll
            break

    # 这些是CE找到的标绿的内存地址偏移量
    ADDRS =[0x2BEE688,0x2C0E7E8,0x2C0E93C,0x2C26AA8,0x2C29BEC,0x2C2B2F4]

    for offset in ADDRS :
        addr =WeChatWindll_base + offset
        v= pm.read_uint(addr)
        print(v)
        if v== 0x63090a1b:#是3.9.10.27，已经修复过了
            continue
        elif v!= 0x63080021: #不是 3.8.0.33 修复也没用，代码是hardcode的，只适配这一个版本
            raise Exception("别修了，版本不对，修了也没啥用。")
        pm.write_uint(addr,0x63090a1b)#改成要伪装的版本3.9.10.27，转换逻辑看链接print("好了，可以扫码登录了")


   
pm = Pymem("Wechat.exe")
fix_version(pm)
    