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
import json


def parse_timeline_array(timeline_list):
    """
    Input timeline_list is a timeline list
    Parse the timeline array.
    Return a string contains stoped airport and duration as following;
    
    Return a timeline_info as a dict contains following:
    "carriers": carrier_list. Every carrier is a dict contains:
        "airline_code": like "QF"
        "airline_name": like "Qantas Airways"
    "stop_info": a string contains stop information as following:
        Yantai(YNT):3h10m;Shanghai(PVG):4h0m
    """
    timeline_info = dict()
    carriers = []
    stop_details = ""
    try:
        for t in timeline_list:
            if t["segment"]==True:
                carrier = dict()
                carrier["airline_code"] = t["carrier"]["airlineCode"]
                carrier["airline_name"] = t["carrier"]["airlineName"]
                carriers.append(carrier)
            else:
                code=t["airport"]["code"]
                city=t["airport"]["city"]
                hour=t["duration"]["hours"]
                minutes=t["duration"]["minutes"]
                du=str(hour)+"h"+str(minutes)+"m"
                stop_details =stop_details+city+"("+code+")"+":"+du+";"
                
        timeline_info["carriers"]=carriers
        timeline_info["stop_details"]=stop_details
    except Exception as inst:
        print("Error happen in parse_timeline_array", inst)
        timeline_info=None
    
    
    return timeline_info

def parse_one_leg_obj(obj):
    """
    leg_obj is one element in the legs array.
    Return a flight_info as a dict
    """
    flight_info = dict()
    
    try:
        price_obj = obj["price"]
        carrierSummary_obj = obj["carrierSummary"]
        departureTime_obj = obj["departureTime"]
        arrivalTime_obj = obj["arrivalTime"]
        duration_obj=obj["duration"]
        timeline_array=obj["timeline"]
        
        #airline_codes is a string list
        
        
        flight_info["index"]=obj["identity"]["index"]
#         flight_info["company"] =carrierSummary_obj["airlineName"]
        flight_info["airline_codes"]=carrierSummary_obj["airlineCodes"]
        flight_info["dep"] =  departureTime_obj["isoStr"]
        flight_info["arr"] =  arrivalTime_obj["isoStr"]
        flight_info["price"] = price_obj["formattedPrice"]
        flight_info["price_currencyCode"] = price_obj["currencyCode"]
        flight_info["duration"] = str(duration_obj["hours"])+"h"+str(duration_obj["minutes"])+"m"
        flight_info["stops"] = obj["stops"]
        flight_info["timeline_info"] = parse_timeline_array(timeline_array)
    except Exception as inst:
        print("Error happened in parse_one_leg_obj", inst)
        print(inst)
        flight_info = None
        
    finally:
        return flight_info
    
def test(file_name):
    flight_list=[]
    
    with open(file_name) as f:
        line=f.readline()
        s1 = json.loads(line)
#         print(type(s1))
        legs = s1["content"]["legs"]
        print("Total keys is %d" %len(legs.keys()))
        for key in legs.keys():
            print(key)
            leg_obj = legs[key]
            flight_info = parse_one_leg_obj(leg_obj)
            print(flight_info)
            break
             
    

def main():
    test('results/2016-09-01.txt')

if __name__=='__main__':
    main()
