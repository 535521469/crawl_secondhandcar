# encoding=utf8
'''
Created on 2013-3-31
@author: Administrator
'''
from crawler.shc.fe.const import FEConstant as const
from crawler.shc.fe.item import SHCFEShopInfo
from crawler.shc.fe.tools import ignore_notice
from scrapy import log
from scrapy.http.request import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from uuid import uuid4
import datetime

class FESpider(BaseSpider):
    
    name = 'FESpider'
    
    home_url = r'http://www.58.com'
    
    second_hand_car = '/ershouche'
    
    def start_requests(self):
        yield self.make_requests_from_url('http://www.58.com/ershouche/changecity/')

class SHCSpider(FESpider):
    
    name = u'SHCSpider'
    
    def start_requests(self):
        req = self.make_requests_from_url('http://www.58.com/ershouche/changecity/')
        yield req

    def parse(self, response):
        city_name = self.settings[const.CITY_NAME]
        hxs = HtmlXPathSelector(response)
        a_tags = hxs.select('//div[@class="index_bo"]/dl//a')
        for a_tag in a_tags:
            city = a_tag.select('text()').extract()[0]
            city_url = a_tag.select('@href').extract()[0]
            if city == city_name:
                yield Request(city_url + '1/?selpic=1', CarListSpider().parse
                              , cookies={const.FILE_NAME :self.settings[const.FILE_NAME ]})
        
class CarListSpider(FESpider):
    
    @ignore_notice
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        cookies = dict(response.request.cookies)
        tr_tags = hxs.select('//table[@class="tbimg list_text_pa"]//tr')
        current_url = response.url
        
        for tr_tag in tr_tags:
            
            td_tags = tr_tag.select('td').extract()
            if len(td_tags) == 1:
                continue
            
            declare_date = None
            try:
                declare_date = tr_tag.select('//span[@class="c_999"]/text()').extract()[0]
            except IndexError as ie:
                pass
            
            if declare_date:
                declare_date_str = u'2013-%s' % declare_date
                try:
                    declare_date = datetime.datetime.strptime(declare_date_str, '%Y-%m-%d')
                    e_date = datetime.datetime(2013, 4, 1)
                    s_date = datetime.datetime(2013, 3, 28)
                    
                    if not (s_date <= declare_date <= e_date):
                        self.log(u"%s ignore " % declare_date_str, log.INFO)
                        continue 
                except ValueError:
                    self.log(u' %s ' % declare_date_str, log.DEBUG)
            
            url = tr_tag.select('td[1]/a/@href').extract()[0]
            
            if url[:url.find('58')] != current_url[:current_url.find('58')]:
                continue
            yield Request(url, CarDetailSpider().parse
                          , cookies=cookies
                          )
#            yield Request('http://sz.58.com/ershouche/13237275862021x.shtml', CarDetailSpider().parse
#                          , cookies=cookies
#                          )
#            break

        else:
            
            self.log(u' add next page into schedual ', log.INFO)
            current_domain = current_url[:current_url.find(u'/ershouche')]
#            http://sh.58.com/ershouche/1/?selpic=1
#                            /ershouche/1/pn2/?selpic=1
            next_url = hxs.select('//a[@class="next"]/@href').extract()[0]
            
            yield Request(current_domain + next_url, CarListSpider().parse, cookies=cookies)
            
        
