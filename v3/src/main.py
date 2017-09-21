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
import datetime
import time
import os
import signal
import logging

from manager import WorkerManager
from enum import Enum
from taskctl import TaskCtlWorker

import settings
import task
import worker_exec


class TaskState(Enum):
    START = 1
    STOP = 2
    CONTINUE = 3


class TimeOut():
    class Timeout_Exception(Exception):
        def __init__(self, err="Timeout_Exception"):
            self.err = err

        def __str__(self):
            return self.err

    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        print('Start to time')
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)

    def __exit__(self, *args):
        # signal.alarm(0)
        print('Exist Timeout')
        # [print(type(x)) for x in args]

    def raise_timeout(self, *args):
        signal.alarm(0)  # Close the time out here
        print('Time out')
        [print(type(x)) for x in args]
        raise self.Timeout_Exception()


class StopException(Exception):
    def __init__(self, error=None):
        self.error = error

    def __str__(self):
        return self.error if self.error is not None else 'stop_exception'


def create_kill_script():
    with open('kill.sh', 'w') as f:
        f.write('echo "kill {}"\n'.format(os.getpid()))
        f.write('kill {}'.format(os.getpid()))


def sig_handle(signum, frame):
    if signum == signal.SIGQUIT:
        print("Receive SIGQUIT")
        raise StopException()
    elif signum == signal.SIGINT:
        print("Receive SIGINT")
        raise StopException()
    elif signum == signal.SIGTERM:
        print("Receive SIGTERM")
        raise StopException()
    elif signum == signal.SIGALRM:
        print("Receive SIGALRM")
        raise TimeOut.Timeout_Exception()


def get_task_state():
    """
    This function return the task should be done.

    """
    gmt1 = time.localtime(time.time())
    if gmt1.tm_hour > 23:
        return TaskState.STOP
    elif gmt1.tm_hour == 0 and gmt1.tm_min >= 30:
        return TaskState.START
    elif gmt1.tm_hour == 15 and gmt1.tm_min >= 4:
        return TaskState.START
    else:
        return TaskState.CONTINUE


def put_tasks_into_queue(task_queue, task_list):
    """
    Each item in task_list is an instance of FlightQueryTask
    """
    # Put task list
    for qtask in task_list:
        d = dict()
        d['cmd'] = 'continue'
        d['task_id'] = qtask.task_id
        d['data'] = qtask.req_url
        d['date'] = datetime.date.today().isoformat()
        d['from_city_id'] = qtask.from_city_id
        d['to_city_id'] = qtask.to_city_id
        d['from_city_name'] = qtask.from_city_name
        d['to_city_name'] = qtask.to_city_name
        d['start_date'] = qtask.start_date
        d['stay_days'] = qtask.stay_days
        d['trip'] = qtask.trip
        task_queue.put(d)


def init_dir():
    """
    Build some sub dir like 'log, results'
    """
    for d in settings.DIR_LIST:
        if os.path.isdir(d) == False:
            os.mkdir(d)


def init_log(stream=False):
    """
    #Init the main logger
    """
    global logger_handle

    d = str(datetime.date.today())
    t1 = datetime.datetime.now()

    logname = os.path.join(settings.LOG_DIR, 'air_{}.log'.format(d))
    errlog = os.path.join(settings.LOG_DIR, 'error_{}.log'.format(d))

    logger_handle = logging.FileHandler(logname)

    formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s')

    logger_handle.setFormatter(formatter)

    main_logger = logging.getLogger('[Main]')
    main_logger.addHandler(logger_handle)
    main_logger.setLevel('INFO')

    worker_logger = logging.getLogger('[Worker]')
    worker_logger.setLevel('INFO')
    worker_logger.addHandler(logger_handle)

    error_logger = logging.getLogger('[Error]')
    error_logger.setLevel('ERROR')
    error_logger.addHandler(logger_handle)

    if stream:
        stream_logger_handle = logging.StreamHandler()
        stream_formatter = logging.Formatter('%(message)s')
        stream_logger_handle.setFormatter(stream_formatter)

        main_logger.addHandler(stream_logger_handle)
        worker_logger.addHandler(stream_logger_handle)
        error_logger.addHandler(stream_logger_handle)

    return main_logger


def main():
    print('Enter the main function')

    init_dir()
    init_log(stream=True)

    create_kill_script()

    signal.signal(signal.SIGINT, sig_handle)
    signal.signal(signal.SIGTERM, sig_handle)
    signal.signal(signal.SIGQUIT, sig_handle)
    signal.signal(signal.SIGALRM, sig_handle)
    task_q = Queue()

    wk_manager = WorkerManager()
    wk_manager.alloc_workers(5, target=worker_exec.run_task, task_q=task_q)

    # wk_manager.alloc_workers(5, target=task.run_query_task, task_q=task_q)

    # [task_q.put(x) for x in range(1, 4)]
    task_list = task.get_task_list_by_route_id(1)

    # [task_q.put(x) for x in task_list[:10]]

    put_tasks_into_queue(task_q, task_list[:10])

    wk_manager.start_workers()

    task_worker = TaskCtlWorker(0, None, task_q)

    task_worker.start()

    try:
        while(1):
            # wk_manager.exec_primary_task(new_task_func, *[1, 2, 3, 4])
            time.sleep(12)
            # time.sleep(5)
            # task_state = get_task_state()
            # print(task_state)
            # [task_q.put(x) for x in range(1, 10)]

    except StopException:
        print("Go into StopException")
    except TimeOut.Timeout_Exception:
        print('current time is {}'.format(time.localtime(time.time())))
    except Exception as e:
        print(e)
    finally:
        wk_manager.stop_workers()
        task_worker.stop()
        task_worker.join()

    # [w.stop() for w in worker_list]

    # [w.join() for w in worker_list]

    print('Exist the main function')


if __name__ == '__main__':
    main()


# def printkey(obj):
#     def f(n):
#         return ',' if n % 8 > 0 else None
#     [print(x, end=f(i + 1)) for i, x in (enumerate(dir(obj)))]

# printkey(threading)
