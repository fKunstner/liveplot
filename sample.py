import numpy as np


def load_data():
    print("Loading data")
    np.random.seed(0)
    N = 30
    xs = np.random.randn(N)
    ys = xs + np.random.randn(N)
    return {"xs": xs, "ys": ys}


def make_figure(fig, data):
    ax = fig.add_subplot(1, 1, 1)

    xs, ys = data["xs"], data["ys"]

    ax.plot(xs, ys, ".")

    # a, b = np.polyfit(xs, ys, deg=1)
    # ax.plot(xs, a * xs + b, linewidth=2)
