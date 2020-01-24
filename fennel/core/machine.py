"""
Defines the abstract class for machine models.
"""


import logging
import heapq
from abc import ABC
from typing import (Iterable, Tuple, Optional, MutableSet, MutableMapping,
                    Callable, List, Union)
from collections import defaultdict


from fennel.core.program import Program
from fennel.core.task import Task
from fennel.core.compute import ComputeModel
from fennel.core.network import NetworkModel


from fennel.visual.canvas import Canvas
from fennel.core.instrument import Instrument
from fennel.tasks.proxy import ProxyTask
from fennel.tasks.put import PutTask
from fennel.tasks.start import StartTask
from fennel.tasks.sleep import SleepTask
from fennel.tasks.compute import ComputeTask


class Machine(ABC):
    """
    Abstract class for all machine models.
    """

    def __init__(self,
                 nodes: int,
                 processes: int,
                 compute: ComputeModel,
                 network: NetworkModel):
        self._nodes = nodes
        self._processes = processes

        self._compute_model = compute
        self._network_model = network

        self._instruments: MutableSet[Instrument] = set()

        # fulfilled dependency counter
        self._dependencies: MutableMapping[str, int] = defaultdict(lambda: 0)

        # max time of dependency, gives task begin time
        # starts will not be included
        self._dtimes: MutableMapping[str, int] = defaultdict(lambda: 0)

        self._node_times: MutableMapping[int, [int, int]]
        self._node_times = [[0] * processes] * nodes

        self._task_handlers: MutableMapping[str,
                                            Union[
                                                Callable[[int, StartTask], int],
                                                Callable[[int, ProxyTask], int],
                                                Callable[[int, SleepTask], int],
                                                Callable[[int, ComputeTask], int],
                                                Callable[[int, PutTask], int],
                                                ]] = dict()

        self._task_handlers['ProxyTask'] = self._execute_proxy_task
        self._task_handlers['StartTask'] = self._execute_start_task
        self._task_handlers['SleepTask'] = self._execute_sleep_task
        self._task_handlers['ComputeTask'] = self._execute_compute_task
        self._task_handlers['PutTask'] = self._execute_put_task

        self._canvas: Optional[Canvas] = None

    def is_finished(self) -> bool:
        """
        Checks whether the machine is finished.
        """

        return not self._dependencies and not self._dtimes

    @property
    def nodes(self) -> int:
        """
        Get the node count.
        """

        return self._nodes

    @property
    def processes(self) -> int:
        """
        Get the process count.
        """

        return self._processes

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

        time = max((proc_time
                    for node in self._node_times
                    for proc_time in node))

        assert time >= 0
        return time

    def run(self, program: Program) -> None:
        """
        Runs the given program on this machine.
        """

        if program.get_process_count() > self.nodes:
            raise RuntimeError(f'{program} requires greater node count '
                               f'{program.get_process_count()} than '
                               f'{self.nodes}.')

        # TODO if sampling mode, then multiprocessing here
        # separate MachineState
        # if not self.draw_mode:
        #     multiprocessing.pool
        #     # give different seeds to the machines

        self._run_program(program)

    def _run_program(self, program: Program) -> None:
        """
        Run the given Program on the current machine state.
        """

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

            assert time >= 0

            # execute task
            successors = self._execute(time, program, task)

            # insert all successor tasks
            for successor in successors:
                heapq.heappush(task_queue, successor)

    def _set_process_time(self, node: int, process: int, time: int) -> None:
        """
        Convenience function to update time of (node, process).
        """

        self._node_times[node][process] = time

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

        logging.debug('execute %s @ %i', task.name, time)

        # find earliest time to execute
        if task.concurrent:
            tmp = list(proc for proc in self._node_times[task.node])
            earliest = min(tmp)
            process = tmp.index(earliest)

        else:
            earliest = max(proc for proc in self._node_times[task.node])
            process = 0

        # delay task if process time is further
        if earliest > time:
            # TODO what is the reason for the delaying?
            return [(earliest, task)]

        # look up task handler and execute
        handler = self._task_handlers[task.__class__.__name__]

        time_successors = handler(time, task, process)

        logging.debug('%s ended %i', task.name, time_successors)

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

        sucs = list(program.get_successors_to_task(task.name))
        # TODO generator is a problem

        # only proxy tasks can have no successors
        if (not isinstance(task, ProxyTask) and
                not sucs):
            raise RuntimeError('All programs must end with proxy tasks. '
                               f'{task.name} is not a ProxyTask.')

        successors = set()

        for successor in sucs:
            # increment completed dependencies for successor
            self._dependencies[successor] += 1

            # forward task to last dependency
            self._dtimes[successor] = max(self._dtimes[successor], time)

            # if successor is any capable
            # TODO clean up logic
            if (program[successor].any and
                    self._dependencies[successor] >= program[successor].any):
                # execute this task
                successors.add(self._load_task(successor, program))

            # check for completion of all dependencies
            elif (self._dependencies[successor] ==
                    program.get_in_degree(successor)):

                successors.add(self._load_task(successor, program))

        return successors

    def _load_task(self,
                   successor: str,
                   program: Program
                   ) -> Tuple[int, Task]:
        """
        """

        successor_task = program.get_task(successor)
        if not successor_task:
            raise RuntimeError('Successor does not exist.')

        time_next = self._dtimes[successor]

        # delete record of program
        del self._dtimes[successor]
        del self._dependencies[successor]

        return (time_next, successor_task)

    @classmethod
    def _execute_proxy_task(cls,
                            time: int,
                            task: ProxyTask,
                            process: int
                            ) -> int:
        """

        Executes proxy task.

        Proxy tasks are used to allow for easier program construction; they
        have no simulation effect therefore just complete the task and return
        the successor tasks.
        """

        assert time >= 0
        assert task is not None
        assert process >= 0

        # proxy tasks complete immediately in simulation time therefore no
        # time is used

        # proxy tasks are never drawn

        return time

    def _execute_start_task(self,
                            time: int,
                            task: StartTask,
                            process: int
                            ) -> int:
        """
        Execute the starting task.
        """

        time_start = time + task.skew
        self._set_process_time(task.node, process, time_start)

        if self.draw_mode:
            assert self.canvas is not None
            self.canvas.draw_start_task(task.node, time_start)

        return time_start

    def _execute_sleep_task(self,
                            time: int,
                            task: SleepTask,
                            process: int
                            ) -> int:
        """
        Executes the sleep task on this machine.

        The sleep tasks just suspends execution for a time delay.
        """

        time_sleep = time + task.delay
        self._set_process_time(task.node, process, time_sleep)

        if self.draw_mode:
            assert self.canvas is not None
            self.canvas.draw_sleep_task(task.node,
                                        time,
                                        time_sleep)

        return time_sleep

    def _execute_compute_task(self,
                              time: int,
                              task: ComputeTask,
                              process: int
                              ) -> int:
        """
        Evaluates the given compute model.
        """

        time_compute = self._compute_model.evaluate(time, task)

        self._set_process_time(task.node, process, time_compute)

        if self.draw_mode:
            assert self.canvas is not None
            self.canvas.draw_compute_task(task.node,
                                          time,
                                          time_compute)

        return time_compute

    def _execute_put_task(self,
                          time: int,
                          task: PutTask,
                          process: int
                          ) -> int:
        """
        Execute the put task.
        """

        local_time, remote_time = self._network_model.evaluate(task)

        self._set_process_time(task.node, process, time + local_time)

        if self.draw_mode:
            assert self._canvas is not None
            self.canvas.draw_blocking_put_task(task.node,
                                               task.target,
                                               time,
                                               time + remote_time)

        return time + local_time


# remove magic 1000, require some intelligent way of memory requirement
# (technically program should know)
# task_queue = libpqueue.PriorityQueue(program.getProcessCount() * 1000
# task_queue.push(0, task)
# while not task_queue.isEmpty():
# time, task = task_queue.pop()
# task_queue.push(*successor)
