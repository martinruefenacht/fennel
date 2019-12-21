"""
Defines the abstract class for machine models.
"""

import heapq
import abc
from typing import Iterable, Tuple, Optional, MutableSet, MutableMapping, Callable, List
from collections import defaultdict

from fennel.core.program import Program
from fennel.core.task import Task
from fennel.visual.canvas import Canvas
from fennel.core.instrument import Instrument


class Machine(abc.ABC):
    """
    Abstract class for all machine models.
    """

    def __init__(self, nodes: int):
        self._nodes = nodes
        self._maximum_time = 0

        self._instruments: MutableSet[Instrument] = set()

        # fulfilled dependency counter
        self._dependencies: MutableMapping[str, int] = defaultdict(lambda: 0)

        # max time of dependency, gives task begin time
        # starts will not be included
        self._dtimes: MutableMapping[str, int] = defaultdict(lambda: 0)

        # task handlers
        self._task_handlers: MutableMapping[str, Optional[Callable[[int, Program, Task], Iterable[Tuple[int, Task]]]]] = defaultdict(lambda: None)

        # program counter
        self._program_counter = 0

        self._canvas: Optional[Canvas] = None

    @property
    def nodes(self) -> int:
        """
        Get the node count.
        """

        return self._nodes

    @property
    def canvas(self) -> Optional[Canvas]:
        """
        Get canvas.
        """

        return self._canvas

    @canvas.setter
    def canvas(self, canvas: Canvas) -> None:
        """
        Set canvas.
        """

        self._canvas = canvas

    def run(self, program: Program) -> None:
        """
        Runs the given program on this machine.
        """

        if program.get_process_count() > self.nodes:
            raise RuntimeError(f'{program} requires greater node count '
                               f'{program.get_process_count()} than '
                               f'{self.nodes}.')

        # TODO how does this need to change to accomodate network simulation?

        # task priority queue
        task_queue: List[Tuple[int, Task]] = []

        # insert all start tasks
        task: Task
        for task in program.get_start_tasks():
            heapq.heappush(task_queue, (0, task))

        # process entire queue
        while task_queue:
            # retrieve next global clock event
            time: int
            time, task = heapq.heappop(task_queue)

            # execute task
            successors = self._execute(time, program, task)

            # insert all successor tasks
            for successor in successors:
                heapq.heappush(task_queue, successor)

    def _execute(self,
                 time: int,
                 program: Program,
                 task: Task
                 ) -> Iterable[Tuple[int, Task]]:
        """
        Looks up required handler for task and executes task using that
        handler.
        """

        assert time >= 0

        # look up task handler and execute
        callable = self._task_handlers[task.__class__.__name__]

        if not callable:
            raise RuntimeError('callable is None')

        return callable(time, program, task)


    def _run_instruments(self,
                         time: int,
                         program: Program,
                         task: Task) -> None:
        """
        Run all instruments on the task completion.
        """

        for instrument in self._instruments:
            instrument.measure(time, program, task)

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
                if not successor_task:
                    raise RuntimeError('Successor does not exist.')

                time_next = self._dtimes[successor]

                # delete record of program
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

#     def drawMachine(self):
#         """
#         """

#         # find max time
#         max_time = int((math.ceil(self.getMaximumTime() / 500) * 500))
#         # TODO required minimum
#         max_time = max(max_time, 2000)

#         # draw time line
#         self.context.drawTimeLine(max_time)

#         # draw process lines
#         self.context.drawProcessLines(self.node_count, max_time)
