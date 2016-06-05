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
    
#    driver = webdriver.Firefox()
    return driver

def closeDriver(driver):
#     driver.close()
    driver.quit()
    
def runDriver(driver,url,id):
    t1 = datetime.datetime.now()
    driver.get(url)
    ret = True
    t2 = datetime.datetime.now()
    tx = t2-t1
    logging.info("%s driver.get cost %d seconds for id[%d]" %(worker_name,tx.seconds,id))
    try:
        t1 = datetime.datetime.now()
        time.sleep(15)
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "feedbackAndImprovements")))
        t2 = datetime.datetime.now()
        tx = t2-t1
        logging.info("%s WebDriverWait cost %d seconds" %(worker_name,tx.seconds))
    except TimeoutException as tterr:
        logging.info("%s Time out for get URL[%d]" %(worker_name,id))
        ret = False
    except Exception as err:
        print("error ",err)
    finally:
        return ret

def execTask(task_q,result_q, stat_q,num):
    """Execute task coming from the task_q squeue"""
    global worker_name
    worker_name = "[worker_"+str(num)+"]"
    logging.info(worker_name+" started")
    print(worker_name, " started")
    
    mydb = db.FlightPlanDatabase()
    mydb.connectDB()
    
    driver = createDriver()
    
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
            logging.info("%s Start handle task with flight id %d" %(worker_name,flight_id))
            
            result_q.put(flight_id)
            
            flight = mydb.get_flight_by_id(flight_id)
            mydb.update_status_in_flight_price_query_task_tbl(flight_id,1,search_date)
            
            url_creater=url.ExpediaReqURL()
            req_url = url_creater.createURL(**flight)
            logging.info("%s send url : %s\n" %(worker_name,req_url))
            
            getFlightPrice(driver, req_url,flight_id, num)
            
            t2 = datetime.datetime.now()
            tx = t2-t1
            logging.info("%s End handle task flight id %d with time [%s] seconds" %(worker_name,flight_id, tx.seconds))
            print("%s End handle task flight id %d with time [%s] seconds" %(worker_name,flight_id, tx.seconds))
            
            # Put the worker number into the stat queue
            stat_q.put(num)
    finally:
        closeDriver(driver)
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
        
#         flight_module_element_list = driver.find_elements_by_css_selector('.flight-module.offer-listing')
        
#         price_element = driver.find_element_by_css_selector('.flight-module.offer-listing.price-column.offer-price')
#         p = price_element.text()
#         
#         company_element = driver.find_element_by_css_selector('.flight-module.offer-listing.flex-card.flex-area-primary.primary-block.secondary')
#         c = company_element.text()
        
#         print("p = %s, c= %s" %(p,c))
#         
#         for flight_module_element in flight_module_element_list:
#             print(flight_module_element)
#             price,company = get_flight_info_from_flight_module_element(flight_module_element)
#             print('price is %s' %price)
#             break


        time.sleep(1)
        re.finish()
    else:
        print("worker[%d] failed to handle flight_id[%d]" %(worker_num, id))

def test():
    d = createDriver()
    url1='''https://www.expedia.com.au/Flights-Search?trip=oneway&leg1=from:SYD,to:SHA,departure:16/06/2016TANYT&passengers=children:0,adults:1,seniors:0,infantinlap:Y&mode=search'''
    
    url2='''https://www.expedia.com.au/Flights-Search?trip=oneway&leg1=from:SYD,to:SHA,departure:17/06/2016TANYT&passengers=children:0,adults:1,seniors:0,infantinlap:Y&mode=search'''
    
    url3='''https://www.expedia.com.au/Flights-Search?trip=oneway&leg1=from:SYD,to:SHA,departure:18/06/2016TANYT&passengers=children:0,adults:1,seniors:0,infantinlap:Y&mode=search'''
    
    try:
        t1 = datetime.datetime.now()
        getFlightPrice(d,url1,1,1)
        t2 = datetime.datetime.now()
        tx = t2-t1
        print("Total cost time for url1 is %d seconds" %tx.seconds)
        
#         t1 = datetime.datetime.now()
#         getFlightPrice(d,url2,2,1)
#         t2 = datetime.datetime.now()
#         tx = t2-t1
#         print("Total cost time for url2 is %d seconds" %tx.seconds)
#          
#         t1 = datetime.datetime.now()
#         getFlightPrice(d,url3,3,1)
#         t2 = datetime.datetime.now()
#         tx = t2-t1
#         print("Total cost time for url3 is %d seconds" %tx.seconds)
    
    finally:    
        closeDriver(d)

def main():
    test()

if __name__=='__main__':
    main()
