# encoding=utf8
'''
Created on 2013-3-31
@author: Administrator
'''
from scrapy.cmdline import execute
from scrapy.settings import CrawlerSettings
import datetime
from crawler.shc.fe.const import FEConstant

    
if __name__ == '__main__':
    
    file_name = 'shanghai'
    
    citys = [u'上海', u'深圳', u'北京', u'福州', u'哈尔滨', u'大连', u'长沙', u'天津', u'西安'
             , u'沈阳', u'厦门', u'广州', u'青岛', u'苏州', u'济南', u'武汉', u'杭州'
             , u'南京', u'长春', u'成都', u'重庆', u'昆明', ]
    
    import_modules = __import__('crawler.shc.fe.settings', globals={}
                                , locals={}, fromlist=['', ])
#    execute(['scrapy', 'crawl', 'SHCSpider',"-o%s" % file_name, "-tjsonlines" ], settings=CrawlerSettings(import_modules, values={'city_name':u'上海'}))
    
    values = {'starttime':datetime.datetime.now().strftime('%Y%m%d%H%M')
              , 'city_name':u'上海'
              , u'customer':1
              , 'op_dir':u'OUTPUT'
              , FEConstant.STARTDATE:datetime.datetime(2013,03,28)
              , }
    
    settings = CrawlerSettings(import_modules, values=values)
    
    execute(['scrapy', 'crawl', 'SHCSpider', ], settings=settings)

#    execute(['scrapy', 'shell', 'http://sh.58.com/ershouche/13225277731713x.shtml', ])
#    execute(['scrapy', 'shell', 'http://image.58.com/showphone.aspx?t=v55&v=A3046056EF018A1AZ87CF35510C9A0427', ])
#    execute(['scrapy', 'shell', 'http://shop.58.com/13947907975169/', ])
