# gitwalk

A Python library that provides an os.walk()-compatible interface that respects .gitignore rules. Walk through your directories while automatically excluding paths matched by .gitignore patterns.

## Installation

Using uv:
```bash
uv pip install gitwalk
```

## Usage

```python
from gitwalk import gitwalk as walk

# Walk through directory respecting .gitignore rules
for dirpath, dirnames, filenames in walk("./my_project"):
    print(f"Directory: {dirpath}")
    print(f"Subdirectories: {dirnames}")
    print(f"Files: {filenames}")
```

## Features

- Same interface as `os.walk()`
- Respects `.gitignore` patterns
- Supports both topdown and bottom-up traversal
- Handles error callbacks
- Follows symbolic links (optional)

## Tests
```
uv pip install -e ".[test]"
pytest
```
