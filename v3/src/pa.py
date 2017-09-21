#!/usr/bin/env python3
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
import argparse

flight_info_keys=["index","price","price_code","dep_time","arr_time","duration","stop","stop_info","company"]

def print_flight_info(flight_info):
    for key in flight_info_keys:
#         print(key,end=' : ')
        print(flight_info[key],end="\t")
    
    print("")

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
    stop_details = None
    try:
        for t in timeline_list:
            if t["segment"]==True:
                carrier = dict()
                carrier["airline_code"] = t["carrier"]["airlineCode"]
                carrier["airline_name"] = t["carrier"]["airlineName"]
                carrier["flight_number"] = t["carrier"]["flightNumber"]
                carrier["plane"] = t["carrier"]["plane"]
                carriers.append(carrier)
            else:
                code=t["airport"]["code"]
                city=t["airport"]["city"]
                hour=t["duration"]["hours"]
                minutes=t["duration"]["minutes"]
                du=str(hour)+"h"+str(minutes)+"m"
                if stop_details == None:
                    stop_details = city+"("+code+")"+":"+du
                else:
                    stop_details =stop_details+";"+city+"("+code+")"+":"+du
                
        timeline_info["carriers"]=carriers
        if stop_details == None:
            timeline_info["stop_details"]=""
        else:
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
        flight_info["airline_codes"]=carrierSummary_obj["airlineCodes"]
        flight_info["dep_time"] =  departureTime_obj["isoStr"]
        flight_info["arr_time"] =  arrivalTime_obj["isoStr"]
        flight_info["price"] = price_obj["exactPrice"]
        flight_info["price_code"] = price_obj["currencyCode"]
        flight_info["duration"] = str(duration_obj["hours"])+"h"+str(duration_obj["minutes"])+"m"
        flight_info["stop"] = obj["stops"]
        timeline_info = parse_timeline_array(timeline_array)
        flight_info["stop_info"] = timeline_info["stop_details"]
        flight_info["span_days"] = 0
        
        flight_info['check_bag_inc'] = price_obj['feesMessage']['showCheckedBagIncludedMsg']
        flight_info["ticket_left"]=carrierSummary_obj["noOfTicketsLeft"]
        if 'wiFiAvailable' in carrierSummary_obj.keys():
            flight_info["wifi"]=carrierSummary_obj["wiFiAvailable"]
        else:
            flight_info["wifi"]=None
            
        if 'videoAvailable' in carrierSummary_obj.keys():
            flight_info["video"]=carrierSummary_obj["videoAvailable"]
        else:
            flight_info["video"]=None
            
        if 'powerSourceAvailable' in carrierSummary_obj.keys():            
            flight_info["power"]=carrierSummary_obj["powerSourceAvailable"]
        else:
            flight_info["power"]=None
        
        company = None
        ### Only get the first name because the database only support one now,
        ### Later consider support multiple company name
        for carrier in timeline_info["carriers"]:
            flight_number = carrier["flight_number"]
            airline_code = carrier["airline_code"] 
            flight_info['flight_code'] = airline_code+ flight_number
            flight_info['airline_code'] = carrier["airline_code"]
            flight_info['flight_number'] = flight_number
            flight_info["company"] = carrier["airline_name"] 
            flight_info["plane"] = carrier["plane"] 
            break
#             if company == None:
#                 company = carrier["airline_name"]
#             else:
#                 company = company+";"+carrier["airline_name"]
        
    except Exception as inst:
        print("Error happened in parse_one_leg_obj", inst)
        print(inst)
        flight_info = None
        
    finally:
        return flight_info

def parse_leg_obj_v2(leg):
    """
    Parser one leg and return (flight_leg, timelines)
    
    flight_leg is a dict
    timelines is a list contains multiple segment
    """
    flight_leg = dict()
    
    try:
        flight_leg['departureTime']= leg['departureTime']
        flight_leg['arrivalTime']= leg['arrivalTime']
        flight_leg['stops']= leg['stops']
        flight_leg['stop_list'] = []
        flight_leg['departureLocation']=leg['departureLocation']
        flight_leg['arrivalLocation']=leg['arrivalLocation']
        flight_leg['carrierSummary'] = leg['carrierSummary']
        flight_leg['stop_list'] = []
        
        time_line_list = []
        for seg in leg['timeline']:
            if seg['type'] == 'Layover':
                stop_info = dict()
                if 'longName' in seg['airport'].keys():
                    stop_info['airport'] = seg['airport']['longName']
                else:
                    print('''Error: no seg['airport']['longName'] ''')
                    stop_info['airport'] = None
                    
                hours = str(seg['duration']['hours'])
                minutes = str(seg['duration']['minutes'])
                stop_info['duration'] = "{0}h:{1}m".format(hours,minutes)
                flight_leg['stop_list'].append(stop_info)
            
            elif seg['type'] == 'Segment':
                segment = seg
                if 'carrier' in segment.keys():
                    segment['carrier'].pop('seatmapLink',0)
                    segment['carrier'].pop('airlineImageFileName',0)
                    segment['carrier'].pop('seatMapAvailable',0)
                    segment['carrier'].pop('operatedBy',0)
                    segment['carrier'].pop('operatedByAirlineCode',0)
                
                segment['duration'] = seg['duration']
                
                if 'duration' in segment.keys():
                    segment['duration'].pop('numOfDays',0)
                    segment['duration'].pop('departureTimeOfDay',0)
                    segment['duration'].pop('arrivalTimeOfDay',0)
                
                time_line_list.append(segment)
    except Exception as err:
        print("Error happened in parse_leg_obj_v2: [%s]" %str(err))
        
    return flight_leg,time_line_list

