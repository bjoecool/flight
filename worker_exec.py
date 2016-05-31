#!/usr/local/bin/python3

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
    driver.close()
    
def runDriver(driver,url,id):
    t1 = datetime.datetime.now()
    driver.get(url)
    ret = True
    t2 = datetime.datetime.now()
    tx = t2-t1
    logging.info("driver.get cost %d seconds for id[%d]" %(tx.seconds,id))
    try:
        t1 = datetime.datetime.now()
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "feedbackAndImprovements")))
        t2 = datetime.datetime.now()
        tx = t2-t1
        logging.info("WebDriverWait cost %d seconds" %tx.seconds)
    except TimeoutException as tterr:
        logging.info("Time out for get URL[%d]" %(id))
        ret = False
    finally:
        return ret

def execTask(task_q,result_q, stat_q,num):
    """Execute task coming from the task_q squeue"""
    name = "[worker_"+str(num)+"]"
    logging.info(name+" started")
    print(name, " started")
    
    mydb = db.FlightPlanDatabase()
    mydb.connectDB()
    
    driver = createDriver()
    
    while(1):
        if task_q.empty() == True:
            time.sleep(10)
            continue
        d = task_q.get()
        
        if d['cmd']=='exit':
            break
        
        t1 = datetime.datetime.now()
        flight_id = d['data']
        print("%s Start handle task with flight id %d" %(name,flight_id))
        logging.info("%s Start handle task with flight id %d" %(name,flight_id))
        
        result_q.put(flight_id)
        
        flight = mydb.get_flight_by_id(flight_id)
        
        url_creater=url.ExpediaReqURL()
        req_url = url_creater.createURL(**flight)
        logging.info("%s send url : %s\n" %(name,req_url))
        getFlightPrice(driver, req_url,flight_id, num)
        t2 = datetime.datetime.now()
        tx = t2-t1
        logging.info("%s End handle task flight id %d with time [%s] seconds" %(name,flight_id, tx.seconds))
        print("%s End handle task flight id %d with time [%s] seconds" %(name,flight_id, tx.seconds))
        
        # Put the worker number into the stat queue
        stat_q.put(num)
        
    closeDriver(driver)
    logging.info(name+" exited")

def getFlightPrice(driver, url, id, worker_num):
        
    flight_id=str(id)
    
    re = Recorder(flight_id,recorder.RecorderMode.binary)
    
    if runDriver(driver,url,id)==True:
        t = driver.title
        print(t)
        
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
        
        t1 = datetime.datetime.now()
        getFlightPrice(d,url2,2,1)
        t2 = datetime.datetime.now()
        tx = t2-t1
        print("Total cost time for url2 is %d seconds" %tx.seconds)
         
        t1 = datetime.datetime.now()
        getFlightPrice(d,url3,3,1)
        t2 = datetime.datetime.now()
        tx = t2-t1
        print("Total cost time for url3 is %d seconds" %tx.seconds)
    
    finally:    
        closeDriver(d)

def main():
    test()

if __name__=='__main__':
    main()
