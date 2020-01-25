"""
Defines the abstract Instrument class.
"""

from typing import List

from fennel.core.program import Program
from fennel.core.task import Task
from fennel.core.time import Time

class Instrument:
    """
    Instrument abstract definition.
    """

    def __init__(self):
        pass

    def task_loaded(self,
                    task: Task,
                    program: Program,
                    time: Time,
                    dependent_times: List[Time]):
        """
        This method is triggered on a listening instrument when the
        TaskEvent LOADED happens.
        """

    def task_delayed(self,
                     task: Task,
                     program: Program,
                     time: Time,
                     earliest: Time):
        """
        This method is triggered when the TaskEvent DELAYED happens.
        """

    def task_completed(self,
                       task: Task,
                       program: Program,
                       time: Time):
        """
        This method is triggered when the TaskEvent COMPLETED happens.
        """
