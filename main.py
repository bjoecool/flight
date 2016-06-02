#!/usr/local/bin/python3

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

g_worker_num = 1

process_name='[main]'

def start_task():
    global g_worker_num
    
    max_task_num = 10

    # create today's flight schedule and task
    create_today_flight_schedule()
        
    mydb = db.FlightPlanDatabase()
    
    mydb.connectDB()
    
    mydb.create_today_task()
    
    i = 0
    total_tasks = 0
    
#     result_p = start_handle_result_process()
#     result_p.start()

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
    
            logging.info("%s Put total %d task into queue" %(process_name,num_tasks))
            
            wait_tasks_finished(result_q, num_tasks)
            
#             delete_tmp()

            time.sleep(10)
            
            break
    except Exception as err:
        logging.info("%s In start_task error happened: %s" %str(err))
    finally:
        logging.info("%s Total tasks %d has been executed" %(process_name,total_tasks))
        
        time.sleep(10)
        
        logging.info("%s Stop the handle result process" %process_name)

        #Send EXIT command to workers
        for i in range(g_worker_num):
            d = dict()
            d['cmd']='exit'
            task_q.put(d)

        #Wait workers exit                       
        time.sleep(10)
                        
        wkm.stop_monitor()
        wkm.stop_workers()
        mydb.disconnectDB()

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
    p = mp.Process(target=result.readResults, args=())
    
    return p
    
def delete_tmp():
    logging.info("%s Function delete_tmp was invoked" %process_name)
    os.system("rm -rf /tmp/*")
    
def create_today_flight_schedule():
    fdb = db.FlightPlanDatabase()
    try:
        fdb.connectDB()
        
        start_date=datetime.date.today()+datetime.timedelta(1)
        start_date_range=90
        
        fdb.add_one_group_flight_schedule(start_date,start_date_range)
        
        fdb.create_today_task()
    
        fdb.disconnectDB()

    except db.DBError as err:
        print("Error: %s" % str(err))   

def main():
    print("Start the main function")
    d = str(datetime.date.today())
    t1 = datetime.datetime.now()
    
    logname='log/air_'+d+'.log'
    
    logging.basicConfig(filename=logname, filemode='a', format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)
    
    logging.info("Start the main function")
    
    #Create 2 queue, one for task and another is for status of workers

    start_task()
        
    t2 = datetime.datetime.now()
    
    tx = t2-t1
    logging.info("Total cost time is %d seconds" %tx.seconds)

    logging.info("Exit the main function")
    print("Exit the main function")
       
    

if __name__=='__main__':
    main()
