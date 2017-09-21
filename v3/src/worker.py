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

import multiprocessing
from multiprocessing import Process, Queue
import time
import os
import queue
import signal
from command import ProcessCommand

# from worker_exec import execTask


class Worker(Process):
    def __init__(self, worker_num, handler, task_q, *args):
        """Initialize Process object and worker."""
#         super().__init__(self,group=None)
        multiprocessing.Process.__init__(self)

        self.num = worker_num  # worker number
        self.running = 1
        self.handler = handler
        self.queue = Queue()
        self.task_q = task_q
        self.stopper = ProcessCommand()
        self.args = args

        self.task_failure_times = 0

    def get_cmd_queue(self):
        """Get the command from queue."""
        try:
            item = self.queue.get_nowait()
        except queue.Empty:
            item = None
        except Exception:
            item = None

        return item

    def get_task(self):
        try:
            item = self.task_q.get_nowait()
        except queue.Empty:
            item = None
        except Exception:
            item = None

        return item

    def run(self):
        print('worker_{} start to run'.format(self.num))

        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGQUIT, signal.SIG_IGN)

        while self.running:
            try:
                item = self.get_cmd_queue()
                if item is not None:
                    if item.type == ProcessCommand.CommandType.STOP:
                        print('worker_{} recieved stop command'.format(self.num))
                        break
                    elif item.type == ProcessCommand.CommandType.TASK:
                        # print('worker_{} recieved new task'.format(self.num))
                        item.func(self.num, *item.args)
                else:
                    task_item = self.get_task()
                    if task_item is not None:
                        if self.handler(self.num, task_item) == False:
                            self.task_failure_times += 1
                        else:
                            self.task_failure_times = 0
                    else:
                        time.sleep(1)
            except Exception as e:
                print(e)
            finally:
                time.sleep(1)

        print('worker_{} exit from run'.format(self.num))

    def stop(self):
        """Put an item in the queue to be processed by the handler."""
        self.queue.put(self.stopper)

    def primary_task(self, task_handle, *args):
        """
        Put primary task into the command_queue. The worker will finishe primary task
        if there is. Then continue to the regular tasks from task_q
        """
        pcmd = ProcessCommand(ProcessCommand.CommandType.TASK, task_handle, *args)
        self.queue.put(pcmd)


def main():
    pass


if __name__ == '__main__':
    main()


# def printkey(obj):
#     def f(n):
#         return ',' if n % 8 > 0 else None
#     [print(x, end=f(i + 1)) for i, x in (enumerate(dir(obj)))]

# printkey(threading)
