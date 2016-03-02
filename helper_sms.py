# -*- coding: utf-8 -*-
import requests

class SMS(object):
    def __init__(self, **kwargs):
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.token = kwargs['token']
        self.headers = {'content-type': 'application/json'}

    def sms_send(self, content, mobiles):
        """发送短信"""
        url = 'http://{host}:{port}/sms'.format(host=self.host, port=self.port)
        data = {'content': content, 'mobiles': mobiles}
        try:
            r = requests.get(url, headers=self.headers, data=json.dumps(data))
            if r.status_code == 201:
                return json.loads(r.text)
        except Exception as e:
            print e

if __name__ == '__main__':
    sms_ini = {
        'host': '127.0.0.1',
        'port': 8090,
        'username': 'test1',
        'password': '123456',
        'token': 'eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ0MzI1NjcyMiwiaWF0IjoxNDQzMjQ5NTIyfQ.eyJzY29wZSI6WyJzY29wZV9nZXQiLCJoemhiY19nZXQiXSwidWlkIjoyM30.Qga6zksBXBu8Aq9zVBb7tsR_vQFI4A7IfzdgMvGEfrw'
    }
    s = SMS(**sms_ini)
    del s
