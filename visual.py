import cairo, math
from tasks import *

def outputPDF(filename, machine, program):
	# calculate resolution
	xmargin = 10
	ymargin = 20
	pheight = 36
	cheight = 3
	theight = 2
	sheight = 5 
	tline = 4
	scale = 1/10

	maxtime = max(machine.procs)
	height = ymargin * 2 + pheight * (machine.size-1)
	width  = xmargin * 2 + int(math.ceil(maxtime / 1000.0)) * 1000 * scale

	# create surface
	pdf = cairo.PDFSurface(filename, width, height) 

	# create context
	ctx = cairo.Context(pdf)

	# set settings
	ctx.set_antialias(cairo.ANTIALIAS_GRAY)
	ctx.set_source_rgb(0, 0, 0)
	ctx.set_line_width(0.5)
	# scale to time tick resolution
	ctx.set_font_size(4)

	# draw process lines
	for proc in range(machine.size):
		ctx.move_to(xmargin - 1, ymargin + proc * pheight + 7)
		ctx.show_text(str(proc))
		
		ctx.move_to(xmargin, ymargin + proc * pheight) 
		ctx.rel_line_to((width - xmargin * 2), 0)
		ctx.stroke()

	# draw max time line
	ctx.set_source_rgb(1,0,0)
	ctx.move_to(xmargin + maxtime * scale, ymargin)
	ctx.rel_line_to(0, height - ymargin*2) 
	ctx.stroke()
	ctx.set_source_rgb(0,0,0)

	# draw timeline
	ctx.move_to(xmargin, ymargin/3)
	ctx.rel_line_to((width-xmargin*2), 0)
	ctx.stroke()	

	for tick in range(int((width - xmargin*2)/10)+1):
		if tick % 5 == 0:
		    # draw number
			ctx.move_to(xmargin + tick / scale - 2, ymargin/3 + 8)
			ctx.show_text(str(tick*100))

		# draw ticks
		ctx.move_to(xmargin + tick / scale, ymargin/3)
		ctx.rel_line_to(0, 4)
		ctx.stroke()

	# draw machine program
	for node, data in program.nodes_iter(data=True):
		task = data['task']

		if isinstance(task, StartTask):
			time = machine.record[node]
			ctx.move_to(xmargin + time*scale, ymargin + pheight * task.proc - sheight/2)
			ctx.rel_line_to(0, sheight)
			ctx.stroke()

		elif isinstance(task, PutTask):
			# draw put task
			# draw local block
			record = machine.record[node]
			
			ctx.rectangle(xmargin + record[0] * scale, ymargin + pheight * task.proc - theight/2, record[1] * scale, theight) 
			ctx.fill()
			
			# draw transfer
			direct = tline if (task.target - task.proc) > 0 else -tline

			ctx.move_to(xmargin + record[0] * scale + record[1] * scale, ymargin + pheight * task.proc)
			ctx.rel_line_to(0, direct)
			ctx.line_to(xmargin + (record[0]+record[1]+record[2])*scale, ymargin + pheight * task.target - direct)
			ctx.rel_line_to(0, direct)
			ctx.stroke()

		elif isinstance(task, ComputeTask):
			# draw compute task
			record = machine.record[node]
			ctx.rectangle(xmargin + record[0]*scale, ymargin + pheight * task.proc - cheight/2, record[1]*scale, cheight) 
			ctx.fill()
			
		else:
			print('Unknown task type:', task)

			
