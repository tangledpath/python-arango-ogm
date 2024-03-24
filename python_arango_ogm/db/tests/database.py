from contextlib import contextmanager
import pathlib
import shutil

from python_arango_ogm.db.pao_migration_builder import PAOMigrationBuilder
from python_arango_ogm.db.pao_database import PAODatabase
from python_arango_ogm.db.pao_migrator import PAOMigrator

mig_path = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
print("MIGRATION PATH:", mig_path)


@contextmanager
def use_database():
    migrator_builder = PAOMigrationBuilder(str(mig_path))
    try:
        migrator_builder.create_model_migrations()
        pao_database = PAODatabase(delete_db=True)
        pao_database.setup_app_database(delete_db=True)

        pao_migrator = PAOMigrator(pao_database, target_path=str(mig_path))
        pao_migrator.apply_migrations()

        yield pao_database

    finally:
        print("Deleting migrations from ", migrator_builder.migration_pathname)
        shutil.rmtree(migrator_builder.migration_pathname)
