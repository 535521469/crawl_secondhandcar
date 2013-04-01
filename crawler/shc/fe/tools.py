'''
Created on 2013-3-31
@author: Administrator
'''
from functools import wraps
from scrapy import log
from scrapy.selector import HtmlXPathSelector

def ignore_notice(parse):
    
    @wraps(parse)
    def parse_simulate(self, response):
        hxs = HtmlXPathSelector(response)
        notice_div = hxs.select('//div[@id="Notice"]')
        url = response.url
        if notice_div:
            self.log(u' ignore crawl %s' % url, log.INFO)
        else:
            rss = parse(self, response)
            for rs in rss:
                yield rs
    
    return parse_simulate
        
