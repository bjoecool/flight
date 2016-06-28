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

# import logger
# import t2

def f1(name, q_list):
    print(type(q_list))
    for q in q_list:
        print(q)
    q_list.append('xxx')
    q_list.sort()
        
    print(name)
    
def read_bin_file(file_name):
    with open(file_name,'rb') as f:
        for line in f.readlines():
            s = line.decode()
            print('line = %s' %line)
            print('s = %s' %s.encode())

def main():
    print("Enter t1 module")
    
    read_bin_file('t1.txt')
        
    print("Exit t1 module")

if __name__=='__main__':
    main()
