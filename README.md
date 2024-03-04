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
```
PAO_MODELS=yourapp.db.models
PAO_GRAPH_NAME=yourapp
PAO_APP_DB_NAME=yourapp
PAO_DB_HOST=localhost
PAO_DB_PORT=8529
PAO_DB_ROOT_USER=root
PAO_DB_ROOT_PASS=<ARANGO_ROOT_PASSWORD>
PAO_APP_DB_USER=yourapp 
PAO_APP_DB_PASS=<ARANGO_yourapp_PASSWORD>
PAO_APP_PACKAGE=yourapp.db
```

In this setup, there should be a `models.py` in the yourapp.db package.  For example:

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
