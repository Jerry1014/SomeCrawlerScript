#小爬虫集合地

## 通用工具类 utils
- proxies/ProxiesCrawler 爬取西刺上提供的免费代理ip
    - GetProxies(num_of_http_proxies, num_of_https_proxies)
    - cls.get_proxies() 爬取方法
    - cls.save_file() 将爬取结果保存到文件中
    - cls.get_proxies_by_file(filename,type) 解析保存文件
    - cls.get_http_proxies_random()/get_https_proxies_random() 获取一个代理ip
    - cls.filter_proxies() 通过ip138剔除不可用的代理ip
- ua/FakeUAGetter 获取随机的虚假UA
    - from FackUA import my_fake_ua # 单例模式
    - my_fake_ua.random # random ua
    
## 其他的小爬虫