import requests
import getopt
import sys
import time


class Main:
    # res = {'status': {'code': '1', 'message': '操作已经成功完成', 'created_at': '2020-08-10 16:40:58'}, 'info': {'domain_total': 1, 'all_total': 1, 'mine_total': 1, 'share_total': 0, 'vip_total': 0, 'ismark_total': 0, 'pause_total': 0, 'error_total': 0, 'lock_total': 0, 'spam_total': 0, 'vip_expire': 0, 'share_out_total': 0}, 'domains': [{'id': 83311578, 'status': 'enable', 'grade': 'DP_Free', 'group_id': '1', 'searchengine_push': 'no', 'is_mark': 'no', 'ttl': '600', 'cname_speedup': 'disable', 'remark': '', 'created_on': '2020-05-08 21:52:29', 'updated_on': '2020-08-06 20:35:00', 'punycode': 'lsxboy.top', 'ext_status': '', 'src_flag': 'DNSPOD', 'name': 'lsxboy.top', 'grade_level': 2, 'grade_ns': ['f1g1ns1.dnspod.net', 'f1g1ns2.dnspod.net'], 'grade_title': '免费版', 'is_vip': 'no', 'owner': 'qcloud_uin_100014126553@qcloud.com', 'records': '3'}]}
    # {'status': {'code': '1', 'message': '操作已经成功完成', 'created_at': '2020-08-12 13:02:11'}, 'domain': {'id': 83311578, 'name': 'lsxboy.top', 'punycode': 'lsxboy.top', 'grade': 'DP_Free', 'owner': 'qcloud_uin_100014126553@qcloud.com', 'ext_status': '', 'ttl': 600, 'min_ttl': 600, 'dnspod_ns': ['f1g1ns1.dnspod.net', 'f1g1ns2.dnspod.net'], 'status': 'enable'}, 'info': {'sub_domains': '3', 'record_total': '3', 'records_num': '3'}, 'records': [{'id': '584162512', 'ttl': '86400', 'value': 'f1g1ns1.dnspod.net.', 'enabled': '1', 'status': 'enable', 'updated_on': '2020-05-08 21:52:29', 'name': '@', 'line': '默认', 'line_id': '0', 'type': 'NS', 'weight': None, 'monitor_status': '', 'remark': '', 'use_aqb': 'no', 'mx': '0', 'hold': 'hold'}, {'id': '584162513', 'ttl': '86400', 'value': 'f1g1ns2.dnspod.net.', 'enabled': '1', 'status': 'enable', 'updated_on': '2020-05-08 21:52:29', 'name': '@', 'line': '默认', 'line_id': '0', 'type': 'NS', 'weight': None, 'monitor_status': '', 'remark': '', 'use_aqb': 'no', 'mx': '0', 'hold': 'hold'}, {'id': '584194994', 'ttl': '10', 'value': '101.229.197.84', 'enabled': '1', 'status': 'enable', 'updated_on': '2020-08-10 21:21:59', 'name': 'www', 'line': '默认', 'line_id': '0', 'type': 'A', 'weight': None, 'monitor_status': 'Down', 'remark': '', 'use_aqb': 'no', 'mx': '0'}]}

    def __init__(self):
        self.token = '175467,0dd7ef108719cce834fb74acd2fd5603'
        self.domain_id = int()
        self.record_data = dict()
        self.internet_ip = str()
        self.protocol_ok = '1'
        self.interval = 30
        self.common_data()
        self.get_config()
        self.get_domain_id()
        self.get_recode_id()
        self.main_loop()

    def common_data(self):
        return dict(login_token=self.token, format='json')

    def get_ip(self):
        url = "http://ip.42.pl/raw"
        self.internet_ip = requests.get(url, timeout=30).text
        # print(f"公网IP获取成功！{self.internet_ip}")

    def get_config(self):
        try:
            options, args = getopt.getopt(sys.argv[1:], "i:", ["interval="])
            for option, value in options:
                if option in ("-i", "--interval"):
                    self.interval = int(value)
                    print(f"使用指定更新频率 {self.interval}")
                    return
        except Exception:
            pass

    def get_domain_id(self):
        url = "https://dnsapi.cn/Domain.List"
        param = dict(type='all')
        tmp = self.common_data()
        param.update(tmp)
        res = requests.post(url, data=param).json()
        if res['status']['code'] == self.protocol_ok:
            self.domain_id = res['domains'][0]['id']
            # print(f"domain_id 获取成功 {self.domain_id}")
        else:
            print(f"domain_id 获取失败 {res['status']['code']} {res['status']['message']}")
        return

    def get_recode_id(self):
        url = "https://dnsapi.cn/Record.List"
        param = dict(domain_id=self.domain_id)
        tmp = self.common_data()
        param.update(tmp)
        res = requests.post(url, data=param).json()
        for i in res['records']:
            if i['name'] == 'www':
                self.record_data['id'] = i['id']
                self.record_data['ip'] = i['value']
                self.record_data['name'] = i['name']
                self.record_data['record_line'] = i['line']
                self.record_data['record_line_id'] = i['line_id']
                # print(f"获取记录ID成功 {self.record_data['id']}")
                break
        if not self.record_data['id']:
            print(f"获取记录ID失败 {res['status']['code']} {res['status']['message']}")
        return

    def update_record(self):
        url = " https://dnsapi.cn/Record.Ddns"
        param = dict(domain_id=self.domain_id,
                     record_id=self.record_data['id'],
                     sub_domain=self.record_data['name'],
                     record_line_id=self.record_data['record_line_id'],
                     value=self.internet_ip
                     )
        tmp = self.common_data()
        param.update(tmp)
        res = requests.post(url=url, data=param).json()
        if res['status']['code'] == self.protocol_ok:
            print(f"记录更新成功 {res['record']['id']}")
        else:
            print(f"记录更新失败 {res['status']['code']} {res['status']['message']}")
        return True

    def main_loop(self):
        while True:
            try:
                self.get_ip()
                if (self.internet_ip and self.record_data['ip']) and (self.internet_ip != self.record_data['ip']):
                    print(f"监测到公网IP变动 当前公网IP：{self.internet_ip}  记录IP：{self.record_data['ip']}， 准备更新。")
                    self.update_record()
                else:
                    print(f"公网ip未变更，当前公网IP：{self.internet_ip}，记录IP：{self.record_data['ip']}")
                
                self.get_recode_id()
                time.sleep(self.interval)
            except Exception:
                pass


Main()
