import os
from email.policy import default

import requests

# 通过github的secrets输入到此
email = os.environ["SHADOWSKY_ACCOUNT"]
psw = os.environ["SHADOWSKY_PSW"]
host = os.environ['SHADOWSKY_HOST']

default_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"}

session = requests.Session()
session.headers.update(default_headers)
login_page = session.post(host + '/auth/login',
                          data={'email': email, 'passwd': psw, 'remember_me': 'week'})

checkin_page = session.post(host + '/user/checkin')
print(checkin_page.json())
