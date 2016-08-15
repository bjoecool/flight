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
import logging
import time
import datetime
import multiprocessing as mp
from enum import Enum

import worker_exec as wke


main_logger=None

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
        self.log = logging.getLogger('[Worker]')
        
    def create_queue(self):
        self.task_q = mp.Queue()
        self.result_q = mp.Queue()
        self.stat_q=mp.Queue()
        return (self.task_q,self.result_q)
        
    def start_monitor(self):
        self.log.info("Enter into start_monitor")
        if self.handle != None:
            return (None,None)
        
        try:
            p = mp.Process(target=monitor_exec, args=(self.worker_list, self.stat_q))
            self.handle = p
            p.start()
        except Exception as err:
            self.handle = None
            self.log.error("WorkerMonitor start failed, reason : %s " %str(err))
            
    def stop_monitor(self):
        self.log.info("Enter into stop_monitor")
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
        
        self.num = num
        self.task_q = task_q   #The queue to receive the command and task
        self.stat_q = stat_q  #The queue to check the worker status
        self.result_q = result_q
        self.status = WorkerStatus.not_start
        self.handle = None
        self.no_heartbeat_times=0
        self.driver = None
        self.log = logging.getLogger('[Worker]')
        self.log.info("Enter worker init")
        
    def getWorkersNum(self):
        return self.num
    
    def start(self):
        try:
            self.log.info("Creating worker process")
#             self.driver = wke.createDriver()
            p = mp.Process(target=wke.execTask, args=(self.task_q, self.result_q, self.stat_q, self.num,None))
            self.handle = p
            self.status = WorkerStatus.running;
            self.no_heartbeat_times = 0
            p.start()
        except Exception as err:
            self.handle = None
            self.log.error("Worker[%d] start failed, reason : %s " %(self.num,str(err)))
            return -1

        return 1
    
    def terminate(self):
        self.log.info("Worker[%d] is terminated" %self.num)
        if self.driver != None:
            self.driver.quit()
            self.driver = None
        self.status = WorkerStatus.not_start
        self.handle.terminate()
        self.heartbeat = False
        self.handle = None
        
                
    def restart(self):
        self.terminate()
        self.start()
        
def monitor_exec(worker_list,stat_q):
    global main_logger
    
    process_name='[monitor_exec]'
    main_logger=logging.getLogger('[Main]')
    
    main_logger.info("Enter into %s" %process_name)
    if len(worker_list) == 0:
        return;
    
    max_heartbeat_times = 3

    while(1):
        for wk in worker_list:
            if wk.no_heartbeat_times>max_heartbeat_times:
                main_logger.info("%s woker[%d] no_heartbeat_times reach to max value %d, restart it" %(process_name,wk.num,max_heartbeat_times))
                wk.terminate()
                wk.start()            
        
        if stat_q.empty() == True:
            time.sleep(20)
            for wk in worker_list:
                wk.no_heartbeat_times = wk.no_heartbeat_times+1
            continue
        
        num = stat_q.get()
        
        for wk in worker_list:
            if wk.num == num:
                wk.no_heartbeat_times=0
#                 main_logger.info("%s Received heartbeat from worker[%d]" %(process_name,num))
        
                
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
