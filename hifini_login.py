import os

import requests

sid = os.environ["HIFINI_SID"]
token = os.environ["HIFINI_TOKEN"]
address = os.environ['HIFINI_SIGN_URL']

headers = {
    "Dnt": "1",
    "Referer": "https://www.hifini.com/",
    "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

cookies = {
    "bbs_token": token,
    "bbs_sid": sid
}

response = requests.post(address, headers=headers, cookies=cookies)

print(response.text)
