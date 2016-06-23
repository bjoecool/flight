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
import selenium
import recorder

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from recorder import Recorder

worker_name=["worker_0"]

worker_logger=None

myProxy = "127.0.0.1:3128"

proxy = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': myProxy,
    'ftpProxy': myProxy,
    'sslProxy': myProxy,
    'noProxy': '' # set this value as desired
    })

def createDriver():
    driver = webdriver.Firefox(proxy=proxy)
    
#     driver = webdriver.Firefox()
    return driver

def closeDriver(driver):
#     driver.close()
    driver.quit()
    
def runDriver(driver,url,id):
    global worker_logger
    
    t1 = datetime.datetime.now()
    driver.get(url)
    ret = True
    t2 = datetime.datetime.now()
    tx = t2-t1
    worker_logger.info("%s driver.get cost %d seconds for id[%d]" %(worker_name,tx.seconds,id))
    try:
        t1 = datetime.datetime.now()
        time.sleep(15)
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "feedbackAndImprovements")))
        t2 = datetime.datetime.now()
        tx = t2-t1
        worker_logger.info("%s WebDriverWait cost %d seconds" %(worker_name,tx.seconds))
    except TimeoutException as tterr:
        worker_logger.info("%s Time out for get URL[%d]" %(worker_name,id))
        ret = False
    except Exception as err:
        print("error ",err)
    finally:
        return ret

def execTask(task_q,result_q, stat_q,num,driver):
    """Execute task coming from the task_q squeue"""
    global worker_name
    global worker_logger
    
    worker_name = "[worker_"+str(num)+"]"
    worker_logger= logging.getLogger('[Worker]')
    worker_logger.info(worker_name+" started")
    print(worker_name, " started")
    
    mydb = db.FlightPlanDatabase()
    mydb.connectDB()
    
#     driver = createDriver()
    
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
            print("%s Start handle task with flight id %d" %(worker_name,flight_id))
            worker_logger.info("%s Start handle task with flight id %d" %(worker_name,flight_id))
            
            result_q.put(flight_id)
            
            flight = mydb.get_flight_by_id(flight_id)
            mydb.update_status_in_flight_price_query_task_tbl(flight_id,1,search_date)
            
            url_creater=url.ExpediaReqURL()
            req_url = url_creater.createURL(**flight)
            worker_logger.info("%s send url : %s\n" %(worker_name,req_url))
            
            getFlightPrice(driver, req_url,flight_id, num)
            
            t2 = datetime.datetime.now()
            tx = t2-t1
            worker_logger.info("%s End handle task flight id %d with time [%s] seconds" %(worker_name,flight_id, tx.seconds))
            print("%s End handle task flight id %d with time [%s] seconds" %(worker_name,flight_id, tx.seconds))
            
            stat_q.put(num)
    finally:
#         closeDriver(driver)
        logging.info(worker_name+" exited")

def get_flight_info_from_flight_module_element(flight_module_element):
    """
    return a tuple cotains:
    1. flight_price as string
    2. flight_company as string
    """
    price_element_class_name='price-column'
#     flight_company_class_name=''
    
    price_element = flight_module_element.find_element_by_css_selector('.flight-module.offer-listing.price-column.offer-price.dollars')
    price = price_element.text()
    
    company_element = flight_module_element.find_element_by_css_selector('.flight-module.offer-listing.flex-card.flex-area-primary.primary-block.secondary')
    company_name = company_element.text()
    
    return price,company_name
    
def getFlightPrice(driver, url, id, worker_num):
    
#     flight_module_class_name='flight-module.segment.offer-listing'
        
    flight_id=str(id)
    
    re = Recorder(flight_id,recorder.RecorderMode.binary)
    
    if runDriver(driver,url,id)==True:
        flight_id="<flight_id>"+flight_id
        re.writeN(flight_id)
        re.write("<url>")
        re.writeN(url)
        t = datetime.datetime.now().strftime("%Y-%m-%d %H %M %S")
        search_date = "<search_date>"+t
        re.writeN(search_date)
          
        time.sleep(1)
        body_element = driver.find_element_by_tag_name('body')
        re.writeN(body_element.text)

        time.sleep(1)
        re.finish()
    else:
        print("worker[%d] failed to handle flight_id[%d]" %(worker_num, id))

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
    d = createDriver()
    
    url_list = get_urls_from_file('test/url_list.txt')
    num=1
    
    try:
        for url in url_list:
            getFlightPrice(d,url,num,1)
            num+=1
    finally:    
        closeDriver(d)

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
