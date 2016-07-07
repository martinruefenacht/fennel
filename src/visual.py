import pyx, math

class Visual:
	xmargin = 0.5
	ymargin = 1
	
	tl_ymargin = 0.5
	tick_freq = 100 #ns
	tick_height = 0.1

	proc_height = 1

	compute_height = 0.1
	sleep_height = 0.1
	start_height = 0.2

	scale = 1/72

	def __init__(self):
		self.canvas = pyx.canvas.canvas()
		
	def getProcessTransform(self, process):
		return pyx.trafo.translate(xmargin, ymargin + process_height * process)

	def drawTimeLine(self, max_time):
		stmax = max_time * Visual.scale

		# draw base time line
		bx = Visual.xmargin
		by = -Visual.tl_ymargin
		base = pyx.path.line(bx, by, bx + stmax, by)
		self.canvas.stroke(base)

		# draw white frame line
		# TODO move to drawProcessLines
		bottom = pyx.path.line(0, 0, bx*2 + stmax, 0)
		self.canvas.stroke(bottom, [pyx.color.rgb.white])

		# draw ticks
		tick_count = int((max_time / Visual.tick_freq) + 1)
		for tid in range(tick_count):
			tx = Visual.xmargin + tid * Visual.tick_freq * Visual.scale
			ty = -Visual.tl_ymargin

			tick = pyx.path.line(tx, ty, tx, ty - Visual.tick_height)
			self.canvas.stroke(tick)

			# draw numbers
			if tid % 5 == 0:
				self.canvas.text(tx - 0.1, ty - 0.4, str(int(tid * Visual.tick_freq)), [pyx.text.size.small])
	
	def drawCircle(self, pid, time, yoffset, radius):
		time = time * Visual.scale
		
		cx = Visual.xmargin + time
		cy = Visual.tl_ymargin + Visual.ymargin + yoffset + pid * Visual.proc_height

		cir = pyx.path.circle(cx, -cy, radius)
		self.canvas.fill(cir)

	def drawRectangle(self, pid, time, duration):
		duration = duration * Visual.scale

		rx = Visual.xmargin + time * Visual.scale 
		ry = Visual.tl_ymargin + Visual.ymargin + pid*Visual.proc_height - Visual.compute_height/2 

		rect = pyx.path.rect(rx, -ry, duration, -Visual.compute_height)

		self.canvas.fill(rect)

	def drawVLine(self, pid, time, yoffset, height):
		time = time * Visual.scale
		
		lx = Visual.xmargin + time
		ly = Visual.tl_ymargin + Visual.ymargin - yoffset + pid*Visual.proc_height

		line = pyx.path.line(lx, -ly, lx, -ly - height)
		self.canvas.stroke(line)
			
	def drawHLine(self, pid, time, duration, yoffset): 
		time = time * Visual.scale
		duration = duration * Visual.scale

		lx = Visual.xmargin + time
		ly = Visual.tl_ymargin + Visual.ymargin - yoffset + pid*Visual.proc_height

		line = pyx.path.line(lx, -ly, lx + duration, -ly)
		self.canvas.stroke(line)

	def drawSLine(self, pid, time, yoffset, target, time_done):
		time = time * Visual.scale
		time_done = time_done * Visual.scale

		sx = Visual.xmargin + time
		sy = Visual.tl_ymargin + Visual.ymargin + pid*Visual.proc_height + yoffset

		ex = Visual.xmargin + time_done
		ey = Visual.tl_ymargin + Visual.ymargin + target*Visual.proc_height - yoffset

		line = pyx.path.line(sx, -sy, ex, -ey)
		self.canvas.stroke(line)

	def drawProcessLines(self, processes, max_time):
		stmax = max_time * Visual.scale

		# for each process
		for pid in range(processes):
			px = Visual.xmargin
			py = -Visual.tl_ymargin -Visual.ymargin - pid * Visual.proc_height

			procline = pyx.path.line(px, py, px + stmax, py) 
			self.canvas.stroke(procline)
			
			# draw process number
			# TODO

		# draw white frame line
		left = pyx.path.line(0, 0, 0, -Visual.ymargin*2 - (processes-1)*Visual.proc_height)
		self.canvas.stroke(left, [pyx.color.rgb.white])

	def savePDF(self, filename):
		self.canvas.writePDFfile(filename)
		
	

