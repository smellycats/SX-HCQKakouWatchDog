# -*- coding: utf-8 -*-
import json

import requests
from requests.auth import HTTPBasicAuth


class Kakou(object):
    def __init__(self, **kwargs):
        self.host = kwargs['host']
        self.port = kwargs['port']
	self.username = kwargs['username']
	self.password = kwargs['password']
        self.headers = {'content-type': 'application/json'}

	self.status = False

    def get_kakou_count(self, st, et, kkdd, fxbh):
        """根据时间,地点,方向获取车流量"""
        url = 'http://%s:%s/stat?q={"st":"%s","et":"%s","kkbh":"%s","fxbh":"%s"}' % (
            self.host, self.port, st, et, kkdd, fxbh)
        try:
            r = requests.get(url, headers=self.headers,
			     auth=HTTPBasicAuth(self.username, self.password))
            if r.status_code == 200:
                return json.loads(r.text)['count']
            else:
                self.status = False
                raise Exception('url: %s, status: %s, %s' % (
                    url, r.status_code, r.text))
        except Exception as e:
	    self.status = False
            raise

    def get_kkdd(self, kkdd_id):
        """获取卡口地点"""
        url = 'http://{0}:{1}/kkdd/{2}'.format(
            self.host, self.port, kkdd_id)
        try:
            r = requests.get(url, headers=self.headers,
		 	     auth=HTTPBasicAuth(self.username, self.password))
            if r.status_code == 200:
                return json.loads(r.text)['items']
            else:
                self.status = False
                raise Exception('url: %s, status: %s, %s' % (
                    url, r.status_code, r.text))
        except Exception as e:
	    self.status = False
            raise

