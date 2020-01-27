from fennel.generators.allreduce import generate_recursive_doubling
from fennel.machines.lbmachine import LBMachine
from fennel.visual.canvas import Canvas
from fennel.core.noise import NormalNoise

if __name__ == "__main__":
    nodes = 2 ** 2
    msg_size = 64

    latency = 1000
    bandwidth = 0
    compute = 1

    program = generate_recursive_doubling(nodes, msg_size)

    machine = LBMachine(nodes, latency, bandwidth, compute)
    machine.canvas = Canvas()
    machine.compute_noise_model = NormalNoise(1234, 100, 5)
    machine.run(program)

    machine.canvas.write('output.pdf')

    print(machine.maximum_time)
