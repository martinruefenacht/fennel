"""
"""


import sys


from argparse import ArgumentParser


def check_version() -> None:
    """
    Check that the executing python version is above 3.6.
    """

    if not (sys.version_info['major'] == 3 and sys.version_info['minor'] > 6):
        raise RuntimeError('Python version required is 3.6.')


def parse_arguments():
    """
    """

    parser = ArgumentParser(description="Fennel, a network simulator.")

    parser.add_argument('--log',
                        default='warning',
                        type=str,
                        help='Set the python logging level.')

    parser.add_argument('mode', choices=['draw', 'measure'])

    parser.add_argument('machine')

    # read program from pickle through stdin


if __name__ == '__main__':
    arguments = parse_arguments()

    # TODO launch fennel with given program

    # multi processesing

    # machine
