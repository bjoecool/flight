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

from multiprocessing import Queue
import time
import os
from worker import Worker

class WorkerManager():
    """
    WokerManager is used to manage the workers including:
    1. alloc_workers
    2. start_workers
    3. stop_workers
    4. exec_primary_task
    """
    def __init__(self):
        self.worker_list = []
        self.task_q = Queue()
        self.running = 1

    def alloc_workers(self, total_workers, target=None, task_q=None, *args):
        """
        Alloc number workers
        """
        print('TaskManager.alloc_workers')
        for i in range(1, total_workers + 1):
            wk = Worker(i, target, task_q, *args)
            self.worker_list.append(wk)

    def start_workers(self):
        print('TaskManager.start_workers')
        [wk.start() for wk in self.worker_list]

    def stop_workers(self):
        print('TaskManager.stop_workers')
        [wk.stop() for wk in self.worker_list]
        [wk.join() for wk in self.worker_list]

    def run(self):
        try:
            while self.running:
                time.sleep(1)
        except StopException:
            self.stop_workers()
        except Exception as e:
            print(str(e))

    def stop(self):
        raise StopException('stop')

    def exec_primary_task(self, task_func, *task_args):
        """
        Put the primary task into the cmd_queue to let the worker
        execute the primary task.
        """
        print('TaskManager.primary_task {}'.format(task_args))
        [w.primary_task(task_func,*task_args) for w in self.worker_list]

