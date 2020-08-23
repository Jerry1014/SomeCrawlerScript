"""
用于爬取自如的脚本
"""
import os
from re import search
from time import sleep

from requests import get

from utils.email.EmailSender import EmailSender
from utils.ua.FakeUAGetter import my_fake_ua

# 尝试引入进度条所需库文件
try:
    from eprogress import LineProgress
except ImportError:
    print('未安装进度条依赖库eprogress，将以极简形式显示当前进度')
    LineProgress = None

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

# court_id 小区id
url_template_for_court = "http://www.ziroom.com/xiaoqu/{court_id}.html"

IF_FILTER_COURT = True


class RoomBaseInfo:
    """
    房屋的信息解析类
    """

    def __init__(self, room_name, room_area, storey, detail_url, img_url, price, sale_class, court_id, court_name):
        """
        :param room_name:  房屋名称
        :param room_area: 面积
        :param storey:  楼层
        :param detail_url:  详细信息的url地址
        :param img_url: 图片地址
        :param price: 价格
        :param sale_class: 销售类型
        """
        self.room_name = room_name
        self.room_area = room_area
        self.storey = storey
        self.detail_url = detail_url
        self.img_url = img_url
        self.price = price
        self.sale_class = sale_class
        self.court_id = court_id
        self.court_name = court_name

    def __str__(self):
        return f'{self.room_name} 价格：{self.price} 面积：{self.room_area} 分类：{self.sale_class} url：{self.detail_url}'

    @classmethod
    def parse(cls, raw_json):
        """
        解析json数据，返回RoomBaseDetail
        :param raw_json: 原始的json数据
        :return: a RoomBaseDetail
        """
        if raw_json:
            room_name = raw_json['name']
            tem_desc = raw_json['desc']
            room_area = float(search(r'(\d+(\.\d{1,2})?)㎡', tem_desc).group(1))
            tem_storey_msg = search(r'(\d{1,3}(/\d{1,3})?)层', tem_desc)
            storey = tem_storey_msg.group(1) if tem_storey_msg else '无楼层数据'
            detail_url = raw_json['detail_url'][2:]
            img_url = raw_json['photo'][2:]
            price = int(raw_json['price'])
            if '天' in raw_json['price_unit']:
                price *= 30
            sale_class = raw_json['sale_class']
            court_id = raw_json['resblock_id']
            court_name = raw_json['resblock_name']

            return RoomBaseInfo(room_name, room_area, storey, detail_url, img_url, price, sale_class, court_id,
                                court_name)


class CourtDetail:
    """
    小区信息
    """

    def __init__(self, age, architecture_type, area, greening_rate, volume_rate, noise):
        self.age = age
        self.architecture_type = architecture_type
        self.area = area
        self.greening_rate = greening_rate
        self.volume_rate = volume_rate
        self.noise = noise

    @classmethod
    def parse(cls, html_div):
        if html_div:
            tem = search(r'建筑年代：(\d+)', html_div)
            age = tem.group(1) if tem else "无建筑年代数据"
            tem = search(r'建筑类型：([\u4E00-\u9FFF]+)', html_div)
            architecture_type = tem.group(1) if tem else "无建筑类型数据"
            tem = search(r'建筑面积：(\d+㎡)', html_div)
            area = tem.group(1) if tem else "无建筑面积数据"
            tem = search(r'绿化率：(\d+％)', html_div)
            greening_rate = tem.group(1) if tem else "无绿化率数据"
            tem = search(r'容积率：(\d+(\.\d+)?)', html_div)
            volume_rate = tem.group(1) if tem else "无容积率数据"
            tem = search(r'小区是否有噪音（毗邻车站机场）：([\u4E00-\u9FFF]+)', html_div)
            noise = tem.group(1) if tem else "无噪音数据"

            return CourtDetail(age, architecture_type, area, greening_rate, volume_rate, noise)


class RoomDetail:
    def __init__(self, room_base_info: RoomBaseInfo, court_info: CourtDetail):
        self.room_base_info = room_base_info
        self.court_info = court_info

    @classmethod
    def parse(cls, room_raw_json, court_html_div):
        return RoomDetail(RoomBaseInfo.parse(room_raw_json), CourtDetail.parse(court_html_div))

    def __str__(self):
        return self.room_base_info.__str__()


class RoomFilterByPrice:
    """
    按照最高价格选择房屋
    """

    def __init__(self, max_price=None):
        self.max_price = max_price

    def filter(self, a_result: RoomBaseInfo):
        if not a_result or a_result.price > self.max_price:
            return False
        else:
            return True


class RoomFilterByBothPriceAndArea:
    """
    兼顾价格和房间面积，其中area_price_pair形如((5, 2500), (10, 3000), (20, 4000))，含义为(0,5平)，价格低于2500，妙哉。[5平,10平)，
    价格为(2500,3000]，妙哉。如此类推。当想设置下界时，可通过将第一个条件设置为(5, 0)来排除小于5平的，上界同理
    """

    def __init__(self, area_price_pair_list):
        self.area_price_pair_list = area_price_pair_list

    def filter(self, a_result: RoomBaseInfo):
        if a_result:
            # 特别用于排除特定小区
            if a_result.court_name in FILTER_COURT:
                return False

            room_price = a_result.price
            for area, price in self.area_price_pair_list:
                if a_result.room_area < area:
                    if room_price > price:
                        return False
                    else:
                        return True
                elif room_price <= price:
                    return True
        else:
            return False


