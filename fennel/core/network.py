"""
Defines the NetworkModel and NetworkTime classes.
"""


from abc import ABC, abstractmethod
from typing import NamedTuple


from fennel.tasks.put import PutTask


class NetworkTime(NamedTuple):
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
