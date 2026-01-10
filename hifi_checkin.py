import os
from time import time

from playwright.sync_api import sync_playwright, expect

sid = os.environ["HIFI_SID"]
token = os.environ["HIFI_TOKEN"]
token_expire_time = os.environ["HIFI_TOKEN_EXPIRE_TIME"]

with sync_playwright() as p:
    # browser = p.chromium.launch(headless=False, slow_mo=50)
    browser = p.chromium.launch()
    browser_context = browser.new_context()

    if time() > int(token_expire_time):
        raise Exception("token已过期")
    browser_context.add_cookies([
        {"name": "bbs_sid", "value": sid, "domain": "www.hifiti.com", "path": "/"}
        , {"name": "bbs_token", "value": token, "domain": "www.hifiti.com", "path": "/"}])

    # 签到
    page = browser_context.new_page()
    page.goto("https://www.hifiti.com/")
    sign_button_locator = page.locator('[id="sign"]')
    expect(sign_button_locator).to_have_count(1)
    sign_button_locator.click()

    # 签到结果
    tips_locator = page.locator('[class="modal-body"]')
    tips_locator.wait_for()
    expect(tips_locator).to_have_count(1)
    print(tips_locator.text_content().strip())

    browser.close()
