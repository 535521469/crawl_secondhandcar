# encoding=utf8
'''
Created on 2013-3-20
@author: corleone
'''
from multiprocessing import Process
from sched import scheduler
from scrapy.cmdline import execute
from scrapy.settings import CrawlerSettings
import collections
import datetime
import time
from crawler.shc.fe.const import FEConstant

class SpiderProcess(Process):
    
    def __init__(self, starttime, city_name):
        Process.__init__(self)
        self.starttime = starttime
        self.city_name = city_name
        
    def run(self):
        try:
#            values = {'starttime':self.starttime, 'city_name':self.city_name}
            values = {'starttime':self.starttime
                          , 'city_name':self.city_name
                          , u'customer':1
                          , 'op_dir':u'OUTPUT'
                          , FEConstant.STARTDATE:datetime.datetime(2013,03,28)
                          , }
            settings = u'crawler.shc.fe.settings'
            module_import = __import__(settings, {}, {}, [''])
            settings = CrawlerSettings(module_import, values=values)
            execute(argv=["scrapy", "crawl", 'SHCSpider' ], settings=settings)
        except Exception as e:
            raise e

spider_process_mapping = {}

def add_task(root_scheduler, city_names=[u'上海', u'深圳', u'北京', u'福州', u'哈尔滨']):
    
#    city_names = [u'上海', u'深圳', u'北京', u'福州', u'哈尔滨', u'大连', u'长沙', u'天津', u'西安', u'沈阳', u'厦门', u'广州', u'青岛', u'苏州', u'济南', u'武汉', u'杭州', u'南京', u'长春', u'成都', u'重庆', u'昆明', ]
    city_names = [u'深圳', u'北京', u'福州', u'哈尔滨', u'大连', u'长沙', u'天津', u'西安', u'沈阳', u'厦门', u'广州', u'青岛', u'苏州', u'济南', u'武汉', u'杭州', u'南京', u'长春', u'成都', u'重庆', u'昆明', ]
    processes = collections.deque()
    
    starttime = datetime.datetime.now().strftime('%Y%m%d%H%M')
    
    for city_name in city_names :
        p = SpiderProcess(starttime, city_name)
        spider_process_mapping[city_name] = p
        processes.append(p)
        
    if len(processes):
        root_scheduler.enter(0, 1, processes.popleft().start, ())
        root_scheduler.enter(1, 1, check_add_process
                             , (spider_process_mapping, processes, root_scheduler))
            
            
def check_add_process(spider_process_mapping, processes, root_scheduler):
    alives = filter(lambda x:x , [p.is_alive() for p in spider_process_mapping.values()])
    
    if len(processes):
        if len(alives) < 4:
            print u'add one processes '
            root_scheduler.enter(0, 1, processes.popleft().start, ())
        root_scheduler.enter(1, 1, check_add_process
                             , (spider_process_mapping, processes, root_scheduler))
            
if __name__ == '__main__':
    
    root_scheduler = scheduler(time.time, time.sleep)
    root_scheduler.enter(0, 0, add_task, (root_scheduler,))
    root_scheduler.run()

