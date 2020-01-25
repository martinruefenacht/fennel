"""
A set of tests which are regression errors.
"""


# pylint: disable=protected-access


import logging


from fennel.core.machine import Machine


def test_set_process_time_sets_all_nodes():
    """
    Verifies that the Machine._set_process_time does not set the time
    for all nodes equally.
    """

    machine = Machine(2, 1, None, None)

    logging.info(machine._node_times)
    assert all(time == 0 for node in machine._node_times for time in node)

    machine._set_process_time(0, 0, 100)
    logging.info(machine._node_times)

    assert machine._node_times[0][0] == 100
    assert machine._node_times[1][0] == 0