def parse_content_obj(flight_info_basic, content):
    legs_dict = content['legs']
    offers_dict = content['offers']
    index_list = content['index']
    
    flight_info_list = []
    
    for index in index_list:
        one_offer = offers_dict[index]
        if len(one_offer['legIds']) == 2:
            legid_1 = one_offer['legIds'][0]
            legid_2 = one_offer['legIds'][1]
            flight_leg1,timeline_leg1 = parse_leg_obj_v2(legs_dict[legid_1])
            flight_leg2,timeline_leg2 = parse_leg_obj_v2(legs_dict[legid_2])
        else:
            legid_1 = one_offer['legIds'][0]
            legid_2 = None
            flight_leg1,timeline_leg1 = parse_leg_obj_v2(legs_dict[legid_1])
            flight_leg2 = None
            timeline_leg2 = None
            
        flight_info= flight_info_basic.copy()
        
        flight_info['price'] = one_offer['price']['exactPrice']
        flight_info['currencyCode'] = one_offer['price']['currencyCode']
        flight_info['leg1'] = flight_leg1
        flight_info['timeline1'] = timeline_leg1
        flight_info['leg2'] = flight_leg2
        flight_info['timeline2'] = timeline_leg2
        
        flight_info_list.append(flight_info)
        
    return flight_info_list
        
    
def parse_one_file(file_name):
    flight_list=[]
    ret = False
    flight_id = None
    search_date = None
    
    ret_dict_basic={}
    ret_dict={}
    ret_dict['basic']=ret_dict_basic
    ret_dict_basic['version']='1.0'
    try:    
        with open(file_name) as f:
            for line in f.readlines():
                if line[0:9]=='<task_id>':
                    task_id = line[9:].strip()
                    ret_dict_basic['task_id']=task_id
                elif line[0:13] == '<search_date>':
                    search_date = line[13:].strip()
                    ret_dict_basic['search_date']=search_date
                elif line[0:12] == '<table_name>':
                    table_name = line[12:].strip()
                    ret_dict_basic['table_name']=table_name
                elif line[0:16] == '<from_city_name>':
                    from_city_name = line[16:].strip()
                    ret_dict_basic['from_city_name']=from_city_name
                elif line[0:14] == '<to_city_name>':
                    to_city_name = line[14:].strip()
                    ret_dict_basic['to_city_name']=to_city_name
                elif line[0:12] == '<start_date>':
                    start_date = line[12:].strip()
                    ret_dict_basic['start_date']=start_date
                elif line[0:11] == '<stay_days>':
                    stay_days = line[11:].strip()
                    ret_dict_basic['stay_days']=stay_days
                elif line[0:6] == '<trip>':
                    trip = line[6:].strip()
                    ret_dict_basic['trip']=trip
                elif line[0:13] == '<flight_info>':
                    content_line = line[13:].strip()
                    s1 = json.loads(content_line)
                    legs = s1["content"]["legs"]
                    for key in legs.keys():
                        leg_obj = legs[key]
                        flight_info = parse_one_leg_obj(leg_obj)
                        flight_info['id']=flight_id
                        flight_info['search_date'] = search_date
                        flight_list.append(flight_info)
                        ret_dict['flight_list']=flight_list
                        ret = True
            
    except FileNotFoundError as err:
        print("File not found for %s" %file_name)
        flight_list = None
        ret_dict['flight_list']=flight_list
    finally:
        return ret,ret_dict

def parse_result_file_v2(file_name):
    ret = False
    ret_dict= dict()
    flight_info_list = []
    flight_info_basic = None
    try:
        with open(file_name) as f:
            orig_flight = json.load(f)
            flight_info_basic = orig_flight['basic']
            flight_info_basic['version']='1.1'
            flight_info_basic.pop('url',0)  #remove url
            content_obj = orig_flight["content"]
            flight_info_list = parse_content_obj(flight_info_basic,content_obj)
            ret = True
            
    except FileNotFoundError as err:
        print("File not found for %s" %file_name)
        flight_info_list = []
        ret = False
    finally:
        ret_dict['basic'] = flight_info_basic
        ret_dict['flight_list'] = flight_info_list
        return ret,ret_dict

def main():
#     test('results/2016-09-01.txt')
    flight_list = parse_one_file('../results/res_2016-08-15_640.txt')
    
    for flight_info in flight_list:
        print_fligth_info(flight_info)

if __name__=='__main__':
    main()
