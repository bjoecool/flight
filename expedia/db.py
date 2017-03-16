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

import psycopg2
import time
import datetime
import url
import logging

main_logger = None

g_dbname='expedia'
g_user='wangj'
g_host='localhost'
g_port=5432
g_pass=''

class DBError(Exception):
    def __init__(self,reason="unknown"):
        self.reason = reason
    
class FlightPlanDatabase():
    def __init__(self):
        self.database=g_dbname
        self.user=g_user
        self.host=g_host
        self.port=g_port
        self.conn=None
        self.connected = False
        self.password = g_pass
        
    def __del__(self):
        if self.connected==True:
            self.disconnectDB()
    
    def connectDB(self):
        try:
            self.conn = psycopg2.connect(database=self.database,
                                        user=self.user,
                                        host=self.host,
                                        port=self.port,
                                        password = self.password)
            self.connected = True
        except psycopg2.OperationalError:
            print("database -- %s" %self.database)
            print("host -- %s" %self.host)
            raise DBError("Failed to connetc to DB : "+self.database )
            
    def disconnectDB(self):
        try:
            self.conn.close()
        except:
            raise DBError("Failed to close connection to DB")
        finally:
            self.connected = False
            
    def create_new_fligt_schedule(self):
        '''
        Create today's flight schedule
        '''
        cur = self.conn.cursor()
        cur.execute('select count(*) from flight_view')
        col = cur.fetchone()
        if col==None:
            print("no return data")
        else:
            if col[0] == 0:
                print("no today's date")
                self.create_today_flight_schedule()
                
        cur.close()
        
    def create_today_flight_schedule(self):
        sql_cmd='''INSERT INTO flight 
                SELECT 
                    nextval('flight_id') as id,
                    from_city,
                    to_city,
                    trip,
                    (current_date+start_day) as start_date,
                    (current_date+start_day+stay_days) as return_date,
                    adults,
                    children,
                    children_age,
                    cabinclass,
                    current_date
                FROM airline;'''
        
        print(sql_cmd)
        cur = self.conn.cursor()
        cur.execute(sql_cmd)
        self.conn.commit()
        cur.close()

    def get_flight_schedule(self, start_date=None,range=1):
        """
        Read the tuples from the flight database.
        start_date --- must be a date
        
        Put the result into a list in which every item is a dict type.
        The dict is as following:
        flight['id']
        flight['from']
        flight['to']
        flight['trip']
        flight['start_date']
        flight['return_date']
        flight['adults']
        flight['children']
        flight['children_age']
        flight['cabinclass']"""
        
        airline_list=[]
        cur = self.conn.cursor()
        if start_date is None:
            cur.execute('select * from flight_view order by id')
        else:
            end_date = start_date+datetime.timedelta(range)
            print(start_date)
            print(end_date)
            cur.execute("select * from flight_view where start_date>=%s and start_date<%s order by id", (start_date,end_date))
        
        while(1):
            col = cur.fetchone()
            if col==None:
                break;
            else:
                flight={}
                flight['id']=col[0]
                flight['from'] = col[1]
                flight['to'] = col[2]
                flight['trip'] = col[3]
                flight['start_date'] = col[4]
                flight['return_date'] = col[5]
                flight['adults'] = col[7]
                flight['children'] = 0
                flight['children_age'] = '{}'
                flight['cabinclass'] = col[8]             
                airline_list.append(flight)
                
        cur.close()
        
        return airline_list
        
    def get_flight_by_id(self, id):
        cur = self.conn.cursor()
        cur.execute('''select id,
                    flight_view.from,
                    flight_view.to,
                    trip,
                    start_date,
                    stay_days,
                    adults,
                    children,
                    age,
                    class 
                    from flight_view where id=%s''', (id,))
        
        tup = cur.fetchone()
        flight={}
        flight['id']=tup[0]
        flight['from'] = tup[1]
        flight['to'] = tup[2]
        flight['trip'] = tup[3]
        flight['start_date'] = tup[4]
        flight['return_date'] = tup[4]
        flight['stay_days'] = tup[5]
        flight['adults'] = tup[6]
        flight['children'] = tup[7]
        flight['children_age'] = tup[8]
        flight['cabinclass'] = tup[9]
        
        cur.close()
        
        return flight

    def get_flight_url_by_id(self, id):
        req_url = None

        cur = self.conn.cursor()
        
        try:
            cur.execute('''select id,
                        flight_url_view.from,
                        flight_url_view.to,
                        trip,
                        start_date,
                        stay_days,
                        adults,
                        children,
                        age,
                        class 
                        from flight_url_view where id=%s''', (id,))
            
            tup = cur.fetchone()
            flight={}
            flight['id']=tup[0]
            flight['from'] = tup[1]
            flight['to'] = tup[2]
            flight['trip'] = tup[3]
            flight['start_date'] = tup[4]
            flight['return_date'] = tup[4]
            flight['stay_days'] = tup[5]
            flight['adults'] = tup[6]
            flight['children'] = tup[7]
            flight['children_age'] = tup[8]
            flight['cabinclass'] = tup[9]
            
            url_creater=url.ExpediaReqURL()
            req_url = url_creater.createURL(**flight)
        finally:
            cur.close()
        
        return req_url

    def add_into_flight_price_tbl(self, flight_info):
        """
        Insert one result for flight price into flight_price table
        """
        cur = self.conn.cursor()
        
