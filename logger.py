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

import logging
import datetime
from enum import Enum

init_flag = False
main_logger = None
worker_logger = None

class LogType(Enum):
    MAIN=0
    WORKER=1
    RESULT=2

def init_main_log():
    d = str(datetime.date.today())
    logname='log/air_'+d+'.log'
    logger_handle=logging.FileHandler(logname)
    
    formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s')
    
    logger_handle.setFormatter(formatter)
    
    main_logger=logging.getLogger('[Main]')
    main_logger.addHandler(logger_handle)
    main_logger.setLevel('INFO')
    pass

def init_worker_log():
    pass

def init_result_log():
    d = str(datetime.date.today())
    logname='log/result_'+d+'.log'
    
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
    logger.setLevel('INFO')
    pass    
    
def init_log():
    global init_flag
    global main_logger
    global worker_logger
    global result_logger
    
    if init_flag == True:
        return
    
    d = str(datetime.date.today())
    logname='log/air_'+d+'.log'
    logger_handle=logging.FileHandler(logname)
    
    formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s')
    
    logger_handle.setFormatter(formatter)
    
    main_logger=logging.getLogger('[Main]')
    main_logger.addHandler(logger_handle)
    main_logger.setLevel('INFO')
    
    worker_logger= logging.getLogger('[Worker]')
    worker_logger.setLevel('DEBUG')
    worker_logger.addHandler(logger_handle)
    
    worker_logger.debug('This is worker log debug message')
    worker_logger.info('This is worker log info message')
    worker_logger.warning('This is worker log warning message')
            
def get_log(log_type):
    global main_logger
    global worker_logger
    global result_logger
    
    if init_flag == False:
        init_log()
        
    if log_type==LogType.MAIN:
        return main_logger
    elif log_type==LogType.WORKER:
        return worker_logger
    elif log_type==LogType.RESULT:
        return result_logger

def main():
    print("Enter init log module")

if __name__=='__main__':
    main()
