# encoding=utf8
'''
Created on 2013-3-31
@author: Administrator
'''
from scrapy.cmdline import execute
from scrapy.settings import CrawlerSettings


if __name__ == '__main__':
    
    file_name = 'shanghai'
    
    citys = [u'上海', u'深圳', u'北京', u'福州', u'哈尔滨', u'大连', u'长沙', u'天津', u'西安', u'沈阳', u'厦门', u'广州', u'青岛', u'苏州', u'济南', u'武汉', u'杭州', u'南京', u'长春', u'成都', u'重庆', u'昆明', ]
    
    import_modules = __import__('crawler.shc.fe.settings', globals={}, locals={}, fromlist=['', ])
#    execute(['scrapy', 'crawl', 'SHCSpider',"-o%s" % file_name, "-tjsonlines" ], settings=CrawlerSettings(import_modules, values={'city_name':u'上海'}))
    execute(['scrapy', 'crawl', 'SHCSpider', ], settings=CrawlerSettings(import_modules, values={'file_name':u'20130331','city_name':u'上海'}))

#    execute(['scrapy', 'shell', 'http://sh.58.com/ershouche/13225277731713x.shtml', ])
#    execute(['scrapy', 'shell', 'http://image.58.com/showphone.aspx?t=v55&v=A3046056EF018A1AZ87CF35510C9A0427', ])
#    execute(['scrapy', 'shell', 'http://shop.58.com/13947907975169/', ])
