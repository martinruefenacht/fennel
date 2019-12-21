"""
"""

import simulator.generators.p2p as p2p
import simulator.models.lbmachine as lbmachine
import simulator.core.noise as noise

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def main():
    """
    """

    data_x = []
    data_y = []

    # msg sizes
    for log2 in range(3, 24):
        msgsize = 1 << log2
        data_x.append(msgsize)

        # samples
        samples = []

        # program generation
        p = p2p.generate_pingpong(msgsize)

        # machine creation
        m = lbmachine.LBPMachine(p, 1000, 0.4, 400)

        # noise configuration
        m.host_noise = noise.BetaPrimeNoise(2, 3)
        m.network_noise = noise.BetaPrimeNoise(2, 3)

        # sampling
        for sample in range(100):
            m.run()
            
            samples.append(m.getMaximumTime()/1000)

            m.reset()

        print(msgsize, np.min(samples), np.median(samples), np.mean(samples))

        data_y.append(samples)

    # boxplot results
    # plt.boxplot(data_y)

    sns.set_context(context='talk')
    sns.set_style('whitegrid')

    sns.boxplot(data=data_y, fliersize=0.5, linewidth=1.0, notch=True, color='#7291ba')
    plt.yscale('log')

    # ticks
    si = ['B', 'KB', 'MB', 'GB', 'TB']
    ticks = []
    for size in data_x:
        d = 0
        b = size
        
        while b > 0:
            n = b >> 10
            if n > 0:
                d = d + 1
                b = n
            else:
                ticks.append('{} {:3}'.format(str(b), si[d]))
                break

    plt.xticks(range(0, len(data_x)+1), ticks, rotation='vertical')
    plt.ylim(1, 4000)
    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    main()
