"""
The Canvas class is the drawn representation of a simulation.
"""

import math
from pathlib import Path
from typing import MutableMapping
from collections import defaultdict


# special testing for pypy environment, pypy can be used to accelerate
# simulation, but cannot be used with drawing (pyx)
PYPY_ENVIRONMENT = False
try:
    import __pypy__  # type: ignore
    PYPY_ENVIRONMENT = True

except ModuleNotFoundError:
    import pyx  # type: ignore


class Canvas:
    """
    Canvas to draw program task timeline.
    """

    MARGIN = 0.5
    TIME_SCALE = 0.01

    # TODO TIME_WIDTH instead of scale
    # find resolution scale

    PROCESS_SPACING = 0.0
    PROCESS_HEIGHT = 1.0
    PROCESS_SCALE = PROCESS_HEIGHT / 2.0

    TICK_RESOLUTION = 100

    def __init__(self):
        if not PYPY_ENVIRONMENT:
            self._base = pyx.canvas.canvas()

            self._plot = self._base.layer('plot')
            self._canvas = self._base.layer('draw')

        else:
            self._canvas = None

        self._minimum_time = 1000
        self._processes: MutableMapping[int, bool] = defaultdict(lambda: False)

    @property
    def minimum_time(self) -> int:
        """
        Find the minimum time to draw the canvas to.
        """

        return int(math.ceil(self._minimum_time / 100.0)) * 100

    @minimum_time.setter
    def minimum_time(self, value: int) -> None:
        """
        """

        self._minimum_time = value

    def _process_offset(self, process: int) -> float:
        """
        Find the vertical offset for the given process number.
        """

        vertical_space = self.PROCESS_HEIGHT + self.PROCESS_SPACING
        timeline_spacing = 0.5

        return (process * vertical_space + timeline_spacing) * -1

    def _draw_timeline(self) -> None:
        """
        """

        if not PYPY_ENVIRONMENT:
            attrs = [pyx.trafo.scale(self.TIME_SCALE, -self.PROCESS_SCALE)]

            self._plot.stroke(pyx.path.line(0.0, -0.25,
                                            self.minimum_time, -0.25),
                              attrs)

            ticks = int(math.ceil(self.minimum_time / self.TICK_RESOLUTION))
            for tick in range(ticks+1):
                # 1000 ticks bigger than 100s
                self._plot.stroke(
                    pyx.path.line(
                        tick * self.TICK_RESOLUTION, -0.5,
                        tick * self.TICK_RESOLUTION, -0.25),
                    attrs)

                # tick labeling
                if (tick % 5) == 0:
                    label = str(tick * self.TICK_RESOLUTION)
                    shift = -1 * (7.5 * len(label))
                    self._canvas.text(
                        (tick * self.TICK_RESOLUTION + shift) * self.TIME_SCALE,
                        0.3,
                        label,
                        [pyx.text.size.footnotesize])

            self._canvas.text(0, 0.6, "nanoseconds", [pyx.text.size.footnotesize])

    def _draw_process_lines(self) -> None:
        """
        """

        if not PYPY_ENVIRONMENT:
            for process in range(len(self._processes)):
                attrs = [pyx.trafo.scale(self.TIME_SCALE, -self.PROCESS_SCALE),
                         pyx.trafo.translate(0, self._process_offset(process)),
                         pyx.style.linestyle.dotted]

                self._plot.stroke(pyx.path.line(0, 0,
                                                self.minimum_time, 0), attrs)

    def _draw_margin(self) -> None:
        """
        Draw white rectangle to force margin.
        """

        if not PYPY_ENVIRONMENT:
            attrs = [pyx.color.rgb.white]

            origin = 0.75 + self.MARGIN
            height = (origin +
                      len(self._processes) * self.PROCESS_HEIGHT)

            self._plot.stroke(
                pyx.path.rect(
                    -self.MARGIN,
                    origin,
                    self.minimum_time*self.TIME_SCALE + 2*self.MARGIN,
                    -height),
                attrs)

    def _draw_process_bound(self, process) -> None:
        """
        """

        if not PYPY_ENVIRONMENT:
            attrs = [pyx.trafo.scale(self.TIME_SCALE, -self.PROCESS_SCALE),
                     pyx.trafo.translate(0.0, self._process_offset(process)),
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

        # debug draw red boxes around processes
        # for process in range(len(self._processes)):
        #     self._draw_process_bound(process)

        self._base.writetofile(str(path))

    def draw_start_task(self, process: int, time: int) -> None:
        """
        Draw triangle to represent start task.
        """

        assert time >= 0
        assert process >= 0

        triangle = pyx.path.path(
            pyx.path.moveto(time, -0.4),
            pyx.path.lineto(time-4, -0.6),
            pyx.path.lineto(time+4, -0.6),
            pyx.path.closepath())

        if not PYPY_ENVIRONMENT:
            attrs = [pyx.trafo.scale(self.TIME_SCALE, -self.PROCESS_SCALE),
                     pyx.trafo.translate(0.0, self._process_offset(process))]

            self._canvas.stroke(pyx.path.line(time, 0.0, time, -0.5), attrs)
            self._canvas.fill(triangle, attrs)

            self._processes[process] = True
            self._minimum_time = max(self._minimum_time, time + 1)

    def draw_sleep_task(self, process: int, start: int, end: int):
        """
        Draw empty rectangle to represent sleep task.
        """

        assert process >= 0
        assert start >= 0
        assert end > start

        if not PYPY_ENVIRONMENT:
            attrs = [pyx.trafo.scale(self.TIME_SCALE, -self.PROCESS_SCALE),
                     pyx.trafo.translate(0.0, self._process_offset(process))]

            self._canvas.stroke(
                pyx.path.rect(start, -0.25, end-start, 0.5),
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
                     pyx.trafo.translate(0.0, self._process_offset(process)),
                     pyx.deco.filled([pyx.pattern.crosshatched45.SMall]),
                     pyx.deco.stroked]

            self._canvas.draw(
                pyx.path.rect(start, -0.2, end-start, 0.4),
                attrs)

            self._processes[process] = True
            self._minimum_time = max(self._minimum_time, end)

    def draw_get_task(self,
                      source: int,
                      target: int,
                      start: int,
                      switch: int,
                      end: int
                      ) -> None:
        """
        Draw a GetTask.
        """

        if not PYPY_ENVIRONMENT:
            attrs = [pyx.trafo.scale(self.TIME_SCALE, 1)]

            source_offset = self._process_offset(source)
            target_offset = self._process_offset(target)

            self._canvas.stroke(pyx.path.line(start, source_offset,
                                              switch, target_offset), attrs)

            self._canvas.stroke(pyx.path.line(switch, target_offset,
                                              end, source_offset), attrs)

            side = -1 if source < target else 1
            triangle = pyx.path.path(
                pyx.path.moveto(switch, 0.0),
                pyx.path.lineto(switch-6, -0.25 * side),
                pyx.path.lineto(switch+6, -0.25 * side),
                pyx.path.closepath())

            attrs = [pyx.trafo.scale(self.TIME_SCALE, -self.PROCESS_SCALE),
                     pyx.trafo.translate(0.0, target_offset)]

            self._canvas.fill(triangle, attrs)

            self._processes[source] = True
            self._processes[target] = True
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

            source_offset = self._process_offset(source)
            target_offset = self._process_offset(target)

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
                     pyx.trafo.translate(0.0, self._process_offset(source))]

            side = 1 if source < target else -1

            self._canvas.stroke(
                pyx.path.line(start, 0.0, start, side * 0.25),
                attrs)
            self._canvas.stroke(
                pyx.path.line(start, side * 0.25, switch, side * 0.25),
                attrs)

            # transfer line
            attrs = [pyx.trafo.scale(self.TIME_SCALE, 1)]

            source_offset = self._process_offset(source)
            target_offset = self._process_offset(target)

            self._canvas.stroke(
                pyx.path.line(
                    switch,
                    source_offset - side * 0.25 * self.PROCESS_SCALE,
                    end,
                    target_offset),
                attrs)

            self._processes[source] = True
            self._processes[target] = True
            self._minimum_time = max(self._minimum_time, end)

    def draw_noise_overlay(self, process: int, start: int, end: int) -> None:
        """
        Draws an additional layered color to represent noise.
        """

        assert process >= 0
        assert start > 0
        assert end > start

        if not PYPY_ENVIRONMENT:
            attrs = [pyx.trafo.scale(self.TIME_SCALE, -self.PROCESS_SCALE),
                     pyx.trafo.translate(0.0, self._process_offset(process)),
                     pyx.color.cmyk.Sepia,
                     pyx.style.linewidth.Thick]

            self._canvas.stroke(pyx.path.line(start, 0.1, end, 0.1), attrs)
