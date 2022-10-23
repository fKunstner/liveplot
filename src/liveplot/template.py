import matplotlib.pyplot as plt


def load_data():
    return {}


def postprocess(data):
    return data


def settings(plt):
    pass


def make_figure(fig, data):
    ax = fig.add_subplot(1, 1, 1)


if __name__ == "__main__":
    fig = plt.figure()
    make_figure(fig, load_data())
    plt.show()
