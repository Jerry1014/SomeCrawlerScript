"""
爬取并提供西刺（可自行替换）上的免费代理ip的模块
"""
import datetime
import random
import re
import time
from string import Template

import bs4
import requests

from utils.ua.FakeUAGetter import my_fake_ua

# 要爬取的，提供代理ip的网址
proxies_url = Template('http://www.xicidaili.com/nn/${page_num}')


# 爬取代理ip地址的url构建方法
def url_build_method(page_num):
    return proxies_url.substitute(page_num=page_num)


class GetProxies:
    """
    从文件中/爬取西刺网提供的代理ip
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GetProxies, cls).__new__(cls)
        return cls.instance

    def __init__(self, num_of_http_proxies, num_of_https_proxies):
        """
        :param num_of_http_proxies: 要爬取的http代理ip数量
        :param num_of_https_proxies: 要爬取的https代理ip数量
        """
        self.ua = my_fake_ua
        self.get_proxies_time_limit = 1000
        self.num_of_http_proxies = num_of_http_proxies
        self.num_of_https_proxies = num_of_https_proxies
        self.filename_of_http_proxies = 'proxies_http.txt'
        self.filename_of_https_proxies = 'proxies_https.txt'
        self.proxies_http_list = list()
        self.proxies_https_list = list()

    def get_proxies_by_file(self, filename, protocol):
        """
        从文件中导入代理ip
        :param filename: 文件名
        :param protocol: 代理ip协议
        :return: None
        """
        tem_list = self.proxies_http_list if protocol == 'http' else self.proxies_https_list
        with open(filename, 'r') as f:
            for i in f.readlines()[1:]:
                a_proxies = i.split(':')
                tem_list.append((a_proxies[0], a_proxies[1][:-1]))

    def get_proxies(self):
        """
        获得代理的ip池，爬取num_of_XXX要求的数目或时间限制到之后终止
        :return: None
        """
        page_num = 1
        start_time = time.time()
        while len(self.proxies_http_list) < self.num_of_http_proxies or len(
                self.proxies_https_list) < self.num_of_https_proxies:
            tem_http_list, tem_https_list = self.get_proxies_from_each_page(str(page_num))
            self.filter_proxies(tem_http_list, 'http')
            self.proxies_http_list += tem_http_list
            print('第' + str(page_num) + '页筛选之后')
            print('http的代理ip数量:' + str(len(self.proxies_http_list)))
            print('https的代理ip数量:' + str(len(self.proxies_https_list)))
            self.proxies_https_list += tem_https_list
            page_num += 1

            if time.time() - start_time > self.get_proxies_time_limit:
                print('获取代理超时')
                return

    def get_proxies_from_each_page(self, page_num=''):
        """
        爬取西刺代理提供的代理ip
        :param page_num: str 要爬取的页面
        :return: (list,list) http代理ip，https代理ip
        """
        # 访问网站
        headers = {'User-Agent': self.ua.random}
        try:
            if page_num == '1':
                page_num = ''
            url = url_build_method(page_num)
            page = requests.get(url, headers=headers)
            page_text = page.text
        except Exception as e:
            print(e)
            return None

        proxies_http = list()
        proxies_https = list()
        page_bs = bs4.BeautifulSoup(page_text, features="html.parser")
        proxies_list_bs = page_bs.find_all('tr', class_='odd')
        for i in proxies_list_bs:
            tem = i.contents
            ip = tem[3].string
            port = tem[5].string
            protocol = tem[11].string
            if protocol == 'HTTP':
                proxies_http.append((ip, port))
            else:
                proxies_https.append((ip, port))
        return proxies_http, proxies_https

    def filter_proxies(self, proxies_list, protocol):
        """
        访问http://www.ip138.com/，测试ip代理是否可用
        :param proxies_list: list 代理ip的list
        :param protocol: str 指定协议时http或https，仅支持这两种
        """
        if protocol == 'http':
            url = 'http://2018.ip138.com/ic.asp'
        else:
            url = 'https://ip.cn/'
        for i in proxies_list:
            headers = {'User-Agent': self.ua.random}

            proxy = {'http': i[0] + ':' + i[1]}
            try:
                test_page = requests.get(url, headers=headers, proxies=proxy, timeout=2)
                tem = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', test_page.text)
                if not (tem and tem.group() == i[0]):
                    proxies_list.remove(i)
            except:
                proxies_list.remove(i)

    def save_file(self):
        """保存文件，默认保存以proxies_http.csv,proxies_https.csv保存在当前工作目录下"""
        with open(self.filename_of_http_proxies, 'w') as f:
            f.write(time.ctime(time.time()) + ' -------------\n')
            for i in self.proxies_http_list:
                f.write(i[0] + ':' + i[1] + '\n')

        with open(self.filename_of_https_proxies, 'w') as f:
            f.write(time.ctime(time.time()) + ' -------------\n')
            for i in self.proxies_https_list:
                f.write(i[0] + ':' + i[1] + '\n')

    def get_http_proxies_random(self):
        return random.choice(self.proxies_http_list)

    def get_https_proxies_random(self):
        return random.choice(self.proxies_https_list)


if __name__ == '__main__':
    test = GetProxies(50, 1)
    test.get_proxies()
    test.save_file()
