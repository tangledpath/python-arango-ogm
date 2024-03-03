from python_arango_ogm.db import model


class MigrationModel(model.Model):
    """ Built-in migration to track migrations. """
    LEVEL = model.LevelEnum.STRICT
    ADDITIONAL_PROPERTIES = False
    SCHEMA_NAME = "pao_migrations"

    migration_number = model.IntField(index_name='migration_number_idx', unique=True, required=True)
    migration_name = model.StrField(index_name='migration_name_idx', required=True)
    migration_filename = model.StrField(index_name='migration_filename_idx', required=True)
    created_at = model.FloatField(required=True)
    updated_at = model.FloatField(required=True)
