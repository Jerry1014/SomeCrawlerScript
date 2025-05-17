import os
from time import time

from playwright.sync_api import sync_playwright, expect

sid = os.environ["HIFI_SID"]
token = os.environ["HIFI_TOKEN"]

with sync_playwright() as p:
    # headless=False, slow_mo=50
    browser = p.chromium.launch()
    browser_context = browser.new_context()

    # token
    # 过期时间 2025-08-25T05:19:06.000Z
    token_expire_time = 1756070346
    if time() > token_expire_time:
        raise Exception("token已过期")
    browser_context.add_cookies([
        {"name": "bbs_sid", "value": sid, "domain": "www.hifini.com", "path": "/"}
        , {"name": "bbs_token", "value": token, "domain": "www.hifini.com", "path": "/"}])

    # 签到
    page = browser_context.new_page()
    page.goto("https://www.hifini.com/")
    sign_button_locator = page.locator('[id="sign"]')
    expect(sign_button_locator).to_have_count(1)
    sign_button_locator.click()

    # 签到结果
    tips_locator = page.locator('[class="modal-body"]')
    tips_locator.wait_for()
    expect(tips_locator).to_have_count(1)
    print(tips_locator.text_content().strip())

    browser.close()
