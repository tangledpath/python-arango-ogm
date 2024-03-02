import json
import os
from pathlib import Path
from typing import Dict, Sequence, Type

from python_arango_ogm.db.model_discovery import ModelDiscovery
from python_arango_ogm.db import model
from python_arango_ogm.utils import str_util
from python_arango_ogm.db.migration_model import MigrationModel

MIGRATION_FILE_TEMPLATE = """
def up(db):
    {migration_up}
    
def down(db):
    {migration_down}
"""

INDENT = "    "


class MigrationBuilder:
    ADD_HASH_INDEX_STR = "{indent}{coll_var}.add_hash_index(name='{idx_name}', fields={fields}, unique={unique})"
    ADD_TTL_INDEX_STR = "{indent}{coll_var}.add_ttl_index({fields}, name='{idx_name}', expiry_time={expiry_time}"

    def __init__(self, target_path: str = '.', overwrite: bool = False):
        self.target_path = target_path
        self.overwrite = overwrite
        self.models_module_name = os.getenv('PAO_MODELS')
        if not self.models_module_name:
            raise RuntimeError("PAO_MODELS must be defined in the environment (or a .env.test file)")

        p = Path(self.target_path)
        self.mig_pathname = p.joinpath("migrations")
        if not self.mig_pathname.exists(follow_symlinks=False):
            self.mig_pathname.mkdir()

        self._sync_existing_migrations()

    def create_blank_migration(self, name):
        self._sync_existing_migrations()
        mig_filename = self.new_migration_filename(name)
        with open(mig_filename, 'w') as f:
            f.write(MIGRATION_FILE_TEMPLATE.format(migration_up='pass', migration_down='pass'))

    def create_model_migrations(self):
        discovery = ModelDiscovery()
        model_hash: Dict[str, type[model.Model]] = discovery.discover()

        graph_edges = []

        mig = self.build_migration(MigrationModel, model_hash)

        # Special collection to track migrations; should always be first migration:
        if "pao_migrations" not in self.existing_migrations.values():
            self.create_model_migration(MigrationModel, mig['mod_schema'], mig['hash_indexes'], mig['other_indexes'])

        for mod in model_hash.values():
            mig = self.build_migration(mod, model_hash)
            self.create_model_migration(mod, mig['mod_schema'], mig['hash_indexes'], mig['other_indexes'])
            graph_edges.extend(mig['graph_edges'])

        self.create_graph_migration(graph_edges)

    def create_graph_migration(self, graph_edges: []):
        # Create migration for graph/edges:
        graph_name = os.getenv('PAO_GRAPH_NAME')
        if graph_name is None:
            raise ValueError("PAO_GRAPH_NAME must be defined in the environment (or a .env file)")

        print("Creating migration for graph: ", graph_edges)
        delete_graph_str = f"db.delete_graph('{graph_name}', ignore_missing=True)"
        graph_json = self._fix_python_json(json.dumps(graph_edges, indent=4)[2:-2])
        graph_mig = []
        graph_mig.append(delete_graph_str)
        graph_mig.append(f"{INDENT}db.create_graph('{graph_name}', [")
        graph_mig.append(str_util.indent(graph_json, 2))
        graph_mig.append(f"{INDENT}])")

        mig_up = "\n".join(graph_mig)
        mig_down = delete_graph_str
        mig_text = MIGRATION_FILE_TEMPLATE.format(migration_up=mig_up, migration_down=mig_down)

        mig_filename = self.new_migration_filename(graph_name)
        mig_pathname = self.mig_pathname.joinpath(mig_filename)
        with open(mig_pathname, mode="w") as file:
            file.write(mig_text)

        self._sync_existing_migrations()

    def create_model_migration(
            self,
            mod: type[model.Model],
            mod_schema: dict,
            hash_indexes: Sequence,
            other_indexes: Sequence
    ):
        """
            Create migration for given model, schema, hash_indexes and other_indexes
        """
        coll_name = mod.collection_name()
        coll_var = f"{coll_name}_collection"
        up_migration = []
        down_migration = []

        schema_var = self._add_migration_schema_up(coll_name, mod_schema, up_migration)

        mig_filename, updating = self._determine_filename_updating(coll_name)

        if updating:
            up_migration.append(f"\n{INDENT}{coll_var}=db.collections('{coll_name}')")
            up_migration.append(f"{INDENT}{coll_var}.configure(schema={schema_var})")
            up_migration.append(f"{INDENT}{coll_var}_indexes={coll_var}.indexes()")
            up_migration.append(
                f"{INDENT}[{coll_var}.delete_index(idx, ignore_missing=True) for idx in {coll_var}_indexes]")
        else:
            up_migration.append(f"\n{INDENT}{coll_var}=db.create_collection('{coll_name}', {schema_var})")

        down_migration.append(f"{coll_var}=db.collections('{coll_name}')")

        # Index migrations:
        idx_up, idx_down = self.build_index_migrations(coll_var, hash_indexes, other_indexes)
        up_migration.extend(idx_up)
        down_migration.extend(idx_down)

        # Down-migration - Delete whole collection:
        down_migration.append(f"{INDENT}db.delete_collection('{coll_name}', ignore_missing=True)")

        # Format migration stuff:
        mig_up = "\n".join(up_migration)
        mig_down = "\n".join(down_migration)
        mig_text = MIGRATION_FILE_TEMPLATE.format(migration_up=mig_up, migration_down=mig_down)

        # Write to file:
        mig_pathname = self.mig_pathname.joinpath(mig_filename)
        with open(mig_pathname, mode="w") as file:
            file.write(mig_text)
        self._sync_existing_migrations()

    def new_migration_filename(self, name: str):
        """ Return filename for a new migration using given name as suffix """
        print(f"NEW_MIGRATION: [{name}]", len(self.existing_migrations))
        print(self.existing_migrations)
        mig_num = len(self.existing_migrations) + 1
        mig_filename = f"{mig_num:04}_{name}.py"
        return mig_filename

    def build_index_migrations(self, coll_var: str, hash_indexes: Sequence, other_indexes: Sequence):
        """ Build migrations for indexes """
        up_migration = []
        down_migration = []

        # Build indexes defined on Field objects:
        self._build_field_index_migrations(coll_var, hash_indexes, up_migration, down_migration)

        # Build indexes defined as Index objects:
        self._build_other_indexes(coll_var, other_indexes, up_migration, down_migration)

        return up_migration, down_migration

    def _build_other_indexes(
            self,
            coll_var: str,
            other_indexes: Sequence,
            up_migration: Sequence,
            down_migration: Sequence
    ):
        """
        Build indexes defined as Index objects:
        """

        for idx in other_indexes:
            idx_type: model.IndexTypeEnum = idx['index_type']
            idx_name = idx['name']
            if idx_type == model.IndexTypeEnum.INVERTED:
                up_migration.append(f"{INDENT}{coll_var}.add_inverted_index(name='{idx_name}', fields={idx['fields']}")
            elif idx_type == model.IndexTypeEnum.GEO:
                up_migration.append(f"{INDENT}{coll_var}.add_geo_index(name='{idx_name}', fields={idx['fields']}")
            elif idx_type == model.IndexTypeEnum.TTL:
                up_migration.append(self.ADD_TTL_INDEX_STR.format(
                    indent=INDENT,
                    coll_var=coll_var,
                    fields=idx['fields'],
                    idx_name=idx_name,
                    expiry_time=idx['expiry_seconds']
                ))
            elif idx_type == model.IndexTypeEnum.HASH:
                up_migration.append(self.ADD_HASH_INDEX_STR.format(
                    indent=INDENT,
                    coll_var=coll_var,
                    idx_name=idx_name,
                    fields=idx['fields'],
                    unique=idx['unique'],
                ))
            # Add down migration for index:
            down_migration.append(f"{INDENT}{coll_var}.delete_index('{idx_name}')")

    def _build_field_index_migrations(
            self,
            coll_var: str,
            hash_indexes: Sequence,
            up_migration: Sequence,
            down_migration: Sequence
    ):
        """ Build indexes defined on Field objects: """
        for hash_index in hash_indexes:
            idx_name = hash_index['name']
            up_migration.append(
                self.ADD_HASH_INDEX_STR.format(
                    indent=INDENT,
                    coll_var=coll_var,
                    idx_name=idx_name,
                    fields=hash_index['fields'],
                    unique=hash_index['unique'],
                )
            )
            down_migration.append(f"{INDENT}{coll_var}.delete_index('{idx_name}')")

    def build_migration(self, mod: type[model.Model], model_hash: Dict[str, Type]) -> Dict[str, any]:
        indexes = [e for e in dir(mod) if isinstance(getattr(mod, e), model.Index)]

        mod_schema, hash_indexes = self.build_schema(mod)
        graph_edges = self.build_model_edges(mod, model_hash)
        other_indexes = []
        for oi in indexes:
            index: model.Index = getattr(mod, oi)
            other_indexes.append({
                'fields': index.fields,
                'index_type': index.index_type,
                'name': index.name,
                'expiry_seconds': index.expiry_seconds,
                'unique': index.unique,
            })

        return {
            'mod_schema': mod_schema,
            'hash_indexes': hash_indexes,
            'graph_edges': graph_edges,
            'other_indexes': other_indexes
        }

    def build_schema(self, mod: type[model.Model]) -> tuple[Dict, Sequence]:
        required = []
        hash_indexes = []
        properties = {}

        fields = [f for f in dir(mod) if isinstance(getattr(mod, f), model.Field)]

        for f in fields:
            field: model.Field = getattr(mod, f)
            properties[f] = field.build_schema_properties()
            if field.required:
                required.append(f)
            if field.index_name or field.unique:
                hash_indexes.append({'name': field.index_name, 'fields': [f], 'unique': field.unique, })

        mod_schema = dict(
            rule=dict(
                properties=properties,
                additionalProperties=mod.ADDITIONAL_PROPERTIES,
                required=required
            ),
            level=mod.LEVEL,
        )
        return mod_schema, hash_indexes

    def build_model_edges(self, mod: type[model.Model], model_hash: Dict[str, Type]) -> Sequence[Dict]:
        """ Build model edges and return as a list of dictionaries """
        graph_edges = []
        edges = [e for e in dir(mod) if isinstance(getattr(mod, e), model.EdgeTo)]
        for e in edges:
            edge: model.EdgeTo = getattr(mod, e)
            to_model = model_hash[edge.to_model] if isinstance(edge.to_model, str) else edge.to_model
            from_name = mod.collection_name()
            to_name = to_model.collection_name()
            edge_name = f"{from_name}__{to_name}"
            graph_edges.append({
                'edge_collection': edge_name,
                'from_vertex_collections': [from_name],
                'to_vertex_collections': [to_name]
            })
        return graph_edges

    def _determine_filename_updating(self, coll_name: str) -> tuple[str, bool]:
        # Determine whether migration already exists
        # and whether we are overwriting.  If not, we
        # to replace the schema in a new migration.
        # Likewise, if there are existing indexes
        # that differ from those specified in the model, they should
        # be removed and re-added

        existing_mig_filename = self._find_existing_migration(coll_name, suffix=".py")
        updating = False
        if (self.overwrite):
            mig_filename = existing_mig_filename or self.new_migration_filename(coll_name)
        else:
            # Don't overwrite the migration; add a new one that updates the schema:
            print(f"NOT OVERWRITE: [{coll_name}]")
            mig_filename = self.new_migration_filename(coll_name)
            updating = existing_mig_filename is not None

        return mig_filename, updating

    def _add_migration_schema_up(self, coll_name: str, mod_schema: dict, up_migration: Sequence) -> str:
        schema_json = self._fix_python_json(json.dumps(mod_schema, indent=4)[2:-2])
        print("SCHEMA_JSON:", schema_json)
        schema_var = f"{coll_name.upper()}_SCHEMA"
        up_migration.append(f"{schema_var}={{")
        up_migration.append(str_util.indent(schema_json, 2))
        up_migration.append(f"{INDENT}}}")
        return schema_var

    def _fix_python_json(self, json_str: str):
        json_str = json_str.replace(': true', ': True')
        return json_str.replace(': false', ': False')

    def _sync_existing_migrations(self):
        """ Synchronize self.existing_migrations with migrations on disk """

        def get_migration_name(migration_filename: str) -> str:
            return migration_filename.split('_', 1)[-1]

        migs = [c.stem for c in self.mig_pathname.iterdir() if not c.is_dir() and c.suffix == '.py']
        self.existing_migrations = {m: get_migration_name(m) for m in sorted(migs)}
        print("self.existing_migrations:", self.existing_migrations)

    def _find_existing_migration(self, collection_name: str, suffix:str=None):
        """ Find existing migration based on collection name """

        try:
            idx = list(self.existing_migrations.values()).index(collection_name)
        except ValueError:
            mig_name = None
        else:
            mig_name = list(self.existing_migrations.keys())[idx] + suffix
        return mig_name
