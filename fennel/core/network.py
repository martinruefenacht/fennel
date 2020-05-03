"""
Defines the NetworkModel and NetworkTime classes.
"""


# pylint: disable=too-few-public-methods


from typing import Union
from abc import ABC, abstractmethod
from dataclasses import dataclass


from fennel.core.time import Time
from fennel.tasks.put import PutTask
from fennel.tasks.get import GetTask


@dataclass
class NetworkTime():
    """
    Dataclass used to represent local return time
    and remote arrival time for a network operation.
    """

    local: Time
    remote: Time


class NetworkModel(ABC):
    """
    Abstract class for all network models.
    """

    @abstractmethod
    def evaluate(self,
                 time: Time,
                 task: Union[PutTask, GetTask]) -> NetworkTime:
        """
        Evaluate this model.
        """
