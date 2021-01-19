from settings import alarm_threshold, alarm_template
from datetime import datetime
from logger import app_logger


# response_dict["keys_info"] = [
#             {
#                 "measurement": "big_keys_info",
#                 "time": int("{0}{1}".format(str(info_create_day_time), "000000000")),
#                 "tags": {
#                     "instance_id": instance_id,
#                     "instance_name": instance_name,
#                     "node_id": x["NodeId"],
#                     "key": x['Key'],
#                     "type": x['Type'],
#                     "expire_time_mills": x['ExpirationTimeMillis'],
#                     "db": x['Db'],
#                 },
#                 "fields": {
#                     "bytes": x['Bytes'],
#                     "count": x['Count'],
#                 }
#             } for x in big_keys_info["bigkeys"]["KeyInfo"]
#         ]

# alarm_template = """### 实例ID:{iid} 实例名字:{i_name}
# > 阈值:hash:{hash}, list:{list}, string:{string}, other:{other}

# {keys}

# 生成时间: {current}

# 详细信息：[grafana](http://www.baidu.com)"""



def check_keys(keys_info):
    
    alarm_keys_list = []
    alarm_log_dict = {}
    if len(keys_info)==0:
        return alarm_log_dict
    
    current_time = datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    instance_id = keys_info[0]["tags"]["instance_id"]
    instance_name = keys_info[0]["tags"]["instance_name"]
    for key in keys_info:
        if key["tags"]["type"] in alarm_threshold.keys():
            if int(key["fields"]["bytes"]) > alarm_threshold[key["tags"]["type"]]:
                alarm_keys_info = {
                    "key": key["tags"]["key"],
                    "type": key["tags"]["type"],
                    "bytes": key["fields"]["bytes"]
                }
                alarm_keys_list.append(alarm_keys_info)
        elif int(key["fields"]["bytes"]) > alarm_threshold["other"]:
            alarm_keys_info = {
                "key": key["tags"]["key"],
                "type": key["tags"]["type"],
                "bytes": key["fields"]["bytes"]
            }
            alarm_keys_list.append(alarm_keys_info)
    
    if len(alarm_keys_list) == 0:
        return alarm_log_dict
            
    alarm_message_dict = {
        "iid":instance_id,
        "i_name":instance_name,
        "keys": alarm_keys_list,
        "current": current_time
    }        
    alarm_message_dict.update(alarm_threshold)
    alarm_message = alarm_template.format(**alarm_message_dict)
    app_logger.info(alarm_message)
    
    alarm_log_dict = {
        "instance_id": instance_id,
        "instance_name": instance_name, 
        "message": alarm_message
    }
    
    return alarm_log_dict
            
        