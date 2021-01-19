from sqlalchemy.util.compat import b
from session import get_influxdb
import time
from datetime import datetime


class Redis_BigKeys:
    @staticmethod
    def slave_to_influxdb(session, param):
        try:
            session.write_points(param)
        except Exception as ex:
            raise Exception("slave_to_influxdb 失败 param: {0}".format(param))
        return 0

    @staticmethod
    # 传入数据生成时间,并且根绝生成时间存入数据,因为influxdb存入时间必须有时间戳
    def format_big_keys_info(big_keys_info, info_create_day: str, instance_id, instance_name):
        response_dict = {
            "keys_info": [],
            "keyprefixes": []
        }

        info_create_day_time = int(time.mktime(
            datetime.strptime(info_create_day, "%Y-%m-%d").timetuple()))
        # 大key
        response_dict["keys_info"] = [
            {
                "measurement": "big_keys_info",
                "time": int("{0}{1}".format(str(info_create_day_time), "000000000")),
                "tags": {
                    "instance_id": instance_id,
                    "instance_name": instance_name,
                    "node_id": x["NodeId"],
                    "key": x['Key'],
                    "type": x['Type'],
                    "expire_time_mills": x['ExpirationTimeMillis'],
                    "db": x['Db'],
                },
                "fields": {
                    "bytes": x['Bytes'],
                    "count": x['Count'],
                }
            } for x in big_keys_info["bigkeys"]["KeyInfo"]
        ]
        # 前缀统计
        response_dict["keyprefixes"] = [
            {
                "measurement": "keyprefixes_info",
                "time": int("{0}{1}".format(str(info_create_day_time), "000000000")),
                "tags": {
                    "instance_id": instance_id,
                    "instance_name": instance_name,
                    "prefix": x['Prefix'],
                    "type": x['Type'],
                },
                "fields": {
                    "keynum": x['KeyNum'],
                    "count": x['Count'],
                    "bytes": x['Bytes']
                }
            } for x in big_keys_info["keyprefixes"]["Prefix"]
        ]

        return response_dict

