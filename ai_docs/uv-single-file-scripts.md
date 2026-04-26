> Source: https://docs.astral.sh/uv/guides/scripts/
> Snapshot: 2026-04-25
> Local cache for Claude Code agent reference. Re-fetch when behavior changes.

# Running Scripts with uv

uv runs single-file Python scripts with optional inline dependencies declared via [PEP 723](https://peps.python.org/pep-0723/) metadata. This is the preferred pattern for hook scripts, slash command helpers, and one-off automation: the script self-bootstraps its own venv, so there's nothing to install ahead of time.

## Running a Script Without Dependencies

Execute scripts without external packages using `uv run`:

```bash
$ uv run example.py
Hello world
```

Scripts using only the standard library also work:

```python
import os

print(os.path.expanduser("~"))
```

```bash
$ uv run example.py
/Users/astral
```

Pass arguments to scripts:

```python
import sys

print(" ".join(sys.argv[1:]))
```

```bash
$ uv run example.py hello world!
hello world!
```

Read scripts from stdin:

```bash
$ echo 'print("hello world!")' | uv run -
```

Or use here-documents:

```bash
uv run - <<EOF
print("hello world!")
EOF
```

When working in a project directory with `pyproject.toml`, use `--no-project` to skip installing the current project:

```bash
$ uv run --no-project example.py
```

## Running a Script With Dependencies

### Using the `--with` Option

Request dependencies per invocation with `--with`:

```bash
$ uv run --with rich example.py
```

Add version constraints:

```bash
$ uv run --with 'rich>12,<13' example.py
```

Specify multiple dependencies by repeating `--with`:

```bash
$ uv run --with requests --with rich example.py
```

## Declaring Script Dependencies with PEP 723 Inline Metadata

Create scripts with inline metadata using `uv init --script`:

```bash
$ uv init --script example.py --python 3.12
```

### Adding Dependencies to Scripts

Use `uv add --script` to declare dependencies within the script:

```bash
$ uv add --script example.py 'requests<3' 'rich'
```

This generates a metadata block at the script's top:

```python
# /// script
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

import requests
from rich.pretty import pprint

resp = requests.get("https://peps.python.org/api/peps.json")
data = resp.json()
pprint([(k, v["title"]) for k, v in data.items()][:10])
```

Run the script with `uv run`:

```bash
$ uv run example.py
```

### Specifying Python Versions

Declare required Python versions in the metadata block:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

type Point = tuple[float, float]
print(Point)
```

The `dependencies` field is required even if empty. uv will search for and use the required Python version, downloading it if needed.

## Using Shebangs for Executable Scripts

Create executable scripts with a shebang line:

```bash
#!/usr/bin/env -S uv run --script

print("Hello, world!")
```

Make the file executable:

```bash
$ chmod +x greet
$ ./greet
Hello, world!
```

Shebangs support inline metadata:

```bash
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx"]
# ///

import httpx

print(httpx.get("https://example.com"))
```

## Using Alternative Package Indexes

Specify alternative package indexes with `--index`:

```bash
$ uv add --index "https://example.com/simple" --script example.py 'requests<3' 'rich'
```

This adds index configuration to the metadata:

```python
# [[tool.uv.index]]
# url = "https://example.com/simple"
```

For authenticated indexes, refer to the package index documentation.

## Locking Dependencies

Lock dependencies for scripts explicitly using `uv lock --script`:

```bash
$ uv lock --script example.py
```

This creates an adjacent `.lock` file (e.g., `example.py.lock`). Subsequently, commands like `uv run --script`, `uv add --script`, and `uv export --script` reuse locked dependencies.

## Improving Reproducibility

Include an `exclude-newer` field in the `tool.uv` section to limit uv to distributions released before a specific date:

```python
# /// script
# dependencies = [
#   "requests",
# ]
# [tool.uv]
# exclude-newer = "2023-10-16T00:00:00Z"
# ///

import requests

print(requests.__version__)
```

Use RFC 3339 timestamp format (e.g., `2006-12-02T02:07:43Z`).

## Using Different Python Versions

Override Python versions per invocation:

```bash
$ uv run --python 3.10 example.py
3.10.15
```

## Using GUI Scripts

On Windows, scripts with `.pyw` extension run using `pythonw`:

```python
from tkinter import Tk, ttk

root = Tk()
root.title("uv")
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="Hello World").grid(column=0, row=0)
root.mainloop()
```

```bash
PS> uv run example.pyw
```

GUI scripts support dependencies:

```python
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout

app = QApplication(sys.argv)
widget = QWidget()
grid = QGridLayout()

text_label = QLabel()
text_label.setText("Hello World!")
grid.addWidget(text_label)

widget.setLayout(grid)
widget.setGeometry(100, 100, 200, 50)
widget.setWindowTitle("uv")
widget.show()
sys.exit(app.exec_())
```

```bash
PS> uv run --with PyQt5 example_pyqt.pyw
```
