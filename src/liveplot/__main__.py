import argparse
import logging
import pathlib

from liveplot.plot_watcher import PlotWatcher


def parse_args():
    parser = argparse.ArgumentParser(description="Live plot updater")
    parser.add_argument("file_path", type=pathlib.Path)
    parser.add_argument("--debug", action="store_true", default=False)
    cli_args = parser.parse_args()

    if not cli_args.file_path.is_file():
        raise FileNotFoundError(f"{cli_args.file_path}")

    return cli_args


def main():
    cli_args = parse_args()

    logger = logging.getLogger("liveplot")
    logger.setLevel(logging.DEBUG if cli_args.debug else logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        logging.Formatter(
            "[%(name)s %(asctime)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)

    figure_code = PlotWatcher(cli_args.file_path)
    figure_code.setup()
    figure_code.refresh_loop()


if __name__ == "__main__":
    main()
