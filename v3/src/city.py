#!/usr/bin/env python3

import csv


class CityList():
    def __init__(self, filename):
        self.city_list = []

        with open(filename, 'r') as f:
            csv_data = csv.reader(f)
            next(csv_data)
            for items in csv_data:
                city = dict()
                city['id'] = items[0]
                city['name'] = items[1]
                city['ap_name'] = items[2]
                self.city_list.append(city)

    def get_city_by_id(self, city_id):
        for city in self.city_list:
            if city['id'] == city_id:
                return city
