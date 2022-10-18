import matplotlib.pyplot as plt
import numpy as np


def load_data():
    n = 50
    x = np.random.randn(n)
    y = 2.0 * x + np.random.randn(n)
    return {"x": x, "y": y}


def make_figure(fig, data):
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(data["x"], data["y"], ".", color="red")


def main():
    fig = plt.figure()
    make_figure(fig, load_data())
    plt.show()


if __name__ == "__main__":
    main()
