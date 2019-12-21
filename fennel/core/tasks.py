"""
"""

class Task:
    """
    """

    task_counter: int = 0

    def __init__(self, name: str, proc: int):
        self._name = name
        self._proc = proc

        self._taskid = Task.task_counter
        Task.task_counter += 1

    def __lt__(self, task):
        return self._taskid < task.taskid

    @property
    def taskid(self) -> int:
        """
        Get task id.
        """

        return self._taskid

    @property
    def process(self) -> int:
        """
        Get process id
        """

        return self._proc

    @property
    def name(self) -> str:
        """
        Get process name.
        """

        return self._name


class StartTask(Task):
    """
    The StartTask is the initial hook for a process.
    """

    def __init__(self, name: str, proc: int, skew: int = 0):
        super().__init__(name, proc)

        # initial skew time, asymmetric arrival time
        self._skew = skew

    @property
    def skew(self) -> int:
        """
        Get initial skew.
        """

        return self._skew


class ProxyTask(Task):
    """
    The ProxyTask is an empty task used be to able to not trigger
    another task.
    """


class SleepTask(Task):
    """
    SleepTask specifies a time delay for this process.
    """

    def __init__(self, name: str, proc: int, delay: int):
        # initialize Task
        super().__init__(name, proc)

        # initialize SleepTask
        self._delay = delay

    @property
    def delay(self) -> int:
        """
        Get the delay value.
        """

        return self._delay


class ComputeTask(Task):
    """
    ComputeTask represents the time of a model during which no communication
    takes place.
    """
    def __init__(self, name: str, proc: int, time: int):
        # initialize task
        super().__init__(name, proc)

        # TODO support data size?

        # initialize compute task
        self._time = time

    @property
    def time(self) -> int:
        """
        Get compute time.
        """

        return self._time


class PutTask(Task):
    """
    Represents an RDMA put.
    """

    def __init__(self,
                 name: str,
                 proc: int,
                 target: int,
                 size: int,
                 block: bool = True):
        super().__init__(name, proc)

        self._target = target
        self._size = size
        self._block = block

    @property
    def target(self) -> int:
        """
        Get target of put operation.
        """

        return self._target

    @property
    def message_size(self) -> int:
        """
        Get put message size.
        """

        return self._size

    @property
    def blocking(self) -> bool:
        """
        Get whether the operation is blocking.
        """

        return self._block


class NICTask(Task):
    def __init__(self, puttask):
        super().__init__('name', puttask.proc)
        
        self.puttask = puttask


class MsgTask(Task):
    def __init__(self, puttask, start, arrival):
        super().__init__('name', puttask.proc)

        self.puttask = puttask
        self.start = start
        self.arrival = arrival
        self.target = puttask.target
        self.size = puttask.size
        self.block = puttask.block
