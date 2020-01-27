"""
Plots a latency vs size plot.
"""


import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


from fennel.core.machine import Machine


from fennel.generators.p2p import generate_send
from fennel.networks.lbmodel import LBModel


def sample(size: int) -> float:
    """
    Calculate the latency of a transfer at the size.
    """

    prog = generate_send(size, True)
    network = LBModel(4000, 0.1)
    machine = Machine(2, 1, None, network)
    machine.run(prog)

    return machine.maximum_time / 1000.0


def main() -> None:
    """
    Calculate the bandwidth plot.
    """

    # x in Bytes up to 100MB
    x = np.logspace(0, 7, num=30)
    y = []

    for xi in x:
        y.append(sample(xi))

    sns.set_style("whitegrid")

    plt.plot(x, y)

    plt.xscale('log')
    plt.yscale('log')

    plt.ylabel('latency (s)')
    plt.xlabel('size (MB)')

    plt.show()


if __name__ == '__main__':
    main()
