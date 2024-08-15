import matplotlib.pyplot as plt
import numpy as np


def load_data():

    N = 1000
    T = 100
    snr = 0.1

    x = np.linspace(0, 4 * np.pi, T)
    y = np.cumsum(np.random.randn(N, T), axis=1)

    num_signal = int(round(snr * N))
    phi = (np.pi / 8) * np.random.randn(num_signal, 1)
    y[:num_signal] = np.sqrt(np.arange(T))[None, :] * (
        np.sin(x[None, :] - phi) + 0.05 * np.random.randn(num_signal, T)
    )

    return x, y


def postprocess(data):
    return data


def settings(plt):
    pass


def make_figure(fig, data):
    fig.set_size_inches(6, 6)
    fig.set_dpi(150)

    axes = [
        fig.add_subplot(311),
        fig.add_subplot(312),
        fig.add_subplot(313),
    ]

    (x, y) = data

    axes[0].plot(x, y.T, color="k", alpha=0.025)
    axes[1].plot(x, y.T, color="k", alpha=0.01)
    axes[2].plot(x, y.T, color="k", alpha=0.005)

    for ax in axes:
        ax.set_xlim(0, 4 * np.pi)
        ax.set_ylim([-30, 30])
        ticks = [0.5, 1, 2, 3, 4]
        ax.set_xticks([i * np.pi for i in ticks])
        ax.set_xticklabels([f"{i}π" for i in ticks])

    fig.tight_layout()


if __name__ == "__main__":
    make_figure(plt.figure(), load_data())
    plt.show()
