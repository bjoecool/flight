#!/usr/local/bin/python3
# Copyright (C) 2015-2025 Fang,jing   <jingwangian@gmail.com>
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

class Result():
    def __init__(self, dir="results"):
        self.dir = dir
        self.fdb = db.FlightPlanDatabase()
      
       
    def handleResults(self):
        """
        This function is used to handle the result file in the results directory.
        It will get the price and company name in the file, insert these info
        into the flight_price table and update the status in the table
        flight_price_query_task;
        """
        self.fdb.connectDB()
        
        file_list = self.getFileNameList(self.dir)
        num_files = 0;
        for file in file_list:
            flight_id,search_date,price_list,company_list = self.handleOneResultFile(file)
            
            price_list_len=len(price_list)
            company_list_len=len(company_list)
            
            if price_list_len == 0:
                logging.warning('No price information in the result file[%s]' %file)
                continue
            
            if company_list_len == 0:
                logging.warning('No company name information in the result file[%s]' %file)
                continue
            
            result_num = min(len(price_list),len(company_list))
                       
            search_date=search_date.split(' ')[0]
            
            if result_num > 0:
                self.fdb.update_status_in_flight_price_query_task_tbl(flight_id, 1,search_date) #update status in flight_price_query_task
                
            for i in range(result_num):
                try:
                    self.fdb.add_into_flight_price_tbl(flight_id,
                                                       price_list[i],
                                                       company_list[i],
                                                       search_date)
                except IndexError:
                    logging.warning("Index error for i is %d, file is %s" %(i,file))
                    break
                except Exception as err:
                    logging.error('Error happened: %s' %str(err))
                    break
                
            num_files+=1
            
            print('Finshed handle file[%s] with results[%d]' %(file,result_num))
            logging.info('Finshed handle file[%s] with results[%d]' %(file,result_num))

        self.fdb.disconnectDB()
        return num_files
        
    def handleOneResultFile(self,filename):
        """
        Analyze one file and get the result.
        Return the result as a tuple including following elements:
        flight_id --- A string indicate the flight id
        search_date --- A string indicate the date which get the result.
        result_list --- A list include all price
        company_list --- A list includes all airline company name. 
        The company_list[n] maps to the result_list[n].
        """
        #Now start to handle the results
        flight_id="None"
        search_date="None"
        
        with open(filename) as f:
            # get flight_id
            line = f.readline()
            if len(line)>0:
                if line.find("<flight_id>") != -1:
                    if line[-1] == '\n':
                        line=line[0:-1]
                    flight_id=line[len("<flight_id>"):]
            # get search_date
            line = f.readline()
            line = f.readline()
            if len(line)>0:
                if line.find("<search_date>") != -1:
                    if line[-1] == '\n':
                        line=line[0:-1]
                    search_date=line[len("<search_date>"):]
            
            result_list=[]
            company_list=[]
            
            # start to get the price        
            for line in f.readlines():
                try:
                    if line.find("Result ") != -1:
                        if line[-1] == '\n':
                            line=line[0:-1]
                        s=line.split(",",maxsplit=1)
                        s1=s[1]
                        info=s1.lstrip().replace("$","")
                        result_list.append(info)
                    elif line.find("company_name_") != -1:
                        if line[-1] == '\n':
                            line=line[0:-1]
                            s=line.split(":",maxsplit=1)
                            s1=s[1]
                            company_list.append(s1)
                except Exception as err:
                    print("Error happened : ", str(err))
                    
        cmd="mv "+filename +" "+"backup/"
        os.system(cmd)
        
        return (flight_id,search_date,result_list,company_list)

    def sort_fun(self,name):
        s = name.split('_')[2]
        s1 = s.split('.')[0]
        n = int(s1)
        
        return n
        
    def getFileNameList(self,dir_name):
        """
        Search the resutls dir and return the file names as a list
        """
        file_list=[]
        for root,dirs,files in os.walk(dir_name):
            new_files=sorted(files,key=sort_fun)
            for f in new_files:
                if '.txt' in f:
                    print(f)
                    new_f=os.path.join(root,f)
                    file_list.append(new_f)
                
        return file_list
    
    def removeFile(self,filename):
        pass

def readResults():
    logging.info("Function result.readResults was invoked")
    re = Result()
    try:
        while 1:
            num_files = re.handleResults();
#             print("Total %d result files are handled" %num_files)
            logging.info("Total %d result files are handled" %num_files)
            time.sleep(10)
    
    except Exception as err:
        print("error happend %s" %str(err))
    finally:
        print("Exit readResults")
#     t1 = datetime.datetime.now()
#     
#     num_files = re.handleResults();
# 
#     t2 = datetime.datetime.now()
#     
#     tx = t2-t1
#     logging.info("Total %d result files are handled" %num_files)
#     logging.info("Total cost time is %d seconds" %tx.seconds)

def sort_fun(name):
    s = name.split('_')[2]
    s1 = s.split('.')[0]
    n = int(s1)
    
    return n

def test3(dir_name):
    re = Result()
    file_list = re.getFileNameList(dir_name)
    
    for f in file_list:
        print(f)
    print('total files are',len(file_list))
    
def test2(top):
    for root,dirs,files in os.walk(top):
        print('root is %s' %root)
        print("============dirs are as following============")
        for d in dirs:
            print("   %s" %d)
        new_files=sorted(files,key=sort_fun)
        print("============file list ============")
        for f in files:
            print("   %s" %os.path.join(root,f))
           
        print("============new file list============")
        for f in new_files:
            print("   %s" %os.path.join(root,f))

def test4():
#     with open('results/res_20160602_168183.txt','rb') as f:
#         block_list = get_block_list(f.readlines())
#         print("len = %d" %len(block_list))
#         for block in block_list:
#             print(block)
#             f = parse_block_info(block)
#             print(f)
#             print('\n')
            
    flight_tup = analyze_one_file('results/res_20160602_168183.txt')
    if flight_tup != None:
        for e in flight_tup:
            if type(e)==type([]):
                for x in e:
                    print(x)
            else:
                print(e)

def get_all_files(dir):
    """
    Go through the dir and return all files as a list
    """
    
def analyze_results(dir):
    """
    Analyze the result files stored in the dir directory.
    Store the results in the database.
    """
    pass

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
#             print(line)
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

def main():
#     readResults()
#     test3('results')
    test4()
    
if __name__=='__main__':
    main()
