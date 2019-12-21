"""
Simple example to use a multicast generator and model to execute it.
"""


from fennel.generators.allreduce import recursive_doubling
from fennel.machines.lbmachine import LBMachine


def main() -> None:
    """
    Generates a multicast program and executes it using LBMachine model.
    """

    nodes = 2 ** 4
    print(f'nodes {nodes}')
    msg_size = 8

    program = recursive_doubling(nodes, msg_size)

    machine = LBMachine(nodes, 1000, 0, 0)
    machine.run(program)
    print(f'maximum time {machine.maximum_time}')


if __name__ == '__main__':
    main()
