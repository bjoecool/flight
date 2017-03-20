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
import os
import time
import db
import worker
import logging
import datetime
import result

import multiprocessing as mp

import task

# from pyvirtualdisplay import Display


main_logger=None
g_worker_num = 4
g_max_task_num = 5400

process_name='[main]'

logger_handle = None

def start_task():
    global g_worker_num
    global main_logger
    global g_max_task_num
    
    main_logger.info("Enter the start_task function")
    
    max_task_num = g_max_task_num

    # create today's flight schedule and task
    db.init_conf()
    
    task_list = task.get_today_tasks()
    
#     db.create_today_flight_schedule()
#     mydb = db.FlightPlanDatabase()
#     mydb.connectDB()
    
    main_logger.info("Conneted to DB")
    
#     total_task_num = mydb.create_today_task()

    total_task_num = len(task_list)
    
    main_logger.info("Created today's task, total_task_num is %d" %total_task_num)
    
    i = 0
    total_tasks = 0
    
    result_p = start_handle_result_process()
    result_p.start()

    wkm = worker.WorkerMonitor()
    
    task_q,result_q = wkm.create_queue()
    main_logger.info("Created queue.")
    
    try:
        while 1:
#             flight_list = mydb.get_today_task_id(max_task_num)
#             num_tasks = len(flight_list)
            
            num_tasks = len(task_list)
            if num_tasks == 0:
                break
            
            total_tasks += num_tasks 
            
            main_logger.info("Starting workers")
            wkm.start_workers(g_worker_num)
            
            main_logger.info("Starting worker monitor")
            wkm.start_monitor()
                        
            t1 = datetime.datetime.now()
            #Put task list
            for qtask in task_list:
                d = dict()
                d['cmd']='continue'
                d['data'] = qtask.req_url
                d['date'] = t1.strftime('%Y-%m-%d')
                d['from'] = qtask.from_city_id
                d['to'] = qtask.to_city_id
                task_q.put(d)
                i +=1
    
            main_logger.info("%s Put total %d task into queue" %(process_name,num_tasks))
            
            wait_tasks_finished(result_q, num_tasks)
            
            time.sleep(10)
            
            break
    except Exception as err:
        main_logger.info("%s In start_task error happened: %s" %str(err))
    finally:
        main_logger.info("%s Total tasks %d has been executed" %(process_name,total_tasks))
        
        time.sleep(10)
        
        main_logger.info("%s Stop the handle result process" %process_name)

        #Send EXIT command to workers
        for i in range(g_worker_num):
            d = dict()
            d['cmd']='exit'
            task_q.put(d)

        #Wait workers exit
        main_logger.info("Waiting 30 seconds for workers finishing their final works")                       
        time.sleep(30)
                        
        wkm.stop_workers()
        wkm.stop_monitor()
#         mydb.disconnectDB()
        result_p.terminate()

def wait_tasks_finished(result_q, total_task_num):
    task_num = 0
    while(1):
        if result_q.empty() == True:
            time.sleep(5)
            continue
        num = result_q.get()
        task_num = task_num+1
        if task_num>=total_task_num:
            break

def start_handle_result_process():
    main_logger.info('Invoking the result.schedule_results_analyze function')
    p = mp.Process(target=result.schedule_results_analyze, args=('results',20))
    
    return p
    
def delete_tmp():
    global main_logger
    
    main_logger.info("%s Function delete_tmp was invoked" %process_name)
    os.system("rm -rf /tmp/*")

def init_configure():
    global g_worker_num
    global g_max_task_num
    
    try:
        with open("flight.conf") as f:
            for line in f.readlines():
                line = line.strip()
                if line[0:8]=="workers:":
                    g_worker_num = line[8:].strip()
                    g_worker_num = int(g_worker_num)
                elif line[0:len('max_tasks_num:')]=="max_tasks_num:":
                    g_max_task_num = line[len('max_tasks_num:'):].strip()
                    g_max_task_num = int(g_max_task_num)

    except Exception as err:
        print("Can't find flight.conf")
    finally:
        pass
                
                    
def init_log():
    """
    #Init the main logger
    """
    global logger_handle
    
    d = str(datetime.date.today())
    t1 = datetime.datetime.now()
    logname='log/air_'+d+'.log'
    errlog = 'log/error_'+d+'.log'
    logger_handle=logging.FileHandler(logname)
    
    formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s')
    
    logger_handle.setFormatter(formatter)
    
    main_logger=logging.getLogger('[Main]')
    main_logger.addHandler(logger_handle)
    main_logger.setLevel('INFO')
    
    worker_logger= logging.getLogger('[Worker]')
    worker_logger.setLevel('INFO')
    worker_logger.addHandler(logger_handle)
    
    error_logger= logging.getLogger('[Error]')
    error_logger.setLevel('ERROR')
    error_logger.addHandler(logger_handle)
        
    return main_logger

def close_log():
    global logger_handle
    
    logger_handle.close()
        
def main():
    global main_logger
    
    print("Start the main function")

#     os.chdir('/db/github/flight/expedia')
        
#     display = Display(visible=0, size=(1024,768))
#     display.start()

    t1 = datetime.datetime.now()
    
    init_configure()
    
    main_logger = init_log()
    result.init_log()
    main_logger.info("\n\n*************************************Start the main function*************************************\n")
    
    start_task()
       
    t2 = datetime.datetime.now()
    tx = t2-t1
    
    end_task(t1,t2)
    
    main_logger.info("Total cost time is %d seconds" %tx.seconds)

    main_logger.info("\n*************************************Exit the main function*************************************\n")
    
#     display.stop()
    
    print("Exit the main function")

def end_task(t1,t2):
    global  g_worker_num
    
    fdb = db.FlightPlanDatabase()
    try:
        fdb.connectDB()
        
        start_time = t1.strftime('%Y-%m-%d %H:%M:%S')
               
        t2 = datetime.datetime.now()
        end_time = t2.strftime('%Y-%m-%d %H:%M:%S')
        
        execute_date = datetime.date.today().isoformat()
        
        fdb.update_fligth_task_status(start_time,end_time,g_worker_num,execute_date)
    
    except db.DBError as err:
        print("Error: %s" % str(err))
    finally:
        fdb.disconnectDB()

def print_time():
    s1=datetime.datetime.now()
    s1 = s1.strftime('%Y-%m-%d %H:%M:%S')
    print(s1)
if __name__=='__main__':
    main()
