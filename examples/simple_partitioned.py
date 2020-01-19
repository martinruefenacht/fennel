"""
Simple example to use a multicast generator and model to execute it.
"""


from fennel.generators.p2p import generate_partitioned_send
from fennel.core.machine import Machine
from fennel.computes.gamma import GammaModel
from fennel.networks.lbpmodel import LBPModel
from fennel.visual.canvas import Canvas


def main() -> None:
    """
    Generates a multicast program and executes it using LBMachine model.
    """

    program = generate_partitioned_send(1, 4, 1)

    # TODO no concurrency for compute at the moment
    compute = GammaModel(0.1)
    network = LBPModel(100, 0.1, 200)

    machine = Machine(2, compute, network)
    machine.canvas = Canvas()

    # TODO machine does not draw non blocking

    machine.run(program)

    print(f'maximum time {machine.maximum_time}')

    machine.canvas.write('out.pdf')


if __name__ == '__main__':
    main()
