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
import worker

main_logger=None
g_worker_num = 4

process_name='[main]'

logger_handle = None

def start_task():
    global g_worker_num
    global main_logger
    
    max_task_num = 5400

    # create today's flight schedule and task
    db.create_today_flight_schedule()
        
    mydb = db.FlightPlanDatabase()
    
    mydb.connectDB()
    
    mydb.create_today_task()
    
    i = 0
    total_tasks = 0
    
    result_p = start_handle_result_process()
    result_p.start()

    wkm = worker.WorkerMonitor()
    
    task_q,result_q = wkm.create_queue()
    
    try:
        while 1:
            flight_list = mydb.get_today_task_id(max_task_num)
            num_tasks = len(flight_list)
            
            if num_tasks == 0:
                break
            
            total_tasks += num_tasks 
            
            print("Starting workers")
            wkm.start_workers(g_worker_num)
            
            print("Starting worker monitor")
            wkm.start_monitor()
                        
            t1 = datetime.datetime.now()
            #Put task list
            for flight_id in flight_list:
                d = dict()
                d['cmd']='continue'
                d['data'] = flight_id
                d['date'] = t1.strftime('%Y-%m-%d')
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
        print("Waiting 30 seconds for workers finishing their final works")                       
        time.sleep(30)
                        
        wkm.stop_workers()
        wkm.stop_monitor()
        mydb.disconnectDB()
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
    p = mp.Process(target=result.schedule_results_analyze, args=('results',60))
    
    return p
    
def delete_tmp():
    global main_logger
    
    main_logger.info("%s Function delete_tmp was invoked" %process_name)
    os.system("rm -rf /tmp/*")
    
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

def close_log():
    global logger_handle
    
    logger_handle.close()
        
def main():
    global main_logger
    
    print("Start the main function")

    t1 = datetime.datetime.now()
    
    main_logger = init_log()
    result.init_log()
    
    start_task()
       
    t2 = datetime.datetime.now()
    tx = t2-t1
    
    main_logger.info("Total cost time is %d seconds" %tx.seconds)

    main_logger.info("Exit the main function")
    print("Exit the main function")
    
if __name__=='__main__':
    main()
