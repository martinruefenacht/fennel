"""
"""


# pylint: disable=protected-access


from pyvis.network import Network


from fennel.core.program import Program
from fennel.tasks.proxy import ProxyTask

from fennel.generators.p2p import generate_send_partitioned_p2p
from fennel.generators.compute import generate_compute
from fennel.generators.broadcast import generate_broacast_ring


def convert(program: Program) -> Network:
    """
    Convert a program into a pyvis Network.
    """

    net = Network(height='100%', width='100%', directed=True)
    net.barnes_hut(overlap=0)

    for name, task in program._metadata.items():
        if task.node == 0:
            color = '#A5BE00'

        elif task.node == 1:
            color = '#427AA1'

        net.add_node(name, color=color)

    for name in program._metadata.keys():
        names = program.get_predecessors(name)
        for sub in names:
            color = '#05668D'

            if program[name].any is not None:
                color = '#679436'

            net.add_edge(sub, name, color=color)

    return net


def main() -> None:
    """
    Main function.
    """

    # prog = generate_send_partitioned_p2p(10, 2, 1, 2)

    prog = generate_broacast_ring(3, 0, 0)

    net = convert(prog)

    net.show('test.html')


if __name__ == "__main__":
    main()
