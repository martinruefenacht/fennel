"""
"""

import sys, math

import fennel.core.program as program
import fennel.core.tasks as tasks

from sympy import factorint
from itertools import combinations
from itertools import permutations
from collections import Counter
from functools import reduce
import operator

from enum import Enum

class StageType(Enum):
        factor = 1

        split = 2
        invsplit = 3
        merge = 4
        invmerge = 5

        ttelim = 6
        ttexp = 7
        toelim = 8
        toexp = 9

class Stage:
        def __init__(self, stype, arg1, arg2=None, arg3=None):
                self.stype = stype
                self.arg1 = arg1
                self.arg2 = arg2
                self.arg3 = arg3
        
        def __str__(self):
                base = str(self.stype.name) + ':' + str(self.arg1)
                
                if self.arg2 is not None:
                        base += ':' + str(self.arg2)

                if self.arg3 is not None:
                        base += ':' + str(self.arg3)

                return base

        def __eq__(self, other):
                eq = (self.stype == other.stype) 
                eq = eq and (self.arg1 == other.arg1)
                eq = eq and (self.arg2 == other.arg2)
                eq = eq and (self.arg3 == other.arg3)
        
                return eq       

        def __hash__(self):
                xor = self.stype.value ^ self.arg1

                if self.arg2 is not None:
                        xor ^= self.arg2

                if self.arg3 is not None:
                        xor ^= self.arg3

                return xor
                        

        def __repr__(self):
                return self.__str__()

class Schedule:
        def __init__(self, process_count, order):
                self.process_count = process_count
                self.order = order

        def addStage(self, stage):
                self.order.append(stage)

        def getProcessCount(self):
                return self.process_count

        def getStageCount(self):
                return len(self.order)

        def __iter__(self):
                for stage in self.order:
                        yield stage 

        def __str__(self):
                return str(self.process_count) + ':' + str(self.order)

        def __repr__(self):
                pass

def convert(primedict):
        schedule = []

        for factor, count in primedict.items():
                for c in range(count):
                        schedule.append(Stage(StageType.factor, factor))
        
        return tuple(schedule)

def generate_factored(N):
        # find prime schedule
        prime_schedule = convert(factorint(N))

        # prime schedule -> combinations
        unique = []

        stack = []
        stack.append(prime_schedule)

        while stack:
                # retrieve item
                item = stack.pop()

                # check if done
                if item not in unique:
                        # add to unique set
                        unique.append(item)

                        # check for combinations
                        if len(item) is not 1:
                                # create pairings
                                pairs = set(combinations(item, 2))

                                for pair in pairs:
                                        # subtract pair
                                        diff_set = Counter(item) - Counter(pair)

                                        # calculate product of pair
                                        value = Stage(StageType.factor, pair[0].arg1 * pair[1].arg1)

                                        # combine into new set
                                        combine_set = diff_set + Counter([value])
                                        
                                        # convert to stages
                                        combined = []
                                        for elem in combine_set.elements():
                                                combined.append(elem)

                                        # push to stack
                                        stack.append(tuple(combined))

        # return unique sets, ordering is not given
        return unique

def permute_factored(order):
        d = list(permutations(order))
        return list(set(d))


def permute_lowhigh(order):
        # forward order
        high = sorted(order, key = lambda x: x.arg1)

        # reverse order
        low = reversed(high)

        return (tuple(high), tuple(low))

def generate_splits(N):
        schedules = []
        
        for threshold in range(2, N+1):
                for base in range(2, threshold+1):
                        if threshold/base == threshold//base:
                                s = generate_split(N, threshold, base)

                                schedules.extend(s)

        return schedules
                                        
