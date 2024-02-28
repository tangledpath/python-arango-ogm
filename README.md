# Python Arango ORM
Python-based package implementing an ORM framework for arango; built on top of python-arango.

## Installation
pip install python-arango-orm

## GitHub

## Documentation


## Usage
TODO:

## Development
### Linting
```bash
   ruff check . # Find linting errors
   ruff check . --fix # Auto-fix linting errors (where possible)
```

### Documentation
```
  # Shows in browser
  poetry run pdoc python_arango_ogm
  # Generates to ./docs
  poetry run pdoc python_arango_ogm -o ./docs
```

### Testing
```bash
  clear; pytest
```

### Building and Publishing
#### Building
`poetry build`
#### Publishing
Note: `--build` flag build before publishing
`poetry publish --build -u __token__ -p $PYPI_TOKEN`
