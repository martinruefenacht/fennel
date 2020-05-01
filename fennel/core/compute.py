"""
Definition of the abstact ComputeModel.
"""


# pylint: disable=too-few-public-methods


from abc import ABC, abstractmethod

from fennel.tasks.compute import ComputeTask


class ComputeModel(ABC):
    """
    Abstract class for all compute models.
    """

    @abstractmethod
    def evaluate(self, time: int, task: ComputeTask) -> int:
        """
        The evaluation of the model for a given task.
        """
