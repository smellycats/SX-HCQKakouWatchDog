# -*- coding: utf-8 -*-
import time
import json

import arrow
import requests

from helper_sms import SMS
from helper_kakou import Kakou
from ini_conf import MyIni


class WatchDog(object):
    def __init__(self):
	# 时间标记
        self.time_flag = arrow.now().replace(hours=-1)
	# 日期标记
	self.date_flag = arrow.now()

        self.my_ini = MyIni()
        
        self.fxbh_dict = {
            'IN': u'进城',
            'OT': u'出城',
            'WE': u'西向东',
            'EW': u'东向西',
            'SN': u'南往北',
            'NS': u'北往南',
            'QT': u'其他'
        }
        self.sms = SMS(**self.my_ini.get_sms())
        self.kakou = Kakou(**self.my_ini.get_kakou())

        self.mobiles_list = self.my_ini.get_mobiles()['number'].split(',')
        self.kkdd_list = []
        # 短信发送记录，形如{('441302001', 'IN'): <Arrow [2016-03-02T20:08:58.190000+08:00]>}
        self.sms_send_dict = {}
        self.sms_send_time = 7

    def __del__(self):
        pass

    def get_kkdd_list(self):
        """卡口地点列表"""
        self.kkdd_list = []
        for i in ['441302', '441304']:
            self.kkdd_list += self.kakou.get_kkdd(i)

    def sms_send_info(self, sms_send_list):
        """发送短信通知"""
        t = arrow.now()
        content = u'[惠城区卡口报警]\n'
        for i in sms_send_list:
            content += u'[{kkdd},{fxbh}]\n'.format(
                kkdd=i['kkdd'], fxbh=i['fx'])
        content += u'超过1小时没数据'

        self.sms.sms_send(content, self.mobiles_list)

    def check_kakou_count(self):
        """遍历检测所有卡口方向车流量"""
        t = arrow.now()
        # 待发送的卡口列表如[{'kkdd': '东江大桥卡口', 'fx': '进城'}]
        sms_send_list = []
	# 是否发送短信
	is_sms_send = False

        for i in self.kkdd_list:
            for fx in i['fxbh_list']:
                # 计算卡口最新1小时流量
                count = self.kakou.get_kakou_count(
                    st=t.replace(hours=-1).format('YYYY-MM-DD HH:mm:ss'),
                    et=t.format('YYYY-MM-DD HH:mm:ss'),
                    kkdd=i['kkdd_id'], fxbh=fx)
                
                # 如果车流量为0则发送短信
                if count <= 0:
		    # 该卡口最近发送日期
                    last_send_date = self.sms_send_dict.get(
                        (i['kkdd_id'], fx), None)
                    # 没有发送记录的
                    if last_send_date is None:
                        sms_send_list.append(
                            {'kkdd': i['kkdd_name'], 'fx': self.fxbh_dict[fx],
                             'kkdd_id': i['kkdd_id'], 'fx_code': fx})
			is_sms_send = True
			continue

                    # 当前时间大于7am，并且发送日期更新
                    if t.datetime.hour > self.sms_send_time and \
		       t.datetime.day != self.date_flag.datetime.day:
			self.date_flag = t
			is_sms_send = True

		    # 当前时间大于7am，并且当前时间大于历史记录发送时间18小时
		    if t.datetime.hour > self.sms_send_time and \
		       t > last_send_date.replace(hours=18):
			is_sms_send = True
                    sms_send_list.append(
                        {'kkdd': i['kkdd_name'], 'fx': self.fxbh_dict[fx],
                         'kkdd_id': i['kkdd_id'], 'fx_code': fx})

        for i in sms_send_list:
            self.sms_send_dict[(i['kkdd_id'], i['fx_code'])] = t
        # 发送短信
        if sms_send_list and is_sms_send:
            self.sms_send_info(sms_send_list)
        
    def run(self):
        while 1:
            try:
                # 当前时间
                t = arrow.now()
                # 每10分钟检查一遍
                if t > self.time_flag.replace(minutes=10):
                    self.get_kkdd_list()
                    self.check_kakou_count()
                    self.time_flag = t
            except Exception as e:
                print e
		raise
                time.sleep(10)
            finally:
                time.sleep(1)


