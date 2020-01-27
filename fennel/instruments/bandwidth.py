"""
Defines the BandwidthInstrument class used to measure the
bandwidth usage of a program run on a machine.
"""


import logging


from fennel.core.instrument import Instrument
from fennel.core.time import Time
from fennel.core.task import Task
from fennel.core.program import Program


from fennel.tasks.put import PutTask


class BandwidthInstrument(Instrument):
    """
    Measures the bandwidth usage of a program.
    """

    def __init__(self):
        super().__init__()

        self._tasks = {}

    def task_executed(self, task: Task, _: Program, time: Time) -> None:
        """
        Record a task executing.
        """

        if not isinstance(task, PutTask):
            return

        assert task not in self._tasks

        self._tasks[task] = {'start': time}

    def task_completed(self, task: Task, _: Program, time: Time) -> None:
        """
        Record successor time of PutTasks.
        """

        if not isinstance(task, PutTask):
            return

        assert task in self._tasks, task.name

        self._tasks[task]['end'] = time

    def calculate_bandwidth(self) -> float:
        """
        Calculates the bandwidth usage (B/s).
        """

        total_transferred = 0
        total_time = 0.0

        for task, times in self._tasks.items():
            total_transferred += task.size

            logging.debug(times)

            total_time += (times['end'] - times['start'])

        return total_transferred / total_time
