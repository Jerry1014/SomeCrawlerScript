# 小爬虫集合地

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
- PaiPaiTracking 京东拍拍上的兴趣商品爬虫
    - 直接运行
    - 在文件的头部位置有如下几个设置
        - if_show_process 是否输出’正在爬取第几页‘的提示
        - if_write_to_file 是否需要保存到文件
        - search_threshold 搜索词匹配阈值
        - filename 结果保存的文件名
    - 搜索算法并不完美，当前使用的方法是
        - 按照空格切分搜索词
        - 计算每个搜索词在商品名称的最大匹配长度并除于关键词长度
        - 计算所有关键词的平均最大匹配长度比
