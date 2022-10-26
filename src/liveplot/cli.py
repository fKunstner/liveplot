import argparse
import importlib.resources
import logging
import sys
import textwrap
from pathlib import Path
from typing import Optional

from liveplot.plot_watcher import PlotWatcher

default_new_template_file = "new_liveplot.py"


def create_template(filepath: Optional[Path]) -> Path:
    if filepath is None:
        filepath = Path(default_new_template_file)

    if filepath.exists():
        raise FileExistsError(f"File {filepath} already exists")

    with importlib.resources.path("liveplot", "template.py") as template:
        with open(filepath, "w", encoding="utf8") as f:
            f.write(template.read_text(encoding="utf8"))

    return filepath


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Update a Matplotlib pyplot figure on save",
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
    )

    parser.add_argument(
        "--new",
        "-n",
        action="store_true",
        default=False,
        help=f"Create a plotting script in script (default: {default_new_template_file})",
    )
    parser.add_argument(
        "script",
        nargs="?",
        type=Path,
        default=None,
        help="The plotting file to update on change",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug logs",
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


def launch_liveplot(filepath: Path):
    figure_watcher = PlotWatcher.from_path(filepath)
    while True:
        figure_watcher.refresh()
        figure_watcher.plt_interface.pause(2)


def main():
    parser = make_parser()
    cli_args = parser.parse_args()

    configure_logs(cli_args.debug)

    no_args = cli_args.new is False and cli_args.script is None

    if no_args:
        parser.print_help()
        sys.exit()

    if cli_args.new is True:
        cli_args.script = create_template(cli_args.script)

    launch_liveplot(cli_args.script)
