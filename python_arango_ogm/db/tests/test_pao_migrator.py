import pathlib
import shutil

from python_arango_ogm.db.migration_builder import MigrationBuilder
from python_arango_ogm.db.pao_database import PAODatabase
from python_arango_ogm.db.pao_migrator import PAOMigrator

def test_simple_migrator():
    mig_path = pathlib.Path(__file__).parent.resolve()
    migrator_builder = MigrationBuilder(mig_path)

    try:
        migrator_builder.create_model_migrations()
        pao_database = PAODatabase(delete_db=True)
        pao_migrator = PAOMigrator(pao_database, target_path=mig_path)
        before_count = len(pao_database.db.collections())
        pao_migrator.apply_migrations()
        assert len(pao_database.db.collections())==before_count + 6
    finally:
        print("Deleting migrations from ", migrator_builder.migration_pathname)
        shutil.rmtree(migrator_builder.migration_pathname)

def test_migrator_idempotency():
    mig_path = pathlib.Path(__file__).parent.resolve()
    migrator_builder = MigrationBuilder(mig_path)
    try:
        migrator_builder.create_model_migrations()
        pao_database = PAODatabase(delete_db=True)
        pao_migrator = PAOMigrator(pao_database, target_path=mig_path)
        before_count = len(pao_database.db.collections())
        pao_migrator.apply_migrations()

        assert len(pao_database.db.collections())==before_count + 6

        # Apply again; should not error or result in duplicates:
        pao_migrator.apply_migrations()
        assert len(pao_database.db.collections())==before_count + 6
    finally:
        print("Deleting migrations from ", migrator_builder.migration_pathname)
        shutil.rmtree(migrator_builder.migration_pathname)

if __name__ == '__main__':
    test_simple_migrator()

