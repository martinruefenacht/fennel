"""
Defines the abstract class for machine models.
"""

import heapq
from abc import ABC
from typing import (Iterable, Tuple, Optional, MutableSet, MutableMapping,
                    Callable, List)
from collections import defaultdict

from fennel.core.program import Program
from fennel.core.task import Task
from fennel.visual.canvas import Canvas
from fennel.core.instrument import Instrument
from fennel.tasks.proxy import ProxyTask


class Machine(ABC):
    """
    Abstract class for all machine models.
    """

    def __init__(self, nodes: int):
        self._nodes = nodes
        self._maximum_time = 0
        self._process_times: MutableMapping[int, int] = defaultdict(lambda: 0)
        #self._process_times = [0] * self._nodes

        self._instruments: MutableSet[Instrument] = set()

        # fulfilled dependency counter
        # TODO could be MachineState abstraction
        self._dependencies: MutableMapping[str, int] = defaultdict(lambda: 0)

        # max time of dependency, gives task begin time
        # starts will not be included
        self._dtimes: MutableMapping[str, int] = defaultdict(lambda: 0)

        self._task_handlers: MutableMapping[str,
                                            Optional[Callable[[int, Task], int]]] = defaultdict(lambda: None)

        self._task_handlers['ProxyTask'] = self._execute_proxy_task

        # program counter
        # TODO where is this used???
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

    @property
    def draw_mode(self) -> bool:
        """
        Determine draw mode from canvas presence.
        """

        return self._canvas is not None

    @property
    def maximum_time(self) -> int:
        """
        Get maximum time of run.
        """

        return self._maximum_time

    def run(self, program: Program) -> None:
        """
        Runs the given program on this machine.
        """

        # TODO if sampling mode, then multiprocessing here
        # separate MachineState

        if program.get_process_count() > self.nodes:
            raise RuntimeError(f'{program} requires greater node count '
                               f'{program.get_process_count()} than '
                               f'{self.nodes}.')

        # TODO how does this need to change to accomodate network simulation?

        # task priority queue
        # this is the core of the simulation
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

    def _set_process_time(self, process: int, time: int) -> None:
        """
        Convenience function to update time of process.
        """

        self._process_times[process] = time
        self._update_maximum_time(time)

    def _update_maximum_time(self, time: int) -> None:
        """
        Convience function to update the maximum time of the machine.
        """

        self._maximum_time = max(self._maximum_time, time)

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

        # delay task if process time is further
        if self._process_times[task.process] > time:
            return [(self._process_times[task.process], task)]

        # look up task handler and execute
        handler = self._task_handlers[task.__class__.__name__]

        if not handler:
            raise RuntimeError('callable look up is None')

        time_successors = handler(time, task)

        return self._complete_task(time_successors,
                                   program,
                                   task)

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

    def _execute_proxy_task(self,
                            time: int,
                            task: ProxyTask
                            ) -> int:
        """
        Executes proxy task.

        Proxy tasks are used to allow for easier program construction; they
        have no simulation effect therefore just complete the task and return
        the successor tasks.
        """

        # proxy tasks complete immediately in simulation time therefore no
        # time is used
        # self._set_process_time(task.process, time)

        # proxy tasks are never drawn

        return time





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
