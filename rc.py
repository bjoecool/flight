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
import requests

proxies = {'http':'127.0.0.1:3128','https':'127.0.0.1:3128'}

def test():
    
    #url='''https://www.expedia.com.au/Flights-Search?trip=oneway&leg1=from:Sydney,%20NSW,%20Australia%20%28SYD-All%20Airports%29,to:BJS,departure:25/08/2016TANYT&passengers=children:0,adults:1,seniors:0,infantinlap:Y&mode=search'''
    
    url='''https://www.expedia.com.au/Flight-Search-Paging?c=f207806f-5b37-4cb1-bc3c-cf44bbdfd6f8&is=1&sp=asc&cz=200&cn=0'''
    
    r = requests.get(url,proxies=proxies)
    
    print(r.status_code)
    
    with open('content.txt', 'wb') as f:
        f.write(r.content)
        
    print(r.json())
        
#     print(r.content)

def main():

    test()

if __name__=='__main__':
    main()