#         print('company --- %s' %flight_info['company'])
        try:
        
            cur.execute('''SELECT * FROM get_airline_company_id_by_name(%s)''',(flight_info['company'],))
            
            
            company_tuple=cur.fetchone()
            company_id=company_tuple[0]
            
            cur.execute('''INSERT INTO flight_price 
                           (flight_id,price,company_id,departure_time,arrival_time,duration,span_days,stop,stop_info,search_date)
                            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);''',
                            (flight_info['id'],
                             flight_info['price'],
                             company_id,
                             flight_info['dep_time'],
                             flight_info['arr_time'],
                             flight_info['duration'],
                             flight_info['span_days'],
                             flight_info['stop'],
                             flight_info['stop_info'],
                             flight_info['search_date']))
            
            self.conn.commit()
        except Exception as e:
            print('db error in add_into_flight_price_tbl: %s' %e)
                
        finally:
            cur.close()
            
    def create_today_task(self):
        """
        Create today's task by select flight_id into flight_price_query_task.
        """
        total_task_num = 0

        cur = self.conn.cursor()
        try:
            cur.execute('''DELETE FROM flight_price_query_task where execute_date<current_date;''')
            cur.execute('''SELECT count(*) from flight_price_query_task where execute_date=current_date;''')
            col = cur.fetchone()
            num = col[0]
            if num<1:
                cur.execute('''insert into flight_price_query_task select id,0,current_date from flight where start_date>current_date;''')
                self.conn.commit()
                cur.execute('''SELECT count(*) from flight_price_query_task where execute_date=current_date;''')
                col = cur.fetchone()
                total_task_num = col[0]
        finally:
            cur.close()
            return total_task_num            
    
    def get_one_task_id(self):
        """
        Get one flight_id from flight_price_query_task where execute_date is
        current_date.
        Return a task_list include all flight_id.
        """
        
        cur = self.conn.cursor()
        cur.execute('''Select flight_id from flight_price_query_task 
                        where execute_date=current_date and status = 0 
                        order by flight_id limit 1''')

        col = cur.fetchone()
        
        if col == None:
            return None
        
        flight_id = col[0]
        
        return flight_id
        
    def get_today_task_id(self,limit_number=1000):
        """
        Get all flight_id from flight_price_query_task where execute_date is
        current_date.
        Return a task_list include all flight_id.
        """
        cur = self.conn.cursor()
        cur.execute('''Select flight_id from flight_price_query_task 
                        where execute_date=current_date and status <> 2 
                        order by flight_id limit %s;''',(limit_number,))

        task_list=[]
        
        while(1):
            col = cur.fetchone()
            if col==None:
                break;
            else:
                task_list.append(col[0])
                
        cur.close()
        
        return task_list
    
    def update_status_in_flight_price_query_task_tbl(self, flight_id, status, search_date):
        """
        update the flight_price_query_task table, set the status to 1 
        for the flight_id = flight_id.
        """
        cur = self.conn.cursor()
        
        cur.execute('''update flight_price_query_task set status=%s 
                    where flight_id=%s and execute_date=%s;''',
                    (status,flight_id,search_date))
        self.conn.commit()
        cur.close()
        
    def add_one_group_flight_schedule(self,start_date,start_date_range):
        """
        This function add a group fligth schedule which start_date will be in 
        a list of start_date_list
        """
        
        cur = self.conn.cursor()
        for i in range(0,start_date_range):
            sd_date = start_date+datetime.timedelta(i)
            sd_str = sd_date.strftime("%Y-%m-%d")
            cur.execute('''select count(*) from flight where start_date=%s''',(sd_str,))
            col = cur.fetchone()
            num = int(col[0])
            if num > 0:
                continue
            cur.execute('''select create_one_way_airlines(%s)''',(sd_str,))
            self.conn.commit()
        cur.close()

    def insert_flight_task_status(self,total_tasks,failure_tasks,success_tasks,total_records,task_start_time,task_finished_time,execute_date):
        cur = self.conn.cursor()
            
        cur.execute('''INSERT INTO flight_task_status 
                       (total_tasks,failure_tasks,success_tasks,total_records,task_start_time,task_finished_time,execute_date)
                        VALUES(%s,%s,%s,%s,%s,%s,%s);''',
                        (total_tasks,
                        failure_tasks,
                        success_tasks,
                        total_records,
                        task_start_time,
                        task_finished_time,
                        execute_date))
        
        self.conn.commit()
        cur.close()
        
    def update_fligth_task_status(self,task_start_time, task_finished_time,workers_num, execute_date):
        cur = self.conn.cursor()
        
        cur.execute('''SELECT COUNT(*) FROM flight_task_status where execute_date=%s''',
                    (execute_date,),)
            
        col = cur.fetchone()
        num = int(col[0])
        if num > 0:
            return        

        cur.execute('''SELECT COUNT(*) FROM flight_price_query_task where execute_date=%s''',
                    (execute_date,),)
        col = cur.fetchone()
        total_tasks = int(col[0])
        
        cur.execute('''SELECT COUNT(*) FROM flight_price_query_task where status = 2 and execute_date=%s''',
                    (execute_date,),)

        col = cur.fetchone()
        success_tasks = int(col[0])


        cur.execute('''SELECT COUNT(*) FROM flight_price where search_date=%s''',
                    (execute_date,),)

        col = cur.fetchone()
        total_records = int(col[0])
       
        cur.execute('''INSERT INTO flight_task_status 
                       (total_tasks,success_tasks,total_records,workers,task_start_time,task_finished_time,execute_date)
                        VALUES(%s,%s,%s,%s,%s,%s,%s);''',
                        (total_tasks,
                        success_tasks,
                        total_records,
                        workers_num,
                        task_start_time,
                        task_finished_time,
                        execute_date))
        
        self.conn.commit()        
        
        cur.close()
                
