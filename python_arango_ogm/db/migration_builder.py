import json
import os
from pathlib import Path
from dotenv import load_dotenv

from python_arango_ogm.db.model_discovery import ModelDiscovery
from python_arango_ogm.db import model
from python_arango_ogm.utils import str_util

load_dotenv()


class MigrationBuilder:
    def __init__(self, target_path: str = '.'):
        self.target_path = target_path
        self.models_module_name = os.getenv('PAO_MODELS')
        if not self.models_module_name:
            raise RuntimeError("PAO_MODELS must be defined in the environment (or a .env.test file)")

        p = Path(self.target_path)
        self.mig_path = p.joinpath("migrations")
        if not self.mig_path.exists(follow_symlinks=False):
            self.mig_path.mkdir()

        self.existing_migrations = [c.stem() for c in self.mig_path.iterdir() if not c.is_dir() and c.suffix == '.py']

    def build_model_migrations(self, overwrite=False):
        discovery = ModelDiscovery()
        models = discovery.discover()

        for n, mod in enumerate(models):
            self.build_migration(mod)

        # Determine whether migration already exists
        # and whether we are overwriting.  If not, we
        # will need to use `StandardCollection.configure`
        # to replace the schema in a new migration.
        # Likewise, if there are existing indexes
        # that differ from those specified in the model, they should
        # be removed and re-added

    def build_migration(self, mod, pluralize=str_util.pluralize):
        fields = [f for f in dir(mod)
                  if isinstance(getattr(mod, f), model.Field)]
        edges = [e for e in dir(mod)
                 if isinstance(getattr(mod, e), model.EdgeTo)]
        other_indexes = [e for e in dir(mod)
                         if isinstance(getattr(mod, e), model.Index)]
        properties = {}
        required = []
        hash_indexes = []
        for f in fields:
            field: model.Field = getattr(mod, f)
            properties[f] = field.build_schema_property()
            if field.required:
                required.append(f)
            if field.index or field.unique:
                hash_indexes.append({'fields': [f], 'unique': field.unique, })
        mod_schema = dict(
            rule=dict(
                properties=properties,
                additionalProperties=mod.ADDITIONAL_PROPERTIES,
                required=required
            ),
            level=mod.LEVEL,
        )

        mod_name = mod.__name__.split('Model')[0]
        schema_name = mod.SCHEMA_NAME if mod.SCHEMA_NAME else str_util.snake_text(mod_name)
        schema_json = json.dumps(mod_schema, indent=4)
        print(f"{schema_name.upper()}_SCHEMA={schema_json}")
