"""
This module defines the machines for the latency-bandwidth models.
"""

import logging


from fennel.core.machine import Machine
from fennel.tasks.start import StartTask
from fennel.tasks.put import PutTask
from fennel.tasks.compute import ComputeTask
from fennel.tasks.sleep import SleepTask


class LBMachine(Machine):
    """
    The latency-bandwidth machine implementation.
    """

    def __init__(self, nodes: int, latency: int, bandwidth: int, compute: int):
        super().__init__(nodes)

        # model parameters
        # network parameters
        # time
        self._alpha = latency
        # time / byte
        self._beta = bandwidth
        # compute parameters
        # time / byte
        self._gamma = compute

        # set supported tasks for LBMachine model
        self._task_handlers['StartTask'] = self._execute_start_task
        self._task_handlers['SleepTask'] = self._execute_sleep_task
        self._task_handlers['ComputeTask'] = self._execute_compute_task
        self._task_handlers['PutTask'] = self._execute_put_task

    def _execute_start_task(self,
                            time: int,
                            task: StartTask
                            ) -> int:
        """
        Execute the starting task.
        """

        time_start = time + task.skew
        self._set_process_time(task.process, time_start)

        if self.draw_mode:
            self.canvas.draw_start_task(task.process, time_start)

        return time_start

    def _execute_sleep_task(self,
                            time: int,
                            task: SleepTask
                            ) -> int:
        """
        Executes the sleep task on this machine.

        The sleep tasks just suspends execution for a time delay.
        """

        time_sleep = time + task.delay
        self._set_process_time(task.process, time_sleep)

        if self.draw_mode:
            self.canvas.draw_sleep_task()

        return time_sleep

    def _execute_compute_task(self,
                              time: int,
                              task: ComputeTask
                              ) -> int:
        """
        """

        time_compute = time + task.size * self._gamma
        self._set_process_time(task.process, time_compute)

        if self.draw_mode:
            self.canvas.draw_compute_task()

        return time_compute

    def _execute_put_task(self,
                          time: int,
                          task: PutTask
                          ) -> int:
        """
        Execute the put task.
        """

        logging.debug('ProxyTask for process %i at %i', task.process, time)

        # put side
        put_time = self._alpha + self._beta * task.message_size
        time_arrival = time + put_time

        # blocking put and put and same with LB machine

        self._set_process_time(task.process, time_arrival)

        if self.draw_mode:
            self.canvas.draw_put_task()

        return time_arrival


class LBPMachine(LBMachine):
    """
    The latency-bandwidth-pipeline machine implementation.
    """

    def __init__(self,
                 nodes: int,
                 latency: int,
                 bandwidth: int,
                 pipelining: int,
                 compute: int):
        super().__init__(nodes, latency, bandwidth, compute)

        self._kappa = pipelining

    def _execute_put_task(self,
                          time: int,
                          task: PutTask
                          ) -> int:
        """
        Execute the put task.
        """

        pipe_time = self._kappa
        time_pipe = time + pipe_time

        put_time = self._alpha + self._beta * task.message_size
        time_arrival = time_pipe + put_time

        if task.blocking:
            self._set_process_time(task.process, time_arrival)

            # if self.draw_mode:
            #     self.canvas.draw_put_task()

        else:
            self._set_process_time(task.process, time_pipe)

            # if self.draw_mode:
            #     self.canvas.draw_put_task()

        # expliclty update maximum time, because there may not be successors
        # and that would not give the correct maximum time
        self._update_maximum_time(time_arrival)

        return time_arrival

# congestion
# class LBPCMachine(LBPMachine):
#     def __init__(self, nodes, latency, bandwidth, pipelining, congest):
#             super().__init__(nodes, latency, bandwidth, pipelining)
# 
#             self.congestion = congest
#             
#             # initialize nic recving side "time"
#             self.nic_recv = [0] * self.node_count
# 
#             self.task_handlers['MsgTask'] = self.executeMsgTask
# 
#     def getMaximumTime(self):
#             return self.maximum_time
# 
#     def _executePutTask(self, time, program, task):
#             # 
#             if self._process_times[task.process] > time:
#                     # fail
#                     # reinsert task at delayed time
#                     return [(self._process_times[task.process], task)]
# 
#             # pipeline
#             pipe_time = self.kappa
#             noise_pipe = self.getHostNoise(pipe_time)
#             time_pipe = time + pipe_time + noise_pipe
# 
#             # draw pipeline
#             self.drawPipe(task, time, self.kappa, noise_pipe)
# 
#             # put side
#             put_time = self.alpha + self.beta * task.size
#             noise_put = self.getNetworkNoise(put_time)
#             arrival = time_pipe + put_time
#             time_put = arrival + noise_put
# 
#             #return MsgTaskType?
# 
#             #if self.nic_recv[task.process] > time_put:
#                     # reinsert recv
# 
#             # draw put side
#             self.drawPut(task, time_pipe, arrival, noise_put)
# 
#             #
#             #if task.block:
#             #       self._process_times[task.process] = time_put
#             #else:
#             self._process_times[task.process] = time_pipe
#             self.maximum_time = max(self.maximum_time, time_put)
# 
#             #self.completeTask(task, program, time_put)
# 
#             msgtask = tasks.MsgTask(task, time_pipe, time_put)
# 
#             return [(time_put, msgtask)]
# 
#     def _executeMsgTask(self, time, program, task):
#             #print(task.name, time, self.nic_recv[task.target])
#             if self.nic_recv[task.target] > time:
#                     # reinsert
#                     return [(self.nic_recv[task.target], task)]
# 
#             self.nic_recv[task.target] = time + self.congestion # + noise
# 
#             self.drawRecv(task, time + self.congestion, 0)
#             
# 
#             return self.completeTask(task.puttask, program, time + self.congestion)
# 
#     def drawRecv(self, task, time, noise):
#             if self.context:
#                     side = 1 if task.process < task.target else -1
#                     
#                     # draw nic recv
#                     self.context.drawHLine(task.target, time-self.congestion, self.congestion, -Visual.put_height*side, 'std')      
