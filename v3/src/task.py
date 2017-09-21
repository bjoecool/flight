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
import os
import time
import argparse
from datetime import date
from datetime import datetime
from datetime import timedelta
import logging
import url
import json
import re

import settings



route_list = []
city_list = []


class FlightQueryTask():
    def __init__(self, task_id=None):
        self.task_id = task_id  # Type is int. A number start from 1 to identify the query task
        self.route_id = None  # Type is int.
        self.machine_name = None
        self.from_city_id = None  # Type is int.
        self.to_city_id = None  # Type is int.
        self.from_city_name = None  # Type is string.
        self.to_city_name = None  # Type is string.
        self.req_url = None
        self.start_date = None  # Type is str
        self.stay_days = None  # Type is int
        self.trip = None  # Type is int. 1 -- oneway, 2 -- roundtrip

        self.state = 0  # 0:unfinished 1:finished
        self.try_times = 0

    def __str__(self):
        return '{}--{}--{}--{}--{}'.format(self.task_id, self.from_city_name, self.to_city_name, self.start_date, self.stay_days)
    
    def get_final_file_name(self):
        """
        Create the final result file name accroding to the ret_dict
        File naming rules: <flight_table_name>_<search_date>_<departure_date>_<trip>_<stay_days>.txt
        
        <flight_table_name> : flight_<from_city_id>_<to_city_id>_price
        <search_date> : The date on which searching this result. Format is YYYY-MM-DD
        <departure_date> : The departure date of this flight plan. Format is YYYY-MM-DD
        <trip> : 1 -- one way.  2 -- round trip
        <staydays> : if <trip> is 1, this is always 0. Otherwise means how many days to stay.
        
        Example: flight_1_5_price_2017-04-01_2017-05-20_2_14.txt
        """
        return 'flight_{}_{}_price_{}_{}_{}_{}'.format(self.from_city_id,
                                                       self.to_city_id,
                                                       datetime.datetime.today().date(),
                                                       self.start_date,
                                                       self.trip,
                                                       self.stay_days)

    def update_state(self, state):
        self.state = state
        
    def print(self):
        print("[route_id] : {}".format(self.route_id))
        print("[task_id] : {}".format(self.task_id))
        print("[from] : {}[{}]".format(self.from_city_name, self.from_city_id))
        print("[to] : {}[{}]".format(self.to_city_name, self.to_city_id))
        print("[start_date] : {}".format(self.start_date))
        print("[stay_days] : {}".format(self.stay_days))
        print("[machine_name] : {}".format(self.machine_name))
        print("[req_url] : {}".format(self.req_url))


class TasksControl():
    res = re.compile(r'res_\d+_(?P<task_id>\d+).txt')

    def __init__(self, route_id):
        self.route_id = route_id
        self.task_list = get_task_list_by_route_id(route_id)
        self.total_tasks = len(self.task_list)
        self.finished_task_num = 0
        
        #Record the tasks put in the queue this time
        self.total_task_num_in_queue = 0
        self.results_dir_empty_times = 0
        self.error_tasks_count = 0 #record the number of error tasks
        
        self.put_tasks_into_queue_times = 0 

    def get_unfinished_task_list(self):
        """
        Return a list contains all unfinished tasks.
        The unfinished task mean the task hasn't been executed or failed 
        """
        return [x for x in self.task_list if x.state == 0]

    def get_task_by_id(self, task_id):
        for task in self.task_list:
            if task.task_id == task_id:
                return task
            
        return None

    def get_task_by_filename(self,filename):
        ret = self.res.search(filename)
        if ret:
            try:
                task_id = ret.group('task_id')
                return self.get_task_by_id(task_id)
            except IndexError:
                return None
        else:
            return None
                        
    def set_task_finished(self, task_id):
        task = self.get_task_by_id(task_id)
        
        try:
            task.state = 1
        except AttributeError:
            print('task is None in set_task_finished')

    def put_tasks_into_queue(self, task_queue, task_list):
        """
        Each item in task_list is an instance of FlightQueryTask
        Only put unfinished task into task_queue
        """
        # Put task list
        self. put_tasks_into_queue_times +=1
        self.total_task_num_in_queue = len(task_list)
        for qtask in task_list:
            d = dict()
            d['cmd'] = 'continue'
            d['task_id'] = qtask.task_id
            d['data'] = qtask.req_url
            d['date'] = datetime.date.today().isoformat()
            d['from_city_id'] = qtask.from_city_id
            d['to_city_id'] = qtask.to_city_id
            d['from_city_name'] = qtask.from_city_name
            d['to_city_name'] = qtask.to_city_name
            d['start_date'] = qtask.start_date
            d['stay_days'] = qtask.stay_days
            d['trip'] = qtask.trip
            task_queue.put(d)

    def handle_task_results(self, result_dir):
        file_list = self.get_all_files(result_dir)

    def sort_fun(self, name):
        s = name.split('_')[2]
        s1 = s.split('.')[0]
        n = int(s1)

        return n

    def get_all_files(self, dir_name):
        """
        Go through the dir and return all files as a list
        """
        file_list = []
        for root, dirs, files in os.walk(dir_name):
            new_files = sorted(files, key=self.sort_fun)
            for f in new_files:
                if f[-4:] == '.txt' or f[-4:] == '.err':
                    new_f = os.path.join(root, f)
                    file_list.append(new_f)

        return file_list


    def save_result_into_file(self, task, ret_dict,dir_name):
        filename = task.get_final_file_name
        
        with open(filename,'w') as f:
            json.dump(ret_dict['flight_list'],f,sort_keys=True)
        
    def analyze_results(self, dir_name, final_ret_dir):
        """
        Analyze the original result files in the dir_name, and put the final result
        into file and database.
        """
        global logger
        global g_total_task_num

        finished_task_num = 0
        file_list = self.get_all_txt_files(dir_name)
        if not file_list:
            self.results_dir_empty_times += 1
            
        try:
            for f in file_list:
                task = self.get_task_by_filename(f)
                if task is None:
                    logger.error("Failed to get task from {}".format(f))
                    continue

                self.total_task_num_in_queue -= 1
                
                if f[-4:] == '.err':
                    self.error_tasks_count +=1
                    cmd = "rm -rf " + f
                    os.system(cmd)
                    continue
                
                ret, ret_dict = pa.parse_result_file_v2(f)

                if ret == False:
                    logger.error("Error happened in analyzing %s" % (f))
                    self.error_tasks_count +=1
                    cmd = "rm -rf " + f
                    os.system(cmd)
                    continue
                else:
                    flight_list = ret_dict['flight_list']
                    logger.info("%s --- result number %d" % (f, len(flight_list)))
                    
                    task.update_state(1)
                    
                final_file_name = os.path.join(final_ret_dir, task.get_final_file_name())
                
                with open(final_file_name,'w') as f:
                    json.dump(ret_dict['flight_list'],f,sort_keys=True)

                cmd = "rm -rf " + f
                os.system(cmd)

        except Exception as e:
            print(e)

        return finished_task_num

    def queue_is_empty(self):
        return (self.total_task_num_in_queue == 0)
    
    def get_unfinished_task_num(self):
        
        for task in self.task_list:
            if task.state == 0:
                pass

    def check_all_task_finished(self):
        """
        Return true if all tasks are finished.
        """
        pass
        
    
