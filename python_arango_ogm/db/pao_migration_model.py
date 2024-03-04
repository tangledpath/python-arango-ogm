from python_arango_ogm.db import pao_fields
from python_arango_ogm.db.pao_model import PAOModel, LevelEnum


class PAOMigrationModel(PAOModel):
    """ Built-in migration to track migrations. """
    LEVEL = LevelEnum.STRICT
    ADDITIONAL_PROPERTIES = False
    SCHEMA_NAME = "pao_migrations"

    migration_number = pao_fields.IntField(index_name='migration_number_idx', unique=True, required=True)
    migration_name = pao_fields.StrField(index_name='migration_name_idx', required=True)
    migration_filename = pao_fields.StrField(index_name='migration_filename_idx', required=True)
    created_at = pao_fields.FloatField(required=True)
    updated_at = pao_fields.FloatField(required=True)
