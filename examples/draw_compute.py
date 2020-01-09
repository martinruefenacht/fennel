"""
"""

from fennel.visual.canvas import Canvas


def main() -> None:
    """
    """

    canvas = Canvas()

    canvas.draw_start_task(0, 0)
    canvas.draw_compute_task(0, 20, 30)
    canvas.draw_sleep_task(0, 30, 40)
    canvas.draw_put_task(0, 1, 50, 60, 70)
    canvas.draw_put_task(1, 0, 70, 80, 90)

    canvas.minimum_time = 1000

    canvas.write("test.pdf")


if __name__ == "__main__":
    main()
