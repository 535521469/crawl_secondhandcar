# encoding=utf8
'''
Created on 2013-3-31
@author: Administrator
'''
from bot.configutil import ConfigFile
from crawler.shc.fe.const import FEConstant as const
from multiprocessing import Lock
from scrapy.cmdline import execute
from scrapy.settings import CrawlerSettings
import datetime
import os

lock = Lock()

class SpiderProcess(object):
    
    def __init__(self, starttime, city_name, configdata):
        self._starttime = starttime
        self.starttime = starttime.strftime('%Y%m%d%H%M%S')
        self.city_name = city_name
        self.configdata = dict(configdata)
        self.configdata[const.CURRENT_CITY] = city_name
    
    def build_values(self):
        feconfig = self.configdata[const.FE_CONFIG]

        try:
        #=======================================================================
        # if the city use the default config
        #=======================================================================
            city_config = eval(feconfig[self.city_name])
        except Exception:
            city_config = {}
        
        output_dir = self.configdata[const.LOG_CONFIG].get(const.LOG_CONFIG_OUTPUT_DIR)
        
        start_date = eval(feconfig[const.DEFAULT_START_DATE]).strftime(u'%Y-%m-%d')
        end_date = eval(feconfig[const.DEFAULT_END_DATE]).strftime(u'%Y-%m-%d')
        
        start_page = city_config.get(const.START_PAGE,
                                     feconfig[const.DEFAULT_START_PAGE])
        end_page = city_config.get(const.END_PAGE,
                                   feconfig[const.DEFAULT_END_PAGE])
        
        output_dir = os.sep.join([output_dir, self.starttime , ])
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        values = {const.START_TIME:self.starttime[:-2]
                  , const.CITY_NAME:self.city_name
                  , const.CURRENT_CITY:self.city_name
                  , const.CUSTOMER_FLAG:1
                  , const.OUTPUT_DIR:output_dir
                  , const.STARTDATE:city_config.get(const.STARTDATE, start_date)
                  , const.ENDDATE:city_config.get(const.ENDDATE, end_date)
                  , const.CONFIG_DATA:self.configdata
                  , const.START_PAGE:int(start_page)
                  , const.END_PAGE:int(end_page)
                  , const.LOCK:lock
                  , }
        
        console_flag = self.configdata[const.LOG_CONFIG].get(const.LOG_CONSOLE_FLAG)
        if console_flag != u'1':
            values[const.LOG_FILE] = os.sep.join([output_dir, self.starttime + u'.log' ])
        
        return values

if __name__ == '__main__':
    
    cfg_file = r'E:\corleone\corleone_GitHub\crawl_secondhandcar\fetch58.cfg'
    configdata = ConfigFile.readconfig(cfg_file).data
    start_time = datetime.datetime.now()
    current_city = configdata[const.FE_CONFIG][const.FE_CONFIG_CITIES].split(u',')[0]
    import_modules = __import__('crawler.shc.fe.settings', globals={}
                                , locals={}, fromlist=['', ])
    
    sp = SpiderProcess(start_time, current_city, configdata)
    values = sp.build_values()
    
    settings = CrawlerSettings(import_modules, values=values)
    execute(['scrapy', 'crawl', 'SHCSpider', ], settings=settings)

#    execute(['scrapy', 'shell', 'http://sh.58.com/ershouche/13225277731713x.shtml', ])
#    execute(['scrapy', 'shell', 'http://image.58.com/showphone.aspx?t=v55&v=A3046056EF018A1AZ87CF35510C9A0427', ])
#    execute(['scrapy', 'shell', 'http://shop.58.com/13947907975169/', ])
