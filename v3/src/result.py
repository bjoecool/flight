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

import os
import sys
import argparse
import time
import datetime
import logging
import db
import re
import pa as pa
import json
from enum import Enum
import fnmatch
import config

logger = None

g_format_version = '1.0'

g_total_task_num = 0
g_finished_task_num = 0


def sort_fun(name):
    s = name.split('_')[2]
    s1 = s.split('.')[0]
    n = int(s1)

    return n


def get_all_files(dir_name):
    """
    Go through the dir and return all files as a list
    """
    file_list = []
    for root, dirs, files in os.walk(dir_name):
        new_files = sorted(files, key=sort_fun)
        for f in new_files:
            if '.txt' in f:
                new_f = os.path.join(root, f)
                file_list.append(new_f)

    return file_list


def print_one_result_file(file_name):

    ret, ret_dict = pa.parse_one_file(file_name)

    print(json.dumps(ret_dict, sort_keys=True, indent=4))


def get_final_result_file_name(ret_dict, dir_name):
    """
    Create the final result file name accroding to the ret_dict
    File naming rules: <flight_table_name>_<search_date>_<departure_date>_<trip>_<stay_days>.txt

    <flight_table_name> : flight_<from_city_id>_<to_city_id>_price
    <search_date> : The date on which searching this result. Format is YYYY-MM-DD
    <departure_date> : The departure date of this flight plan. Format is YYYY-MM-DD
    <trip> : 1 -- one way.  2 -- round trip
    <staydays> : if <trip> is 1, this is always 0. Otherwise means how many days to stay.

    Example: flight_1_5_price_2017-04-01_2017-05-20_2_14.txt
    """

    file_name = None

    ret_dict_basic = ret_dict['basic']
    try:
        flight_table_name = ret_dict_basic['tableName']
        search_date = ret_dict_basic['searchDate']
        departure_date = ret_dict_basic['depDate']
        trip = ret_dict_basic['trip']
        stay_days = ret_dict_basic['stayDays']

        if trip is not str:
            trip = str(trip)

        if stay_days is not str:
            stay_days = str(stay_days)

        file_name = flight_table_name + '_' + search_date + '_' + departure_date + '_' + trip + '_' + stay_days + '.txt'
    except Exception as err:
        print('[get_final_result_file_name]: Error happen :', err)

    full_path_name = os.path.join(dir_name, file_name)

    return full_path_name


def save_result_into_file(ret_dict, dir_name):
    filename = get_final_result_file_name(ret_dict, dir_name)

    with open(filename, 'w') as f:
        json.dump(ret_dict['flight_list'], f, sort_keys=True)


def save_result_into_file_v2(flight_list, dir_name):
    filename = get_final_result_file_name(ret_dict, dir_name)

    with open(filename, 'w') as f:
        #         json.dump(ret_dict,f,sort_keys=True, indent=2)
        json.dump(ret_dict, f, sort_keys=True)


def get_task_list_from_err(dir_name):
    """
    Analyze the *.err file and put the task_id into a file named task_err.txt.
    """
    global logger
    file_list = os.listdir(dir_name)

    date_str = datetime.date.today().strftime("%Y%m%d")
    filter_str = '*res_' + date_str + '_*.err'

    file_list = fnmatch.filter(file_list, filter_str)

    err_task_id_list = []
    for file in file_list:
        full_file_name = os.path.join(dir_name, file)
        file = file[:-4]
        task_id = file.split('_')[2]
        task_id = int(task_id)
        err_task_id_list.append(task_id)
        rm_cmd = 'rm -f ' + full_file_name
        os.system(rm_cmd)

    return err_task_id_list


def update_task_status_file(total_task_num, finished_task_num):
    with open(g_status_file_name, 'w') as f:
        json.dump(d1, f)


def analyze_results(result_q, dir_name, final_ret_dir):
    """
    Analyze the original result files in the dir_name, and put the final result
    into file and database.
    """
    global logger
    global g_total_task_num

    finished_task_num = 0
    file_list = get_all_files(dir_name)
    try:
        for f in file_list:
            ret, ret_dict = pa.parse_result_file_v2(f)

            if ret == False:
                logger.error("Error happened in analyzing %s" % (f))
                err_file_name = f.replace('.txt', '.err')
                cmd = "mv " + f + ' ' + err_file_name
                os.system(cmd)
                logger.info("%s" % (cmd))
                continue
            else:
                flight_list = ret_dict['flight_list']
                logger.info("%s --- result number %d" % (f, len(flight_list)))

            finished_task_num = finished_task_num + 1
            save_result_into_file(ret_dict, final_ret_dir)

            cmd = "rm -rf " + f
            os.system(cmd)

    return finished_task_num


def init_log():
    global logger

    d = str(datetime.date.today())
    logname = 'log/result_' + d + '.log'
#     logging.basicConfig(filemode='a', format='%(levelname)s: %(asctime)s %(message)s', level=logging.DEBUG)

    # Create a Filehandler
    logger_handle = logging.FileHandler(logname)

    # create formatter
    formatter = logging.Formatter('%(levelname)s: %(asctime)s - %(name)-8s %(message)s')

    # add formatter to logger_handle
    logger_handle.setFormatter(formatter)

    # get a logger instance
    logger = logging.getLogger('[result]')

    # Add handle
    logger.addHandler(logger_handle)

    # Set level
    logger.setLevel('INFO')

#     logger_handle.emit()
    logger_handle.close()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('cmd', help='Command [print,printall,printerrors,insertdb,inserts3]')
    parser.add_argument('--filename', help='One result file.')
    parser.add_argument('--dirname', default='results', help='The results directory')
    parser.add_argument('--indent', help='0 means print to jsonl format')

    args = parser.parse_args()

    cmd_ind = args.cmd
    file_name = args.filename
    dir_name = args.dirname
    indent = args.indent

    init_log()
    config.init_configure()
    db.init_conf()

    if cmd_ind == 'print':
        if file_name is None:
            print("Please set the --filename")
            quit(0)
        print_one_result_file(file_name)
    elif cmd_ind == 'insertdb':
        #         analyze_results_to_db(dir_name='results',print_flag=False)
        analyze_results(None, 'results', 'final_results')
    elif cmd_ind == 'printall':
        analyze_results(None, 'results', 'final_results', no_db=True)
    elif cmd_ind == 'inserts3':
        save_result_file_into_s3(file_name)
    elif cmd_ind == 'printerrors':
        err_task_list = get_task_list_from_err(dir_name)
        for t in err_task_list:
            print(t)
    elif cmd_ind == 'list':
        file_list = get_all_files(dir_name)
        for file in file_list:
            print(file)
    elif cmd_ind == 'print2':
        ret, flight_info_list = pa.parse_result_file_v2(file_name)
        if indent is None:
            print(json.dumps(flight_info_list, sort_keys=True))
        else:
            print(json.dumps(flight_info_list, sort_keys=True, indent=int(indent)))
    else:
        print("Unkonw the command ", cmd_ind)
        parser.print_usage()


if __name__ == '__main__':
    #     log_test()
    main()
