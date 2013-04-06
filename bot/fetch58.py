# encoding=utf8
'''
Created on 2013-3-20
@author: corleone
'''
from bot.configutil import ConfigFile
from crawler.shc.fe.const import FEConstant as const
from multiprocessing import Process
from sched import scheduler
from scrapy.cmdline import execute
from scrapy.settings import CrawlerSettings
import collections
import datetime
import os
import time

class SpiderProcess(Process):
    
    def __init__(self, starttime, city_name, configdata):
        Process.__init__(self)
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
                  , }
        
        console_flag = self.configdata[const.LOG_CONFIG].get(const.LOG_CONSOLE_FLAG)
        if console_flag != u'1':
            values[const.LOG_FILE] = os.sep.join([output_dir, self.starttime + u'.log' ])
        
        return values
    
    def run(self):
        try:
            
            values = self.build_values()
        except Exception as e:
            raise e
        settings = u'crawler.shc.fe.settings'
        module_import = __import__(settings, {}, {}, [''])
        settings = CrawlerSettings(module_import, values=values)
        execute(argv=["scrapy", "crawl", 'SHCSpider' ], settings=settings)

spider_process_mapping = {}

def add_task(root_scheduler):
    
    cfg_path = os.sep.join([os.getcwd(), r'..\fetch58.cfg'])
    configdata = ConfigFile.readconfig(cfg_path).data
    
    city_names = configdata[const.FE_CONFIG][const.FE_CONFIG_CITIES].split(u',')
#    city_names = [u'深圳', u'北京', u'福州', u'哈尔滨', u'大连', u'长沙', u'天津', u'西安', u'沈阳', u'厦门', u'广州', u'青岛', u'苏州', u'济南', u'武汉', u'杭州', u'南京', u'长春', u'成都', u'重庆', u'昆明', ]
    processes = collections.deque()
    
    starttime = datetime.datetime.now()
    
    for city_name in city_names :
        p = SpiderProcess(starttime, city_name, configdata)
#        p.daemon=False
        spider_process_mapping[city_name] = p
        processes.append(p)
        
    if len(processes):
#        root_scheduler.enter(0, 1, processes.popleft().start, ())
        root_scheduler.enter(1, 1, check_add_process
                             , (spider_process_mapping, processes, root_scheduler))
            
            
def check_add_process(spider_process_mapping, processes, root_scheduler):
    
    alives = filter(lambda x:x , [p.is_alive() for p in spider_process_mapping.values()])
#    print len(alives)
    
    if len(processes):
        if len(alives) < 5:
            p = processes.popleft()
            print (u'%s add one processes , crawl %s , %d cities '
                   'waiting ') % (datetime.datetime.now(), p.city_name, len(processes) + 1)
            root_scheduler.enter(0, 1, p.start, ())
        root_scheduler.enter(1, 1, check_add_process
                             , (spider_process_mapping, processes, root_scheduler))
            
if __name__ == '__main__':
    
    root_scheduler = scheduler(time.time, time.sleep)
    root_scheduler.enter(0, 0, add_task, (root_scheduler,))
    root_scheduler.run()

