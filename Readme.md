# Redis慢日志分析脚本
### 数据存储

#### 实例信息
mysql

#### 分析结果
influxdb

#### 展示
kernel grafana

### 查看帮助信息
python main.py --help
### 创建分析作业
-f 1 为强制刷新redis实例信息到数据库.

python main.py cron-create-job -f 1

### 获取分析作业结果并存入influxdb

python main.py cron-save-job-data

### 发送报警信息
python main.py alarm



## 发布脚本
更改配置文件
```bash
curent=`date +"%Y%m%d%H%M%S"`
if [ -f "./bak_settings.py" ]; then
  mv ./bak_settings.py ./bak_settings.py_"$curent"
fi
mv ./redis_monitor/settings.py ./bak_settings.py
cp ./pro_settings.py ./redis_monitor/settings.py
```

## 线上更新代码

```bash
sh get_code.sh
```

## 计划任务

```
35 14 * * * cd /opt/redis_ann_job/redis_monitor && /root/.pyenv/versions/redis_ana_job/bin/python main.py cron-create-job -f 1
*/5 * * * * cd /opt/redis_ann_job/redis_monitor && /root/.pyenv/versions/redis_ana_job/bin/python main.py cron-save-job-data
*/5 * * * * cd /opt/redis_ann_job/redis_monitor && /root/.pyenv/versions/redis_ana_job/bin/python main.py alarm
```

## grafana 展示配置

```json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": 1,
  "iteration": 1610941376011,
  "links": [],
  "panels": [
    {
      "datasource": "redismonitor",
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "custom": {
            "align": "left",
            "displayMode": "auto",
            "filterable": false
          },
          "mappings": [
            {
              "from": "",
              "id": 1,
              "text": "",
              "to": "",
              "type": 1,
              "value": ""
            }
          ],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "none"
        },
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "instance_name"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 116
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "instance_id"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 176
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Time"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 112
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "key"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 366
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "字节"
            },
            "properties": [
              {
                "id": "unit",
                "value": "bytes"
              },
              {
                "id": "custom.displayMode",
                "value": "gradient-gauge"
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "db"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 50
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "type"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 95
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 14,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 2,
      "options": {
        "frameIndex": 4,
        "showHeader": true,
        "sortBy": [
          {
            "desc": true,
            "displayName": "字节"
          }
        ]
      },
      "pluginVersion": "7.3.6",
      "targets": [
        {
          "groupBy": [],
          "hide": false,
          "measurement": "big_keys_info",
          "orderByTime": "ASC",
          "policy": "default",
          "query": "SELECT \"node_id\",\"instance_name\", \"key\",\"db\",\"type\",\"bytes\" as \"字节\", \"count\" as \"元素数量\" FROM \"big_keys_info\" WHERE instance_id='$instance_id' and $timeFilter ",
          "rawQuery": true,
          "refId": "A",
          "resultFormat": "table",
          "select": [
            [
              {
                "params": [
                  "bytes"
                ],
                "type": "field"
              }
            ],
            [
              {
                "params": [
                  "count"
                ],
                "type": "field"
              }
            ]
          ],
          "tags": []
        }
      ],
      "timeFrom": null,
      "timeShift": null,
      "title": "redis大key信息",
      "transformations": [],
      "type": "table"
    },
    {
      "datasource": "redismonitor",
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "custom": {
            "align": "left",
            "displayMode": "auto",
            "filterable": false
          },
          "mappings": [
            {
              "from": "",
              "id": 1,
              "text": "",
              "to": "",
              "type": 1,
              "value": ""
            }
          ],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "none"
        },
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "instance_name"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 116
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "instance_id"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 176
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Time"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 112
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "key"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 366
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "字节"
            },
            "properties": [
              {
                "id": "unit",
                "value": "bytes"
              },
              {
                "id": "custom.displayMode",
                "value": "gradient-gauge"
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 14,
        "w": 24,
        "x": 0,
        "y": 14
      },
      "id": 3,
      "options": {
        "frameIndex": 4,
        "showHeader": true,
        "sortBy": [
          {
            "desc": true,
            "displayName": "字节"
          }
        ]
      },
      "pluginVersion": "7.3.6",
      "targets": [
        {
          "groupBy": [],
          "hide": false,
          "measurement": "big_keys_info",
          "orderByTime": "ASC",
          "policy": "default",
          "query": "SELECT \"instance_id\",\"instance_name\", \"prefix\",\"type\",\"bytes\" as \"字节\",\"keynum\" as \"此前缀Key数量\", \"count\" as \"此前缀元素数量\" FROM \"keyprefixes_info\" WHERE  instance_id='$instance_id' and $timeFilter\n",
          "rawQuery": true,
          "refId": "A",
          "resultFormat": "table",
          "select": [
            [
              {
                "params": [
                  "bytes"
                ],
                "type": "field"
              }
            ],
            [
              {
                "params": [
                  "count"
                ],
                "type": "field"
              }
            ]
          ],
          "tags": []
        }
      ],
      "timeFrom": null,
      "timeShift": null,
      "title": "redis前缀统计信息",
      "transformations": [],
      "type": "table"
    }
  ],
  "schemaVersion": 26,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": [
      {
        "allValue": null,
        "current": {
          "selected": false,
          "text": "xxxxx",
          "value": "xxxxx"
        },
        "datasource": "MySQL",
        "definition": "select instance_name from instances_info where isdel=0 group by instance_id;",
        "error": null,
        "hide": 0,
        "includeAll": false,
        "label": "实例名",
        "multi": false,
        "name": "instance_name",
        "options": [],
        "query": "select instance_name from instances_info where isdel=0 group by instance_id;",
        "refresh": 1,
        "regex": "",
        "skipUrlSync": false,
        "sort": 0,
        "tagValuesQuery": "",
        "tags": [],
        "tagsQuery": "",
        "type": "query",
        "useTags": false
      },
      {
        "allValue": null,
        "current": {
          "selected": false,
          "text": "r-2ze1ai5yjeh5yp1dl5",
          "value": "r-2ze1ai5yjeh5yp1dl5"
        },
        "datasource": "MySQL",
        "definition": "select instance_id from instances_info where instance_name='$instance_name' and isdel='0' group by instance_id",
        "error": null,
        "hide": 0,
        "includeAll": false,
        "label": "实例ID",
        "multi": false,
        "name": "instance_id",
        "options": [],
        "query": "select instance_id from instances_info where instance_name='$instance_name' and isdel='0' group by instance_id",
        "refresh": 1,
        "regex": "",
        "skipUrlSync": false,
        "sort": 0,
        "tagValuesQuery": "",
        "tags": [],
        "tagsQuery": "",
        "type": "query",
        "useTags": false
      }
    ]
  },
  "time": {
    "from": "now/d",
    "to": "now/d"
  },
  "timepicker": {},
  "timezone": "",
  "title": "Redis大Key分析",
  "uid": "A3upNgfGk",
  "version": 12
}
```