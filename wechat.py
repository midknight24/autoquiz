import requests
import random
import time
from .config import WX_AGENTID, WX_CORPID, WX_CORPSECRET


class WXWorkAPI:
    def __init__(self, agentid=WX_AGENTID, corpid=WX_CORPID, corpsecret=WX_CORPSECRET, WXCPT=None):
        self.wxcpt = WXCPT
        self.agentid = agentid
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.get_access_token()

    def get_access_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        resp = requests.get(url, params={
            'corpid': self.corpid,
            'corpsecret': self.corpsecret
        })
        self.token = resp.json().get('access_token')

    def send_msg(self, content):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
        data = {
            'touser': '@all',
            'msgtype': 'text',
            'agentid': self.agentid,
            'text': {
                'content': content
            }
        }
        resp = requests.post(url, params={'access_token': self.token}, json=data)
        return resp

    def gen_task_id(self, uuid):
        ts = int(time.time())
        return f'{uuid}-{ts}' 


    def send_card(self, title, content, uuid, can_ans_url, cant_ans_url):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
        data = {
            "touser" : "@all",
            "msgtype" : "template_card",
            "agentid" : self.agentid,
            "template_card" : {
                "card_type" : "button_interaction",
                "main_title" : {
                    "title" : title,
                },
                "quote_area": {
                    "type": 0,
                    "quote_text": content
                },
                "task_id": self.gen_task_id(uuid),
                "button_list": [
                    {
                        "text": "懂",
                        "style": 1,
                        "key": can_ans_url
                    },
                    { 
                        "text": "不懂",
                        "style": 3,
                        "key": cant_ans_url
                    }
                ]
            },
            "enable_id_trans": 0
        }
        resp = requests.post(url, params={'access_token': self.token}, json=data)
        print(resp)
        print(resp.text)
        return resp

    def update_card(self, title, userid, response_code, url):
        update_url = "https://qyapi.weixin.qq.com/cgi-bin/message/update_template_card?debug=1"
        data = {
            "userids": [userid],
            "agentid" : self.agentid,
            "response_code": response_code,
            "template_card" : {
                "card_type" : "text_notice",
                "main_title" : {
                    "title" : title,
                    "desc": url
                },
                "card_action": {
                    "type": 1,
                    "url": url,
                },
                "horizontal_content_list": [],
                "jump_list": [],
            }
        }
        resp = requests.post(update_url, params={'access_token': self.token}, json=data)
        print(resp.text)
        return resp


