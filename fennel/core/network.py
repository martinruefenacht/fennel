"""
"""


from abc import ABC, abstractmethod


from fennel.tasks.put import PutTask


class NetworkModel(ABC):
    """
    Abstract class for all network models.
    """

    @abstractmethod
    def evaluate(self, task: PutTask) -> (int, int):
        """
        Evaluate this model.
        """
