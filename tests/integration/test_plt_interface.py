"""We have to run those in a subprocess so that the main process isn't killed
when a figure is closed."""

from multiprocessing import Pipe, Process

from liveplot.plt_interface import PltInterface


def _test_closing(connection):
    plt_interface = PltInterface()
    plt_interface.new_figure()

    before = plt_interface.plt.fignum_exists(plt_interface.fig.number)
    plt_interface.plt.close(plt_interface.fig)
    after = plt_interface.plt.fignum_exists(plt_interface.fig.number)

    connection.send([before, after])


def test_closing():
    conn1, conn2 = Pipe()
    process = Process(target=_test_closing, args=(conn2,))
    process.start()
    process.join()
    before, after = conn1.recv()
    assert before
    assert not after


def _test_new_twice(connection):
    checks = []

    plt_interface = PltInterface()
    plt_interface.new_figure()
    plt_interface.new_figure()

    checks.append(len(plt_interface.fig.get_axes()) == 0)

    plt_interface.fig.add_subplot(111)

    checks.append(len(plt_interface.fig.get_axes()) == 1)

    plt_interface.draw()
    plt_interface.pause(0.1)
    plt_interface.clear()

    checks.append(len(plt_interface.fig.get_axes()) == 0)

    checks.append(plt_interface.plt.fignum_exists(plt_interface.fig.number))

    plt_interface.plt.close(plt_interface.fig)

    checks.append(not plt_interface.plt.fignum_exists(plt_interface.fig.number))

    connection.send(checks)


def test_new_twice():
    conn1, conn2 = Pipe()
    process = Process(target=_test_new_twice, args=(conn2,))
    process.start()
    process.join()
    checks = conn1.recv()

    for i, check in enumerate(checks):
        print(i)
        assert check
