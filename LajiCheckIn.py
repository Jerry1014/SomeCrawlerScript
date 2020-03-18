import json
from configparser import ConfigParser
from time import time

from requests import Session

post_data = {"xm": "黄相铭", "xh": "20164634", "xy": "计算机科学与工程学院", "njjzy": "2016级计算机科学与技术", "bj": "计算机1603", "xq": "浑南校区",
             "ss": "五舍", "qy": "A", "fjh": "219", "brsjhm": "13940240405", "sylx": "内地学生", "jtxxdz_sf": "广东",
             "jtxxdz_cs": "茂名", "jtxxdz_qx": "高州市", "jtxxdz": "根子镇南华村1903", "mqxxdz_sf": "广东", "mqxxdz_cs": "茂名",
             "mqxxdz_qx": "高州市", "mqxxdz": "根子镇南华村1903", "mqjzdzsm": "居家学习", "jzsjhm": "17342879470", "mqzk": "A",
             "zjtw": "", "zzkssj": "", "sfjy": "", "sfyqjc": "", "mqsfzj": "", "jtms": "", "glyyms": "",
             "gldxxdz_sf": "", "gldxxdz": "", "mqstzk": "", "sfgcyiqz": "否", "cjlqk": "曾经医学观察，后隔离解除", "dsjtqkms": "",
             "hjnznl": "在家", "qgnl": "在家", "sfqtdqlxs": "否", "sfqtdqlxsmsxj": "", "sfjcgbr": "否", "sfjcgbrmsxj": "",
             "sfjcglxsry": "否", "sfjcglxsrymsxj": "", "sfjcgysqzbr": "否", "sfjcgysqzbrmsxj": "", "sfjtcyjjfbqk": "否",
             "sfjtcyjjfbqkmsxj": "", "sfqgfrmz": "否", "yljgmc": "", "zzzd": "", "sfygfr": "无", "zgtw": "",
             "zgtwcxsj": "", "sfyghxdbsy": "无", "sfyghxdbsycxsj": "", "sfygxhdbsy": "无", "sfygxhdbsycxsj": "",
             "sfbrtb": "是", "fdysfty": "否", "tbrxm": "", "tbrxh": "", "tbrxy": "", "dtyy": "",
             "id": None}
with Session() as sess:
    payload = {'_t': int(time())}
    header = {'Authorization': 'Basic dnVlOnZ1ZQ=='}
    # 此处的配置文件为了隐藏我的账号密码而设
    # 可不使用配置文件，而直接将post处的第一个参数（url）修改成（如下），将两处的{}修改为对应的值
    # http://stuinfo.neu.edu.cn/api/auth/oauth/token?username={学号}&grant_type=password&password={密码}&imageCodeResult=&imageKey=
    cfg = ConfigParser()
    cfg.read('config.ini')
    login_json = json.loads(sess.post(cfg['Laji CheckIn']['url with psw'], headers=header, json=payload).text)
    # cookies_dict = {'access_token': login_json['access_token'], 'userName': login_json['userName']}
    # add_dict_to_cookiejar(sess.cookies, cookies_dict)

    header['Authorization'] = 'Bearer ' + login_json['access_token']
    payload['_t'] = int(time())
    data = json.loads(sess.post('http://stuinfo.neu.edu.cn/cloud-xxbl/studenLogin', headers=header, json=payload).text)[
        'data']

    post_data['id'] = data.split(':')[-1]
    cur_time = int(time() * 1000)

    sess.get(f'http://stuinfo.neu.edu.cn/cloud-xxbl/studentinfo?tag={data}')
    result = sess.post(f'http://stuinfo.neu.edu.cn/cloud-xxbl/updateStudentInfo?t={cur_time}', json=post_data)
    input(result.text)
