import os

import requests

sid = os.environ["HIFINI_SID"]
token = os.environ["HIFINI_TOKEN"]
address = os.environ['HIFINI_SIGN_URL']

cookies = {
    'bbs_sid': 'j8htrta2i9thrff5t19kmbiqmc',
    'bbs_token': 'CeYUOPBAr8UAmWHaeI_2BWw3G5t66YbmD9pTuoDsdARABgi_2FU3_2B6v71_2FtBjEo_2F59yrOw87otWYtXwhRTufw6BUnhcxTorEBreu',
}

headers = {
    'accept': 'text/plain, */*; q=0.01',
    'accept-language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'dnt': '1',
    'origin': 'https://www.hifini.com',
    'priority': 'u=1, i',
    'referer': 'https://www.hifini.com/sg_sign.htm',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

data = {
    'sign': '72028b9b4be4fc186d21ab4aa138817e5e7532531aec34ea5ac0e6b7152c7e05',
}

response = requests.post('https://www.hifini.com/sg_sign.htm', cookies=cookies, headers=headers, data=data)

print(response.text)
