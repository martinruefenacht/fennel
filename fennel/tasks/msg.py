"""
"""

from fennel.core.task import Task


class MsgTask(Task):
    """
    """

    def __init__(self, puttask, start, arrival):
        super().__init__('name', puttask.proc)

        self.puttask = puttask
        self.start = start
        self.arrival = arrival
        self.target = puttask.target
        self.size = puttask.size
        self.block = puttask.block
