"""
Simple example to use a multicast generator and model to execute it.
"""


from fennel.generators.recursive_doubling import generate_recursive_doubling
from fennel.models.lbmachine import LBMachine


def main() -> None:
    """
    Generates a multicast program and executes it using LBMachine model.
    """

    nodes = 256
    msg_size = 8

    program = generate_recursive_doubling(nodes, msg_size)

    machine = LBMachine(nodes, 1000, 0, 0)
    machine.run(program)
    print(f'maximum time {machine.maximum_time}')


if __name__ == '__main__':
    main()
