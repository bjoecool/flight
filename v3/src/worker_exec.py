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
import os
import logging
import time
import datetime
import url
import subprocess
import cr as crawler_worker
import json

import settings

worker_name = ["worker_0"]
g_store_dir = settings.RESULT_DIR


worker_logger = None


def create_tmp_result_file_name(task_id, store_dir):
    t1 = datetime.datetime.now()
    t1 = t1.strftime('%Y%m%d')

    file_name = os.path.join(store_dir,'res_{}_{}._xt'.format(t1,task_id))

    return file_name


def finalize_tmp_result_file_name(tmp_file_name, success=1):
    if tmp_file_name == None:
        return

    if success == 1:
        finalname = '{}.txt'.format(os.path.splitext(tmp_file_name)[0])
    else:
        finalname = '{}.err'.format(os.path.splitext(tmp_file_name)[0])


    print("mv " + tmp_file_name + " " + finalname)
    try:
        retcode = subprocess.call("mv " + tmp_file_name + " " + finalname, shell=True)
        if retcode < 0:
            print("Child was terminated by signal", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)


def run_task(num, task):
    """
    Execute task coming from the task_q squeue.
    Input Parameters:
        num : type[int], the worker number.
        task_q: The queue for the input task;
        result_q: The queue for the worker return task state.
        stat_q: The queue for the worker_monitor check the worker hearbeat.

    Return : True --- success; False --- failed
    """
    global worker_name
    global worker_logger
    global g_store_dir

    worker_name = "[worker_" + str(num) + "]"
    worker_logger = logging.getLogger('[Worker]')
    worker_logger.info(worker_name + " started")

    return_ret = True

    try:
        d = task
        t1 = datetime.datetime.now()
        req_url = d['data']
        task_id = d['task_id']
        from_city_id = d['from_city_id']
        to_city_id = d['to_city_id']
        from_city_name = d['from_city_name']
        to_city_name = d['to_city_name']
        search_date = d['date']
        start_date = d['start_date']
        stay_days = d['stay_days']
        trip = d['trip']

        worker_logger.info("{} running task[{}]\n".format(worker_name, task_id))

        # wj add for debug
        ret = None
        time.sleep(1)
        ret = crawler_worker.request_one_flight_by_url(task_id, req_url)

        file_name = create_tmp_result_file_name(task_id, g_store_dir)
        table_name = "flight_{0}_{1}_price".format(str(from_city_id), str(to_city_id))

        flight = dict()
        flight_basic = dict()
        flight['basic'] = flight_basic
        flight_basic['task_id'] = task_id
        flight_basic['fromCity'] = from_city_name
        flight_basic['toCity'] = to_city_name
        flight_basic['trip'] = trip
        flight_basic['tableName'] = table_name
        flight_basic['depDate'] = start_date
        flight_basic['stayDays'] = stay_days
        flight_basic['searchDate'] = search_date
        flight_basic['url'] = req_url

        success_flag = 1
        if ret is None or ret.content is None or len(ret.content) == 0:
            flight['content'] = None
            success_flag = 0
            return_ret = False
        else:
            content_obj = json.loads(ret.content.decode())
            if 'content' in content_obj.keys():
                flight['content'] = content_obj['content']
            else:
                flight['content'] = None
                return_ret = False

        with open(file_name, 'w') as f:
            json.dump(flight, f, sort_keys=True, indent=2)

        time.sleep(1)

        finalize_tmp_result_file_name(file_name, success_flag)

        t2 = datetime.datetime.now()
        tx = t2 - t1
        worker_logger.info("{} finished task[{}] with time [{}] seconds".format(worker_name, task_id, tx.seconds))

    except Exception as e:
        print(e)
        return_ret = False

    return return_ret


def get_flight_info_from_flight_module_element(flight_module_element):
    """
    return a tuple cotains:
    1. flight_price as string
    2. flight_company as string
    """
    price_element_class_name = 'price-column'

    price_element = flight_module_element.find_element_by_css_selector('.flight-module.offer-listing.price-column.offer-price.dollars')
    price = price_element.text()

    company_element = flight_module_element.find_element_by_css_selector('.flight-module.offer-listing.flex-card.flex-area-primary.primary-block.secondary')
    company_name = company_element.text()

    return price, company_name


def get_urls_from_file(filename):
    """
    Get the urls from the file and return as a list.
    """
    url_list = []

    with open(filename, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) == 0:
                continue
            else:
                url_list.append(line)

    return url_list


def test():
    #     d = createDriver()
    #
    #     url_list = get_urls_from_file('test/url_list.txt')
    #     num=1
    #
    #     try:
    #         for url in url_list:
    #             getFlightPrice(d,url,num,1)
    #             num+=1
    #     finally:
    #         closeDriver(d)
    pass


def init_log():
    """
    #Init the main logger
    """
    global logger_handle

    d = str(datetime.date.today())
    t1 = datetime.datetime.now()
    logname = 'log/air_' + d + '.log'
    logger_handle = logging.FileHandler(logname)

    formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s')

    logger_handle.setFormatter(formatter)

    main_logger = logging.getLogger('[Main]')
    main_logger.addHandler(logger_handle)
    main_logger.setLevel('INFO')

    worker_logger = logging.getLogger('[Worker]')
    worker_logger.setLevel('INFO')
    worker_logger.addHandler(logger_handle)

    return main_logger


def main():
    init_log()
    test()


if __name__ == '__main__':
    main()
