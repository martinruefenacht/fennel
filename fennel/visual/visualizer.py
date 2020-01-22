"""
"""


# pylint: disable=protected-access


from pyvis.network import Network


from fennel.core.program import Program
from fennel.tasks.proxy import ProxyTask

from fennel.generators.p2p import generate_partitioned_send
from fennel.generators.compute import generate_compute


def convert(program: Program) -> Network:
    """
    Convert a program into a pyvis Network.
    """

    net = Network(height='100%', width='100%', directed=True)
    net.barnes_hut(overlap=0)

    for name, task in program._metadata.items():
        if isinstance(task, ProxyTask):
            continue

        net.add_node(name, label=str(task.__class__.__name__))

    for name, task in program._metadata.items():
        if isinstance(task, ProxyTask):
            continue

        names = program.get_successors_to_task(name)
        for sub in names:
            if sub.startswith('x'):
                subs = program.get_successors_to_task(sub)

                for sub2 in subs:
                    if sub2.startswith('x'):
                        subs2 = program.get_successors_to_task(sub2)

                        for sub3 in subs2:
                            net.add_edge(name, sub3)

                    else:
                        net.add_edge(name, sub2)

            else:
                net.add_edge(name, sub)

    return net


def main() -> None:
    """
    Main function.
    """

    # prog = generate_pingpong(1, 10)

    # prog = generate_multicast(0, 10)

    # prog = generate_partitioned_send(0, 4, 2, 1)

    prog = generate_compute(1, 2, 10, False, 3)

    net = convert(prog)

    net.show('test.html')


if __name__ == "__main__":
    main()
