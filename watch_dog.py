# -*- coding: utf-8 -*-
import time
import json

import arrow
import requests

from helper_sms import SMS
from helper_kakou import Kakou


class WatchDog(object):
    def __init__(self):
        self.date_flag = arrow.now().replace(hours=-1)
        #早上9时发送信息
        #self.send_time = 9
        self.mobiles_list = ['123', '456']
        self.kakou_ini = {
            'host': '127.0.0.1',
            'port': 8080
        }
        self.sms_ini = {
            'host': '127.0.0.1',
            'port': 8090,
            'username': 'test1',
            'password': '123456',
            'token': 'eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ0MzI1NjcyMiwiaWF0IjoxNDQzMjQ5NTIyfQ.eyJzY29wZSI6WyJzY29wZV9nZXQiLCJoemhiY19nZXQiXSwidWlkIjoyM30.Qga6zksBXBu8Aq9zVBb7tsR_vQFI4A7IfzdgMvGEfrw'
        }
        self.fxbh_dict = {
            'IN' = u'进城',
            'OT' = u'出城',
            'WE' = u'西向东',
            'EW' = u'东向西',
            'SN' = u'南往北',
            'NS' = u'北往南',
            'QT' = u'其他',
        }
        self.sms = SMS(**sms_ini)
        self.kakou = Kakou(**kakou_ini)
        self.kkdd_list = []
        # 短信发送记录，形如{('441302001', 'IN'): <Arrow [2016-03-02T20:08:58.190000+08:00]>}
        self.sms_send_dict = {}
        self.sms_send_time = 6

    def __del__(self):
        pass

    def get_kkdd_list(self):
        self.kkdd_list = []
        for i in ['441302', '441304']:
            self.kkdd_list += self.kakou.get_kkdd(i)

    def sms_send(self, kkdd, fx):
        """发送短信通知"""
        t = arrow.now()
        content = u'{kkdd},{fxbh}方向超过1小时没有数据'.format(
            kkdd=i['kkdd_name'], fxbh=self.fxbh_dict[fx])
        last_send_date = self.sms_send_dict.get((kkdd, fx), None)
        if last_send_date is None:
            self.sms.sms_send(content, self.mobiles_list)
            self.sms_send_dict((kkdd, fx)) = t
            return
        # 当前时间 大于6am，并且当前时间大于历史记录发送时间18小时
        if t.datetime.hour > self.sms_send_time and t > last_send_date.replace(hours=18):
            self.sms.sms_send(content, self.mobiles_list)
            self.sms_send_dict((kkdd, fx)) = t


    def check_kakou_count(self):
        """遍历检测所有卡口方向车流量"""
        t = arrow.now()
        for i in self.kkdd_list:
            for fx in i['fxbh_list']:
                count = self.kakou.get_kakou_count(
                    st=t.replace(hours=-1).format('YYYY-MM-DD HH:mm:ss'),
                    et=t.format('YYYY-MM-DD HH:mm:ss'),
                    kkdd=i['kkdd_id'], fxbh=fx)
                # 如果车流量为0则发送短信
                if count <= 0:
                    self.sms_send(kkdd=i['kkdd_name'], fxbh=self.fxbh_dict[fx])
     
        
    def run(self):
        while 1:
            try:
                # 当前时间
                t = arrow.now()
                # 每10分钟检查一遍
                if t > self.date_flag.replace(minutes=10):
                    self.get_kkdd_list()
                    self.check_kakou_count()
                    self.date_flag = t
            except Exception as e:
                print e
                time.sleep(10)
            finally:
                time.sleep(1)

if __name__ == "__main__":
    wd = WatchDog()
    wd.run()
    #print wd.hbc_count('2014-02-03')
    del wd
