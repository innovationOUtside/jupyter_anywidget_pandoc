# jupyter_anywidget_pandoc

Example Jupyter anywidget that will sideload [`georgestagg/pandoc-wasm`](https://github.com/georgestagg/pandoc-wasm) into the browser and support pandoc conversions using it.

For example:

```python
from jupyter_anywidget_pandoc import pandoc_headless

# Load the headless widget
p = pandoc_headless()

# Wait for pandoc wasm to load (blocking;; does not work in JupyterLite)
p.ready()

# Try a conversion
# This is blocking - does not work in JupyterLite
output = p.convert("## Some markdown\nWith *feeling...*")
output
> '<h2 id="some-markdown">Some markdown</h2>\n<p>With <em>feeling…</em></p>'

#Non-blocking
p.base_convert("## Some markdown\nWith *feeling...*")
# When it's ready, collect from:
p.response
> {'status': 'processing'}
> {'status': 'completed', 'output_raw': '<p>Another example</p>'}
```

Use `p.convert_from_file(path, output_format="markdown", timeout=3)` etc. to load from a local file path or a URL. If no `input_format=` is specified, the function will attempt to identify the input file type from a file suffix in the path.

## Installation

```sh
pip install jupyter_anywidget_pandoc
```

or with [uv](https://github.com/astral-sh/uv):

```sh
uv add jupyter_anywidget_pandoc
```

Open `example.ipynb` in JupyterLab, VS Code, for a demo...
