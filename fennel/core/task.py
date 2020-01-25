"""
"""


from typing import Optional, Tuple
from enum import Enum, auto


from fennel.core.time import Time


PlannedTask = Tuple[Time, 'Task']


class TaskEvent(Enum):
    # triggered when the task is taken from the priority
    # queue
    SCHEDULED = auto()

    # triggered when the task is delayed because of the
    # process time
    DELAYED = auto()

    # triggered during the execution function 
    EXECUTED = auto()

    # triggered when the task is completed before any
    # successors are being loaded
    COMPLETED = auto()

    # triggered when the _load_task method is called
    LOADED = auto()


class Task:
    """
    The abstract definition of what a task is.
    """

    task_counter: int = 0

    def __init__(self, name: str, node: int, concurrent: bool = False):
        self._name = name
        self._node = node

        self._concurrent = concurrent

        self._any = None

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
    def node(self) -> int:
        """
        Get node id
        """

        return self._node

    @property
    def name(self) -> str:
        """
        Get task name.
        """

        return self._name

    @property
    def concurrent(self) -> bool:
        """
        Gets concurrency.
        """

        return self._concurrent

    @concurrent.setter
    def concurrent(self, concurrency: bool) -> None:
        self._concurrent = concurrency

    @property
    def any(self) -> Optional[int]:
        """
        Gets the any count if not None.
        """

        return self._any

    @any.setter
    def any(self, any_count: int) -> None:
        if any_count <= 0:
            raise RuntimeError('Any property must be greater than 0.')

        self._any = any_count
