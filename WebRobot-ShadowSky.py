import requests

shadowsky_headers = {
    "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

login_data = {'email': '', 'passwd': '', 'remember_me': 'week'}
shadowsky_session = requests.Session()
shadowsky_login_page = shadowsky_session.post('https://www.shadowsky.icu/auth/login', headers=shadowsky_headers,
                                              data=login_data)
shadowsky_headers.update({'Origin': 'https://www.shadowsky.icu', 'Referer': 'https://www.shadowsky.icu/user',
                          'Accept': 'application/json, text/javascript, */*; q=0.01',
                          'X-Requested-With': 'XMLHttpRequest'})
shadowsky_checkin_page = shadowsky_session.post('https://www.shadowsky.icu/user/checkin', headers=shadowsky_headers)
