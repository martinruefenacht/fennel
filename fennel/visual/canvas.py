"""
"""


from pathlib import Path
from typing import Optional

PYPY_ENVIRONMENT = False
try:
    import __pypy__
    PYPY_ENVIRONMENT = True

except ModuleNotFoundError:
    import pyx


class Canvas:
    """
    """

    xmargin = 0.5
    ymargin = 1

    tl_ymargin = 0.5
    tick_freq = 100
    tick_height = 0.1

    proc_height = 2

    compute_height = 0.1
    compute_base = 0.0

    sleep_height = 0.1

    start_height = 0.3
    start_radius = 0.075

    put_base = 0.0
    put_height = 0.15
    put_offset = 0.075

    scale = 1/72

    def __init__(self):
        if not PYPY_ENVIRONMENT:
            self._canvas = pyx.canvas.canvas()

        else:
            self._canvas = None

#    def getProcessTransform(self, process):
#        return pyx.trafo.translate(xmargin, ymargin + process_height * process)

#    def drawTimeLine(self, max_time):
#        stmax = max_time * Canvas.scale
#
#        # draw base time line
#        bx = Canvas.xmargin
#        by = -Canvas.tl_ymargin
#        base = pyx.path.line(bx, by, bx + stmax, by)
#        self._canvas.stroke(base)
#
#        # draw white frame line
#        # TODO move to drawProcessLines
#        bottom = pyx.path.line(0, 0, bx*2 + stmax, 0)
#        self._canvas.stroke(bottom, [pyx.color.rgb.white])
#
#        self._canvas.text(Canvas.xmargin, 0.1-Canvas.tl_ymargin, 'nanoseconds', [pyx.text.size.large])   
#
#        # draw ticks
#        tick_count = int((max_time / Canvas.tick_freq) + 1)
#        for tid in range(tick_count):
#            tx = Canvas.xmargin + tid * Canvas.tick_freq * Canvas.scale
#            ty = -Canvas.tl_ymargin
#
#            tick = pyx.path.line(tx, ty, tx, ty - Canvas.tick_height)
#            self._canvas.stroke(tick)
#
#            # draw numbers
#            if tid % 5 == 0:
#                tex =  str(int(tid * Canvas.tick_freq))
#                xoffset = len(tex) * 0.1
#                self._canvas.text(tx - xoffset, ty - 0.5, tex, [pyx.text.size.large])
    
#    def drawCircle(self, pid, time, yoffset, radius):
#        time = time * Canvas.scale
#        
#        cx = Canvas.xmargin + time
#        cy = Canvas.tl_ymargin + Canvas.ymargin + yoffset + pid * Canvas.proc_height
#
#        cir = pyx.path.circle(cx, -cy, radius)
#        self._canvas.fill(cir)

#    def drawRectangle(self, pid, time, duration, centerline, height, dtype):
#        if dtype == 'std':
#            color = pyx.color.rgb.black
#        elif dtype == 'err':
#            color = pyx.color.rgb.red
#
#        duration = duration * Canvas.scale
#
#        rx = Canvas.xmargin + time * Canvas.scale 
#        ry = Canvas.tl_ymargin + Canvas.ymargin + pid*Canvas.proc_height + centerline + height/2
#
#        rect = pyx.path.rect(rx, -ry, duration, height)
#
#        self._canvas.fill(rect, [color])

#    def drawVLine(self, pid, time, yoffset, height, dtype):
#        if dtype == 'std':
#            color = pyx.color.rgb.black
#        elif dtype == 'sec':
#            color = pyx.color.cmyk.Gray
#        elif dtype == 'blu':
#            color = pyx.color.rgb.blue
#        elif dtype == 'err':
#            color = pyx.color.rgb.red
#
#        time = time * Canvas.scale
#        
#        lx = Canvas.xmargin + time
#        ly = Canvas.tl_ymargin + Canvas.ymargin - yoffset + pid*Canvas.proc_height
#
#        line = pyx.path.line(lx, -ly, lx, -ly - height)
#        self._canvas.stroke(line, [color])

#    def drawHLine(self, pid, time, duration, yoffset, dtype):
#        if dtype == 'std':
#            color = pyx.color.rgb.black
#        elif dtype == 'sec':
#            color = pyx.color.cmyk.Gray
#        elif dtype == 'blu':
#            color = pyx.color.rgb.blue
#        elif dtype == 'err':
#            color = pyx.color.rgb.red
#
#        time = time * Canvas.scale
#        duration = duration * Canvas.scale
#
#        lx = Canvas.xmargin + time
#        ly = Canvas.tl_ymargin + Canvas.ymargin + yoffset + pid*Canvas.proc_height
#
#        line = pyx.path.line(lx, -ly, lx + duration, -ly)
#        self._canvas.stroke(line, [color])

#    def drawSLine(self, pid, time, yoffset, target, time_done, dtype):
#        if dtype == 'std':
#            color = pyx.color.rgb.black
#        elif dtype == 'sec':
#            color = pyx.color.cmyk.Gray
#        elif dtype == 'blu':
#            color = pyx.color.rgb.blue
#        elif dtype == 'err':
#            color = pyx.color.rgb.red
#        
#        time = time * Canvas.scale
#        time_done = time_done * Canvas.scale
#
#        if pid > target:
#            yoffset *= -1
#
#        sx = Canvas.xmargin + time
#        sy = Canvas.tl_ymargin + Canvas.ymargin + pid*Canvas.proc_height + yoffset
#
#        ex = Canvas.xmargin + time_done
#        ey = Canvas.tl_ymargin + Canvas.ymargin + target*Canvas.proc_height - yoffset
#
#        line = pyx.path.line(sx, -sy, ex, -ey)
#        self._canvas.stroke(line, [color])

#    def drawProcessLines(self, processes, max_time):
#        stmax = max_time * Canvas.scale
#
#        # for each process
#        for pid in range(processes):
#                px = Canvas.xmargin
#                py = -Canvas.tl_ymargin -Canvas.ymargin - pid * Canvas.proc_height
#
#                procline = pyx.path.line(px, py, px + stmax, py) 
#                self._canvas.stroke(procline, [pyx.color.cmyk.Gray])
#                
#                # draw process number
#                # TODO
#
#        # draw white frame line
#        left = pyx.path.line(0, 0, 0, -Canvas.ymargin*2 - (processes-1)*Canvas.proc_height)
#        self._canvas.stroke(left, [pyx.color.rgb.white])

    def _draw_time_lines(self) -> None:
        """
        """

#        if not PYPY_ENVIRONMENT:
#            for process 

        pass

    def write(self, path: Path):
        """
        Write the drawn canvas out to a given file path.

        Determines the file format from the extension.
        """

        self._canvas.writetofile(str(path))

    def draw_start_task(self, process: int, time: int) -> None:
        """
        Draw triangle to represent start task.
        """

        assert time >= 0
        assert process >= 0

        if not PYPY_ENVIRONMENT:
            self._canvas.fill()

    def draw_sleep_task(self):
        """
        """

        pass

    def draw_compute_task(self):
        """
        """
        
        pass

    def draw_compute_task(self):
        """
        """

        pass

    def draw_put_task(self):
        """
        """

        pass
