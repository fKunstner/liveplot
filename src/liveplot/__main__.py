import argparse
import importlib.resources
import logging
import sys
from pathlib import Path

from liveplot.plot_watcher import PlotWatcher


def quick_guide():
    with importlib.resources.path("liveplot", "quick_guide.md") as data_path:
        return data_path.read_text()


def create_template(filepath: Path):
    if filepath.exists():
        print(f"File {filepath} already exists")
    else:
        with importlib.resources.path("liveplot", "template.py") as template:
            with open(filepath, "w", encoding="utf8") as fh:
                fh.write(template.read_text(encoding="utf8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update a Matplotlib pyplot figure on save, "
        "without having to re-run a script or reload data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=quick_guide(),
    )
    parser.add_argument(
        "file_path",
        nargs="?",
        type=Path,
        default=None,
        help="The plotting file to update on change",
    )
    parser.add_argument(
        "--debug", action="store_true", default=False, help="Enable debug logs"
    )
    parser.add_argument(
        "--new",
        metavar="filename",
        action="store",
        nargs="?",
        const=Path("new_plot.py"),
        default=None,
        type=Path,
        help="Create a new plotting script with basic functions in filename (defaults to new_liveplot.py)",
    )
    cli_args = parser.parse_args()

    if cli_args.file_path is None:
        if cli_args.new is not None:
            create_template(cli_args.new)
        else:
            parser.print_help()
        sys.exit()

    if not cli_args.file_path.is_file():
        raise FileNotFoundError(f"{cli_args.file_path}")

    return cli_args


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


def main():
    cli_args = parse_args()
    configure_logs(cli_args.debug)
    figure_watcher = PlotWatcher.from_path(cli_args.file_path)
    while True:
        figure_watcher.refresh()
        figure_watcher.plt_interface.pause(2)


if __name__ == "__main__":
    main()