def create_one_task_url(from_city_item, to_city_item, trip, start_date, return_date):
    flight = {}
    flight['from'] = from_city_item['ap_name']
    flight['to'] = to_city_item['ap_name']
    flight['trip'] = trip
    flight['start_date'] = start_date
    flight['return_date'] = return_date
    flight['adults'] = 1
    flight['children'] = 0
    flight['children_age'] = 0
    flight['cabinclass'] = 'economy'

    url_creater = url.ExpediaReqURL()
    req_url = url_creater.createURL(**flight)

    return req_url


def get_today_tasks_from_file(machine_name, route_filename):
    """
    The route_filename is a json format file contains route information.
    """


def get_route_list(machine_name):
    fdb = db.FlightPlanDatabase()
    fdb.connectDB()

    route_list = fdb.get_route_list(machine_name)

    fdb.disconnectDB()

    return route_list


def get_route_list_from_csv(filename, machine_name=None):
    """
    Get the route list from csv file which contains all route information.
    If mahine_name is None , return all routes, otherwise only return
    the route which machine match machine_name.
    filename -- the csv file name.
    """

    with open(filename, 'r') as f:
        file_lines_list = f.readlines()[1:]

    route_list = []

    for line in file_lines_list:
        line = line.strip()
        items = line.split(',', maxsplit=6)
        route = dict()
        route['id'] = int(items[0])
        route['machine_name'] = items[1]
        route['from_city_id'] = items[2]
        route['to_city_id'] = items[3]
        route['from_city_name'] = items[4]
        route['to_city_name'] = items[5]
        route['table_name'] = items[6]

        if machine_name is not None:
            if route['machine_name'] != machine_name:
                continue

        route_list.append(route)

    return route_list


def get_city_list_from_csv(filename):
    with open(filename, 'r') as f:
        file_lines_list = f.readlines()[1:]

    city_list = []
    for line in file_lines_list:
        line = line.strip()
        items = line.split(',', maxsplit=3)
        city = dict()
        city['id'] = items[0]
        city['name'] = items[1]
        city['ap_acronym'] = items[2]
        ap_name = items[3]
        if ap_name[0:1] == '"':
            ap_name = ap_name[1:-1]
        city['ap_name'] = ap_name

        city_list.append(city)

    return city_list


def get_city_from_id(city_list, city_id):
    for city in city_list:
        if city['id'] == city_id:
            return city

    return []
    # [return city if city['id'] == city_id else [] for city in city_list]


def get_today_tasks(machine_name):
    '''
    This function will return the task_list
    Every task in the task_list is a class FlightQueryTask instance
    '''
#     fdb = db.FlightPlanDatabase()
#     fdb.connectDB()

