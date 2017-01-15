# input DAG

# verify all processes have same final order and content

def verify_allreduce(program):
	#process_count = program.getProcessCount()
	process_count = 12
	
	offset = 13
	process_memory = [[proc + offset] for proc in range(process_count)]
	print(process_memory)

	# analytic result
	summation = 0
	for memory in process_memory:
		summation += memory[0]
	print('Analytic: ', summation)
