"""
Simple example to use a multicast generator and model to execute it.
"""


from fennel.generators.recursive_multiplying import generate_recursive_multiplying
from fennel.machines.lbmachine import LBPMachine


def main() -> None:
    """
    Generates a multicast program and executes it using LBMachine model.
    """

    nodes = 16
    print(f'nodes {nodes}')
    msg_size = 8

    program = generate_recursive_multiplying(nodes, msg_size)

    machine = LBPMachine(nodes, 900, 0, 0, 100)
    machine.run(program)
    print(f'maximum time {machine.maximum_time}')


if __name__ == '__main__':
    main()
