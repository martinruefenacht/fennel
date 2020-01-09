"""
This module defines the machines for the latency-bandwidth models.
"""

import logging
from typing import Optional

from fennel.core.noise import NoiseModel
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
        self._alpha = latency
        self._beta = bandwidth

        # compute parameters
        self._gamma = compute

        self._compute_noise: Optional[NoiseModel] = None
        self._network_noise: Optional[NoiseModel] = None

        # set supported tasks for LBMachine model
        self._task_handlers['StartTask'] = self._execute_start_task
        self._task_handlers['SleepTask'] = self._execute_sleep_task
        self._task_handlers['ComputeTask'] = self._execute_compute_task
        self._task_handlers['PutTask'] = self._execute_put_task

    @property
    def compute_noise_model(self) -> NoiseModel:
        """
        """

        return self._compute_noise

    @compute_noise_model.setter
    def compute_noise_model(self, model: NoiseModel) -> None:
        """
        """

        self._compute_noise = model

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
            assert self.canvas is not None
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
            assert self.canvas is not None
            self.canvas.draw_sleep_task(task.process,
                                        time,
                                        time_sleep)

        return time_sleep

    def _execute_compute_task(self,
                              time: int,
                              task: ComputeTask
                              ) -> int:
        """
        """

        time_compute = time + task.size * self._gamma

        if self._compute_noise is not None:
            time_noise = self._compute_noise.sample()
            time_compute += time_noise

        self._set_process_time(task.process, time_compute)

        if self.draw_mode:
            assert self.canvas is not None
            self.canvas.draw_compute_task(task.process,
                                          time,
                                          time_compute)

            if self._compute_noise is not None:
                self.canvas.draw_noise_overlay(task.process,
                                               time_compute - time_noise,
                                               time_compute)

        return time_compute

    def _execute_put_task(self,
                          time: int,
                          task: PutTask
                          ) -> int:
        """
        Execute the put task.
        """

        put_time = self._alpha + self._beta * task.message_size
        time_arrival = time + put_time

        if self._network_noise is not None:
            time_noise = self._network_noise.sample()
            time_arrival += time_noise

        assert time_arrival > time

        # blocking put and put and same with LB machine
        self._set_process_time(task.process, time_arrival)

        if self.draw_mode:
            assert self.canvas is not None
            self.canvas.draw_blocking_put_task(task.process,
                                               task.target,
                                               time,
                                               time_arrival)

            # TODO draw noise on transfer line somehow
#             if self._network_noise is not None:
#                 self._canvas.draw_noise_overlay(task.target,
#                                                 

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

        self._pipe_noise = None

    def _execute_put_task(self,
                          time: int,
                          task: PutTask
                          ) -> int:
        """
        Execute the put task.
        """

        pipe_time = self._kappa
        time_pipe = time + pipe_time

        if self._pipe_noise is not None:
            time_pipe += self._pipe_noise.sample()

        put_time = self._alpha + self._beta * task.message_size
        time_arrival = time_pipe + put_time

        if self._network_noise is not None:
            time_arrival += self._network_noise.sample()

        if task.blocking:
            self._set_process_time(task.process, time_arrival)
 
            # TODO
            # if self.draw_mode:
            #     self.canvas.draw_put_task()

        else:
            self._set_process_time(task.process, time_pipe)

            # TODO
            # if self.draw_mode:
            #     self.canvas.draw_put_task()

            # expliclty update maximum time, because there may not be
            # successors and that would not give the correct maximum time
            self._update_maximum_time(time_arrival)

        return time_arrival

# receive nic congestion or network congestion?

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
