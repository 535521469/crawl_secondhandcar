'''
Created on 2013-3-31
@author: Administrator
'''
from functools import wraps
from scrapy import log
from scrapy.selector import HtmlXPathSelector
import os
from uuid import uuid4

def ignore_notice(parse):
    
    @wraps(parse)
    def parse_simulate(self, response):
        hxs = HtmlXPathSelector(response)
        notice_div = hxs.select('//div[@id="Notice"]')
        url = response.url
        if notice_div:
            file_name = unicode(uuid4())
            file_path = os.sep.join([self.build_ignore_file_dir(response.request.cookies), file_name])
            with open(file_path, u'wb') as f:
                f.write(response.body)
            self.log(u' ignore crawl , with Notice div %s, %s' % (url, file_name), log.INFO)
        else:
            rss = parse(self, response)
            for rs in rss:
                yield rs
    return parse_simulate

#def ignore_(parse):
#    @wraps(parse)
#    def parse_simulate(self, response):
#        hxs = HtmlXPathSelector(response)
#        notice_div = hxs.select('//div[@id="Notice"]')
#        url = response.url
#        if notice_div:
#            self.log(u' ignore crawl %s' % url, log.INFO)
#        else:
#            rss = parse(self, response)
#            for rs in rss:
#                yield rs
#    return parse_simulate
        
