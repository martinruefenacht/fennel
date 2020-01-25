"""
Simple example to use a multicast generator and model to execute it.
"""


import logging


from fennel.core.program import Program
from fennel.generators.p2p import generate_partitioned_send
from fennel.core.machine import Machine
from fennel.computes.gamma import GammaModel
from fennel.networks.lbpmodel import LBPModel
from fennel.visual.canvas import Canvas
from fennel.tasks.start import StartTask
from fennel.tasks.compute import ComputeTask
from fennel.tasks.proxy import ProxyTask


def main() -> None:
    """
    Generates a multicast program and executes it using LBMachine model.
    """

    logging.basicConfig(level=10)

    # TODO this is hardcoded
    # program = generate_partitioned_send(1, 4, 2, 1)

    program = Program()
    program.add_node(StartTask('s0', 0))

    program.add_node(ComputeTask('c0', 0, time=10))
    program.add_node(ComputeTask('c1', 0, time=100))
    program.add_node(ComputeTask('c2', 0, time=15))

    x0 = ProxyTask('x0', 0)
    x0.any = 2
    program.add_node(x0)
    x1 = ProxyTask('x1', 0)
    program.add_node(x1)

    program.add_node(ComputeTask('c3', 0, time=5))
    program.add_node(ComputeTask('c4', 0, time=5))

    program.add_node(ProxyTask('x3', 0))

    program.add_edge('s0', 'c0')
    program.add_edge('s0', 'c1')
    program.add_edge('s0', 'c2')

    program.add_edge('c0', 'x0')
    program.add_edge('c1', 'x0')
    program.add_edge('c2', 'x0')

    program.add_edge('c0', 'x1')
    program.add_edge('c1', 'x1')
    program.add_edge('c2', 'x1')

    program.add_edge('x0', 'c3')
    program.add_edge('x1', 'c4')

    program.add_edge('c3', 'x3')
    program.add_edge('c4', 'x3')

    compute = GammaModel(0.1)
    network = LBPModel(100, 0.1, 200)

    machine = Machine(2, 1, compute, network)
    machine.canvas = Canvas()

    machine.run(program)

    print(f'maximum time {machine.maximum_time}')


if __name__ == '__main__':
    main()
