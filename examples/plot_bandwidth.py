"""
"""


import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


from fennel.core.machine import Machine
from fennel.core.task import TaskEvent


from fennel.generators.p2p import generate_send
from fennel.instruments.bandwidth import BandwidthInstrument
from fennel.networks.lbmodel import LBModel


def sample(size: int) -> float:
    """
    """

    instrument = BandwidthInstrument()

    prog = generate_send(size, True)
    network = LBModel(4000, 0.1)
    machine = Machine(2, 1, None, network)

    machine.register_instrument(TaskEvent.EXECUTED, instrument)
    machine.register_instrument(TaskEvent.COMPLETED, instrument)

    machine.run(prog)
    usage = instrument.calculate_bandwidth()

    # B/ns -> MB/s
    usage *= 953.674
    return usage


def main() -> None:
    """
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

    plt.xlabel('size (MB)')
    plt.ylabel('bandwidth (MB/s)')

    plt.show()


if __name__ == '__main__':
    main()
