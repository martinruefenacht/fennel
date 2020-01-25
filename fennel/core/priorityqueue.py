"""
Defines the internal priority queue implementation.
"""


from typing import List, Iterable
import heapq


from fennel.core.task import Task, PlannedTask
from fennel.core.time import Time


class PriorityQueue:
    """
    A wrapper around any particular priority queue implementation.
    """

    def __init__(self):
        self._task_queue: List[PlannedTask] = []

    def is_not_empty(self) -> bool:
        """
        """

        return bool(self._task_queue)

    def pop(self) -> PlannedTask:
        """
        """

        return heapq.heappop(self._task_queue)

    def push(self, time: Time, task: Task) -> None:
        """
        Push a task into the priority queue at a time priority.
        """

        heapq.heappush(self._task_queue, (time, task))

    def push_iterable_with_time(self,
                                time: Time,
                                tasks: Iterable[Task]) -> None:
        """
        """

        for task in tasks:
            self.push(time, task)

    def push_iterable(self, iterable: Iterable[PlannedTask]) -> None:
        """
        """

        for combined in iterable:
            heapq.heappush(self._task_queue, combined)
