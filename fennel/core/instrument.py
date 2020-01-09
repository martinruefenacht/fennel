"""
Defines the abstract Instrument class.
"""

from abc import ABC, abstractmethod

from fennel.core.program import Program
from fennel.core.task import Task

class Instrument(ABC):
    """
    Instrument abstract definition.
    """

    def __init__(self):
        pass


    def measure(self, time: int, program: Program, task: Task):
        """
        """

        pass
