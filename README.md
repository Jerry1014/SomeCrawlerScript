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
- email/EmailSender 用于发送email
    - EmailSender(smtp_server, sender_name, psw=None)
    - cls.send_email(subject, msg, receiver_name) 发送email
    
## 其他的小爬虫
- PaiPaiTracking 京东拍拍上的兴趣商品爬虫
    - 运行方式
        - 直接运行 （if_crawling设置为False）
        - GitHub action自动运行 （通过PAIPAI_KEYWORD传递keyword，邮箱设置参照自如爬虫）
    - 在文件的头部位置有如下几个设置
        - if_show_process 是否输出’正在爬取第几页‘的提示
        - if_write_to_file 是否需要保存到文件
        - search_threshold 搜索词匹配阈值
        - filename 结果保存的文件名
    - 搜索算法并不完美，当前使用的方法是
        - 按照空格切分搜索词
        - 计算每个搜索词在商品名称的最大匹配长度并除于关键词长度
        - 计算所有关键词的平均最大匹配长度比
- WebRobot-ShadowSky shadowsky的签到爬虫
    - 设置Github的secrets或通过os添加环境变量
        - SHADOWSKY_ACCOUNT
        - SHADOWSKY_PSW
    - 通过GitHub的action定时运行
- WechatRobot 微信上的Kindle杂志公社签到爬虫
    - 第一次需要修改user_code为自己的签到值
    - 直接运行
    - 扫码登录
- ZiroomCrawler 自如租房小爬虫
    - get_room_search_result(min_lng, max_lng, min_lat, max_lat, zoom, page_num, order_by, sort_flag, min_price='',
                             max_price='', feature='', leasetype='', tag='', resblock_id='', transport='', minute='')
        - lng经度 lat维度 zoom缩放等级 此三项用于确定搜索的地图范围 百度地图
        - order_by：sellPrice sort_flag：asc 排列方式和顺序
        - feature 3 独卫 4 阳台 多选时为：3|4
        - leasetype 2 年租
        - tag 1 立即 9 预定
        - resblock_id 小区id 使用此项则为在该小区中搜索
        - trainsport 通勤工具 transit 公交 walk 走路 ride 骑行 minute 通勤时间（分钟） 骑行10分钟大致路程为2km
    - 房屋筛选
        - RoomFilterByPrice(max_price)
            - 大于设置的最高价的房屋均会被排除
        - RoomFilterByBothPriceAndArea(compare_list)
            - compare_list 例如形如((5, 2500), (10, 3000), (20, 4000))，含义为(0,5平)，价格低于2500，妙哉。[5平,10平)，价格为(2500,3000]，妙哉。如此类推。当想设置下界时，可通过将第一个条件设置为(5, 0)来排除小于5平的，上界同理
        
        

