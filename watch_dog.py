# -*- coding: utf-8 -*-
import time
import json

import arrow
import requests

from helper_sms import SMS
from helper_kakou import Kakou


class WatchDog(object):
    def __init__(self):
        # 时间标记
        self.date_flag = arrow.now().replace(hours=-1)
        # 待发送的手机号码
        self.mobiles_list = ['123']
        self.kakou_ini = {
            'host': '10.47.187.123',
            'port': 80
        }
        self.sms_ini = {
            'host': '10.47.187.123',
            'port': 8090,
            'username': 'test1',
            'password': '123456'
        }
        self.fxbh_dict = {
            'IN': u'进城',
            'OT': u'出城',
            'WE': u'西向东',
            'EW': u'东向西',
            'SN': u'南往北',
            'NS': u'北往南',
            'QT': u'其他'
        }
        self.sms = SMS(**self.sms_ini)
        self.kakou = Kakou(**self.kakou_ini)
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

    def sms_send_info(self, sms_send_list):
        """发送短信通知"""
        t = arrow.now()

        content = ''
        for i in sms_send_list:
            content += u'[{kkdd},{fxbh}]'.format(
                kkdd=i['kkdd'], fxbh=i['fx'])
        content += u'超过1小时没数据'
        print content
        #self.sms.sms_send(content, self.mobiles_list)


    def check_kakou_count(self):
        """遍历检测所有卡口方向车流量"""
        t = arrow.now()
        # 待发送的卡口列表如[{'kkdd': '东江大桥卡口', 'fx': '进城'}]
        sms_send_list = []
        for i in self.kkdd_list:
            for fx in i['fxbh_list']:
                count = self.kakou.get_kakou_count(
                    st=t.replace(hours=-1).format('YYYY-MM-DD HH:mm:ss'),
                    et=t.format('YYYY-MM-DD HH:mm:ss'),
                    kkdd=i['kkdd_id'], fxbh=fx)
                # 如果车流量为0则发送短信
                #print u'{0}{1}:{2}'.format(i['kkdd_name'], fx, count)
                if count <= 0:
                    last_send_date = self.sms_send_dict.get(
                        (i['kkdd_id'], fx), None)
                    # 没有发送记录的
                    if last_send_date is None:
                        self.sms_send_dict[(i['kkdd_id'], fx)] = t
                        sms_send_list.append(
                            {'kkdd': i['kkdd_name'], 'fx': self.fxbh_dict[fx]})
                        continue
                    # 当前时间 大于6am，并且当前时间大于历史记录发送时间18小时
                    if t.datetime.hour > self.sms_send_time and \
                       t > last_send_date.replace(hours=18):
                        self.sms_send_dict[(i['kkdd_id'], fx)] = t
                        sms_send_list.append(
                            {'kkdd': i['kkdd_name'], 'fx': self.fxbh_dict[fx]})
        if sms_send_list:
            print 'done'
            self.sms_send_info(sms_send_list)
        
    def run(self):
        while 1:
            try:
                # 当前时间
                t = arrow.now()
                # 每10分钟检查一遍
                if t > self.date_flag.replace(minutes=1):
                    self.get_kkdd_list()
                    self.check_kakou_count()
                    self.date_flag = t
                    #print self.sms_send_dict
                    print 'date_flag %s' % t
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
