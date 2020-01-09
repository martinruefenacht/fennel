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
    canvas.draw_blocking_put_task(0, 1, 50, 60)
    canvas.draw_non_blocking_put_task(1, 0, 60, 70, 80)
    canvas.draw_non_blocking_put_task(0, 1, 100, 110, 120)

    canvas.minimum_time = 200

    canvas.write("output.pdf")


if __name__ == "__main__":
    main()
