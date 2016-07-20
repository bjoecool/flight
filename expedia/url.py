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

import datetime
import urllib.request


def create_request_obj(url):
    """
    Input is a request object.
    Return a request
    """
    request = urllib.request.Request(url)
    request.set_proxy('127.0.0.1:3128','http')
    request.set_proxy('127.0.0.1:3128','https')
    request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0')
    request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    request.add_header('Accept-Language', 'en-US,en;q=0.5')
    request.add_header('Accept-Encoding','gzip, deflate, br')
    
    print(request.get_full_url())
    print(request.header_items())
    
    return request

def create_request_obj_from_file(file_name):
    req_dict=dict()
    
    with open(file_name) as f:
        for line in f.readlines():
            line=line.strip()
            
            if line == None or len(line)==0:
                continue
            
            if line[0:3]=='GET':
                url = line[4:]
                print(url)
                continue
            
            s=line.split(':',maxsplit=1)
            key=s[0]
            data=s[1]
            req_dict[key]=data

    full_url="https://"+req_dict['Host']+url
    print(full_url)
                
    request = urllib.request.Request(full_url)
    request.set_proxy('127.0.0.1:3128','http')
    request.set_proxy('127.0.0.1:3128','https')
    for key in req_dict.keys():
        request.add_header(key,req_dict[key])
        
    print(request.get_full_url())
    print(request.header_items())
    
    return request
    
def send_url_req(url):
    request = create_request_obj(url)
    response = urllib.request.urlopen(request)
    
    res_headers = response.getheaders()
    print(response.status)
    print(res_headers)
    
def send_url_get_data():
    request = create_request_obj_from_file('req_data_header.txt')
    response = urllib.request.urlopen(request)
    
    res_headers = response.getheaders()
    print(response.status)
    print(res_headers)
    
def main():
#     send_url_req('https://www.expedia.com.au/')
    send_url_get_data()


if __name__=='__main__':
    main()
