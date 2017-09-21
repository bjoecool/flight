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

import time
import os
import signal
from worker import Worker
from command import ProcessCommand

class TaskCtlWorker(Worker):
    name = "task_controler"

    task_status = 'notstart'

    def run(self):
        print('worker_{} start to run'.format(self.name))

        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGQUIT, signal.SIG_IGN)

        while self.running:
            try:
                item = self.get_cmd_queue()
                if item is not None:
                    if item.type == ProcessCommand.CommandType.STOP:
                        print('worker_{} recieved stop command'.format(self.name))
                        break
                else:
                    time.sleep(5)
                    print("{} put task into task_q".format(self.name))
                    # [self.task_q.put(x) for x in range(1,11)]
            except Exception as e:
                print(e)
            finally:
                time.sleep(1)

        print('worker_{} exit from run'.format(self.name))


def get_route_task():
    """
    Get a route task from the task_center.
    This function will send a request to the task_center and
    get a RESTFul API as following:
    {"route_id":1}
    """


def create_tasks_by_routeid():
    pass


def main():
    pass


if __name__ == '__main__':
    main()


# def printkey(obj):
#     def f(n):
#         return ',' if n % 8 > 0 else None
#     [print(x, end=f(i + 1)) for i, x in (enumerate(dir(obj)))]

# printkey(threading)
