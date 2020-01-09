import pyx

def draw(schedule, program, positions, filename):
	# create canvas
	canvas = pyx.canvas.canvas()

	# base color
	gradient = pyx.color.gradient.Rainbow 
	stages = schedule.getStageCount()

	# draw nodes
	for node in program.metadata.keys():
		
		canvas.fill(pyx.path.circle(*positions[node], 0.1), [pyx.color.rgb.red])

	# output pdf
	canvas.writePDFfile(filename)
	
