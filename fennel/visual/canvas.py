"""
"""

import math
from pathlib import Path
from typing import MutableMapping
from collections import defaultdict

PYPY_ENVIRONMENT = False
try:
    import __pypy__
    PYPY_ENVIRONMENT = True

except ModuleNotFoundError:
    import pyx


class Canvas:
    """
    Canvas to draw program task timeline.
    """

    MARGIN = 1
    TIME_SCALE = 0.01

    # TODO TIME_WIDTH instead of scale
    # find resolution scale

    PROCESS_SPACING = 0.0
    PROCESS_HEIGHT = 1.0
    PROCESS_SCALE = PROCESS_HEIGHT / 2.0

    TICK_RESOLUTION = 100

    def __init__(self):
        if not PYPY_ENVIRONMENT:
            self._canvas = pyx.canvas.canvas()

        else:
            self._canvas = None

        self._minimum_time = 100
        self._processes: MutableMapping[int, bool] = defaultdict(lambda: False)

    @property
    def minimum_time(self) -> int:
        """
        """

        return int(math.ceil(self._minimum_time / 100.0)) * 100

    @minimum_time.setter
    def minimum_time(self, value: int) -> None:
        """
        """

        self._minimum_time = value

    def process_offset(self, process) -> float:
        """
        """

        return (process * (self.PROCESS_HEIGHT + self.PROCESS_SPACING) + 0.5) * -1

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

    def _draw_timeline(self) -> None:
        """
        """

        if not PYPY_ENVIRONMENT:
            attrs = [pyx.trafo.scale(self.TIME_SCALE, -self.PROCESS_SCALE)]

            self._canvas.stroke(pyx.path.line(0.0, -0.25, self.minimum_time, -0.25), attrs)

            ticks = int(math.ceil(self.minimum_time / self.TICK_RESOLUTION))
            for tick in range(ticks+1):
                # 1000 ticks bigger than 100s
                self._canvas.stroke(pyx.path.line(tick * self.TICK_RESOLUTION, -0.5,
                                                  tick * self.TICK_RESOLUTION, -0.15), attrs)

                # TODO tick labeling
                # self._canvas.text(tick * self.TICK_RESOLUTION, 0.0, str(tick * self.TICK_RESOLUTION), attrs)

    def _draw_process_lines(self) -> None:
        """
        """

        if not PYPY_ENVIRONMENT:
            for process in range(len(self._processes)):
                attrs = [pyx.trafo.scale(self.TIME_SCALE, -self.PROCESS_SCALE),
                         pyx.trafo.translate(0, self.process_offset(process))]

                self._canvas.stroke(pyx.path.line(0, 0,
                                                  self.minimum_time, 0), attrs)

    def _draw_margin(self) -> None:
        """
        Draw white rectangle to force margin.
        """

        if not PYPY_ENVIRONMENT:
            attrs = [pyx.color.rgb.white]

            self._canvas.stroke(
                pyx.path.rect(-self.MARGIN, self.MARGIN,
                              self.minimum_time*self.TIME_SCALE + 2*self.MARGIN,
                              (len(self._processes) + 1) * -self.PROCESS_SCALE - 2*self.MARGIN),
                attrs)

    def _draw_process_bound(self, process) -> None:
        """
        """

        if not PYPY_ENVIRONMENT:
            attrs = [pyx.trafo.scale(self.TIME_SCALE, -self.PROCESS_SCALE),
                     pyx.trafo.translate(0.0, self.process_offset(process)),
                     pyx.color.rgb.red]

            self._canvas.stroke(pyx.path.circle(0, 0, 0.1), attrs)
            self._canvas.stroke(pyx.path.rect(0.0, -1.0,
                                              self.minimum_time, 2.0), attrs)

    def write(self, path: Path):
        """
        Write the drawn canvas out to a given file path.

        Determines the file format from the extension.
        """

        self._draw_margin()
        self._draw_timeline()
        self._draw_process_lines()

        self._canvas.writetofile(str(path))

    def draw_start_task(self, process: int, time: int) -> None:
        """
        Draw triangle to represent start task.
        """

        assert time >= 0
        assert process >= 0

        if not PYPY_ENVIRONMENT:

            attrs = [pyx.trafo.scale(self.TIME_SCALE, -self.PROCESS_SCALE),
                     pyx.trafo.translate(time, self.process_offset(process))]

            self._canvas.stroke(pyx.path.line(0.0, 0.0, 0.0, -0.5), attrs)

            attrs = [pyx.trafo.scale(self.PROCESS_SCALE, -self.PROCESS_SCALE),
                     pyx.trafo.translate(time, self.process_offset(process))]

            self._canvas.fill(pyx.path.circle(0.0, -0.5, 0.1), attrs)

            self._processes[process] = True
            self._minimum_time = max(self._minimum_time, time+1)

    def draw_sleep_task(self, process: int, start: int, end: int):
        """
        Draw empty rectangle to represent sleep task.
        """

        assert process >= 0
        assert start >= 0
        assert end > start

        if not PYPY_ENVIRONMENT:
            attrs = [pyx.trafo.scale(self.TIME_SCALE, -self.PROCESS_SCALE),
                     pyx.trafo.translate(0.0, self.process_offset(process))]

            self._canvas.stroke(
                pyx.path.rect(start, -0.25, start-end, 0.5),
                attrs)

            self._processes[process] = True
            self._minimum_time = max(self._minimum_time, end)

    def draw_compute_task(self, process: int, start: int, end: int) -> None:
        """
        Draw filled rectangle to represent compute task.
        """

        assert process >= 0
        assert start >= 0
        assert end > start

        if not PYPY_ENVIRONMENT:
            attrs = [pyx.trafo.scale(self.TIME_SCALE, -self.PROCESS_SCALE),
                     pyx.trafo.translate(0.0, self.process_offset(process))]

            self._canvas.fill(pyx.path.rect(start, -0.25, start-end, 0.5), attrs)

            self._processes[process] = True
            self._minimum_time = max(self._minimum_time, end)

    def draw_blocking_put_task(self, source: int, target: int, start: int,
                               end: int) -> None:
        """
        Draw a blocking put between source and target.
        """

        assert source >= 0
        assert target >= 0
        assert start >= 0
        assert end > start

        if not PYPY_ENVIRONMENT:
            attrs = [pyx.trafo.scale(self.TIME_SCALE, 1)]

            source_offset = self.process_offset(source)
            target_offset = self.process_offset(target)

            self._canvas.stroke(pyx.path.line(start, source_offset,
                                              end, target_offset), attrs)

            self._processes[source] = True
            self._processes[target] = True
            self._minimum_time = max(self._minimum_time, end)


    def draw_non_blocking_put_task(self, source: int, target: int, start: int,
                                   switch: int, end: int) -> None:
        """
        Draw filled rectangle for occupied time on source and draw transfer
        line.
        """

        assert source >= 0
        assert target >= 0
        assert start >= 0
        assert switch > start
        assert end > switch

        if not PYPY_ENVIRONMENT:
            attrs = [pyx.trafo.scale(self.TIME_SCALE, -self.PROCESS_SCALE),
                     pyx.trafo.translate(0.0, self.process_offset(source))]

            side = 1 if source < target else -1

            self._canvas.stroke(pyx.path.line(start, 0.0, start, side * 0.25), attrs)
            self._canvas.stroke(pyx.path.line(start, side * 0.25, switch, side * 0.25), attrs)

            # transfer line
            attrs = [pyx.trafo.scale(self.TIME_SCALE, 1)]

            source_offset = self.process_offset(source)
            target_offset = self.process_offset(target)

            self._canvas.stroke(pyx.path.line(switch,
                                              (source_offset -
                                               side * 0.25 * self.PROCESS_SCALE),
                                              end, target_offset), attrs)

            self._processes[source] = True
            self._processes[target] = True
            self._minimum_time = max(self._minimum_time, end)
