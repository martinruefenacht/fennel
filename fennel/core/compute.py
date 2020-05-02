"""
Definition of the abstact ComputeModel.
"""


# pylint: disable=too-few-public-methods


from abc import ABC, abstractmethod

from fennel.tasks.compute import ComputeTask
from fennel.core.time import Time


class ComputeModel(ABC):
    """
    Abstract class for all compute models.
    """

    @abstractmethod
    def evaluate(self, time: Time, task: ComputeTask) -> Time:
        """
        The evaluation of the model for a given task.
        """
