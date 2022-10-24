import argparse
import importlib.resources
import logging
import sys
import textwrap
from pathlib import Path

from liveplot.plot_watcher import PlotWatcher


def create_template(filepath: Path):
    if filepath.exists():
        print(f"File {filepath} already exists")
    else:
        with importlib.resources.path("liveplot", "template.py") as template:
            with open(filepath, "w", encoding="utf8") as f:
                f.write(template.read_text(encoding="utf8"))


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Update a Matplotlib pyplot figure on save, "
            "without having to re-run a script or reload data"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Calling liveplot on the code below will produce the same result as 
            calling the script, but the plot will update when the file changes. 
            The data is saved and re-used if load_data does not change.
            
                import matplotlib.pyplot as plt 
                
                def load_data(): 
                    return ([1, 2, 3], [1, 4, 9])
                    
                def make_figure(fig, data): 
                    fig.add_subplot(111).plot(*data, ".")
                    
                if __name__ == "__main__":
                    make_figure(plt.figure(), load_data())
                    plt.show()
            
            Functions supported:
            
                def settings(plt): pass
                def load_data(): return None
                def postprocess(data): return data
                def make_figure(fig, data): pass
            
            Find the documentation and examples at https://github.com/fkunstner/liveplot
            """
        ),
        usage="""liveplot [-h] (script | --new [filename]) [--debug]
        """,
    )
    parser.add_argument(
        "script",
        nargs="?",
        type=Path,
        default=None,
        help="The plotting file to update on change",
    )
    parser.add_argument(
        "--new",
        metavar="filename",
        action="store",
        nargs="?",
        const=Path("new_plot.py"),
        default=None,
        type=Path,
        help=(
            "Create a plotting script template "
            "in filename (defaults to new_liveplot.py)"
        ),
    )
    parser.add_argument(
        "--debug", action="store_true", default=False, help="Enable debug logs"
    )
    return parser


def configure_logs(debug: bool = False):
    logger = logging.getLogger("liveplot")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        logging.Formatter(
            "[%(name)s %(asctime)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)


def launch_liveplot(filepath: Path, debug: bool):
    if not filepath.is_file():
        raise FileNotFoundError(f"{filepath}")

    configure_logs(debug)

    figure_watcher = PlotWatcher.from_path(filepath)
    while True:
        figure_watcher.refresh()
        figure_watcher.plt_interface.pause(2)


def main():
    parser = make_parser()
    cli_args = parser.parse_args()

    no_input = cli_args.script is None and cli_args.new is None

    if no_input:
        parser.print_help()
    elif cli_args.new is not None:
        create_template(cli_args.new)
    elif cli_args.script is not None:
        launch_liveplot(cli_args.script, cli_args.debug)

    sys.exit()
