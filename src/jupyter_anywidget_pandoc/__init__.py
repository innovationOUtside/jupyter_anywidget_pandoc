import importlib.metadata
import pathlib

import anywidget
import traitlets
import time
import warnings

from IPython.display import display

try:
    __version__ = importlib.metadata.version("jupyter_anywidget_pandoc")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

try:
    from jupyter_ui_poll import ui_events
except:
    warnings.warn(
        "You must install jupyter_ui_poll if you want to return cell responses / blocking waits (not JupyerLite); install necessary packages then restart the notebook kernel:%pip install jupyter_ui_poll",
        UserWarning,
    )

class Widget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "widget.js"
    _css = pathlib.Path(__file__).parent / "static" / "widget.css"
    value = traitlets.Int(0).tag(sync=True)


class pandocWidget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "pandoc.js"
    _css = pathlib.Path(__file__).parent / "static" / "pandoc.css"

    headless = traitlets.Bool(False).tag(sync=True)
    doc_content = traitlets.Unicode("").tag(sync=True)
    output_raw = traitlets.Unicode("").tag(sync=True)
    input_format = traitlets.Unicode("").tag(sync=True)
    output_format = traitlets.Unicode("").tag(sync=True)
    about = traitlets.Dict().tag(sync=True)
    response = traitlets.Dict().tag(sync=True)

    def __init__(self, headless=False, **kwargs):
        super().__init__(**kwargs)
        self.headless = headless
        self.response = {"status": "initialising"}

    def _wait(self, timeout, conditions=("status", "completed")):
        start_time = time.time()
        with ui_events() as ui_poll:
            while self.response[conditions[0]] != conditions[1]:
                ui_poll(10)
                if timeout and ((time.time() - start_time) > timeout):
                    raise TimeoutError(
                        "Action not completed within the specified timeout."
                    )
                time.sleep(0.1)
        self.response["time"] = time.time() - start_time
        return

    def ready(self, timeout=5):
        self._wait(timeout, ("status", "ready"))

    # Need to guard this out in JupyterLite (definitely in pyodide)
    def blocking_reply(self, timeout=None):
        self._wait(timeout)
        return self.response

    def set_doc_content(self, value):
        self.response = {"status": "processing"}
        self.doc_content = value

    def set_input_format(self, value):
        self.input_format = value

    def set_output_format(self, value):
        self.output_format = value

    def base_convert(self, input_text, input_format="markdown", output_format="html"):
        self.set_input_format(input_format)
        self.set_output_format(output_format)
        self.set_doc_content(input_text)

    def convert(self, input_text, input_format="markdown", output_format="html", timeout=None):
        self.base_convert(input_text, input_format, output_format)
        self.blocking_reply(timeout)
        return self.output_raw


def pandoc_headless():
    widget_ = pandocWidget(headless=True)
    display(widget_)
    return widget_


def pandoc_inline():
    widget_ = pandocWidget()
    display(widget_)
    return widget_


from .magics import PandocAnywidgetMagic

def load_ipython_extension(ipython):
    ipython.register_magics(PandocAnywidgetMagic)

from .panel import create_panel

# Launch with custom title as: pandoc_panel("Pandoc")
# Use second parameter for anchor
@create_panel
def pandoc_panel(title=None, anchor=None):
    return pandocWidget()