#def outputPDF(filename, machine, program):
#	if not machine.recording:
#		print('Machine was not recording! FAILED')
#		return
#	
#	# calculate resolution
#	xmargin = 10
#	ymargin = 20
#	pheight = 36
#	cheight = 3
#	theight = 2
#	sheight = 5 
#	tline = 4
#	scale = 1/10
#
#	maxtime = max(machine.procs)
#	height = ymargin * 2 + pheight * (machine.size-1)
#	width  = xmargin * 2 + int(math.ceil(maxtime / 1000.0)) * 1000 * scale
#
#	# create surface
#	pdf = cairo.PDFSurface(filename, width, height) 
#
#	# create context
#	ctx = cairo.Context(pdf)
#
#	# set settings
#	ctx.set_antialias(cairo.ANTIALIAS_GRAY)
#	ctx.set_source_rgb(0, 0, 0)
#	ctx.set_line_width(0.5)
#	# scale to time tick resolution
#	ctx.set_font_size(4)
#
#	# draw process lines
#	for proc in range(machine.size):
#		ctx.move_to(xmargin - 1, ymargin + proc * pheight + 7)
#		ctx.show_text(str(proc))
#		
#		ctx.move_to(xmargin, ymargin + proc * pheight) 
#		ctx.rel_line_to((width - xmargin * 2), 0)
#		ctx.stroke()
#
#	# draw max time line
#	ctx.set_source_rgb(0,0,1)
#	ctx.move_to(xmargin + maxtime * scale, ymargin/3)
#	ctx.rel_line_to(0, height - ymargin*4/3) 
#	ctx.stroke()
#	ctx.set_source_rgb(0,0,0)
#
#	# draw timeline
#	ctx.move_to(xmargin, ymargin/3)
#	ctx.rel_line_to((width-xmargin*2), 0)
#	ctx.stroke()	
#
#	for tick in range(int((width - xmargin*2)/10)+1):
#		if tick % 5 == 0:
#		    # draw number
#			ctx.move_to(xmargin + tick / scale - 2, ymargin/3 + 8)
#			ctx.show_text(str(tick*100))
#
#		# draw ticks
#		ctx.move_to(xmargin + tick / scale, ymargin/3)
#		ctx.rel_line_to(0, 4)
#		ctx.stroke()
#
#	# draw machine program
#	for node, data in program.nodes_iter(data=True):
#		task = data['task']
#
#		if isinstance(task, StartTask):
#			time = machine.record[node][0]
#			ctx.move_to(xmargin + time*scale, ymargin + pheight * task.proc - sheight/2)
#			ctx.rel_line_to(0, sheight)
#			ctx.stroke()
#
#		elif isinstance(task, PutTask):
#			# draw put task
#			# draw local block
#			record = machine.record[node]
#			
#			ctx.rectangle(xmargin + record[0] * scale, ymargin + pheight * task.proc - theight/2, record[1] * scale, theight) 
#			ctx.fill()
#
#			#ctx.move_to(xmargin + record[0]*scale, ymargin + pheight*task.proc + theight +2)
#			#ctx.show_text(task.node)
#
#			if record[1] != 0:
#				ctx.set_source_rgb(1,0,0)
#				ctx.rectangle(xmargin + (record[0]+record[1])*scale, ymargin + pheight*task.proc - theight/2, record[3]*scale, theight)
#				ctx.fill()
#				ctx.set_source_rgb(0,0,0)
#			
#			# draw transfer
#			direct = tline if (task.target - task.proc) > 0 else -tline
#
#			ctx.move_to(xmargin + (record[0]+record[1]+record[3]) * scale, ymargin + pheight * task.proc)
#			ctx.rel_line_to(0, direct)
#			ctx.rel_line_to(Machine.g_s*scale, 0)
#			ctx.line_to(xmargin + (record[0]+record[1]+record[2]+record[3])*scale, ymargin + pheight * task.target - direct)
#			#ctx.rel_line_to(Machine.g_r*scale, 0)
#			ctx.rel_line_to(0, direct)
#			ctx.stroke()
#
#
#			if record[4] != 0:
#				ctx.set_source_rgb(1,0,0)
#				ctx.move_to(xmargin + (record[0]+record[1]+record[2]+record[3])*scale, ymargin + pheight * task.target - direct)
#				ctx.rel_line_to(record[4]*scale, 0)
#				ctx.rel_line_to(0, direct)
#				ctx.stroke()
#				ctx.set_source_rgb(0,0,0)
#
#		elif isinstance(task, ComputeTask):
#			# draw compute task
#			record = machine.record[node]
#			ctx.rectangle(xmargin + record[0]*scale, ymargin + pheight * task.proc - cheight/2, record[1]*scale, cheight) 
#			ctx.fill()
#
#
#			if record[1] != 0:
#				ctx.set_source_rgb(1,0,0)
#				ctx.rectangle(xmargin+(record[0]+record[1])*scale, ymargin+pheight*task.proc -cheight/2,
#	record[2]*scale, cheight)
#				ctx.fill()
#				ctx.set_source_rgb(0,0,0)
#
#			#ctx.move_to(xmargin+record[0]*scale, ymargin+pheight*task.proc+cheight+2)
#			#ctx.show_text(task.node)
#
#		elif isinstance(task, SleepTask):
#			record = machine.record[node]
#
#			# draw sleep
#			ctx.move_to(xmargin + record[0]*scale, ymargin + pheight * task.proc - cheight/3)
#			ctx.rel_line_to(record[1]*scale, 0)
#			ctx.stroke()
#
#			if record[2] != 0:
#				ctx.set_source_rgb(1,0,0)
#				ctx.move_to(xmargin + (record[0]+record[1])*scale, ymargin + pheight * task.proc - cheight/3)
#				ctx.rel_line_to(record[2]*scale, 0)
#				ctx.stroke()
#				ctx.set_source_rgb(0,0,0)
#	
#		elif isinstance(task, ProxyTask):
#			pass
#			
#		else:
#			print('Unknown task type:', task)

			
