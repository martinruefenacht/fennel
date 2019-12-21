"""
Simple example to use a multicast generator and model to execute it.
"""


from fennel.generators.p2p import generate_pingpong
from fennel.machines.lbmachine import LBMachine


def main() -> None:
    """
    Generates a multicast program and executes it using LBMachine model.
    """

    nodes = 2
    msg_size = 0
    rounds = 1

    program = generate_pingpong(msg_size, rounds)

    machine = LBMachine(nodes, 1000, 0, 0)
    machine.run(program)
    print(f'maximum time {machine.maximum_time}')


if __name__ == '__main__':
    main()