class CarDetailSpider(FESpider):
    
    @ignore_notice
    def parse(self, response):
        info = SHCFEShopInfo()
        cookies = dict(response.request.cookies)
        cookies[u'customer_info'] = info
        
        hxs = HtmlXPathSelector(response)
        city_ = hxs.select('//div[@class="breadCrumb f12"]/span/a[1]/text()').extract()[0]
        city_name = city_[:city_.find(u'58')]
        info['cityname'] = city_name
        
        continue_flag = 1
        
        if hxs.select('//div[@id="Notice"]').extract():
            continue_flag = 0
        
        contacter_phone_picture_url = hxs.select('//span[@id="t_phone"]/script/text()').extract()
        if contacter_phone_picture_url and continue_flag:
            try:
                contacter_phone_picture_url = contacter_phone_picture_url[0]
                contacter_phone_picture_url = contacter_phone_picture_url.split('\'')[1]
                
                title = hxs.select('//div[@class="col_sub mainTitle"]/h1/text()').extract()[0]
                info['title'] = title
                        
            except Exception as e:
                print response.url
                raise e
            
            try:
                declaretime = hxs.select('//li[@class="time"]/text()').extract()[0]
                info['declaretime'] = declaretime
            except Exception as e:
                print response.url
                raise e
            
            li_tags = hxs.select('//div[@class="col_sub sumary"]/ul[@class="suUl"]/li')
            for idx, li_tag in enumerate(li_tags):
                try:
                    div_val = li_tag.select('div[1]/text()').extract()[0].strip()
                except IndexError as ie:
                    print response.url
                    raise ie
                
                title_div_tag_val = div_val.replace(u'：', u'')
                if title_div_tag_val == u'价    格':
                    price_num = li_tag.select('div[2]/span/text()').extract()[0]
                    price_unit = li_tag.select('div[2]/text()').extract()[0]
                    info['price'] = price_num + price_unit
                elif title_div_tag_val == u'联 系 人':
                    try:
                        contacter = li_tag.select('div[2]/a/text()').extract()[0]
                        contacter_url = li_tag.select('div[2]/a/@href').extract()[0]
                    except IndexError:
                        contacter = li_tag.select('div[2]/span/a/text()').extract()[0]
                        contacter_url = li_tag.select('div[2]/span/a/@href').extract()[0]
                    info['contacter'] = contacter.strip()
                elif title_div_tag_val == u"车型名称":
                    val = []
                    a_vals = li_tag.select('div[2]/a/text()').extract()
                    cartype = u"-".join(a_vals)
                    info['cartype'] = cartype
                    
                
            
            li_tags = hxs.select('//ul[@class="ulDec clearfix"]/li')
            
            for label_tag in li_tags:
                label = label_tag.select('span[@class="it_l fb"]/text()').extract()[0].strip().replace(' ', '')
                if label == u'车辆颜色':
                    car_color = label_tag.select('span[2]/text()').extract()[0]
                    info['car_color'] = car_color
                elif label == u'变  速  箱':
                    gearbox = label_tag.select('span[2]/text()').extract()[0]
                    info['gearbox'] = gearbox
                elif label == u'上牌时间':
                    license_date = label_tag.select('span[2]/text()').extract()[0]
                    info['license_date'] = license_date
                elif label == u'车辆排量':
                    displacement = label_tag.select('span[2]/text()').extract()[0]
                    info['displacement'] = displacement
                elif label == u'行驶里程':
                    road_haul = label_tag.select('span[2]/text()').extract()[0]
                    info['road_haul'] = road_haul
            
            try:
                info['info_url'] = response.url
                cookies[u'customer_info'] = info
            except Exception as e:
                print response.url
                raise e
            
            try:
                contacter_url
            except UnboundLocalError as ue:
                print response.url
                raise ue
            
            if contacter_url.find(u'my') > -1:
                yield Request(contacter_phone_picture_url, PersonPhoneSpider().parse, cookies=cookies)
            else:
                cookies['contacter_phone_url'] = contacter_phone_picture_url
                yield Request(contacter_url, CustomerShopSpider().parse, cookies=cookies)
            
        else:
            self.log(u" information deprecated %s " % response.url, log.INFO)
            yield None
        
class PersonPhoneSpider(FESpider):

    DOWNLOAD_DELAY = 0.5

    def parse(self, response):
        
        cookies = response.request.cookies
        info = cookies[u'customer_info']
        
        uuid = uuid4()
        filename = unicode(uuid) + '.gif'
        with open(filename, 'wb') as f:
            f.write(response.body)
        
        info['contacter_phone_picture'] = filename
        
        x = u','.join(map(lambda i:u"{m}{k}{m}:{m}{v}{m}".format(m="\"", k=unicode(i[0]), v=unicode(i[1]).encode('utf8')) 
                      , [(k, v) for k, v in info.items()]))
        x = u"{%s}\n" % x
        
        with open(cookies[const.FILE_NAME] + u".json", 'a') as f:
            f.write(x)
            
        self.log(u"fetch 1 %s , %s" % (info['cityname'], info['info_url']), log.INFO)   
        
        
class CustomerShopSpider(FESpider):
    
    def parse(self, response):
        
        hxs = HtmlXPathSelector(response)
        
        cookies = response.request.cookies
        info = dict(cookies[u'customer_info'])
        
        try:
            shop_name = hxs.select('//div[@class="bi_tit"]/text()').extract()[0]
            info['shop_name'] = shop_name.strip()
        except Exception:
            pass
        
        try:
            shop_address = hxs.select('//div[@class="title_top"]/ul[1]/li[2]/text()').extract()[0]
            info['shop_address'] = shop_address[3:].strip()
        except Exception as e:
            pass
        
        try:
            shop_phone = hxs.select('//dl[@class="ri_info_dl_01"][1]/dt/text()').extract()[0]
            info['shop_phone'] = shop_phone.strip()
        except Exception as e:
            pass
        
        try:
            enter_time = hxs.select('//dl[@class="ri_info_dl_01"][3]/dt/text()').extract()[0]
            info['enter_time'] = enter_time.strip()
        except Exception as e:
            pass
        
        cookies[u'customer_info'] = info
        
        yield Request(response.request.cookies['contacter_phone_url']
                      , PersonPhoneSpider().parse, cookies=cookies)
        
