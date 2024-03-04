from python_arango_ogm.db import pao_model


class PAOMigrationModel(pao_model.PAOModel):
    """ Built-in migration to track migrations. """
    LEVEL = pao_model.LevelEnum.STRICT
    ADDITIONAL_PROPERTIES = False
    SCHEMA_NAME = "pao_migrations"

    migration_number = pao_model.IntField(index_name='migration_number_idx', unique=True, required=True)
    migration_name = pao_model.StrField(index_name='migration_name_idx', required=True)
    migration_filename = pao_model.StrField(index_name='migration_filename_idx', required=True)
    created_at = pao_model.FloatField(required=True)
    updated_at = pao_model.FloatField(required=True)