#     route_list = fdb.get_route_list(machine_name)
    task_url_list = []
    task_num = 1
    for route in route_list:
        if machine_name != route['machine_name']:
            continue

        from_city_id = route['from_city_id']
        to_city_id = route['to_city_id']

        from_city_name = route['from_city_name']
        to_city_name = route['to_city_name']

        from_city_item = get_city_from_id(city_list, from_city_id)
        to_city_item = get_city_from_id(city_list, to_city_id)

        for offset_days in range(1, 181):
            start_date = date.today() + timedelta(days=offset_days)
            # oneway flight trip
            task_url = create_one_task_url(from_city_item, to_city_item, 'oneway', start_date, start_date)
            task = FlightQueryTask(task_num)
            task_num = task_num + 1
            task.from_city_id = from_city_id
            task.to_city_id = to_city_id
            task.from_city_name = from_city_name
            task.to_city_name = to_city_name
            task.machine_name = machine_name
            task.req_url = task_url
            task.start_date = start_date.isoformat()
            task.stay_days = 0
            task.trip = 1
            task_url_list.append(task)

            # round trip flight
            for stay_days in [7, 14, 21, 28]:
                return_date = start_date + timedelta(days=stay_days)
                task_url = create_one_task_url(from_city_item, to_city_item, 'roundtrip', start_date, return_date)
                task = FlightQueryTask(task_num)
                task_num = task_num + 1
                task.from_city_id = from_city_id
                task.to_city_id = to_city_id
                task.from_city_name = from_city_name
                task.to_city_name = to_city_name
                task.machine_name = machine_name
                task.req_url = task_url
                task.start_date = start_date.isoformat()
                task.stay_days = stay_days
                task.trip = 2
                task_url_list.append(task)

#     fdb.disconnectDB()

    return task_url_list


def get_route_by_id(route_id):
    for route in route_list:
        if route['id'] == route_id:
            return route

    return None


def get_tasks_by_route(route):
    """
    Create task list according to route.

    """
    task_url_list = []
    task_num = 1

    route_id = route['id']

    from_city_id = route['from_city_id']
    to_city_id = route['to_city_id']

    from_city_name = route['from_city_name']
    to_city_name = route['to_city_name']

    from_city_item = get_city_from_id(city_list, from_city_id)
    to_city_item = get_city_from_id(city_list, to_city_id)

    machine_name = route['machine_name']

    for offset_days in range(1, 181):
        start_date = date.today() + timedelta(days=offset_days)
        # oneway flight trip
        task_url = create_one_task_url(from_city_item, to_city_item, 'oneway', start_date, start_date)
        task = FlightQueryTask(task_num)
        task_num = task_num + 1
        task.route_id = route_id
        task.from_city_id = from_city_id
        task.to_city_id = to_city_id
        task.from_city_name = from_city_name
        task.to_city_name = to_city_name
        task.machine_name = machine_name
        task.req_url = task_url
        task.start_date = start_date.isoformat()
        task.stay_days = 0
        task.trip = 1
        task_url_list.append(task)

        # round trip flight
        for stay_days in [7, 14, 21, 28]:
            return_date = start_date + timedelta(days=stay_days)
            task_url = create_one_task_url(from_city_item, to_city_item, 'roundtrip', start_date, return_date)
            task = FlightQueryTask(task_num)
            task_num = task_num + 1
            task.route_id = route_id
            task.from_city_id = from_city_id
            task.to_city_id = to_city_id
            task.from_city_name = from_city_name
            task.to_city_name = to_city_name
            task.machine_name = machine_name
            task.req_url = task_url
            task.start_date = start_date.isoformat()
            task.stay_days = stay_days
            task.trip = 2
            task_url_list.append(task)

    return task_url_list


def get_task_list_by_route_id(id):
    route = get_route_by_id(id)
    if route is None:
        return []
    else:
        return get_tasks_by_route(route)


def print_task_list(task_list):
    for tk in task_list:
        tk.print()
        print('')


def run_query_task(num, task):
    print("worker is running {}".format(task))


route_list = get_route_list_from_csv(settings.ROUTE_LIST_FILE)
city_list = get_city_list_from_csv(settings.CITY_LIST_FILE)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('cmd', help='Command [print_route,print_task]')
    parser.add_argument('--id', help='id name')

    args = parser.parse_args()

    cmd_ind = args.cmd
    obj_id = args.id

    if cmd_ind == 'print_task':
        route = get_route_by_id(obj_id)
        task_list = get_tasks_by_route(route)
        print_task_list(task_list)
        print("total tasks is %d" % len(task_list))
    elif cmd_ind == 'print_route':
        route = get_route_by_id(int(obj_id))
        print(route)
    elif cmd_ind == 'test':
        task_list = get_task_list_by_route_id(1)
        # print_task_list(task_list)
        # [print(''.format(x)) for x in task_list]
        # print type(task_list[1])
        t = task_list[0]
        print(t)
    else:
        print("Invalid cmd input!")


if __name__ == '__main__':
    main()
