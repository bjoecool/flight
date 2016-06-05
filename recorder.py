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
import subprocess
import datetime
from enum import Enum

class RecorderMode(Enum):
    string = 0
    binary = 1
    
class Recorder():
    def __init__(self,schedule_id, mode=RecorderMode.string):
        dir="results"
        prefix="res_"
        date=str(datetime.date.today().strftime('%Y%m%d'))
        self.filename=dir+"/"+prefix+date+"_"+schedule_id+"._xt"
        self.finalname=dir+"/"+prefix+date+"_"+schedule_id+".txt"
        self.mode=mode
        
        if mode == RecorderMode.binary:
            self.f = open(self.filename,"wb")
        else:
            self.f = open(self.filename,"w")
    
#     def checkResultFile(self, filename):
#         if os.path.isfile(filename):
#             print("%s has already there, remove it" %filename)
#             os.remove(filename)

    def __del__(self):
        self.f.close()
        
    def new_line(self):
        if self.mode == RecorderMode.binary:
            self.f.write(bytes('\n','utf-8'))
        else:
            self.f.write('\n')
        
    def write(self,text):
        '''
        Write the text into the file without append \n
        '''
        if len(text)>0:
            if self.mode == RecorderMode.binary:
                self.f.write(bytes(text,'utf-8'))
            else:
                self.f.write(text)

    def writeN(self,text):
        '''
        Write the text into the file with '\n' at end
        '''
        if len(text)>0:
            if self.mode == RecorderMode.binary:
                self.f.write(bytes(text,'utf-8'))
                self.f.write(bytes('\n','utf-8'))
            else:
                self.f.write(text)
                self.f.write("\n")
                
    def getPriceList(self,filename):
        '''
        Handle the result_x.txt file and get the price in it.
        Return a list contains all price
        '''
        price_list=[]
        with open(filename) as f:
            for line in f.readlines():
                if line.find("Result ") != -1:
                    if line[-1] == '\n':
                        line=line[0:-1]
                    s=line.split(",")
                    s1=s[1]
                    s2=s1.lstrip().replace("$","")
                    price_list.append(s2)
            f.close()
            
        return price_list

    def savePriceintoDB(self,price_list,schedule_id):
        pass
    
    def finish(self):
        """
        rename the file._xt to file.txt 
        """
        try:
            retcode = subprocess.call("mv "+self.filename+" "+self.finalname, shell=True)
            if retcode<0:
                print("Child was terminated by signal",retcode, file=sys.stderr)
        except OSError as e:
            print("Execution failed:", e, file=sys.stderr)
            
def main():
    print("main")
    re = Recorder('123')
    re.write("hello world")
    re.write("1234567")
    re.write("fasfasdfasfa")

if __name__=='__main__':
    main()
