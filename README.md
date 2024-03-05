# Python Arango OGM
Python-based package implementing an OGM (Object Graph Model) framework for arango; built on top of [python-arango]([url](https://github.com/arangodb/python-arango/)).  
**N.B.** This is extracted from a project that uses Arango heavily.  Obviously, with a graph database, you don't want to be tied too closely to an ORM due to the impedance mismatch between models and graph nodes and edges.  Still to do is to marshall query results into models when necessary for that good old model experience.  That will be done in the coming week(s).  

## GitHub
https://github.com/tangledpath/python-arango-ogm

## Documentation
https://tangledpath.github.io/python-arango-ogm/python_arango_ogm.html

## Installation
pip install python-arango-ogm

## Getting started
Create a .env file at the root of your repository with the following keys; values to be adjusted for your application:

### Environment file (or production configuration/secretes):
```
PAO_APP_DB_NAME=your_app
PAO_APP_DB_USER=your_app 
PAO_APP_DB_PASS=<ARANGO_YOUR_APP_PASSWORD>
PAO_APP_PACKAGE=your_app.gdb
PAO_DB_HOST=localhost
PAO_DB_PORT=8529
PAO_DB_ROOT_USER=root
PAO_DB_ROOT_PASS=<ARANGO_ROOT_PASSWORD>
PAO_GRAPH_NAME=your_app
PAO_MODELS=your_app.gdb.models
```

### Initializing the database:
Create an `__init__.py` file in your application's source tree to initialize the database; causing it to inject itself into the models.  PAODatabase is a based on a singleton metaclass:
Modify as necessary:
```python
# Filename = your-app/your_app/gdb
import os
from dotenv import load_dotenv
from python_arango_ogm.db.pao_database import PAODatabase

# This assumes a development environment, you can add other environments; e.g., test.
# Production environments will most likely not use the dotenv:
if os.getenv('YOUR_APP_ENV', 'development') == 'development':
    load_dotenv('.env') # Or '.env.dev', '.env.test', etc....

PAODatabase()
```

In this setup, there should be a `models.py` in the your_app.gdb package.  For example:

```python
from python_arango_ogm.db import pao_fields
from python_arango_ogm.db.pao_edges import PAOEdge
from python_arango_ogm.db.pao_model import PAOModel


class FooModel(PAOModel):
    field_int = pao_fields.IntField(index_name='field_int_idx')
    field_str = pao_fields.StrField(unique=True, index_name='field_str_idx')
    bar_edge = PAOEdge("FooModel", "BarModel")


class BarModel(PAOModel):
    field_int = pao_fields.IntField(index_name='field_int_idx', required=True)
    field_str = pao_fields.StrField(unique=True, index_name='field_str_idx')


class BazModel(PAOModel):
    field_int = pao_fields.IntField(index_name='field_int_idx', unique=True, required=True)
    field_str = pao_fields.StrField(index_name='field_str_idx')
    foo_edge = PAOEdge("BazModel", FooModel)
```

## Usage:
### pao-migrate CLI
* Make uncreated migrations for models: `pao-migrate make-migrations`
* Migrate the database: `pao-migrate migrate`
* Remove and Migrate the database: `pao-migrate migrate --clean`
* List migrations: `pao-migrate list-migrations`
* Rollback last migration: `pao-migrate migrate-rollback`
* Create a blank migration: `pao-migrate new-migration <MIGRATION_NAME>`
* To see help `pao-migrate --help`
* To see help for a specific command, for example: `pao-migrate migrate --help`

### In code
You may use your models to perform various queries and commands
**TODO**: document this more

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
