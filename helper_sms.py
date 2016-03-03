# -*- coding: utf-8 -*-
import json

import requests


class SMS(object):
    def __init__(self, **kwargs):
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.headers = {'content-type': 'application/json'}

    def sms_send(self, content, mobiles):
        """发送短信"""
        url = 'http://{host}:{port}/sms'.format(host=self.host, port=self.port)
        data = {'content': content, 'mobiles': mobiles}
        try:
            r = requests.post(url, headers=self.headers, data=json.dumps(data))
            if r.status_code == 201:
                return json.loads(r.text)
        except Exception as e:
            print 'sms:',e

