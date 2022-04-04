import json
from urllib import request
import requests
from .config import WX_AGENTID, WX_CORPID, WX_CORPSECRET


class WXWorkAPI:
    def __init__(self, agentid=WX_AGENTID, corpid=WX_CORPID, corpsecret=WX_CORPSECRET):
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