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
import logging
import datetime
import multiprocessing as mp
import psycopg2

def worker_run(worker_number, sleep_time):
    
    logging.info('worker [%d] started!' % worker_number)
    
    time.sleep(sleep_time)
    
    logging.info('worker [%d] existed!' % worker_number)

def test_psycopg2():
    conn_ok = False
    try:
        conn = psycopg2.connect(database='expedia', 
                                user='wangj',
                                password='flightpass', 
                                host='flight-db.c6vuzqnavuqr.ap-southeast-2.rds.amazonaws.com', 
                                port=5432)
        
        conn_ok = True
        cur = conn.cursor()
        cur.execute("""SELECT * from airline""")
        rows = cur.fetchall()
        for row in rows:
            print(row[0])
    except:
        print("I am unable to connect to the database")
        
    finally:
        if conn_ok == True:
            conn.close()

def test():
    os.chdir('/db2/github/flight')
    logging.basicConfig(filename='log/test.log',format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)
    
    logging.info('Enter into test function!')
    
    wk1 = mp.Process(target=worker_run, args=(1,4))
    wk2 = mp.Process(target=worker_run, args=(2,2))
    
    wk1.start()
    wk2.start()
    
    
    wk1.join()
    wk2.join()
    
    logging.info('Exit test function!')
        
def main():
#     test()
    test_psycopg2()
    
if __name__=='__main__':
    main()