def generate_split(N, threshold, base):
        if (threshold // base) != (threshold / base):
                raise ValueError

        schedules = []

        # calculate number of remaining peers
        peers = threshold / base + (N - threshold)

        # factor peers
        subs = generate_factored(peers)

        for sub in subs:
                construct = []
                construct.append(Stage(StageType.split, threshold, base))
                construct.extend(sub)
                construct.append(Stage(StageType.invsplit, threshold, base))

                schedules.append(tuple(construct))
        
        return list(set(schedules))

def generate_mpich(nodes):
        power = int(math.floor(math.log(nodes)/math.log(2)))
        remainder = nodes - 2 ** power
        threshold = 2 * remainder

        if remainder == 0:
                return tuple([Stage(StageType.factor, 2)] * power)
        else:
                schedule = []
                schedule.append(Stage(StageType.split, threshold , 2))
                schedule.extend([Stage(StageType.factor, 2)] * power) 
                schedule.append(Stage(StageType.invsplit, threshold, 2))
                
                return tuple(schedule)

def generate_normal_schedules(nodes):
        schedules = []

        # mpich schedule
        schedules.append(generate_mpich(nodes))

        # factored
        factored = generate_factored(nodes)
        for schedule in factored:
                schedules.append(permute_lowhigh(schedule)[1])

        return list(set(schedules))

def generate_merge(N, r):
        if r < 1:
                return None

        peers = N - r
        subs = generate_factored(peers)

        schedules = []

        for sub in subs:
                # check that the sub schedule is suitable, ie > than 2
                if len(sub) < 2:
                        continue

                for perm in permute_factored(sub):
                        # change first and last stages
                        first = perm[0]
                        last = perm[-1]

                        # eval groups
                        fgroups = reduce(operator.mul, (stage.arg1 for stage in perm[1:]))

                        nfirst = Stage(StageType.merge, r, fgroups, first.arg1)

                        lgroups = reduce(operator.mul, (stage.arg1 for stage in perm[:-1]))

                        nlast = Stage(StageType.invmerge, r, lgroups, last.arg1)

                        s = []
                        s.append(nfirst)
                        s.extend(perm[1:-1])
                        s.append(nlast)
                        
                        schedules.append(tuple(s))
                
        return schedules

def generate_merges(N):
        schedules = []
        
        for r in range(1, N-3):
                s = generate_merge(N, r)
                
                if s is not None:
                        schedules.extend(s)

        return list(set(schedules))

def convert_schedule(schedule):
        # input schedule types
        # output tuple of strings
        
        output = []

        for stage in schedule:
                if stage.stype is StageType.factor:
                        output.append('a' + str(stage.arg1))

                elif stage.stype is StageType.split:
                        output.append('c'+ str(stage.arg1) + 'm' + str(stage.arg2))

                elif stage.stype is StageType.invsplit:
                        output.append('e'+ str(stage.arg1) + 'm' + str(stage.arg2))

                elif stage.stype is StageType.merge:
                        output.append('m'+ str(stage.arg1) + 'g' + str(stage.arg2) + 'a' + str(stage.arg3))

                elif stage.stype is StageType.invmerge:
                        output.append('n'+ str(stage.arg1) + 'g' + str(stage.arg2) + 'a' + str(stage.arg3))
                        
                else:
                        print('ERROR')
        
        return tuple(output)

def schedule_to_program_generator(scheduleob, block=False, block_size=1):
        msgsize = 8 
        p = program.Program()

        size = scheduleob.getProcessCount()
        schedule = scheduleob.order

        # create start tasks
        for rid in range(size):
                name = 'r' + str(rid) + 'c0'
                p.addNode(name, tasks.StartTask(name, rid))

        # run through schedule
        split_stack = []
        stage_mask = 1
        wids = {}
        
        for scount, staget in enumerate(schedule):
                # stage id
                sid = scount + 1

                # if factor
                if staget.stype is StageType.factor:
                        # decode stage
                        factor = staget.arg1

                        # 
                        group_size = factor * stage_mask
                        
                        # for every node
                        for rid in range(size):
                                # working id
                                if len(wids) == 0:
                                        wid = rid
                                else:
                                        wid = wids[rid]

                                # check for activeness
                                if wid < 0:
                                        continue
                                
                                #
                                group = (wid // group_size) * group_size

                                # compute
                                name = 'r' + str(rid) + 'c' + str(sid)
                                p.addNode(name, tasks.ComputeTask(name, rid, delay=10))
                                
                                # compute is dependent on previous compute
                                p.addEdge('r' + str(rid) + 'c' + str(sid-1), name)

                                # for each peer
                                for idx in range(factor-1):
                                        # staggered multicast
                                        mask = (idx + 1) * stage_mask
                                        offset = (wid + mask) % group_size
                                        pwid = group + offset

                                        # convert wid to rid
                                        if len(split_stack) > 0:
                                                cthreshold, cbase = split_stack[len(split_stack)-1]
                                                prid = pwid + cthreshold // cbase * (cbase - 1)
                                                if prid < cthreshold:
                                                        prid = (pwid * cbase) + (cbase - 1)
                                        else:
                                                prid = pwid
                                                
                                        # create put for peer
                                        pname = 'r' + str(rid) + 'p' + str(sid) + '_' + str(idx)
                                        ptask = tasks.PutTask(pname, rid, prid, msgsize, block)
                                        p.addNode(pname, ptask)
                                        
                                        # depends on previous compute
                                        p.addEdge('r' + str(rid) + 'c' + str(sid-1), pname)
                                        # add dependency for all follow computes
                                        p.addEdge(pname, 'r' + str(prid) + 'c' + str(sid)) 

                        # increment mask
                        stage_mask *= factor

                elif staget.stype is StageType.split:
                        # decode stage
                        threshold = staget.arg1
                        base = staget.arg2

                        # insert into stack
                        split_stack.append((threshold, base))

                        # sensical names
                        groups = threshold/base
                        group_size = base
                        group_uppermost = base - 1

                        # for all procs
                        for rid in range(size):

                                # if in collapse region
                                if rid < threshold:

                                        # if not leader of group
                                        if rid % group_size != group_uppermost:
                                                # assign wid
                                                wid = -1 - rid

                                                # send to uppermost in group
                                                group_leader = (rid // group_size) * group_size + group_uppermost

                                                # construct put
                                                name = 'r' + str(rid) + 'p' + str(sid)
                                                p.addNode(name, tasks.PutTask(name, rid, group_leader, msgsize, block))
                                                p.addEdge('r'+str(rid)+'c'+str(sid-1), name)
        
                                        # if leader of group
                                        else:
                                                # assign working id
                                                wid = rid // group_size

                                                # construct compute
                                                name = 'r'+str(rid)+'c'+str(sid)
                                                p.addNode(name, tasks.ComputeTask(name, rid, delay=10))
                                                p.addEdge('r'+str(rid)+'c'+str(sid-1), name)

                                                # add dependencies
                                                for idx in range(group_uppermost):
                                                        pid = (rid // group_size) * group_size + idx
                                                        pname = 'r' + str(pid) + 'p' + str(sid)
                                                        p.addEdge(pname, name)                                                  

                                # above collapse region
                                else:
                                        # assign wid
                                        wid = rid - int(groups * group_uppermost)

                                        # create proxy
                                        name = 'r' + str(rid) + 'c' + str(sid)
                                        p.addNode(name, tasks.ProxyTask(name, rid))
                                        p.addEdge('r' + str(rid) + 'c' + str(sid-1), name)

                                # insert rid & wid into translation dict
                                wids[rid] = wid

                elif staget.stype is StageType.invsplit:
                        # decode stage
                        threshold = staget.arg1
                        base = staget.arg2

                        # sensical names
                        group_size = base
                        group_uppermost = base - 1
                        
                        # for all procs
                        for rid in range(size):
                                wid = wids[rid]
                                
                                # if in collapse region
                                if rid < threshold:
                                        
                                        # if leader in group
                                        if rid % group_size == group_uppermost:
                                                for offset in range(group_uppermost):
                                                        prid = wid * group_size + offset

                                                        name = 'r' + str(rid) + 'p' + str(sid) + '_' + str(offset)
                                                        p.addNode(name, tasks.PutTask(name, rid, prid, msgsize, block))
                                                        p.addEdge('r'+str(rid)+'c'+str(sid-1), name)

                                                        p.addEdge(name, 'r'+str(prid)+'c'+str(sid))

                                        # if not leader
                                        else:
                                                # construct compute
                                                name = 'r' + str(rid) + 'c' + str(sid)
                                                p.addNode(name, tasks.ComputeTask(name, rid, delay=10))
                
                elif staget.stype is StageType.merge:
                        # decode
                        merge_threshold = staget.arg1
                        groups = staget.arg2

                        factor = staget.arg3
                        group_size = staget.arg3 * stage_mask

                        # for all procs
                        for rid in range(size):

                                # if in merge region
                                if rid < merge_threshold:
                                        wids[rid] = -1 -rid
                                        
                                        # which group to
                                        group = rid % groups
                                        
                                        # group base rid
                                        group_first = merge_threshold + group * group_size

                                        # for each in group
                                        for idx in range(group_size):
                                                prid = group_first + idx

                                                # put
                                                pname = 'r' + str(rid) + 'p' + str(sid) + '_' + str(idx)
                                                p.addNode(pname, tasks.PutTask(pname, rid, prid, msgsize, block))
                                                p.addEdge('r'+str(rid)+'c'+str(sid-1), pname)
                                                p.addEdge(pname, 'r' + str(prid) + 'c' + str(sid))

                                else:
                                        wid = rid - merge_threshold
                                        wids[rid] = wid
                                        
                                        # normal factor exchange
                                        group = (wid // group_size) * group_size

                                        # compute
                                        name = 'r' + str(rid) + 'c' + str(sid)
                                        p.addNode(name, tasks.ComputeTask(name, rid, delay=10))
                                        p.addEdge('r'+str(rid)+'c'+str(sid-1), name)
                                        
                                        # for each group peer
                                        for idx in range(factor-1):
                                                # staggered multicast
                                                mask = (idx + 1) * stage_mask
                                                offset = (wid + mask) % group_size
                                                pwid = group + offset
                                                
                                                # convert wid -> rid
                                                prid = pwid + merge_threshold
                                                
                                                #
                                                pname = 'r' + str(rid) + 'p' + str(sid) + '_' + str(idx)
                                                p.addNode(pname, tasks.PutTask(pname, rid, prid, msgsize, block))

                                                #
                                                p.addEdge('r'+str(rid)+'c'+str(sid-1), pname)
                                                p.addEdge(pname, 'r'+str(prid)+'c'+str(sid))

                        # 
                        stage_mask *= factor
                
                elif staget.stype is StageType.invmerge:
                        # decode
                        merge_threshold = staget.arg1
                        groups = staget.arg2
                        factor = staget.arg3
                        group_size = staget.arg3 * stage_mask

                        for rid in range(size):
                                if rid < merge_threshold:
                                        # compute
                                        name = 'r' + str(rid) + 'c' + str(sid)
                                        p.addNode(name, tasks.ComputeTask(name, rid, delay=10))

                                else:
                                        wid = wids[rid]

                                        # normal factor exchange
                                        group = (wid // group_size) * group_size

                                        # compute
                                        name = 'r' + str(rid) + 'c' + str(sid)
                                        p.addNode(name, tasks.ComputeTask(name, rid, delay=10))
                                        p.addEdge('r'+str(rid)+'c'+str(sid-1), name)
                                        
                                        # for each group peer
                                        for idx in range(factor-1):
                                                # staggered multicast
                                                mask = (idx + 1) * stage_mask
                                                offset = (wid + mask) % group_size
                                                pwid = group + offset
                                                
                                                # convert wid -> rid
                                                prid = pwid + merge_threshold
                                                
                                                #
                                                pname = 'r' + str(rid) + 'p' + str(sid) + '_' + str(idx)
                                                p.addNode(pname, tasks.PutTask(pname, rid, prid, msgsize, block))

                                                #
                                                p.addEdge('r'+str(rid)+'c'+str(sid-1), pname)
                                                p.addEdge(pname, 'r'+str(prid)+'c'+str(sid))

                                        # outmerge
                                        for idx in range(merge_threshold):
                                                if idx % groups == wid % groups:
                                                        #
                                                        pname = 'r' + str(rid) + 'p' + str(sid) + '_m' + str(idx)
                                                        p.addNode(pname, tasks.PutTask(pname, rid, idx, msgsize, block))
                                                        p.addEdge('r'+str(rid)+'c'+str(sid-1), pname)
                                                        p.addEdge(pname, 'r'+str(idx)+'c'+str(sid))

                else:
                        raise ValueError('Unknown StageType.')

        return p

