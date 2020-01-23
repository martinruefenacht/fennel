from fennel.core.program import Program

from fennel.tasks.start import StartTask
from fennel.tasks.compute import ComputeTask

from fennel.core.machine import Machine
from fennel.computes.gamma import GammaModel, NoisyGammaModel
from fennel.networks.lbmodel import LBModel

import statistics

def sample():
    program = Program()

    program.add_node(StartTask('c0', 0))

    for idx in range(1, 100):
        program.add_node(ComputeTask(f'c{idx}', 0, 10000, False))
        program.add_edge(f'c{idx-1}', f'c{idx}')

    # bytes 10000, 10kb

    machine = Machine(1, 1, NoisyGammaModel(0.1), LBModel(100, 0))
    machine.run(program)

    return machine.maximum_time


if __name__ == "__main__":
    samples = []

    for idx in range(1000):
        samples.append(sample())

    m = statistics.mean(samples)

    print(m)
    print((min(samples) - m) / m)
    print((max(samples) - m) / m)

