#!/usr/local/bin/python3
# Copyright (C) 2015-2025 Wang,Jing   <jingwangian@gmail.com>
#
# This file is part of Flight Inforation Query System (fiqs)
#
# fiqs is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# fiqs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with fiqs.  If not, see <http://www.gnu.org/licenses/>.

import sys
import logging
import time
import datetime
import url
import db
# import selenium
import recorder
import cr as crawler_worker

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.remote.webelement import WebElement
# from selenium.webdriver.common.proxy import *
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
from recorder import Recorder

worker_name=["worker_0"]

worker_logger=None

def execTask(task_q,result_q, stat_q,num,driver):
    """
    Execute task coming from the task_q squeue.
    Input Parameters:
        task_q: The queue for the input task;
        result_q: The queue for the worker return task state.
        stat_q: The queue for the worker_monitor check the worker hearbeat.
        num : type[int], the worker number.
        driver: the web driver.
    """
    global worker_name
    global worker_logger
    
    worker_name = "[worker_"+str(num)+"]"
    worker_logger= logging.getLogger('[Worker]')
    worker_logger.info(worker_name+" started")
    print(worker_name, " started")
    
    db.init_conf()
    mydb = db.FlightPlanDatabase()
    mydb.connectDB()
    
    try:
        while(1):
            if task_q.empty() == True:
                time.sleep(10)
                continue
            d = task_q.get()
            
            if d['cmd']=='exit':
                break
            
            t1 = datetime.datetime.now()
            flight_id = d['data']
            search_date=d['date']
#             worker_logger.info("%s Start handle task with flight id %d" %(worker_name,flight_id))
            
            result_q.put(flight_id)
            
            req_url = mydb.get_flight_url_by_id(flight_id)
            mydb.update_status_in_flight_price_query_task_tbl(flight_id,1,search_date)
            
            worker_logger.info("%s send url : %s\n" %(worker_name,req_url))
            
            crawler_worker.request_one_flight_by_url(flight_id,req_url)
            
            t2 = datetime.datetime.now()
            tx = t2-t1
            worker_logger.info("%s End handle task flight id %d with time [%s] seconds" %(worker_name,flight_id, tx.seconds))
            
            stat_q.put(num)
    finally:
        worker_logger.info(worker_name+" exited")
        print(worker_name, " exited")

def get_flight_info_from_flight_module_element(flight_module_element):
    """
    return a tuple cotains:
    1. flight_price as string
    2. flight_company as string
    """
    price_element_class_name='price-column'
    
    price_element = flight_module_element.find_element_by_css_selector('.flight-module.offer-listing.price-column.offer-price.dollars')
    price = price_element.text()
    
    company_element = flight_module_element.find_element_by_css_selector('.flight-module.offer-listing.flex-card.flex-area-primary.primary-block.secondary')
    company_name = company_element.text()
    
    return price,company_name
    
def get_urls_from_file(filename):
    """
    Get the urls from the file and return as a list.
    """
    url_list = []
    
    with open(filename,'r') as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) == 0:
                continue
            else:
                url_list.append(line)

    return url_list

def test():
#     d = createDriver()
#     
#     url_list = get_urls_from_file('test/url_list.txt')
#     num=1
#     
#     try:
#         for url in url_list:
#             getFlightPrice(d,url,num,1)
#             num+=1
#     finally:    
#         closeDriver(d)
    pass

def init_log():
    """
    #Init the main logger
    """
    global logger_handle
    
    d = str(datetime.date.today())
    t1 = datetime.datetime.now()
    logname='log/air_'+d+'.log'
    logger_handle=logging.FileHandler(logname)
    
    formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s')
    
    logger_handle.setFormatter(formatter)
    
    main_logger=logging.getLogger('[Main]')
    main_logger.addHandler(logger_handle)
    main_logger.setLevel('INFO')
    
    worker_logger= logging.getLogger('[Worker]')
    worker_logger.setLevel('INFO')
    worker_logger.addHandler(logger_handle)
    
    return main_logger

def main():
    init_log()
    test()

if __name__=='__main__':
    main()
