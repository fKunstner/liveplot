import matplotlib.pyplot as plt


def load_data():
    return {}


def postprocess(data):
    return data


def settings(plt):
    pass


def make_figure(fig, data):
    axes = [
        fig.add_subplot(111),
    ]


if __name__ == "__main__":
    make_figure(plt.figure(), load_data())
    plt.show()
