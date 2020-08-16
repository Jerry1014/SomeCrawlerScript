"""
爬取京东拍拍上的拍卖信息，提前找到兴趣商品的拍卖时间
"""
import os
from math import ceil
from os import remove
from os.path import exists
from time import ctime
from difflib import SequenceMatcher

from requests import get

from utils.email.EmailSender import EmailSender
from utils.ua.FakeUAGetter import my_fake_ua

# 标记 是否显示爬取进度 是否将结果写入文件 搜索匹配阈值
if_crawling = True
if_show_process = False
if_write_to_file = False
search_threshold = 0.6
filename = 'product.txt'
if if_write_to_file:
    if exists(filename):
        remove(filename)

if if_crawling:
    key_word_list = [os.environ['PAIPAI_KEYWORD']]
else:
    key_word_list = input('输入要搜索的关键字：').split()
total_num = 1
page_size = 100
cur_page_num = 1
result_list = list()
url_format = 'https://used-api.paipai.com/auction/list?pageNo={page_num}&pageSize={page_size}'
product_detail_url_format = 'https://sell.paipai.com/auction-detail/{product_id}'


def show_result(need_showed_result_list):
    """
    输出结果
    :param need_showed_result_list: 结果列表
    """
    if need_showed_result_list:
        if if_write_to_file:
            f = open(filename, 'a')
        else:
            f = None
        for i in need_showed_result_list:
            for j in i.items():
                my_str = f'{j[0]}:{j[1]}'
                print(my_str)
                if f is not None:
                    f.write(my_str + '\n')
            print()
            if f is not None:
                f.write('\n')
        result_list.extend(need_showed_result_list)
        need_showed_result_list.clear()
        if f is not None:
            f.close()


while cur_page_num <= ceil(total_num / page_size):
    if if_show_process:
        print(f'爬取第{cur_page_num}页中')
    headers = {'user-agent': my_fake_ua.random}
    response = get(url_format.format(page_num=cur_page_num, page_size=page_size), headers=headers)
    tem_result_list = list()
    if response.status_code == 200:
        try:
            data = response.json()['data']
            total_num = data['totalNumber']
            product_list = data['auctionInfos']
            for product in product_list:
                product_name = product['productName']
                key_word_match_point = 0
                for key_word in key_word_list:
                    key_word_match_point += \
                    SequenceMatcher(None, key_word.lower(), product_name.lower()).\
                    find_longest_match(0, len(key_word),0,len(product_name))[-1] / len(key_word)
                key_word_match_point = key_word_match_point / len(key_word_list)
                if key_word_match_point > search_threshold:
                    end_time = ctime(product['endTime'] // 1000)
                    current_price = product['currentPrice']
                    url = product_detail_url_format.format(product_id=product['id'])
                    tem_result_list.append(
                        {'商品名称': product_name, '当前价格': current_price, '结束时间': end_time, '商品链接': url})
        except TypeError as e:
            print(f'出现bug\n{e}\n请呼叫程序员\n')
        show_result(tem_result_list)
    else:
        print(f'网络请求失败，状态码{response.status_code}')
    cur_page_num += 1

if if_crawling and result_list:
    sender_name = os.environ['EMAIL_COUNT']
    psw = os.environ['EMAIL_PSW']
    sender = EmailSender('smtp.163.com', sender_name, psw)

    subject = '拍拍爬取结果'
    msg = '\n'.join([str(i) for i in result_list])
    receiver_name = os.environ['EMAIL_RECEIVE']
    sender.send_email(subject, msg, receiver_name)
else:
    show_result(result_list)
