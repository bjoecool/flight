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

import os
import sys

import time
import datetime
import logging
import db
import re
from enum import Enum

class BlockParserStat(Enum):
    not_start = 0
    start_block = 1  #find Result
    in_block = 2 #find content but not Result when in start_block or in_block state

def sort_fun(name):
    s = name.split('_')[2]
    s1 = s.split('.')[0]
    n = int(s1)
    
    return n

def update_flight_list_into_db(fdb, flight_id,search_date,flight_list):
    flight_list_len = len(flight_list)
    if flight_list_len > 0:
        fdb.update_status_in_flight_price_query_task_tbl(flight_id, 2, search_date)

        for flight_dict in flight_list:
            fdb.add_into_flight_price_tbl(flight_id,flight_dict['price'],flight_dict['company'],search_date)
    else:
        fdb.update_status_in_flight_price_query_task_tbl(flight_id, 0, search_date)
  
def get_all_files(dir_name):
    """
    Go through the dir and return all files as a list
    """
    file_list=[]
    for root,dirs,files in os.walk(dir_name):
        new_files=sorted(files,key=sort_fun)
        for f in new_files:
            if '.txt' in f:
                new_f=os.path.join(root,f)
                file_list.append(new_f)
            
    return file_list
    
def get_block_list(lines):
    """
    Read the lines and return the result_list.
    Every result in the result_list is a list contains following information:
        Result 5, $636.77
        Departure
        10:05am - 9:35pm
        Multiple Airlines
        13h 30m
        SYD - PVG
        1 stop
        1h 15m in HKG
        5 left at From
        $636.77
        $636 .77
        one way
        Select
        Select result 5
        Show flight details
        Show Flight Details for result 5
        Good Flight (7.1 out of 10)
    """
    fsm_state = BlockParserStat.not_start
    block_list = []
    for line in lines:
        if line.find(b'Result ')==0:
            if fsm_state == BlockParserStat.not_start:
                fsm_state = BlockParserStat.start_block
                block_info = []
                block_info.append(line)
            elif fsm_state == BlockParserStat.start_block:
                pass
            elif fsm_state == BlockParserStat.in_block:
                fsm_state = BlockParserStat.start_block
                block_list.append(block_info)
                block_info = []
                block_info.append(line)
        else:
            if fsm_state == BlockParserStat.not_start:
                pass
            elif fsm_state == BlockParserStat.start_block:
                fsm_state = BlockParserStat.in_block
                block_info.append(line)
            elif fsm_state == BlockParserStat.in_block:
                block_info.append(line)

    return block_list

def parse_block_info(block_info):
    """
    Input is a block_info with list type contains the flight inforation as following:
        Result 5, $636.77
        Departure
        10:05am - 9:35pm
        Multiple Airlines
        13h 30m
        SYD - PVG
        1 stop
        1h 15m in HKG
        5 left at From
        $636.77
        $636 .77
        one way
        Select
        Select result 5
        Show flight details
        Show Flight Details for result 5
        Good Flight (7.1 out of 10)
    Return a fligh_info dict including following information:
    flight_info['price']  as a string
    flight_info['company'] as a string
    """
    flight_info = None
    
    line_1 = block_info[0]
    
    if line_1.find(b'Result ')==0:
        price = line_1.split(b',',maxsplit=1)[1]
        price = price.strip()
        price = price.replace(b'$',b'').replace(b',',b'')
        if price != None:
            flight_info=dict()
            flight_info['price']=price.decode()
        else:
            return flight_info
    
    i = 0
    for line in block_info:
        s = line
        if re.search(b'.*m - .*m$',s)!=None:
            company_name = block_info[i+1].strip()
            flight_info['company'] = company_name.decode()
            break
        elif re.search(b'.*m - .*m +.*$',s)!=None:
            company_name = block_info[i+2].strip()
            flight_info['company'] = company_name.decode()
            break
        i = i+1
    
    return flight_info
        
