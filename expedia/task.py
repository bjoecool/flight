#!/usr/bin/env python3
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


# This module is used to create crawling tasks
# Created by Wang,Jing 
# Created at 2017-03-19
 
import sys
import time
import argparse
from datetime import date
from datetime import datetime
from datetime import timedelta
import logging
import db
import url

class FlightQueryTask():
    def __init__(self,task_id=None):
        self.task_id = task_id  #Type is int. A number start from 1 to identify the query task
        self.machine_name=None
        self.from_city_id=None  #Type is int. 
        self.to_city_id=None    #Type is int. 
        self.req_url=None
        self.start_date=None    #Type is str
        self.stay_days=None     #Type is int
        self.trip=None          #Type is int. 1 -- oneway, 2 -- roundtrip
        
        self.state=0  #Used by main.py , 1: success  0:failed  
        self.try_times=0
        
    def print(self):
        print("[task_id] : %d" %self.task_id)
        print("[from_id] : %s" %self.from_city_id)
        print("[to_id] : %s" %self.to_city_id)
        print("[machine_name] : %s" %self.machine_name)
        print("[req_url] : %s" %self.req_url)

def create_one_task_url(from_city_item,to_city_item,trip,start_date,return_date):
        flight={}
        flight['from'] = from_city_item['ap_name']
        flight['to'] = to_city_item['ap_name']
        flight['trip'] = trip
        flight['start_date'] = start_date
        flight['return_date'] = return_date
        flight['adults'] = 1
        flight['children'] = 0
        flight['children_age'] = 0
        flight['cabinclass'] = 'economy'
        
        url_creater=url.ExpediaReqURL()
        req_url = url_creater.createURL(**flight)
        
        return req_url
            
def get_today_tasks(machine_name):
    '''
    This function will return the task_list
    Every task in the task_list is a class FlightQueryTask instance
    '''
    fdb = db.FlightPlanDatabase()
    fdb.connectDB()
    
    route_list = fdb.get_route_list(machine_name)
    
    task_url_list = []
    task_num = 1
    for route in route_list:
        if machine_name != route['machine_name']:
            continue
        
        from_city_id=route['from_city_id']
        to_city_id=route['to_city_id']
        
        from_city_item = fdb.get_city_from_id(from_city_id)
        to_city_item = fdb.get_city_from_id(to_city_id)
        
        for offset_days in range(1,181):
            start_date = date.today()+timedelta(days=offset_days)
            #oneway flight trip
            task_url = create_one_task_url(from_city_item,to_city_item,'oneway',start_date,start_date)
            task = FlightQueryTask(task_num)
            task_num = task_num + 1
            task.from_city_id = from_city_id
            task.to_city_id = to_city_id
            task.machine_name = machine_name
            task.req_url = task_url
            task.start_date = start_date.isoformat()
            task.stay_days = 0
            task.trip = 1
            task_url_list.append(task)
            
            #round trip flight
            for stay_days in [7,14,21,28]:
                return_date = start_date + timedelta(days=stay_days)
                task_url = create_one_task_url(from_city_item,to_city_item,'roundtrip',start_date,return_date)
                task = FlightQueryTask(task_num)
                task_num = task_num + 1
                task.from_city_id = from_city_id
                task.to_city_id = to_city_id
                task.machine_name = machine_name
                task.req_url = task_url
                task.start_date = start_date.isoformat()
                task.stay_days = stay_days
                task.trip = 2
                task_url_list.append(task)
        
    fdb.disconnectDB()
    
    return task_url_list

def print_task_list(task_list):
    for tk in task_list:
        tk.print()
        print('')
        
def main():
    parser =argparse.ArgumentParser()
    
    parser.add_argument('cmd',help='Command [print]')
    parser.add_argument('--obj',help='Table to be created[task]')
    
    args = parser.parse_args()
    
    cmd_ind = args.cmd
    obj_name = args.obj
    
#     if obj_name is None:
#         print("Please set table name by using --obj")
#         quit(0)
     
#     init_log()
    
    if cmd_ind == 'print':
        task_list = get_today_tasks('machine1')
        print_task_list(task_list)
        print("total tasks is %d" %len(task_list))
    else:
        print("Invalid cmd input!")
        
if __name__=='__main__':
    main()
