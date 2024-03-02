import pathlib
import shutil

from python_arango_ogm.db.migration_builder import MigrationBuilder

def test_simple_migrator():
    mig_path = pathlib.Path(__file__).parent.resolve()
    migrator = MigrationBuilder(mig_path)

    try:
        migrator.create_model_migrations()
        assert len(migrator.existing_migrations)==5

        # Check that no new migrations were created:
        migrator.create_model_migrations()
        assert len(migrator.existing_migrations)==5
    finally:
        print("Deleting migrations from ", migrator.migration_pathname)
        shutil.rmtree(migrator.migration_pathname)


