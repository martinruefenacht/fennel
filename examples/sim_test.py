#! /usr/bin/python3

"""
"""

import sys
import parser
import lbmachine
import logpmachine
import visual


def main():
    """
    """

    # parse program
    program = parser.parseGOAL(sys.argv[1])
    # TODO by pipe

    # create machine for program
    machine = lbmachine.LBPMachine(program, 1000, 0, 400)

    # machine = lbmachine.LBMachine(program, 700, 0)
    # machine = logpmachine.LogPMachine(program)

    # set noise
    # machine.host_noise = True
    # machine.network_noise = True

    # set visual
    # visual = visual.Visual()
    # machine.setVisual(visual)

    machine.run()

    # TODO which metric evaluated
    print(machine.procs)

    # visual.savePDF('test.pdf')


if __name__ == "__main__":
    main()
