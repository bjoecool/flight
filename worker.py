#!/usr/local/bin/python3

import sys
import logging
import time
import datetime
import multiprocessing as mp
from enum import Enum

import worker_exec as wke

class WorkerStatus(Enum):
    not_start = 0
    running = 1
    suspend = 2
    normal_exit = 3
    
    
class MSGType(Enum):
    # Folloiwng is for msg in task_q
    task = 0 #execute a task
    exit = 1 #Let worker exit 
    
    # Following is for msg in stat_q 
    heartbeat = 100   #worker heartbeat msg
    normalexit = 101  #worker has normal exited 

class WorkerMonitor():
    def __init__(self):
        self.task_q = None
        self.result_q = None
        self.stat_q = None
        self.handle = None
        self.worker_list = []
        
    def create_queue(self):
        self.task_q = mp.Queue()
        self.result_q = mp.Queue()
        self.stat_q=mp.Queue()
        return (self.task_q,self.result_q)
        
    def start_monitor(self):
        print("Enter into start_monitor")
        if self.handle != None:
            return (None,None)
        
        try:
            p = mp.Process(target=monitor_exec, args=(self.worker_list, self.stat_q))
            self.handle = p
            p.start()
        except Exception as err:
            self.handle = None
            print("WorkerMonitor start failed, reason : %s " %str(err))
            
    def stop_monitor(self):
        print("Enter into stop_monitor")
        if self.handle != None:
            self.handle.terminate()
            self.handle=None
            
    def start_workers(self,num):
        """
        Start number of workers.
        The worker number start from 1.
        Return task_q,result_q
        """
        #worker number start from 1
        print("Enter into start_workers")
        for i in range(num):
            wk_num = i+1
            wk = Worker(wk_num,self.task_q,self.result_q,self.stat_q)
            wk.start()
            self.worker_list.append(wk)
        
    def stop_workers(self):
        """
        Stop all workers
        """
        for wk in self.worker_list:
            wk.terminate()
    
class Worker():
    def __init__(self, num, task_q, result_q, stat_q):
        print("Enter worker init")
        self.num = num
        self.task_q = task_q   #The queue to receive the command and task
        self.stat_q = stat_q  #The queue to check the worker status
        self.result_q = result_q
        self.status = WorkerStatus.not_start
        self.handle = None
        self.no_heartbeat_times=0

        
    def getWorkersNum(self):
        return self.num
    
    def start(self):
        print("enter worker.start")
        try:
            print("Creating worker process")
            p = mp.Process(target=wke.execTask, args=(self.task_q, self.result_q, self.stat_q, self.num))
            self.handle = p
            self.status = WorkerStatus.running;
            self.no_heartbeat_times = 0
            p.start()
            print("woker[%d] started" %self.num)
        except Exception as err:
            self.handle = None
            print("Worker[%d] start failed, reason : %s " %(self.num,str(err)))
            return -1

        return 1
    
    def terminate(self):
        print("Worker[%d] is terminated" %self.num)
        self.status = WorkerStatus.not_start
        self.handle.terminate()
        self.heartbeat = False
        self.handle = None
                
    def restart(self):
        self.terminate()
        self.start()
        
def alloc_workers(task_q,result_q,g_worker_num):
    worker_list=[]
    
    logging.info("Function alloc_workers was invoked")
    
    #worker number start from 1
    for i in range(g_worker_num):
        w = Worker(i+1,task_q,result_q)
        worker_list.append(w)
        
    return worker_list

def start_workers(worker_list):
    logging.info("Function start_workers was invoked")
    for wk in worker_list:
        wk.start()

def wait_workers(worker_list):
    logging.info("Function wait_workers was invoked")
    for p in worker_list:
        p.join()

def check_worker_status(worker_list, total_task_num):
    """
    Check the workers status. If no heartbeat received from workers then 
    terminate that worker and start a new one.
    worker_num --- indicate how many workers are there.
    stat_q --- the queue that recevie heartbeat message from worker side
    """
    logging.info("Function check_worker_status was invoked")
    
    task_num = 0
    while(1):
        for wk in worker_list:
            if wk.getHeartBeat()==False:
                if wk.getStatus() == WorkerStatus.running:
                    logging.warning("Worker[%d] is suspend" %wk.num)
                    wk.restart()
                elif wk.getStatus() == WorkerStatus.normal_exit:
                    worker_list.remove(wk)
                    logging.info("Removed worker[%d] " %wk.num)
            else:
                task_num += wk.getFinshedTaskNumber()
                
       
        print("Current finished task num = %d" %task_num)

        if len(worker_list) == 0:
            print("All workers have exited")
            break

        time.sleep(300)  #Every 5min to check workers status once

def monitor_exec(worker_list,stat_q):
    process_name='monitor_exec'
    
    print("Enter into %s" %process_name)
    if len(worker_list) == 0:
        return;
    
    

    while(1):
        for wk in worker_list:
            if wk.no_heartbeat_times>3:
                logging.info("[%process_name] woker[%d] no_heartbeat_times reach to max value 3, restart it" %process_name)
                wk.terminate()
                wk.start()            
        
        if stat_q.empty() == True:
            time.sleep(30)
            for wk in worker_list:
                wk.no_heartbeat_times = wk.no_heartbeat_times+1
            continue
        
        num = stat_q.get()
        
        for wk in worker_list:
            if wk.num == num:
                wk.no_heartbeat_times=0
                logging.info("[%process_name] Received heartbeat from worker[%d]" %(process_name,num))
        
                
def test(url,id):
    print("enter workers test,url[%s], id[%s]" %(url,id))
    
    time.sleep(int(id))
    print("exit workers test,url[%s], id[%s]" %(url,id))
    

def main():
#     getFlightPrice(sys.argv[1],sys.argv[2])
#     getFlightPrice(sys.argv[1],sys.argv[2])
    pass    

if __name__=='__main__':
    main()
