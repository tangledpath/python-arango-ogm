import json
import pathlib
import shutil

from python_arango_ogm.db.pao_migration_builder import PAOMigrationBuilder
from python_arango_ogm.db.pao_database import PAODatabase
from python_arango_ogm.db.pao_migrator import PAOMigrator

from python_arango_ogm.db.tests.models import FooModel, BarModel, BazModel

mig_path = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
print("MIGRATION PATH:", mig_path)


def test_simple_migrator():
    migrator_builder = PAOMigrationBuilder(mig_path)

    try:
        migrator_builder.create_model_migrations()
        pao_database = PAODatabase(delete_db=True)
        pao_database.setup_app_database(delete_db=True)

        pao_migrator = PAOMigrator(pao_database, target_path=mig_path)
        before_count = len(pao_database.db.collections())

        pao_migrator.apply_migrations()
        assert len(pao_database.db.collections()) == before_count + 6
    finally:
        print("Deleting migrations from ", migrator_builder.migration_pathname)
        shutil.rmtree(migrator_builder.migration_pathname)


def test_migrator_idempotency():
    migrator_builder = PAOMigrationBuilder(mig_path)
    try:
        migrator_builder.create_model_migrations()
        pao_database = PAODatabase(delete_db=True)
        pao_database.setup_app_database(delete_db=True)
        pao_migrator = PAOMigrator(pao_database, target_path=mig_path)
        before_count = len(pao_database.db.collections())

        pao_migrator.apply_migrations()
        assert len(pao_database.db.collections()) == before_count + 6

        # Apply again; should not error or result in duplicates:
        pao_migrator.apply_migrations()
        assert len(pao_database.db.collections()) == before_count + 6
        migrations = pao_migrator.list_migrations()
        assert len(migrations) == 5
    finally:
        print("Deleting migrations from ", migrator_builder.migration_pathname)
        shutil.rmtree(migrator_builder.migration_pathname)

def test_migrator_models():
    migrator_builder = PAOMigrationBuilder(mig_path)
    try:
        migrator_builder.create_model_migrations()
        pao_database = PAODatabase(delete_db=True)
        pao_database.setup_app_database(delete_db=True)
        pao_migrator = PAOMigrator(pao_database, target_path=mig_path)
        pao_migrator.apply_migrations()
        foo_model = FooModel()
        # foo_model.bar_edge.
    finally:
        print("Deleting migrations from ", migrator_builder.migration_pathname)
        shutil.rmtree(migrator_builder.migration_pathname)


if __name__ == '__main__':
    test_simple_migrator()
    # test_migrator_idempotency()
