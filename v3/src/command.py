from enum import Enum

class ProcessCommand():
    class CommandType(Enum):
        NONE = 0
        STOP = 1
        TASK = 2

    def __init__(self, type=CommandType.STOP, func=None, *args):
        self.type = type
        self.func = func
        self.args = args
