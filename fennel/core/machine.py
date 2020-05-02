"""
Defines the abstract class for machine models.
"""


# pylint: disable=too-many-instance-attributes


import logging
from abc import ABC
from typing import Optional, MutableMapping, Callable, List, Union, NewType
from collections import defaultdict


from fennel.core.time import Time
from fennel.core.program import Program
from fennel.core.task import Task, PlannedTask, TaskEvent
from fennel.core.compute import ComputeModel
from fennel.core.network import NetworkModel
from fennel.core.priorityqueue import PriorityQueue


from fennel.visual.canvas import Canvas
from fennel.core.instrument import Instrument
from fennel.tasks.proxy import ProxyTask
from fennel.tasks.put import PutTask
from fennel.tasks.start import StartTask
from fennel.tasks.sleep import SleepTask
from fennel.tasks.compute import ComputeTask


# type aliases
Node = NewType('Node', int)


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

        # registered instruments
        self._registered_instruments: MutableMapping[TaskEvent,
                                                     List[Instrument]]
        self._registered_instruments = defaultdict(lambda: [])

        # fulfilled dependency counter
        self._dependencies: MutableMapping[str, int] = defaultdict(lambda: 0)

        # max time of dependency, gives task begin time
        # starts will not be included
        self._dtimes: MutableMapping[str, List[Time]] = defaultdict(lambda: [])

        self._node_times: List[List[int, Time]]
        # self._node_times = [[0] * processes] * nodes needs deepcopy!
        # self._node_times = defaultdict(lambda: defaultdict(lambda: 0))
        self._node_times = []
        for nidx in range(nodes):
            self._node_times.append([])
            for _ in range(processes):
                self._node_times[nidx].append(0)

        self._task_handlers: MutableMapping[str,
                                            Union[
                                                Callable[[Time, StartTask], int],
                                                Callable[[Time, ProxyTask], int],
                                                Callable[[Time, SleepTask], int],
                                                Callable[[Time, ComputeTask], int],
                                                Callable[[Time, PutTask], int],
                                                ]] = dict()

        self._task_handlers['ProxyTask'] = self._execute_proxy_task
        self._task_handlers['StartTask'] = self._execute_start_task
        self._task_handlers['SleepTask'] = self._execute_sleep_task
        self._task_handlers['ComputeTask'] = self._execute_compute_task
        self._task_handlers['PutTask'] = self._execute_put_task

        self._canvas: Optional[Canvas] = None

    def register_instrument(self,
                            event: TaskEvent,
                            instrument: Instrument
                            ) -> None:
        """
        Register an instrument for a specific task event.

        Observer pattern is used for instruments.
        """

        self._registered_instruments[event].append(instrument)

    def is_finished(self) -> bool:
        """
        Checks whether the machine is finished, i.e. no waiting tasks.
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
    def maximum_time(self) -> Time:
        """
        Get maximum time of run.
        """

        time = max((proc_time
                    for node in self._node_times
                    for proc_time in node))

        assert time >= 0
        return time

    def get_node_process_time(self, node: Node, process: int) -> Time:
        """
        Get the time of a process in a node.
        """

        return self._node_times[node][process]

    def run(self, program: Program) -> None:
        """
        Runs the given Program on this machine.
        """

        # check if program requires larger machine
        if program.get_process_count() > self.nodes:
            raise RuntimeError(f'{program} requires greater node count '
                               f'{program.get_process_count()} than '
                               f'{self.nodes}.')

        # TODO if sampling mode, then multiprocessing here
        # separate MachineState
        # if not self.draw_mode:
        #     multiprocessing.pool
        #     # give different seeds to the machines

        self._run(program)

    def _run(self, program: Program) -> None:
        """
        Run the given Program on the current machine state.
        """

        queue = PriorityQueue()

        # insert all start tasks
        starts = program.get_start_tasks()
        assert starts
        queue.push_iterable_with_time(0, starts)

        # process entire queue
        while queue.is_not_empty():
            # execute next task
            plannedtask = queue.pop()

            # for instrument in self._registered_instruments[TaskEvent.SCHEDULED]:
            #     instrument.task_scheduled(plannedtask)

            successors = self._execute(program, plannedtask)

            # insert all successor tasks
            queue.push_iterable(successors)

    def _execute(self,
                 program: Program,
                 planned_task: PlannedTask
                 ) -> List[PlannedTask]:
        """
        Looks up required handler for task and executes task using that
        handler.
        """

        assert program is not None
        assert planned_task is not None

        time, task = planned_task

        assert task is not None
        assert time >= 0

        logging.debug('scheduled %s @ %i', task.name, time)

        # find earliest time to execute of processes in node
        if task.concurrent:
            tmp = list(proc for proc in self._node_times[task.node])
            earliest = min(tmp)
            process = tmp.index(earliest)

        else:
            earliest = max(proc for proc in self._node_times[task.node])
            process = 0

        # delay task if process time is further
        if earliest > time:
            # this happens with multiple successors on the same node

            for instrument in self._registered_instruments[TaskEvent.DELAYED]:
                instrument.task_delayed(task, program, time, earliest)

            return [(earliest, task)]

        # execute instruments for EXECUTED event
        for instrument in self._registered_instruments[TaskEvent.EXECUTED]:
            instrument.task_executed(task, program, earliest)

        # look up task handler and execute
        handler = self._task_handlers[task.__class__.__name__]

        logging.debug('execute %s @ %i', task.name, time)

        time_successors = handler(time, task, process)
        # TODO branching tasks would require dependency mapping here
        #      instead of returning successors return dict mapping of:
        #      name: time
        #      name: never

        return self._complete_task(time_successors,
                                   program,
                                   task)

    def _complete_task(self,
                       time: int,
                       program: Program,
                       task: Task
                       ) -> List[PlannedTask]:
        """
        For every successor of this task, increment a completion counter,
        and update the time. If all dependencies are complete then return
        all such successors.
        """

        for instrument in self._registered_instruments[TaskEvent.COMPLETED]:
            instrument.task_completed(task, program, time)

        successors = program.get_successors(task.name)

        # only proxy tasks can have no successors
        if not (isinstance(task, ProxyTask) or successors):
            raise RuntimeError('All programs must end with proxy tasks. '
                               f'{task.name} is not a ProxyTask.')

        planned = []

        for successor in successors:
            # increment completed dependencies for successor
            # forward task to last dependency
            self._dependencies[successor] += 1

            # save successors dependency end time
            self._dtimes[successor].append(time)

            # check there aren't more dependencies completed than there are
            # dependencies for the task
            assert (self._dependencies[successor] <=
                    program.get_in_degree(successor))

            # check if all dependencies completed
            if (self._dependencies[successor] ==
                    program.get_in_degree(successor)):

                planned.append(self._load_task(successor, program))

        return planned

    def _set_process_time(self, node: Node, process: int, time: Time) -> None:
        """
        Convenience function to update time of (node, process).
        """

        self._node_times[node][process] = time

    def _load_task(self,
                   name: str,
                   program: Program
                   ) -> PlannedTask:
        """
        Loads the Task from the Program and creates a PlannedTask.
        """

        task = program[name]
        if not task:
            raise RuntimeError('Successor does not exist.')

        # find successor start time
        if task.any is not None:
            # find lowest end time of dependencies of any #
            time_next = sorted(self._dtimes[name])[task.any - 1]

        else:
            time_next = max(self._dtimes[name])

        assert isinstance(time_next, int), time_next

        # trigger the TaskEvent LOADED
        for instrument in self._registered_instruments[TaskEvent.LOADED]:
            instrument.task_loaded(task, program, time_next, self._dtimes[name])

        # delete record of program
        del self._dtimes[name]
        del self._dependencies[name]

        return (time_next, task)

    def _execute_proxy_task(self,
                            time: Time,
                            task: ProxyTask,
                            process: int
                            ) -> Time:
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

        self._set_process_time(task.node, process, time)

        # proxy tasks are never drawn

        return time

    def _execute_start_task(self,
                            time: Time,
                            task: StartTask,
                            process: int
                            ) -> Time:
        """
        Execute the starting task.
        """

        time_start = time + task.skew
        self._set_process_time(task.node, process, time_start)

        if self.draw_mode and task.drawable:
            assert self.canvas is not None
            self.canvas.draw_start_task(task.node, time_start)

        return time_start

    def _execute_sleep_task(self,
                            time: Time,
                            task: SleepTask,
                            process: int
                            ) -> Time:
        """
        Executes the sleep task on this machine.

        The sleep tasks just suspends execution for a time delay.
        """

        time_sleep = time + task.delay
        self._set_process_time(task.node, process, time_sleep)

        if self.draw_mode and task.drawable:
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

        logging.debug('compute task @ %i on (%i, %i)', time,
                      task.node, process)

        assert self._compute_model is not None
        time_compute = self._compute_model.evaluate(time, task)

        self._set_process_time(task.node, process, time_compute)

        if self.draw_mode and task.drawable:
            assert self.canvas is not None
            self.canvas.draw_compute_task(task.node,
                                          time,
                                          time_compute)

        return time_compute

    def _execute_put_task(self,
                          time: Time,
                          task: PutTask,
                          process: int
                          ) -> Time:
        """
        Execute the put task.
        """

        assert self._network_model is not None
        times = self._network_model.evaluate(time, task)

        self._set_process_time(task.node, process, times.local)

        if self.draw_mode and task.drawable:
            assert self._canvas is not None

            if task.blocking:
                self.canvas.draw_blocking_put_task(task.node,
                                                   task.target,
                                                   time,
                                                   times.remote)

            else:
                self.canvas.draw_non_blocking_put_task(task.node,
                                                       task.target,
                                                       time,
                                                       times.local,
                                                       times.remote)

        return times.remote


# remove magic 1000, require some intelligent way of memory requirement
# (technically program should know)
# task_queue = libpqueue.PriorityQueue(program.getProcessCount() * 1000
# task_queue.push(0, task)
# while not task_queue.isEmpty():
# time, task = task_queue.pop()
# task_queue.push(*successor)
