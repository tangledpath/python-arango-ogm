import pathlib

from python_arango_ogm.db.migration_builder import MigrationBuilder
from python_arango_ogm.db.tests.models import FooModel, BarModel


def test_simple_migrator():
    mig_path = pathlib.Path(__file__).parent.resolve()
    migrator = MigrationBuilder(mig_path)
    migrator.create_model_migrations()
