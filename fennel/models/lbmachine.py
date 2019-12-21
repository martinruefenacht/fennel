"""
This module defines the machines for the latency-bandwidth models.
"""

from typing import Iterable, Tuple
import logging


from fennel.core.machine import Machine
from fennel.core.program import Program
from fennel.core.tasks import Task, StartTask, ProxyTask, PutTask, ComputeTask


class LBMachine(Machine):
    """
    The latency-bandwidth machine implementation.
    """

    def __init__(self, nodes: int, latency: int, bandwidth: int, compute: int):
        super().__init__(nodes)

        # model parameters
        self._alpha = latency
        self._beta = bandwidth
        self._gamma = compute

        # process times
        self._process_times = [0] * self.nodes

        # set supported tasks for LBMachine model
        self._task_handlers['StartTask'] = self.execute_start_task
        self._task_handlers['ProxyTask'] = self.execute_proxy_task
        self._task_handlers['SleepTask'] = self.executeSleepTask
        self._task_handlers['ComputeTask'] = self.execute_compute_task
        self._task_handlers['PutTask'] = self.execute_put_task

    def execute_start_task(self,
                           time: int,
                           program: Program,
                           task: StartTask
                           ) -> Iterable[Tuple[int, Task]]:
        """
        Execute the starting task.
        """

        # logic
        if self._process_times[task.process] > time:
            return [(self._process_times[task.process], task)]

        logging.debug('StartTask for process %i at %i', task.process, time)

        # forward proc
        self._process_times[task.process] = time + task.skew
        self._maximum_time = max(self._maximum_time,
                                 self._process_times[task.process])

        # return list of dependencies which are fulfilled
        return self._complete_task(self._process_times[task.process],
                                   program,
                                   task)

#    def drawStart(self, time, task):
#        if self.context:
#            start_height = self.context.start_height
#            start_radius = self.context.start_radius
#
#            self.context.drawVLine(task.process, time, start_height, start_height, 'std')
#            self.context.drawCircle(task.process, time, -start_height, start_radius)

    def execute_proxy_task(self,
                           time: int,
                           program: Program,
                           task: ProxyTask
                           ) -> Iterable[Tuple[int, Task]]:
        """
        """

        logging.debug('ProxyTask for process %i at %i', task.process, time)

        self._process_times[task.process] = time
        self._maximum_time = max(self._maximum_time, time)

        return self._complete_task(self._process_times[task.process],
                                   program,
                                   task)

    def executeSleepTask(self, time, program, task):
        """
        """

        # logic
        if self._process_times[task.process] <= time:
            # forward proc
            self._process_times[task.process] = time + task.delay

            # visual
            #self.drawSleepTask(time, task)

            #
            return self.completeTask(task, program, self._process_times[task.process])

        else:
            return [(self._process_times[task.process], task)]

#    def drawSleepTask(self, time, task):
#        """
#        """
#
#        if self.context is not None:
#            self.context.drawHLine(task.process, time, task.delay, -self.context.sleep_height, 'std')  

    def execute_compute_task(self,
                             time: int,
                             program: Program,
                             task: ComputeTask
                             ) -> Iterable[Tuple[int, Task]]:
        """
        """

        if self._process_times[task.process] > time:
            return [(self._process_times[task.process], task)]

        # forward proc
        self._process_times[task.process] = time + task.size * self._gamma

        return self._complete_task(self._process_times[task.process],
                                   program,
                                   task)

#    def drawCompute(self, task, time, noise):               
#        """
#        """
#
#        if self.context is not None:
#            self.context.drawRectangle(task.process, time, task.delay, Visual.compute_base, Visual.compute_height, 'std')
#
#            if self.host_noise is not None:
#                self.context.drawRectangle(task.process, time+task.delay, noise, -self.context.compute_height/2, self.context.compute_height, 'err')

    def execute_put_task(self,
                         time: int,
                         program: Program,
                         task: PutTask
                         ) -> Iterable[Tuple[int, Task]]:
        """
        Execute the put task.
        """

        if self._process_times[task.process] > time:
            return [(self._process_times[task.process], task)]

        logging.debug('ProxyTask for process %i at %i', task.process, time)

        # put side
        put_time = self._alpha + self._beta * task.message_size
        # noise_put = self.getNetworkNoise(put_time)
        arrival = time + put_time
        # time_put = arrival + noise_put

        # blocking put and put and same under LB machine

        self._process_times[task.process] = arrival
        self._maximum_time = max(self._maximum_time, arrival)

        return self._complete_task(arrival, program, task)

#    def drawPut(self, task, time, arrival, noise):
#        # check for visual context
#        if self.context:
#            side = 1 if task.process < task.target else -1
#            
#            # draw put msg
#            self.context.drawVLine(task.process, time, Visual.put_base, Visual.put_height*side, 'std')
#            self.context.drawSLine(task.process, time, Visual.put_height, task.target, arrival, 'std')
#            self.context.drawVLine(task.target, arrival, Visual.put_base, Visual.put_height*-side, 'std')
#    
#            # draw noise
#            if noise != 0:
#                self.context.drawHLine(task.target, arrival, noise, -Visual.put_height*side, 'err')     
#                self.context.drawVLine(task.target, arrival+noise, Visual.put_base, -Visual.put_height*side, 'err')


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

    def execute_put_task(self, time, program, task):
        """
        Execute the put task.
        """

        if self._process_times[task.process] > time:
            # reinsert task at delayed time
            return [(self._process_times[task.process], task)]

        # pipeline
        pipe_time = self._kappa
        time_pipe = time + pipe_time

        #  XXX NETWORK LOCK quick and dirty
        # if self.network_lock[time_pipe // 50]:
        #        return [(((time_pipe // 50) + 1) * 50, task)]
        # self.network_lock[time_pipe // 50] = True

        # put side
        put_time = self._alpha + self._beta * task.size
        arrival = time_pipe + put_time
        time_put = arrival

        # draw put side
        # self.drawPut(task, time_pipe, arrival, noise_put)

        if task.block:
            self._process_times[task.process] = time_put

        else:
            self._process_times[task.process] = time_pipe

        self._maximum_time = max(self._maximum_time, time_put)

        return self._complete_task(time_put, program, task)

#     def drawPipe(self, task, time, delay, noise):
#             #
#             if self.context:
#                     side = 1 if task.process < task.target else -1
#
#                     self.context.drawVLine(task.process, time, Visual.put_base, Visual.put_height*side, 'std')
#
#                     boxheight = Visual.put_height - Visual.put_offset
#                     offset = boxheight/2 + Visual.put_offset
#                     self.context.drawRectangle(task.process, time, delay, offset*side, boxheight, 'std')
#
#                     if noise != 0:
#                             self.context.drawHLine(task.process, time+delay, noise, Visual.put_height*side, 'err')

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
#     def executePutTask(self, time, program, task):
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
#     def executeMsgTask(self, time, program, task):
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
