import requests
import json
from settings import dingtalk


class Ding(object):
    def __init__(self, url):
        self.url = url

    def rasie_dingtalk_error(self, resp):  #resp type: json
        if resp['errcode'] != 0:
            raise Exception(("钉钉调用失败,resp:{resp}".format(resp=resp)))

    def make_markdown_json(self, title, text):
        markdown_dict = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            },
            "at": {
                # "atMobiles": [
                #     "156xxxx8827",
                #     "189xxxx8325"
                # ],
                "isAtAll": "false"
            }
        }
        markdown_json = json.dumps(markdown_dict)
        return markdown_json

    def sendto_ding(self, title, text):
        try:
            post_data = self.make_markdown_json(title, text)
            headers = {"Content-Type": "application/json;charset=UTF-8"}
            response = requests.post(self.url,
                                     headers=headers,
                                     data=post_data,
                                     timeout=3)
        except Exception as ex:
            raise Exception("推送钉钉失败,errer:{ex}".format(ex=ex))
        response = response.json()
        self.rasie_dingtalk_error(response)
        return response


dingclient = Ding(dingtalk["url"])

