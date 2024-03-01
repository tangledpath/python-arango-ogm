from python_arango_ogm.db.migration_builder import MigrationBuilder
from python_arango_ogm.db.tests.models import FooModel, BarModel


def test_simple_migrator():
    migrator = MigrationBuilder()
    migrator.build_model_migrations()
