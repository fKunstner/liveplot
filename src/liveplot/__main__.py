import os
import sys
import inspect
import pathlib
import logging
import argparse
import datetime
import traceback
import importlib.util
import matplotlib.pyplot as plt

logging.basicConfig()
log = logging.getLogger(__name__)


DATA_FNAME = "load_data"
FIG_FNAME = "make_figure"
SETTINGS_FNAME = "settings"


def except_exec(func, *args, **kwargs):
    """
    Log any exception thrown by func (except Interrupts and SystemExit).
    Returns the value of func(*args, **kwargs) if successful, None otherwise.
    """
    try:
        return func(*args, **kwargs)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        log.warning(f"Triggered exception at {datetime.datetime.now()}")
        log.warning(traceback.format_exc())
        return None


def parse_args():
    parser = argparse.ArgumentParser(description="Live plot updater")
    parser.add_argument("file_path", type=pathlib.Path)
    args = parser.parse_args()

    if not args.file_path.is_file():
        raise FileNotFoundError(f"{args.file_path}")

    return args


def file_modified_date(file_path):
    return os.stat(file_path)[8]


if __name__ == "__main__":
    args = parse_args()

    file_path = args.file_path
    modified_date = None
    module = None
    data_code = None
    settings_code = None
    fig_code = None
    data = None
    interactive_elements = None

    fig = plt.figure()
    cid = fig.canvas.mpl_connect("close_event", lambda event: sys.exit())

    def load_module():
        """Loads the module in file_path.

        Creates dummy functions for DATA_FNAME or FIG_FNAME if not defined.
        """
        spec = importlib.util.spec_from_file_location("module.name", file_path)
        foo = importlib.util.module_from_spec(spec)
        except_exec(spec.loader.exec_module, foo)

        if not hasattr(foo, DATA_FNAME):
            setattr(foo, DATA_FNAME, lambda: None)
            log.warning(f"Function {DATA_FNAME} not found.")

        if not hasattr(foo, SETTINGS_FNAME):
            setattr(foo, SETTINGS_FNAME, lambda plt: None)
            log.warning(f"Function {SETTINGS_FNAME} not found.")

        if not hasattr(foo, FIG_FNAME):
            setattr(foo, FIG_FNAME, lambda fig, data: None)
            log.warning(f"Function {FIG_FNAME} not found.")

        return foo

    def check_for_file_change():
        new_date = except_exec(file_modified_date, file_path)
        return modified_date != new_date, new_date

    def check_for_data_change():
        new_data_code = except_exec(inspect.getsource, getattr(module, DATA_FNAME))
        return data_code != new_data_code, new_data_code

    def check_for_settings_change():
        new_settings_code = except_exec(inspect.getsource, getattr(module, SETTINGS_FNAME))
        return settings_code != new_settings_code, new_settings_code

    def check_for_fig_change():
        new_fig_code = except_exec(inspect.getsource, getattr(module, FIG_FNAME))
        return fig_code != new_fig_code, new_fig_code

    plt.show(block=False)
    while True:
        has_file_changed, modified_date = check_for_file_change()
        if has_file_changed:
            module = load_module()

            data_loading_has_changed, data_code = check_for_data_change()
            if data_loading_has_changed:
                data = except_exec(getattr(module, DATA_FNAME))
                print("Liveplot: reloaded data", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            settings_has_changed, settings_code = check_for_settings_change()
            if settings_has_changed:
                except_exec(getattr(module, SETTINGS_FNAME), plt)
                fig.canvas.mpl_disconnect(cid)
                plt.close(fig)
                fig = plt.figure()
                cid = fig.canvas.mpl_connect("close_event", lambda event: sys.exit())
                plt.show(block=False)
                print("Liveplot: reloaded settings", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


            update_fig_has_changed, fig_code = check_for_fig_change()
            if data_loading_has_changed or settings_has_changed or update_fig_has_changed:
                fig.clear()
                interactive_elements = except_exec(getattr(module, FIG_FNAME), fig, data)
                plt.draw()
                print("Liveplot: reloaded figure", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        plt.pause(1)
