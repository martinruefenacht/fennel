"""
Tests associated with the BandwidthInstrument.
"""


import logging


from fennel.core.machine import Machine
from fennel.core.task import TaskEvent


from fennel.generators.p2p import generate_send
from fennel.instruments.bandwidth import BandwidthInstrument
from fennel.networks.lbmodel import LBModel


def test_bandwidth_single_put():
    """
    Tests whether a single send is measured correctly.
    """

    instrument = BandwidthInstrument()

    # send 125000B 125KB 0.125MB
    prog = generate_send(125000, True)
    network = LBModel(100, 1)
    machine = Machine(2, 1, None, network)

    machine.register_instrument(TaskEvent.EXECUTED, instrument)
    machine.register_instrument(TaskEvent.COMPLETED, instrument)

    machine.run(prog)
    usage = instrument.calculate_bandwidth()

    # B/ns -> MB/s
    usage *= 953.674

    logging.info('bandwidth usage %f', usage)

    assert usage
