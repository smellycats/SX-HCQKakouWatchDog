# -*- coding: utf-8 -*-
import requests

class Kakou(object):
    def __init__(self, **kwargs):
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.headers = {'content-type': 'application/json'}

    def get_kakou_count(self, st, et, kkdd, fxbh):
        """根据时间,地点,方向获取车流量"""
        url = 'http://{host}:{port}/index.php/kakou/carinfo?q={kkdd}+st:{st}+et:{et}+fxbh:{fxbh}'.format(
            host=self.host, port=self.port, st=st, et=et, kkdd=kkdd, fxbh=fxbh)
        try:
            r = requests.get(url, headers=self.headers)
            if r.status_code == 200:
                return json.loads(r.text)['count']
        except Exception as e:
            print e
            raise

    def get_kkdd(self, kkdd_id):
        """获取卡口地点"""
        url = 'http://{host}:{port}/index.php/kakou/kkdd/{kkdd_id}'.format(
            host=self.host, port=self.port, kkdd_id=kkdd_id)
        try:
            r = requests.get(url, headers)
            if r.status_code == 200:
                return json.loads(r.text)['items']
        except Exception as e:
            print e
            raise

