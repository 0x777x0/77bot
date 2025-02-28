from wcferry import Wcf
from queue import Empty
from ca.ca_info import is_solca, is_eths, math_price, math_cex_price, math_km, math_percent, math_bjtime, get_bundles, is_cexToken, is_pump

import time

wcf = Wcf()
groups = ["58224083481@chatroom"]
wcf.enable_receiving_msg()

print('机器人启动')

ca_datas = [] 
while wcf.is_receiving_msg():
        try:
            msg = wcf.get_msg()
            # 处理消息的逻辑...
            time.sleep(1)
            if msg.from_group() and msg.roomid in groups:
                
                sol_id, sol_ca = is_solca(msg.content)
                eths_id, eths_ca = is_eths(msg.content)
                
                # 如果是sol和eth合约，就把你要把 群id  wxid 昵称 合约 时间戳    存下来
                if sol_id or eths_id:
                    roomid = msg.roomid
                    caller_wxid = msg.sender      
                    chatroom_members = wcf.get_chatroom_members(roomid = roomid)
                    caller_simulate_name = chatroom_members[caller_wxid]
                    ca = sol_ca if sol_ca else eths_ca
                    query_time = int(time.time()*1000)
                    
                    ca_data = [msg.roomid, caller_wxid, caller_simulate_name, ca, query_time]
                    ca_datas.append(ca_data) 
                    print(ca_datas)      
        
        except Empty:
            continue
        except Exception as e:
            print(e)


wcf.keep_running()   
