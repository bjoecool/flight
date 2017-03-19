#!/usr/bin/env python3

import argparse
import re

def convert_city_names(filename):
    with open(filename) as f:
        id_num=10
        for line in f.readlines():
            line = line.strip()
            if len(line)==0:
                continue
            
            item_list = line.split(',')
            if len(item_list)==3:
                city_name = item_list[0]
                airport_name=item_list[2]
                pass
            elif len(item_list)==2:
                city_name = item_list[0]
                airport_name=item_list[1]
            
            full_name = line
            city_name = city_name.strip()
            airport_name = airport_name.strip()    
            ret = re.search('\((?P<acronym_name>[a-zA-Z]+)',airport_name)
            
            
            if ret is not None:
                sql_str = '''insert into city values({3},'{0}','{1}','{2}');'''.format(city_name,ret.group('acronym_name'),full_name,str(id_num))
                print(sql_str)
                id_num=id_num+1

            

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-f','--file',help='The input text file contains city names')
    
    args = parser.parse_args()
    
    filename = args.file
    
    convert_city_names(filename)

if __name__=='__main__':
    main()
