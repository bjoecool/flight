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


import urllib.request

def get_dict_from_file(file_name):
    d = dict()
    with open(file_name,'r') as f:
        for line in f.readlines():
            line = line.strip()
            str_list=line.spilit(':',maxspilit=1)
            if len(str_list)<=1:
                continue
            d[str_list]

def main():

if __name__=='__main__':
    main()
