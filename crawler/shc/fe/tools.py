'''
Created on 2013-3-31
@author: Administrator
'''
from functools import wraps
from scrapy import log
from scrapy.selector import HtmlXPathSelector
import os
from uuid import uuid4
from scrapy.http.request import Request

def ignore_notice(parse):
    
    @wraps(parse)
    def parse_simulate(self, response):
        '''
        the page is not exist
        '''
        hxs = HtmlXPathSelector(response)
        notice_div = hxs.select('//div[@id="Notice"]')
        url = response.url
        cookies = response.request.cookies
        if notice_div:
            file_name = unicode(uuid4())
            file_path = os.sep.join([
                         self.build_ignore_file_dir(response.request.cookies),
                         file_name])
            
            if self.is_develop_debug(cookies):
                with open(file_path + u'.html', u'wb') as f:
                    f.write(response.body)
            self.log((u'ignore crawl , with Notice div %s, '
                                '%s') % (url, file_name), log.INFO)
        else:
            rss = parse(self, response)
            for rs in rss:
                yield rs
    return parse_simulate

def check_verification_code(parse):
    @wraps(parse)
    def parse_simulate(self, response):
        '''
        need you to input verification code
        '''
        cookies = response.request.cookies
        hxs = HtmlXPathSelector(response)
        verification_div = hxs.select('//div[@class="w_990"]')
        url = response.url
        if verification_div:
            self.log(u'need input verification code crawl %s' % url, log.CRITICAL)
            precede_url = url[url.index(u'url=') + 4:]
            shield_file_name = self.get_random_id()
            
            self.log((u'use ip proxy to request %s again , '
                      'shield %s') % (precede_url, shield_file_name), log.INFO)
            meta = {'proxy':u'http://218.108.242.108:3128'}
            
            if self.is_develop_debug(cookies):
                self.save_body(self.build_shield_file_dir(cookies),
                                shield_file_name + u'.html', response)
            
            yield Request(precede_url, self.parse, meta=meta,
                          cookies=cookies, dont_filter=True)
        else:
            rss = parse(self, response)
            for rs in rss:
                yield rs
                
    return parse_simulate

def check_verification_code_gif(parse):
    @wraps(parse)
    def parse_simulate(self, response):
        '''
        need you to input verification code
        '''
        try:
            hxs = HtmlXPathSelector(response)
            cookies = response.request.cookies
            verification_div = hxs.select('//div[@class="w_990"]')
            url = response.url
            if verification_div:
                self.log(u'need input verification code crawl %s' % url, log.CRITICAL)
                precede_url = url[url.index(u'url=') + 4:]
                shield_file_name = self.get_random_id()
                
                self.log((u'use ip proxy to request %s again , '
                          'shield %s') % (precede_url, shield_file_name), log.INFO)
                meta = {'proxy':u'http://218.108.242.108:3128'}
                
                if self.is_develop_debug(cookies):
                    self.save_body(self.build_shield_file_dir(cookies),
                                    shield_file_name + u'.html', response)
                
                yield Request(precede_url, self.parse, meta=meta,
                              cookies=cookies, dont_filter=True)
                    
        except Exception:
            rss = parse(self, response)
            if rss:
                for rs in rss:
                    yield rs
                
    return parse_simulate
        
def with_ip_proxy(parse):
    @wraps(parse)
    def parse_simulate(self, response):
        
        rss = parse(self, response)
        if rss:
            for rs in rss:
                if isinstance(rs, Request):
                    meta = {'proxy':u'http://218.108.242.108:3128'}
                    rs = rs.replace(meta=meta)
                    yield rs
                else:
                    yield rs
        
    return parse_simulate
        
