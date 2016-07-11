import pyx, math

class Visual:
	xmargin = 0.5
	ymargin = 1
	
	tl_ymargin = 0.5
	tick_freq = 100 #ns
	tick_height = 0.1

	proc_height = 2

	compute_height = 0.1
	sleep_height = 0.1

	start_height = 0.3
	start_radius = 0.075

	put_base = 0
	put_height = 0.1
	put_offset = 0.1

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

	def drawRectangle(self, pid, time, duration, yoffset, height, dtype):
		if dtype == 'std':
			color = pyx.color.rgb.black
		elif dtype == 'err':
			color = pyx.color.rgb.red

		duration = duration * Visual.scale

		rx = Visual.xmargin + time * Visual.scale 
		ry = Visual.tl_ymargin + Visual.ymargin + pid*Visual.proc_height + yoffset 

		rect = pyx.path.rect(rx, -ry, duration, -height)

		self.canvas.fill(rect, [color])

	def drawVLine(self, pid, time, yoffset, height, dtype):
		if dtype == 'std':
			color = pyx.color.rgb.black
		elif dtype == 'sec':
			color = pyx.color.cmyk.Gray
		elif dtype == 'err':
			color = pyx.color.rgb.red

		time = time * Visual.scale
		
		lx = Visual.xmargin + time
		ly = Visual.tl_ymargin + Visual.ymargin - yoffset + pid*Visual.proc_height

		line = pyx.path.line(lx, -ly, lx, -ly - height)
		self.canvas.stroke(line, [color])
			
	def drawHLine(self, pid, time, duration, yoffset, dtype):
		if dtype == 'std':
			color = pyx.color.rgb.black
		elif dtype == 'sec':
			color = pyx.color.cmyk.Gray
		elif dtype == 'err':
			color = pyx.color.rgb.red

		time = time * Visual.scale
		duration = duration * Visual.scale

		lx = Visual.xmargin + time
		ly = Visual.tl_ymargin + Visual.ymargin + yoffset + pid*Visual.proc_height

		line = pyx.path.line(lx, -ly, lx + duration, -ly)
		self.canvas.stroke(line, [color])

	def drawSLine(self, pid, time, yoffset, target, time_done, dtype):
		if dtype == 'std':
			color = pyx.color.rgb.black
		elif dtype == 'sec':
			color = pyx.color.cmyk.Gray
		elif dtype == 'err':
			color = pyx.color.rgb.red
		
		time = time * Visual.scale
		time_done = time_done * Visual.scale

		if pid > target:
			yoffset *= -1

		sx = Visual.xmargin + time
		sy = Visual.tl_ymargin + Visual.ymargin + pid*Visual.proc_height + yoffset

		ex = Visual.xmargin + time_done
		ey = Visual.tl_ymargin + Visual.ymargin + target*Visual.proc_height - yoffset

		line = pyx.path.line(sx, -sy, ex, -ey)
		self.canvas.stroke(line, [color])

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
