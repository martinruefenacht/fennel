"""
"""

from fennel.core.task import Task


class NICTask(Task):
    """
    """

    def __init__(self, puttask):
        super().__init__('name', puttask.proc)

        self.puttask = puttask
