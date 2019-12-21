"""
Simple example to use a multicast generator and model to execute it.
"""

from typing import Tuple

from fennel.generators.p2p import generate_multicast
from fennel.models.lbmachine import LBMachine


def sample(data: Tuple[int, int]) -> None:
    """
    """

    msg_size, fan_out = data

    program = generate_multicast(msg_size, fan_out)

    machine = LBMachine(fan_out + 1, 1000, 10)
    machine.run(program)
    print(f'maximum time {machine.maximum_time}')


def main() -> None:
    """
    Generates a multicast program and executes it using LBMachine model.
    """

    msg_sizes = range(0, 10)
    fan_outs = range(1, 10)

    list(map(sample, ((msg_size, fan_out)
                      for msg_size in msg_sizes
                      for fan_out in fan_outs)))


if __name__ == '__main__':
    main()
