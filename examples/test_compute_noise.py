from fennel.core.program import Program
from fennel.tasks.compute import ComputeTask
from fennel.tasks.start import StartTask
from fennel.machines.lbmachine import LBMachine
from fennel.core.noise import NormalNoise

if __name__ == "__main__":
    machine = LBMachine(1, 0, 0, 100)
    machine.compute_noise_model = NormalNoise(1000, 100, 50)

    start = StartTask('start', 0, 0)
    task = ComputeTask('compute', 0, 100)

    program = Program()
    program.add_node(start)
    program.add_node(task)

    program.add_edge('start', 'compute')

    machine.run(program)

    print(machine.maximum_time)
