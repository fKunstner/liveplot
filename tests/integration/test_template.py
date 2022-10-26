from unittest.mock import patch

from matplotlib import pyplot as plt

from liveplot import template


def test_template():
    template.settings(plt)
    template.make_figure(plt.figure(), template.postprocess(template.load_data()))
