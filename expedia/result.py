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
import pa as pa
from enum import Enum

logger = None

class BlockParserStat(Enum):
    not_start = 0
    start_block = 1  #find Result
    in_block = 2 #find content but not Result when in start_block or in_block state

def sort_fun(name):
    s = name.split('_')[2]
    s1 = s.split('.')[0]
    n = int(s1)
    
    return n

def print_flight_list(fdb, flight_id,search_date,flight_list):
    print('flight_id = %s, search_date = %s' %(flight_id,search_date))

    i = 1
    for flight_info in flight_list:
        print('Result[%d], %s' %(i,flight_info['price']))
        i +=1
        for key in flight_info.keys():
            print('\t%s -- %s' %(key,flight_info[key]))
        print('\n')

    
    print('\n\n')
                
def update_flight_list_into_db(fdb, table_name,start_date,stay_days,trip,flight_list,value):
    if flight_id == None or search_date == None:
        return
    
    flight_list_len = len(flight_list)
    if flight_list_len > 0:
#         fdb.update_status_in_flight_price_query_task_tbl(flight_id, value, search_date)

        for flight_info in flight_list:
            fdb.add_into_flight_price_tbl(table_name,flight_info)
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

    #Append the last one,don't forget it
    block_list.append(block_info)
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
    flight_info['dep_time'] as a string   ---departure time
    flight_info['arr_time'] as a string   ---arrival time
    flight_info['span_days'] as a int  ---flight span days, default 0
    flight_info['stop'] as a string --- n stop  or direct
    flight_info['stop_info'] as a string --- stop information
    """
    flight_info = None
    
    line_1 = block_info[0]
    
    if line_1.find(b'Result ')==0 and b'$' in line_1:
        price = line_1.split(b'$',maxsplit=1)[1]
        price = price.strip()
        if price != None:
            flight_info=dict()
            flight_info['price']=price.decode()
        else:
            return flight_info
    else:
        return None
    
    i = 0
    j=1
    for line in block_info:
        s = line
        if re.search(b'.*m - .*m$',s)!=None:
            t = s.split(b'-',maxsplit=1)
            dep_time = t[0].strip()
            arr_time = t[1].strip()
            
            flight_info['dep_time'] = dep_time.decode()
            flight_info['arr_time'] = arr_time.decode()
            flight_info['span_days'] = 0
            
            offset_num = 0
            company_name = block_info[i+1+offset_num].strip()
            duration = block_info[i+2+offset_num].strip()
            start_from = block_info[i+3+offset_num].strip()
            stop = block_info[i+4+offset_num].strip()
            if b'stop' in stop:
                stop_info = block_info[i+5+offset_num].strip()
            else:
                stop_info = None
            
            flight_info['company'] = company_name.decode()
            flight_info['duration'] = duration.decode()
            flight_info['stop'] = stop.decode()
            if stop_info != None:
                flight_info['stop_info'] = stop_info.decode()
            else:
                flight_info['stop_info'] = ''
        elif re.search(b'.*m - .*m +.*$',s)!=None:
            t = s.split(b'-',maxsplit=1)
            dep_time = t[0].strip()
            t2 = t[1].split(b'+',maxsplit=1)
            arr_time = t2[0].strip()
            span_days = t2[1].strip()
            
            flight_info['dep_time'] = dep_time.decode()
            flight_info['arr_time'] = arr_time.decode()
            flight_info['span_days'] = int(span_days.decode())
            
            offset_num = 1
            company_name = block_info[i+1+offset_num].strip()
            duration = block_info[i+2+offset_num].strip()
            start_from = block_info[i+3+offset_num].strip()
            stop = block_info[i+4+offset_num].strip()
            if b'stop' in stop:
                stop_info = block_info[i+5+offset_num].strip()
            else:
                stop_info = None
            
            flight_info['company'] = company_name.decode()
            flight_info['duration'] = duration.decode()
            flight_info['stop'] = stop.decode()
            if stop_info != None:
                flight_info['stop_info'] = stop_info.decode()
            else:
                flight_info['stop_info'] = ''
        i +=1

    return flight_info
        
def analyze_one_file(filename):
    """
    Analyze one result file and return the result as a tuple
    The return tuple include 3 elements:
    flight_list: Every element is a flight_info dict
        flight_info dict has following keys:
        flight_info['id']
        flight_info['search_date']
        flight_info['price']  as a string
        flight_info['company'] as a string
        flight_info['dep_time'] as a string   ---departure time
        flight_info['arr_time'] as a string   ---arrival time
        flight_info['span_days'] as a int  ---flight span days, default 0
        flight_info['stop'] as a string --- n stop  or direct
        flight_info['stop_info'] as a string --- stop information
    """
    global logger
    
    flight_id=None
    search_date=None
    flight_list=[]
    ret = True
    
    try:
        t1 = datetime.datetime.now()
    
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
                    search_date = search_date.split(' ')[0]
            
            # Now get the flight list
            block_list = get_block_list(f.readlines())
            
    #         num=1
            for block in block_list:
                flight_info = parse_block_info(block)
                if flight_info != None:
                    flight_info['id'] = flight_id
                    flight_info['search_date'] = search_date
                    flight_list.append(flight_info)
            
        t2 = datetime.datetime.now()
        tx = t2-t1
        flight_list_len = len(flight_list)
        logger.info("%s [%s] --- result number %d, cost seconds %d" %(filename, flight_id,flight_list_len,tx.seconds))
    except Exception as e:
#         print('Error happened when analyze file %s, the %s',filename, e.value)
        ret = False
        logger.error("Error happened in analyzing %s,Error is: %s " %(filename, e))
        print("Error happened in analyzing %s,Error is: %s " %(filename, e))
    finally:
        return ret,flight_id,search_date,flight_list

def print_flight_info_dict(flight_info_dict):
    ret_dict = flight_info_dict
    task_id = ret_dict['task_id']
    search_date = ret_dict['search_date']
    table_name = ret_dict['table_name']
    start_date = ret_dict['start_date']
    stay_days = ret_dict['stay_days']
    trip = ret_dict['trip']
    flight_list = ret_dict['flight_list']
    
    for flight_info in flight_list:
        price = flight_info['price']
        company_name = flight_info["company"]
        dep_time = flight_info['dep_time']
        arr_time = flight_info['arr_time']
        duration = flight_info['duration']
        span_days = flight_info['span_days']
        stop = flight_info['stop']
        stop_info = flight_info['stop_info']
        flight_code = flight_info["flight_code"]
        plane = flight_info["plane"]

        
        print('''[table_name]:''',table_name)
        print('''[task_id]:''',task_id)
        print('''[start_date]:''',start_date)
        print('''[stay_days]:''',stay_days)
        print('''[trip]:''',trip)
        print('''[price]:''',price)
        print('''[company_name]:''',company_name)
        print('''[dep_time]:''',dep_time)
        print('''[arr_time]:''',arr_time)
        print('''[duration]:''',duration)
        print('''[span_days]:''',span_days)
        print('''[stop]:''',stop)
        print('''[stop_info]:''',stop_info)
        print('''[flight_code]:''',flight_code)
        print('''[plane]:''',plane)
        print('')
        
def analyze_results_to_db(dir_name='results',test_flag=False):
    """
    Analyze the result files stored in the dir directory.
    Store the results in the database.
    """
    global logger
    
    file_list = get_all_files(dir_name)
    
    fdb = db.FlightPlanDatabase()
    fdb.connectDB()
    try:
        for f in file_list:
            ret, ret_dict = pa.parse_one_file(f)
            if test_flag == True:
                print_flight_info_dict(ret_dict)
                continue
            
            if ret==True:
                task_id = ret_dict['task_id']
                search_date = ret_dict['search_date']
                table_name = ret_dict['table_name']
                start_date = ret_dict['start_date']
                stay_days = ret_dict['stay_days']
                trip = ret_dict['trip']
                flight_list = ret_dict['flight_list']
                
#                 update_flight_list_into_db(fdb,flight_id,search_date,flight_list,2)
                
                flight_list_len = len(flight_list)
                if flight_list_len > 0:
            #         fdb.update_status_in_flight_price_query_task_tbl(flight_id, value, search_date)
                    for flight_info in flight_list:
                        fdb.add_into_flight_price_tbl(table_name,start_date,stay_days,trip,search_date,flight_info)
                logger.info("%s [%s] --- result number %d" %(f, task_id,flight_list_len))
                print("%s [%s] --- result number %d" %(f, task_id,flight_list_len))
            else:
                logger.error("Error happened in analyzing %s" %(f))
                
#             cmd="rm -rf "+f
#             os.system(cmd)
    finally:
        fdb.disconnectDB()

def schedule_results_analyze(dir_name='results', interval_time=10):
    """
    This function start a task to analyze the results in the dir_name
    by invoking the analyze_results at a interval_time.
    interval_time --- how many seconds the function start a task
    """
    global logger
    
    logger.info("Start schedule_results_analyze")
    try:
        while 1:
            analyze_results_to_db(dir_name)
            time.sleep(interval_time)
            
    finally:
        logger.info("End schedule_results_analyze")

def init_log():
    global logger
    
    d = str(datetime.date.today())
    logname='log/result_'+d+'.log'
#     logging.basicConfig(filemode='a', format='%(levelname)s: %(asctime)s %(message)s', level=logging.DEBUG)
    
    #Create a Filehandler
    logger_handle=logging.FileHandler(logname)
    
    # create formatter
    formatter = logging.Formatter('%(levelname)s: %(asctime)s - %(name)-8s %(message)s')

    # add formatter to logger_handle
    logger_handle.setFormatter(formatter)

    #get a logger instance
    logger=logging.getLogger('[result]')
    
    #Add handle    
    logger.addHandler(logger_handle)
    
    #Set level
    logger.setLevel('INFO')

#     logger_handle.emit()
    logger_handle.close()
                
def main():

    init_log()
    
    analyze_results_to_db(dir_name='results',test_flag=True)
#     schedule_results_analyze()
#     t1()
    

def test():
    flight_tup = analyze_one_file('results/res_20160602_168183.txt')
    if flight_tup != None:
        for e in flight_tup:
            if type(e)==type([]):
                for x in e:
                    print(x)
            else:
                print(e)
def t1():
    flight_list = pa.parse_one_file('results/res_2016-08-15_2122.txt')
    for flight_info in flight_list:
        pa.print_fligth_info(flight_info)
    
if __name__=='__main__':
#     log_test()
    main()
