"""
This module defines the RecorderInstrument.

The RecorderInstrument records all completion events of tasks.
"""


from typing import MutableMapping, Mapping


from fennel.core.instrument import Instrument
from fennel.core.time import Time
from fennel.core.task import Task
from fennel.core.program import Program


class RecorderInstrument(Instrument):
    """
    """

    def __init__(self):
        super().__init__()

        self._record: MutableMapping[str, Time] = {}

    def task_completed(self,
                       task: Task,
                       program: Program,
                       time: Time):
        """
        """

        self._record[task.name] = time

    @property
    def record(self) -> Mapping[str, Time]:
        """
        """

        return self._record