class CourtFilterByAge:
    """
    按建筑年代筛选小区
    """

    def __init__(self, filter_age, make_sure=True):
        """
        :param filter_age: 可以接受的最老的建筑年代，大于等于会被保留
        :param make_sure: 是否放过无年代信息的房间，为True时，能保证筛选结果符合条件，但会排除没有建筑年代信息，但实际符合条件的房间
        """
        self.age = filter_age
        self.make_sure = make_sure

    def filter(self, court_info: CourtDetail):
        # 通常情况下，没有小区信息直接false，但如果是指定不爬取小区信息，则为True
        if not court_info:
            return not (False ^ IF_FILTER_COURT)
        try:
            if int(court_info.age) >= self.age:
                return True
            else:
                return False
        except ValueError:
            return not self.make_sure


class ResultListWithFilter:
    def __init__(self, room_filter, court_filter):
        self._result_list = list()
        self.room_filter = room_filter
        self.court_filter = court_filter
        self.count = 0

    def append(self, a_room: RoomDetail):
        self.count += 1
        if self.room_filter.filter(a_room.room_base_info) and self.court_filter.filter(a_room.court_info):
            self._result_list.append(a_room)

    def append_from_iterable(self, rooms):
        for i in rooms:
            self.append(i)

    def get_result_list(self):
        return self._result_list


def get_page(url, max_retry=3):
    """
    获取一页html
    :param time_out: time out
    :param max_retry: 最大重试次数
    :param url: url
    :return: requests.Respond
    """
    while max_retry > 0:
        headers = {'User-Agent': my_fake_ua.random}
        try:
            respond = get(url, headers=headers)
            if respond.status_code != 200 and respond.text:
                max_retry -= 1
                if max_retry < 0:
                    return None
            else:
                return respond
        except Exception as e:
            sleep(5)
            print('网络不稳定或已经断开')


def get_result_from_one_page(min_lng, max_lng, min_lat, max_lat, zoom, page_num, order_by, sort_flag, min_price='',
                             max_price='', feature='', leasetype='', tag='', resblock_id='', transport='', minute=''):
    """
    爬取一页搜索结果
    :return json or None
    """
    url = url_template.format(min_lng=min_lng, max_lng=max_lng, min_lat=min_lat, max_lat=max_lat, zoom=zoom,
                              page_num=page_num, order_by=order_by, sort_flag=sort_flag, min_price=min_price,
                              max_price=max_price, feature=feature, leasetype=leasetype, tag=tag,
                              resblock_id=resblock_id, transport=transport, minute=minute)
    page_content = get_page(url)
    if page_content:
        return page_content.json()['data']
    else:
        return None


def get_court_info(court_id):
    """
    获取小区信息
    :param court_id: 小区id
    :return: CourtDetail
    """
    if IF_FILTER_COURT:
        url = url_template_for_court.format(court_id=court_id)
        page_content = get_page(url)
        if page_content:
            return search(r'<h2>基本信息</h2>(\s|.*)*?</div>', page_content.text).group()
        else:
            return None


def get_room_search_result(min_lng, max_lng, min_lat, max_lat, zoom, order_by, sort_flag, room_filter_args,
                           court_filter_args=None, min_price='', max_price='', feature='', leasetype='', tag='',
                           resblock_id='', transport='', minute=''):
    """
    爬取搜索结果，参数含义请看文件开头对url的描述
    :return list of ARoomResult, total_num of room
    """
    global IF_FILTER_COURT
    if not court_filter_args:
        IF_FILTER_COURT = False

    results = ResultListWithFilter(RoomFilterByBothPriceAndArea(room_filter_args), CourtFilterByAge(court_filter_args))
    first_result = get_result_from_one_page(min_lng, max_lng, min_lat, max_lat, zoom, 1, order_by, sort_flag, min_price,
                                            max_price, feature, leasetype, tag, resblock_id, transport, minute)
    total_room_num = first_result['total']
    print(f'过滤前的搜索到的房间总数为{total_room_num}')
    # 设置进度条
    line_progress = LineProgress(total=total_room_num) if LineProgress else None

    for i in first_result['rooms']:
        tem_room_base_info = RoomBaseInfo.parse(i)
        tem_court_info = CourtDetail.parse(get_court_info(tem_room_base_info.court_id))
        results.append(RoomDetail(tem_room_base_info, tem_court_info))
        if line_progress:
            line_progress.update_by_cur_num(results.count)
    if first_result:
        total_page_num = int(first_result['pages'])
        for page_num in range(2, total_page_num):
            page_result = get_result_from_one_page(min_lng, max_lng, min_lat, max_lat, zoom, page_num, order_by,
                                                   sort_flag,
                                                   min_price, max_price, feature, leasetype, tag, resblock_id)
            if page_result:
                for i in page_result['rooms']:
                    tem_room_base_info = RoomBaseInfo.parse(i)
                    tem_court_info = CourtDetail.parse(get_court_info(tem_room_base_info.court_id))
                    results.append(RoomDetail(tem_room_base_info, tem_court_info))
                    if line_progress:
                        line_progress.update_by_cur_num(results.count)

    return results.get_result_list(), total_room_num


if __name__ == '__main__':
    # 特别设置的小区排除名单
    FILTER_COURT = ('芍药居北里',)
    the_lowest_price_list, total_num = get_room_search_result(116.427356, 116.491171, 39.960641, 39.999453, 16,
                                                              'sellPrice', 'asc',
                                                              ((6, 1800), (8, 2160)), 2003,
                                                              transport='ride', minute='10')

    # 发邮件
    if the_lowest_price_list:
        the_lowest_price_list.append(f'总数：{total_num}')
        sender_name = os.environ['EMAIL_COUNT']
        psw = os.environ['EMAIL_PSW']
        sender = EmailSender('smtp.163.com', sender_name, psw)

        subject = '自如爬取结果'
        msg = '\n'.join([str(i) for i in the_lowest_price_list])
        receiver_name = os.environ['EMAIL_RECEIVE']
        sender.send_email(subject, msg, receiver_name)
