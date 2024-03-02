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
    def __init__(self, target_path: str = '.', overwrite: bool = False):
        self.target_path = target_path
        self.overwrite = overwrite
        self.models_module_name = os.getenv('PAO_MODELS')
        if not self.models_module_name:
            raise RuntimeError("PAO_MODELS must be defined in the environment (or a .env.test file)")

        p = Path(self.target_path)
        self.mig_path = p.joinpath("migrations")
        if not self.mig_path.exists(follow_symlinks=False):
            self.mig_path.mkdir()

        def get_migration_name(migration_filename:str)->str:
            return migration_filename.split('_', 1)[-1]

        migs = [c.stem for c in self.mig_path.iterdir() if not c.is_dir() and c.suffix == '.py']
        self.existing_migrations = {get_migration_name(m): m for m in sorted(migs)}
        print("self.existing_migrations:", self.existing_migrations)

    def create_model_migrations(self):
        discovery = ModelDiscovery()
        model_hash = discovery.discover()

        graph_edges = []

        mig = self.build_migration(MigrationModel, model_hash)
        self.create_model_migration(0, MigrationModel, mig['mod_schema'], mig['hash_indexes'], mig['other_indexes'])

        for n, mod in enumerate(model_hash.values()):
            mig = self.build_migration(mod, model_hash)
            self.create_model_migration(n+1, mod, mig['mod_schema'], mig['hash_indexes'], mig['other_indexes'])
            graph_edges.extend(mig['graph_edges'])

        # Create migration for graph/edges:
        graph_name = os.getenv('PAO_GRAPH_NAME')
        if graph_name is None:
            raise ValueError("PAO_GRAPH_NAME must be defined in the environment (or a .env file)")

        print("Creating migration for graph: ", graph_edges)
        graph_json = self._fix_python_json(json.dumps(graph_edges, indent=4)[2:-2])
        graph_mig = [f"{graph_name} = db.create_graph('{graph_name}', ["]
        graph_mig.append(str_util.indent(graph_json, 2))
        graph_mig.append(f"{INDENT}])")
        mig_up = "\n".join(graph_mig)
        mig_down = f"db.delete_graph('{graph_name}', ignore_missing=True)"

        filename = f"{len(model_hash):04}_{graph_name}.py"
        filepath = self.mig_path.joinpath(filename)

        mig_text = MIGRATION_FILE_TEMPLATE.format(migration_up=mig_up, migration_down=mig_down)
        with open(filepath, mode="w") as file:
            file.write(mig_text)



        # Determine whether migration already exists
        # and whether we are overwriting.  If not, we
        # will need to use `StandardCollection.configure`
        # to replace the schema in a new migration.
        # Likewise, if there are existing indexes
        # that differ from those specified in the model, they should
        # be removed and re-added

    def create_model_migration(self, num:int, mod:Type, mod_schema:dict, hash_indexes:Sequence, other_indexes:Sequence):
        coll_name = mod.collection_name()


        schema_json = self._fix_python_json(json.dumps(mod_schema, indent=4)[2:-2])
        print("SCHEMA_JSON:", schema_json)
        schema_var = f"{coll_name.upper()}_SCHEMA"
        up_migration = [f"{schema_var}={{"]
        up_migration.append(str_util.indent(schema_json, 2))
        up_migration.append(f"{INDENT}}}")
        coll_var = f"{coll_name}_collection"

        up_migration.append(f"\n{INDENT}{coll_var}=db.create_collection('{coll_name}', {schema_var})")
        down_migration = [f"{coll_var}=db.collections('{coll_name}')"]

        # Index migrations:
        idx_up, idx_down = self.create_index_migrations(coll_var, hash_indexes, other_indexes)
        up_migration.extend(idx_up)
        down_migration.extend(idx_down)

        # Delete whole collection:
        down_migration.append(f"{INDENT}db.delete_collection('{coll_name}', ignore_missing=True)")

        # Format migration stuff:
        mig_up = "\n".join(up_migration)
        mig_down = "\n".join(down_migration)
        mig_text = MIGRATION_FILE_TEMPLATE.format(migration_up=mig_up, migration_down=mig_down)

        # TODO:
        if (not self.overwrite) and (coll_name in self.existing_migrations.keys()):
            # Don't overwrite the migration; add a new one that updates the schema:
            pass

        # Write to file:
        filename = f"{num:04}_{coll_name}.py"
        filepath = self.mig_path.joinpath(filename)
        with open(filepath, mode="w") as file:
            file.write(mig_text)

    def create_index_migrations(self, coll_var, hash_indexes, other_indexes):
        up_migration = []
        down_migration = []
        for hash_index in hash_indexes:
            idx_name = hash_index['name']
            up_migration.append(
                f"{INDENT}{coll_var}.add_hash_index(name='{idx_name}', fields={hash_index['fields']}, unique={hash_index['unique']})")
            down_migration.append(f"{INDENT}{coll_var}.delete_index('{idx_name}')")
        for idx in other_indexes:
            idx_type: model.IndexTypeEnum = idx['index_type']
            idx_name = idx['name']
            if idx_type == model.IndexTypeEnum.INVERTED:
                up_migration.append(f"{INDENT}{coll_var}.add_inverted_index(name='{idx_name}', fields={idx['fields']}")
            elif idx_type == model.IndexTypeEnum.GEO:
                up_migration.append(f"{INDENT}{coll_var}.add_geo_index(name='{idx_name}', fields={idx['fields']}")
            elif idx_type == model.IndexTypeEnum.TTL:
                up_migration.append(
                    f"{INDENT}{coll_var}.add_ttl_index(name='{idx_name}', fields={idx['fields']}, expiry_time={idx['expiry_seconds']}")
            elif idx_type == model.IndexTypeEnum.HASH:
                up_migration.append(
                    f"{INDENT}{coll_var}.add_hash_index(name='{idx_name}', fields={idx['fields']}, unique={idx['unique']})"
                )
            down_migration.append(f"{INDENT}{coll_var}.delete_index('{idx_name}')")
        return up_migration, down_migration

    def build_migration(self, mod, model_hash):
        indexes = [e for e in dir(mod)
                   if isinstance(getattr(mod, e), model.Index)]

        mod_schema, hash_indexes = self.build_schema(mod)
        graph_edges = self.build_edges(mod, model_hash)
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

    def build_schema(self, mod):
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

    def build_edges(self, mod, model_hash):
        graph_edges = []
        edges = [e for e in dir(mod) if isinstance(getattr(mod, e), model.EdgeTo)]
        for e in edges:
            edge: model.Edge = getattr(mod, e)
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
    def _fix_python_json(self, json):
        json_str = json.replace(': true', ': True')
        return json_str.replace(': false', ': False')