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


# This module is used to create crawling tasks
# Created by Wang,Jing
# Created at 2017-09-17


import os

WORKERS = 6
BASE_DIR = '../'


def get_sub_dir(sub_dir):
    return os.path.join(BASE_DIR, sub_dir)


WORKING_DIR = '../work'
RESULT_DIR = get_sub_dir('results')

FIN_RESULT_DIR = get_sub_dir('final_results')
ZIP_DIR = get_sub_dir('zip_results')

STATUS_DIR = get_sub_dir('status')
LOG_DIR = get_sub_dir('log')

DIR_LIST = [RESULT_DIR, FIN_RESULT_DIR, ZIP_DIR, STATUS_DIR, LOG_DIR]

ROUTE_LIST_FILE = 'script/route.csv'
CITY_LIST_FILE = 'script/city.csv'


def main():
    print('WORKERS = {}'.format(WORKERS))
    print('RESULT_DIR = {}'.format(RESULT_DIR))
    print('FIN_RESULT_DIR = {}'.format(FIN_RESULT_DIR))
    print('ROUTE_LIST_FILE = {}'.format(ROUTE_LIST_FILE))
    print('CITY_LIST_FILE = {}'.format(CITY_LIST_FILE))

    print(DIR_LIST)


if __name__ == '__main__':
    main()