def analyze_one_file(filename):
    """
    Analyze one result file and return the result as a tuple
    The return tuple include 3 elements:
    1. flight_id
    2. search_date
    3. flight_list: Every element is a flight_info dict
        flight_info dict has following keys:
        flight_info['price']  ---- the price as a string
        flight_info['company'] ---- the company name as a string
    """
    flight_id="None"
    search_date="None"
    flight_list=[]

    with open(filename,'rb') as f:
        # get flight_id
        line = f.readline().strip()
        if len(line)>0:
            if line.find(b"<flight_id>") != -1:
                if line[-1] == b'\n':
                    line=line[0:-1]
                flight_id=line[len("<flight_id>"):].decode()
                
        # get the url
        line = f.readline()
        
        # get search_date
        line = f.readline().strip()
        if len(line)>0:
            if line.find(b"<search_date>") != -1:
                if line[-1] == b'\n':
                    line=line[0:-1]
                search_date=line[len(b"<search_date>"):].decode()
        
        # Now get the flight list
        block_list = get_block_list(f.readlines())
        
        for block in block_list:
            flight_info = parse_block_info(block)
            if flight_info != None:
                flight_list.append(flight_info)
        
    return flight_id,search_date,flight_list

def analyze_results(dir_name='results'):
    """
    Analyze the result files stored in the dir directory.
    Store the results in the database.
    """
    file_list = get_all_files(dir_name)
    fdb = db.FlightPlanDatabase()
    fdb.connectDB()
    try:
        for f in file_list:
            t1 = datetime.datetime.now()
            flight_id,search_date,flight_list = analyze_one_file(f)
            search_date = search_date.split(' ')[0]
            t2 = datetime.datetime.now()
            tx = t2-t1
            flight_list_len = len(flight_list)
            logging.info("[result] %s [%s] --- result number %d, cost seconds %d" %(f, flight_id,flight_list_len,tx.seconds))
            update_flight_list_into_db(fdb,flight_id,search_date,flight_list)
            
            #Now move the file into backup directory
            cmd="mv "+f +" "+"backup/"
            os.system(cmd)
    finally:
        fdb.disconnectDB()

def schedule_results_analyze(dir_name='results', interval_time=60):
    """
    This function start a task to analyze the results in the dir_name
    by invoking the analyze_results at a interval_time.
    interval_time --- how many seconds the function start a task
    """
    while True:
        time.sleep(interval_time)
        analyze_results(dir_name)
                
def main():
    d = str(datetime.date.today())
    logname='log/result_'+d+'.log'
#     logging.basicConfig(filemode='a', format='%(levelname)s: %(asctime)s %(message)s', level=logging.DEBUG)
    
    #Create a Filehandler
    logger_handle=logging.FileHandler(logname)
    
    # create formatter
    formatter = logging.Formatter('%(levelname)s: %(asctime)s - %(message)s')

    # add formatter to logger_handle
    logger_handle.setFormatter(formatter)

    #get a logger instance
    logger=logging.getLogger('[result]')
    
    #Add handle    
    logger.addHandler(logger_handle)
    
    #Set level
    logger.setLevel('DEBUG')
    
    #Output message
    logger.warning('warning message')
    logger.info('info message')
    logger.debug('debug message')

#     logger_handle.emit()
    logger_handle.close()

def test():
    flight_tup = analyze_one_file('results/res_20160602_168183.txt')
    if flight_tup != None:
        for e in flight_tup:
            if type(e)==type([]):
                for x in e:
                    print(x)
            else:
                print(e)
    
def log_test():
    print("The name is %s" %__name__)
    
    print("login into log_test")
    
    d = str(datetime.date.today())
    logname='log/result_'+d+'.log'
#     logging.basicConfig(filemode='a', format='%(levelname)s: %(asctime)s %(message)s', level=logging.DEBUG)
    
    #Create a Filehandler
    logger_handle=logging.FileHandler(logname)
    
    # create formatter
#     formatter = logging.Formatter('%(levelname)s: %(asctime)s - %(message)s')
    formatter = logging.Formatter('%(name)s -- %(levelname)s -- %(asctime)s - %(message)s')

    # add formatter to logger_handle
    logger_handle.setFormatter(formatter)

    #get a logger instance
    logger=logging.getLogger('[result]')
    
    #Add handle    
    logger.addHandler(logger_handle)
    
    #Set level
    logger.setLevel('DEBUG')
    
    #Output message
    logger.warning('warning message')
    logger.info('info message')
    logger.debug('debug message')
    
    flight_logger=logging.getLogger('[Main]')
    
    flight_logger.info('Using flight_logger to put message')

#     logger_handle.emit()
    logger_handle.close()
    
if __name__=='__main__':
#     log_test()
    main()
