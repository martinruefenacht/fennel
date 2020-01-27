"""
Compute sampling
"""

from fennel.core.program import Program

from fennel.tasks.start import StartTask
from fennel.tasks.proxy import ProxyTask
from fennel.tasks.compute import ComputeTask

from fennel.core.machine import Machine
from fennel.computes.gamma import NoisyGammaModel
from fennel.networks.lbmodel import LBModel


import statistics


def sample():
    program = Program()

    program.add_node(StartTask('c0', 0))

    for idx in range(1, 10):
        program.add_node(ComputeTask(f'c{idx}', 0, size=10000))
        program.add_edge(f'c{idx-1}', f'c{idx}')

    # bytes 10000, 10kb

    program.add_node(ProxyTask('x', 0))
    program.add_edge('c9', 'x')

    machine = Machine(1, 1, NoisyGammaModel(0.1, 0.05), None)
    machine.run(program)

    return machine.maximum_time


def main() -> None:
    """
    Main function.
    """

    samples = []

    for _ in range(1000):
        samples.append(sample())

    assert samples

    m = statistics.mean(samples)
    assert m != 0.0

    print(m, statistics.median(samples), min(samples), max(samples))
    print((min(samples) - m) / m)
    print((max(samples) - m) / m)


if __name__ == "__main__":
    main()
