import json
import os
from time import time

from playwright.sync_api import sync_playwright

sid = os.environ["HIFI_SID"]
token = os.environ["HIFI_TOKEN"]

with sync_playwright() as p:
    # headless=False, slow_mo=50
    browser = p.chromium.launch()
    browser_context = browser.new_context()

    # token过期时间 2025-06-17T13:40:56.053Z
    token_expire_time = 1750138856
    if time() > token_expire_time:
        raise Exception("token已过期")

    browser_context.add_cookies([
        {"name": "bbs_sid", "value": sid, "domain": "www.hifini.com", "path": "/"}
        , {"name": "bbs_token", "value": token, "domain": "www.hifini.com", "path": "/"}])

    # 登录页
    page = browser_context.new_page()
    page.goto("https://www.hifini.com/")
    page.locator('[id="sign"]').click()
    page.wait_for_url("**/sg_sign.htm")
    print(page.title())

    browser.close()