def test():
    fdb = FlightPlanDatabase()
  
    u = url.ExpediaReqURL()
    
    try:
        fdb.connectDB()
        task_id = fdb.get_one_task_id()
    
        print(task_id)
        flight = fdb.get_flight_by_id(task_id)
        req_url = u.createURL(**flight)
        print(req_url)
    
        fdb.disconnectDB()

    except DBError as err:
        print("Error: %s" % str(err))
    
def test_add_flight_schedule():
    fdb = FlightPlanDatabase()
    try:
        fdb.connectDB()
        
        start_date=datetime.date.today()+datetime.timedelta(1)
        start_date_range=90
        
        flight = fdb.add_one_group_flight_schedule(start_date,start_date_range)
    
        fdb.disconnectDB()

    except DBError as err:
        print("Error: %s" % str(err))    

def create_today_flight_schedule():
    fdb = FlightPlanDatabase()
    try:
        fdb.connectDB()
        
        start_date=datetime.date.today()+datetime.timedelta(1)
        start_date_range=180   #Create 180 days data
        
        fdb.add_one_group_flight_schedule(start_date,start_date_range)
        
        fdb.create_today_task()

    except DBError as err:
        print("Error: %s" % str(err))
    finally:
        fdb.disconnectDB()

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

def init_conf():
    """
    Read configure file.
    """
    global g_dbname
    global g_user
    global g_host
    global g_port
    global g_pass
    
    with open("db.conf") as f:
        for line in f.readlines():
            line = line.strip()
            if line[0:7]=="dbname:":
                g_dbname = line[7:]
            elif line[0:5]=="user:":
                g_user = line[5:] 
            elif line[0:5]=="host:":
                g_host = line[5:]
            elif line[0:9]=="password:":
                g_pass = line[9:]

def connect_db():
    global g_dbname
    global g_user
    global g_host
    global g_port
    global g_pass
    
    conn = None
    
    try:
        conn = psycopg2.connect(database=g_dbname,
                                    user=g_user,
                                    host=g_host,
                                    port=g_port,
                                    password = g_pass)
    except psycopg2.OperationalError:
        print("database -- %s" %g_dbname)
        print("host -- %s" %g_host)
        raise DBError("Failed to connetc to DB : "+g_dbname )
    finally:
        return conn
       
def main():
    init_log()
#     init_conf()
    test_update_fligth_task_status()
#     create_today_flight_schedule()
#     test_get_flight_url_by_id()
    

def test_get_flight_url_by_id():
    
    fdb = FlightPlanDatabase()
    try:
        fdb.connectDB()
        
        for id in range(1,31):
            req_url = fdb.get_flight_url_by_id(id)
            print(req_url)

    except DBError as err:
        print("Error: %s" % str(err))
    finally:
        fdb.disconnectDB() 

def test_update_fligth_task_status():
    fdb = FlightPlanDatabase()
    try:
        fdb.connectDB()
        
        t1 = datetime.datetime.now()
        
        start_time = t1.strftime('%Y-%m-%d %H:%M:%S')
               
        time.sleep(5)
        
        t2 = datetime.datetime.now()
        end_time = t2.strftime('%Y-%m-%d %H:%M:%S')
        
        execute_date = datetime.date.today().isoformat()
        
        fdb.update_fligth_task_status(start_time,end_time,4,execute_date)

    except DBError as err:
        print("Error: %s" % str(err))
    finally:
        fdb.disconnectDB()
        
if __name__=='__main__':
    main()
