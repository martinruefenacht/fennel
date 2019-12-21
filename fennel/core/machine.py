"""
Defines the abstract class for machine models.
"""

import heapq
import abc
from typing import Optional, Iterable, Tuple
from collections import defaultdict

from fennel.core.program import Program
from fennel.core.tasks import Task


class Machine(abc.ABC):
    """
    Abstract class for all machine models.
    """

    def __init__(self, nodes: int):
        self._nodes = nodes
        self._maximum_time = 0

        # fulfilled dependency counter
        self._dependencies = defaultdict(lambda: 0)

        # max time of dependency, gives task begin time
        # starts will not be included
        self._dtimes = defaultdict(lambda: 0)

        # task handlers
        self._task_handlers = {}

        # program counter
        self._program_counter = 0

    @property
    def nodes(self) -> int:
        """
        Get the node count.
        """

        return self._nodes

    def run(self, program: Program) -> None:
        """
        Runs the given program on this machine.
        """

        if program.get_node_count() > self.nodes:
            raise RuntimeError(f'{program} requires greater node count '
                               f'{program.get_process_count()} than '
                               f'{self.nodes}.')

        # task priority queue
        task_queue = []

        # insert all start tasks
        for task in program.get_start_tasks():
            heapq.heappush(task_queue, (0, task))

        # process entire queue
        while task_queue:
            # retrieve next global clock event
            time, task = heapq.heappop(task_queue)

            # execute task
            successors = self._execute(time, program, task)

            # insert all successor tasks
            for successor in successors:
                heapq.heappush(task_queue, successor)

#    def reset(self) -> None:
#        """
#        Reset machine back to initial state.
#        """
#
#        self._dependencies.clear()
#        self._dtimes.clear()

    def _execute(self, time: int, program: Program, task: Task) -> None:
        """
        Looks up required handler for task and executes task using that
        handler.
        """

        assert time >= 0

        # look up task handler and execute
        return self._task_handlers[task.__class__.__name__](time,
                                                            program,
                                                            task)

    def _complete_task(self,
                       time: int,
                       program: Program,
                       task: Task
                       ) -> Iterable[Tuple[int, Task]]:
        """
        For every successor of this task, increment a completion counter,
        and update the time. If all dependencies are complete then return
        all such successors.
        """

        successors = set()

        for successor in program.get_successors_to_task(task.name):
            # increment completed dependencies for successor
            self._dependencies[successor] += 1

            # forward task to last dependency
            self._dtimes[successor] = max(self._dtimes[successor], time)

            # check for completion
            if (self._dependencies[successor] ==
                    program.get_in_degree(successor)):
                successor_task = program.get_task(successor)
                time_next = self._dtimes[successor]

                # delete record of program
                # TODO do we need to do this? they should be unique?
                del self._dtimes[successor]
                del self._dependencies[successor]

                successors.add((time_next, successor_task))

        return successors

    @property
    def maximum_time(self) -> int:
        """
        Get maximum time of run.
        """

        return self._maximum_time






# remove magic 1000, require some intelligent way of memory requirement
# (technically program should know)
# task_queue = libpqueue.PriorityQueue(program.getProcessCount() * 1000
# task_queue.push(0, task)
# while not task_queue.isEmpty():
# time, task = task_queue.pop()
# task_queue.push(*successor)


#     def setVisual(self, context):
#         """
#         """
# 
#         self.context = context
# 
#     def registerVisualContext(self, context):
#         """
#         """
# 
#         self.context = context
# 
#     def drawMachine(self):
#         """
#         """
# 
#         # find max time
#         max_time = int((math.ceil(self.getMaximumTime() / 500) * 500))
#         # TODO required minimum
#         max_time = max(max_time, 2000)
# 
#         # draw time line
#         self.context.drawTimeLine(max_time)
# 
#         # draw process lines
#         self.context.drawProcessLines(self.node_count, max_time)
# 
#     
# 

