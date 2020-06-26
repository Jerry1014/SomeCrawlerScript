"""
用于爬取自如的脚本
"""
import os

from requests import get
from re import search

from utils.email.EmailSender import EmailSender
from utils.ua.FakeUAGetter import my_fake_ua

# lng经度 lat维度 zoom百度地图中的缩放等级 此三项用于确定搜索的地图范围
# order_by：sellPrice sort_flag：asc 排列方式和顺序
# feature 3 独卫 4 阳台 多选时为：3|4
# leasetype 2 年租
# tag 1 立即 9 预定
# resblock_id 小区id 使用此项则为在该小区中搜索
url_template = 'http://www.ziroom.com/map/room/list?' \
               'min_lng={min_lng}&max_lng={max_lng}&min_lat={min_lat}&max_lat={max_lat}&zoom={zoom}&p={page_num}&' \
               'order_by{order_by}=&sort_flag={sort_flag}&price={min_price},{max_price}&' \
               'feature={feature}&leasetype={leasetype}&tag={tag}&resblock_id={resblock_id}'


class ARoomResult:
    """
    房屋的信息解析类
    """

    def __init__(self, raw_json):
        self.room_name = raw_json['name']
        desc = raw_json['desc']
        self.room_area = float(search(r'(\d+(\.\d{1,2})?)㎡', desc).groups()[0])
        self.storey = search(r'(\d{1,3}(/\d{1,3})?)层', desc).groups()[0]
        self.detail_url = raw_json['detail_url'][2:]
        self.img_url = raw_json['photo'][2:]
        self.price = int(raw_json['price'])
        if '天' in raw_json['price_unit']:
            self.price *= 30
        self.sale_class = raw_json['sale_class']

    def __str__(self):
        return f'{self.room_name} 价格：{self.price} 面积：{self.room_area} 分类：{self.sale_class} url：{self.detail_url}'


class RoomFilterBase:
    """
    兴趣房屋的过滤类
    """

    def compare_list(self, room_list):
        result_list = list()
        for i in room_list:
            if self.compare(i):
                result_list.append(i)
        return result_list

    def compare(self, a_room_info):
        raise NotImplementedError()


class RoomFilterByPrice(RoomFilterBase):
    """
    按照最高价格选择房屋
    """

    def __init__(self, max_price=None):
        self.max_price = max_price

    def compare(self, a_result: ARoomResult):
        if a_result.price > self.max_price:
            return False
        else:
            return True


class RoomFilterByBothPriceAndArea(RoomFilterBase):
    """
    兼顾价格和房间面积，其中area_price_pair形如((5, 2500), (10, 3000), (20, 4000))，含义为小于5平，价格低于2500，妙哉。大于5平小于10
    平，价格为2500-3000，妙哉。如此类推
    """

    def __init__(self, area_price_pair_list, special_tag_price_dict=None):
        self.area_price_pair_list = area_price_pair_list
        self.special_tag_price_dict = special_tag_price_dict

    def compare(self, a_result: ARoomResult):
        room_price = a_result.price
        if self.special_tag_price_dict:
            for i in a_result.tags_list:
                if i in self.special_tag_price_dict.keys():
                    room_price -= self.special_tag_price_dict[i]

        for area, price in self.area_price_pair_list:
            if a_result.room_area < area:
                if room_price > price:
                    return False
                else:
                    return True
            elif room_price <= price:
                return True


def get_result_from_one_page(min_lng, max_lng, min_lat, max_lat, zoom, page_num, order_by, sort_flag, min_price='',
                             max_price='', feature='', leasetype='', tag='', resblock_id=''):
    """
    爬取一页搜索结果
    """
    url = url_template.format(min_lng=min_lng, max_lng=max_lng, min_lat=min_lat, max_lat=max_lat, zoom=zoom,
                              page_num=page_num, order_by=order_by, sort_flag=sort_flag, min_price=min_price,
                              max_price=max_price, feature=feature, leasetype=leasetype, tag=tag,
                              resblock_id=resblock_id)
    max_retry = 3
    while max_retry > 0:
        headers = {'User-Agent': my_fake_ua.random}
        page_content = get(url, headers=headers)
        if page_content.status_code != 200:
            max_retry -= 1
            if max_retry < 0:
                return False
        else:
            if page_content.text:
                return page_content.json()['data']
            else:
                return False


def get_room_search_result(min_lng, max_lng, min_lat, max_lat, zoom, order_by, sort_flag, min_price='', max_price='',
                           feature='', leasetype='', tag='', resblock_id=''):
    """
    爬取搜索结果，参数含义请看文件开头对url的描述
    """
    room_result_list = list()
    first_result = get_result_from_one_page(min_lng, max_lng, min_lat, max_lat, zoom, 1, order_by, sort_flag, min_price,
                                            max_price, feature, leasetype, tag, resblock_id)
    for i in first_result['rooms']:
        room_result_list.append(ARoomResult(i))
    if first_result:
        total_page_num = int(first_result['pages'])
        for page_num in range(2, total_page_num):
            result = get_result_from_one_page(min_lng, max_lng, min_lat, max_lat, zoom, page_num, order_by, sort_flag,
                                              min_price, max_price, feature, leasetype, tag, resblock_id)
            if result:
                for i in result['rooms']:
                    room_result_list.append(ARoomResult(i))
    return room_result_list


if __name__ == '__main__':
    # 啥都行的
    the_lowest_price_result = get_room_search_result(116.48986, 116.513611, 39.974244, 39.998265, 16, 'sellPrice', 'asc'
                                                     , leasetype='2')
    the_lowest_price_list = RoomFilterByBothPriceAndArea(((5, 2500), (6, 2700))). \
        compare_list(the_lowest_price_result)

    # 独立卫浴的
    room_with_toilet_result = get_room_search_result(116.48986, 116.513611, 39.974244, 39.998265, 16, 'sellPrice', 'asc'
                                                     , leasetype='2', feature='3')
    room_with_toilet_list = RoomFilterByBothPriceAndArea(((10, 3200),)).compare_list(room_with_toilet_result)

    # 发邮件
    sender_name = os.environ['EMAIL_COUNT']
    psw = os.environ['EMAIL_PSW']
    sender = EmailSender('smtp.163.com', sender_name, psw)

    subject = '自如爬取结果'
    msg = '\n'.join(
        [str(i) for i in the_lowest_price_list] + ['---------------------'] + [str(i) for i in room_with_toilet_list])
    receiver_name = os.environ['EMAIL_RECEIVE']
    sender.send_email(subject, msg, receiver_name)
