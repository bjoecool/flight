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
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
import requests

proxies = {'http':'127.0.0.1:3128','https':'127.0.0.1:3128'}

url_temp = '''\
https://www.expedia.com.au/Flights-Search?\
trip=oneway&\
leg1=from:Sydney,%20NSW,%20Australia%20%28SYD-All%20Airports%29,to:BJS,\
departure:{0}TANYT&\
passengers=children:0,adults:1,seniors:0,infantinlap:Y&mode=search'''

def get_urls(y,m,d, range_days):
    """
    y -- year
    m -- month
    d -- day
    Return a url list
    """
    url_list=[]
    url_temp = '''\
https://www.expedia.com.au/Flights-Search?\
trip=oneway&\
leg1=from:Sydney,%20NSW,%20Australia%20%28SYD-All%20Airports%29,to:BJS,\
departure:{0}TANYT&\
passengers=children:0,adults:1,seniors:0,infantinlap:Y&mode=search'''
    
    
    for i in range(range_days):
        dep_date= (date(y,m,d)+timedelta(days=i)).strftime('%d/%m/%Y')
        url = url_temp.format(dep_date)
        url_list.append(url)
        
    return url_list     

def get_departure_date(base_date,days):
    """
    Get the dep date by base_date+days.
    """
    dep_date= base_date+timedelta(days=days)
    
    return dep_date

def get_json_url(content):
    content_list=content.split(b'\n')
    for line in content_list:
        if line.find(b'originalContinuationId')!=-1:
            line = line.strip()
            s = line.split(b'>')[1]
            s = s.split(b'<')[0]
            s = s.decode()
            url = '''https://www.expedia.com.au/Flight-Search-Paging?c={0}&is=1&sp=asc&cz=200&cn=0 HTTP/1.1'''.format(s)
            return url

def reuqest_one_flight(departure_date):
    """
    departure_date is a datetime.date 
    """
    dep_date = departure_date.strftime('%d/%m/%Y')
    url = url_temp.format(dep_date)

    file_name='ret/'+departure_date.strftime('%Y-%m-%d')+'.txt'
    
    r = requests.get(url,proxies=proxies)
           
    json_url = get_json_url(r.content)
    
    r = requests.get(json_url,proxies=proxies)
    
    if r.status_code==200:
        with open(file_name,'wb') as f:
            ret = r.content
    #         ret = ret.replace(b'}',b'}\n')
            f.write(ret)
            print("Created file %s" %file_name)
    else:
        print("Get %d code for json_url:%s" %(r.status_code,json_url))
    
def test():
    t1 = datetime.now()
    
    for i in range(0,50):
        dep_date = get_departure_date(date(2016,10,1),i)
        reuqest_one_flight(dep_date)
        
    t2 = datetime.now()
    
    tx = t2 - t1
    
    print("Total cost time is %d seconds" %tx.seconds)
    

def main():
#     get_urls(2000,1,1,10)
    test()

if __name__=='__main__':
    main()
