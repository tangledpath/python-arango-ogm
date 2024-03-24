import pathlib
import shutil

from python_arango_ogm.db.pao_migration_builder import PAOMigrationBuilder

mig_path = pathlib.Path(__file__).parent.parent.parent.parent.resolve()
print("MIGRATION PATH:", mig_path)

def test_simple_migration_builder():
    migrator_builder = PAOMigrationBuilder(mig_path)

    try:
        migrator_builder.create_model_migrations()
        assert len(migrator_builder.existing_migrations)==5

        # Check that no new migrations were created:
        migrator_builder.create_model_migrations()
        assert len(migrator_builder.existing_migrations)==5
    finally:
        print("Deleting migrations from ", migrator_builder.migration_pathname)
        # shutil.rmtree(migrator_builder.migration_pathname)


if __name__ == '__main__':
    test_simple_migration_builder()

