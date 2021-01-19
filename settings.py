## 阿里云账号,需要有redis和DAS权限
## redis权限用来获取列表
## DAS权限用来创建分析作业,获取分析结果
aliyun_client = {
    "accessKeyId": "XXXXXXXXXXXXX",
    "accessSecret": "XXXXXXXXXXXXX",
    "region": "cn-beijing"
}

## 用来存储实例信息,作业信息,及报警信息,使用mysql,因为使用orm开发,可以使用其他数据库,部分modle语句需要调整
cmdb = {
    "host": "127.0.0.1",
    "port": "3306",
    "user": "root",
    "password": "password",
    "database": "aliyun_cmdb"
}

# influxdb用来存分析结果
redismontir = {
    "host": "127.0.0.1",
    "port": "8086",
    "database": "redismonitor"
}

# 钉钉报警配置信息
dingtalk = {
    "url": "https://oapi.dingtalk.com/robot/send?access_token=XXXXXXXXXXXX",
    "token": "XXXXXXXXXXX",
    "keyword": "CacheJobAl"
}

alarm_threshold = {
    "hash":50*1024*1024,
    "list":50*1024*1024,
    "string":2*1024*1024,
    "other":5*1024*1024
}

# 报警模板
alarm_template = """#### CacheJobAl 实例ID:{iid} 实例名字:{i_name}
> 阈值 **hash**: {hash}, **list**: {list}, **string**: {string}, **other**: {other}

 
**{keys}**

生成时间: {current}

详细信息：[grafana](http://www.baidu.com)"""


# 日志配置
logging_conf = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(filename)s %(module)s %(funcName)s %(lineno)d: %(message)s'
        },
        "verbose": {
            'format': "%(levelname)s %(asctime)s %(pathname)s %(filename)s %(module)s %(funcName)s %(lineno)d: %(message)s"

        },
    },
    'handlers': {
        'dingtalk': {
            'class': 'dingtalk_log_handler.DingTalkHandler',
            'webhook': 'https://oapi.dingtalk.com/robot/send?access_token=XXXXXXXXX',
            # 'secret': '',
            'keyword': 'CacheJobAl',
            'formatter': 'verbose',
            'level': 'ERROR',  # 指定handler 响应日志的最低级别
        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',  # 默认midnight进行轮转
            'filename': "redis_analysis.log",
            'formatter': 'standard'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'dingding': {
            'handlers': ['dingtalk', 'request_handler'],
            'level': 'INFO',  # 指定logger 接收日志的最低级别
            'propagate': False,
        },
    }
}
