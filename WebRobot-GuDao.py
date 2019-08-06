import requests

from FackUA import FakeUA

a_fack_ua = FakeUA()
headers = {"user-agent": a_fack_ua.rondom}

my_session = requests.Session()
login_page = my_session.get('https://www.shadowsky.icu/auth/login', headers=headers)

user_page = my_session.get('https://www.shadowsky.icu',headers=headers)

print(user_page.text)