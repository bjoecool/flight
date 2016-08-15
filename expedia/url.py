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

import datetime

class ExpediaReqURL():
    """
    This class focus on creating the url send request URL to 
    https://www.expedia.com.au to get the flight price information.
    """
    def __init__(self,filename="//media//sf_hostshare//air//airport.xlsx"):
        self.filename=filename
        
    def createURL(self,**fly):
        http_head="https://www.expedia.com.au/Flights-Search?mode=search"
        
        from_city_name = fly["from"].lower()
        to_city_name=fly["to"].lower()
        
        departure_date=fly['start_date'].strftime("%d-%m-%Y")
        
        
        leg1=self.createleg(from_city_name,
                            to_city_name,
                            departure_date)
        trip=fly["trip"]
        if trip=="roundtrip":
            return_date=fly['return_date'].strftime("%d-%m-%Y")
            leg2=self.createleg(to_city_name,
                                from_city_name,
                                return_date)
        else:
            leg2=""
            
        children_num = fly['children']
        adults_num = fly['adults']
        
        if children_num > 0:
            passengers='children:'+ str(children_num) + '[8]' + ','
        else:
            passengers='children:'+ str(children_num) +','
        passengers += 'adults:'+ str(adults_num) +','
        passengers += 'infantinlap:N'
        
        options='cabinclass:'+fly['cabinclass']
#         origref='www.expedia.com.au%2FFlight-Search-All'
        
        url = http_head + "&leg1=" + leg1
        url += '&trip=' + trip
        if len(leg2) > 0:
            url += '&leg2=' + leg2
        url += '&passengers=' + passengers
        url += '&options=' + options
#         url += '&origref=' + origref
        
        return url
    
    def createleg(self,from_city_name,to_city_name,departure_date):
        leg = "from:"+from_city_name+","
        leg += "to:"+to_city_name+","
        leg += "departure:"+departure_date
        leg += 'TANYT'
        
        return leg
        
    def get_date(self, dateFormat="%d-%m-%Y", addDays=0):
    
        timeNow = datetime.datetime.now()
        if (addDays!=0):
            anotherTime = timeNow + datetime.timedelta(days=addDays)
        else:
            anotherTime = timeNow
    
        return anotherTime.strftime(dateFormat)

def main():
    print("main")



if __name__=='__main__':
    main()
