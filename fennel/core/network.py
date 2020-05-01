"""
Defines the NetworkModel and NetworkTime classes.
"""


# pylint: disable=too-few-public-methods


from abc import ABC, abstractmethod
from dataclasses import dataclass


from fennel.tasks.put import PutTask


@dataclass
class NetworkTime():
    """
    Dataclass used to represent local return time
    and remote arrival time for a network operation.
    """

    local: int
    remote: int


class NetworkModel(ABC):
    """
    Abstract class for all network models.
    """

    @abstractmethod
    def evaluate(self, task: PutTask) -> NetworkTime:
        """
        Evaluate this model.
        """

        assert task
