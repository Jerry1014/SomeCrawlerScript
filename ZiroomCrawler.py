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
# trainsport 通勤工具 transit 公交 walk 走路 ride 骑行 minute 通勤时间（分钟） 骑行10分钟大致路程为2km
url_template = 'http://www.ziroom.com/map/room/list?' \
               'min_lng={min_lng}&max_lng={max_lng}&min_lat={min_lat}&max_lat={max_lat}&zoom={zoom}&p={page_num}&' \
               'order_by={order_by}&sort_flag={sort_flag}&price={min_price},{max_price}&feature={feature}&' \
               'leasetype={leasetype}&tag={tag}&resblock_id={resblock_id}&transport={transport}&minute={minute}'


class ARoomResult:
    """
    房屋的信息解析类
    """

    def __init__(self, raw_json):
        self.room_name = raw_json['name']
        desc = raw_json['desc']
        self.room_area = float(search(r'(\d+(\.\d{1,2})?)㎡', desc).groups()[0])
        try:
            self.storey = search(r'(\d{1,3}(/\d{1,3})?)层', desc).groups()[0]
        except AttributeError:
            self.storey = '无楼层数据'
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
    兼顾价格和房间面积，其中area_price_pair形如((5, 2500), (10, 3000), (20, 4000))，含义为(0,5平)，价格低于2500，妙哉。[5平,10平)，
    价格为(2500,3000]，妙哉。如此类推。当想设置下界时，可通过将第一个条件设置为(5, 0)来排除小于5平的，上界同理
    """

    def __init__(self, area_price_pair_list):
        self.area_price_pair_list = area_price_pair_list

    def compare(self, a_result: ARoomResult):
        room_price = a_result.price
        for area, price in self.area_price_pair_list:
            if a_result.room_area < area:
                if room_price > price:
                    return False
                else:
                    return True
            elif room_price <= price:
                return True


def get_result_from_one_page(min_lng, max_lng, min_lat, max_lat, zoom, page_num, order_by, sort_flag, min_price='',
                             max_price='', feature='', leasetype='', tag='', resblock_id='', transport='', minute=''):
    """
    爬取一页搜索结果
    """
    url = url_template.format(min_lng=min_lng, max_lng=max_lng, min_lat=min_lat, max_lat=max_lat, zoom=zoom,
                              page_num=page_num, order_by=order_by, sort_flag=sort_flag, min_price=min_price,
                              max_price=max_price, feature=feature, leasetype=leasetype, tag=tag,
                              resblock_id=resblock_id, transport=transport, minute=minute)
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
                           feature='', leasetype='', tag='', resblock_id='', transport='', minute=''):
    """
    爬取搜索结果，参数含义请看文件开头对url的描述
    :return list of ARoomResult, total_num of room
    """
    room_result_list = list()
    first_result = get_result_from_one_page(min_lng, max_lng, min_lat, max_lat, zoom, 1, order_by, sort_flag, min_price,
                                            max_price, feature, leasetype, tag, resblock_id, transport, minute)
    total_room_num = first_result['total']
    print(f'过滤前的搜索到的房间总数为{total_room_num}')
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
    return room_result_list, total_room_num


if __name__ == '__main__':
    # 啥都行的
    the_lowest_price_result, total_num = get_room_search_result(116.427356, 116.491171, 39.960641, 39.999453, 16,
                                                                'sellPrice', 'asc', 
                                                                transport='ride', minute='10')
    the_lowest_price_list = RoomFilterByBothPriceAndArea(((5, 2400), (6, 2600))). \
        compare_list(the_lowest_price_result)
    the_lowest_price_list.append(f'总数：{total_num}')

    # 发邮件
    sender_name = os.environ['EMAIL_COUNT']
    psw = os.environ['EMAIL_PSW']
    sender = EmailSender('smtp.163.com', sender_name, psw)

    subject = '自如爬取结果'
    msg = '\n'.join([str(i) for i in the_lowest_price_list])
    receiver_name = os.environ['EMAIL_RECEIVE']
    sender.send_email(subject, msg, receiver_name)
