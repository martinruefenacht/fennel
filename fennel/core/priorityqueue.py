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
        Deteremines whether the queue is empty.
        """

        return bool(self._task_queue)

    def pop(self) -> PlannedTask:
        """
        Removes the high priority PlannedTask.
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
        Appends all Tasks to the queue with a globally given time..
        """

        for task in tasks:
            self.push(time, task)

    def push_iterable(self, tasks: Iterable[PlannedTask]) -> None:
        """
        Appens all Tasks to the queue with each having a given time.
        """

        for combined in tasks:
            heapq.heappush(self._task_queue, combined)
