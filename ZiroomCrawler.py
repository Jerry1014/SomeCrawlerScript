from requests import get
from re import search
from utils.ua.FakeUAGetter import my_fake_ua

# sellPrice asc 1500,2500 3 独卫 4 阳台 3|4 2 年租 1 立即 9 预定
url_template = 'http://www.ziroom.com/map/room/list?' \
               'min_lng={min_lng}&max_lng={max_lng}&min_lat={min_lat}&max_lat={max_lat}&zoom={zoom}&p={page_num}&' \
               'order_by{order_by}=&sort_flag={sort_flag}&price={min_price},{max_price}&' \
               'feature={feature}&leasetype={leasetype}&tag={tag}&resblock_id={resblock_id}'


class ARoomResult:
    def __init__(self, raw_json):
        self.room_name = raw_json['name']
        desc = raw_json['desc']
        try:
            self.room_area = search(r'(\d+(\.\d{1,2})?)㎡', desc).groups()[0]
            self.storey = search(r'(\d{1,3}(/\d{1,3})?)层', desc).groups()[0]
        except Exception:
            print(raw_json)
        self.detail_url = raw_json['detail_url'][2:]
        self.img_url = raw_json['photo'][2:]
        self.price = raw_json['price']
        if '天' in raw_json['price_unit']:
            self.price *= 30
        self.sale_class = raw_json['sale_class']

    def __str__(self):
        return f'房名{self.room_name} 房价{self.price} url{self.detail_url}'


class RoomRequests:
    def __init__(self, max_price=None):
        self.max_price = max_price

    def compare_list(self, room_list):
        result_list = list()
        for i in room_list:
            if self.compare(i):
                result_list.append(i)
        return result_list

    def compare(self, a_result: ARoomResult):
        if a_result.price > self.max_price:
            return False
        else:
            return True


def get_result_from_one_page(min_lng, max_lng, min_lat, max_lat, zoom, page_num, order_by, sort_flag, min_price='',
                             max_price='', feature='', leasetype='', tag='', resblock_id=''):
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
    test = get_room_search_result(116.48986, 116.513611, 39.974244, 39.998265, 16, 'sellPrice', 'asc',
                                  leasetype='2')
    test2 = RoomRequests(3000)
    for i in test2.compare_list(test):
        print(i)
