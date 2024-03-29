import json
import os
import site
import sys

import typer
from dotenv import load_dotenv

from python_arango_ogm.db.pao_database import PAODatabase
from python_arango_ogm.db.pao_migration_builder import PAOMigrationBuilder
from python_arango_ogm.db.pao_migrator import PAOMigrator

# print("Setting app root to ", os.getcwd())
app = typer.Typer()


@app.command()
def make_migrations(env_file: str = None):
    """
    Make migrations from models
    """
    app_root = get_app_root()
    load_environment(env_file=env_file)
    migration_builder = PAOMigrationBuilder(app_root)
    migration_builder.create_model_migrations()


@app.command()
def new_migration(name: str, env_file: str = None):
    """
    Make a new migration with a new number prefix and suffix of given name

    @params:
        name is the suffix of the migration
    """
    app_root = get_app_root()
    load_environment(env_file=env_file)
    migration_builder = PAOMigrationBuilder(app_root)
    migration_builder.create_blank_migration(name)


@app.command()
def migrate(clean: bool = False, env_file: str = None):
    """ Runs all unapplied migrations.  If clean is true, database will be deleted first. """
    app_root = get_app_root()
    load_environment(env_file=env_file)
    pao_db = PAODatabase(delete_db=clean)
    migrator = PAOMigrator(pao_db, app_root)
    migrator.apply_migrations()


@app.command()
def migrate_rollback(env_file: str = None):
    """ Runs all unapplied migrations """
    app_root = get_app_root()
    load_environment(env_file=env_file)
    pao_db = PAODatabase()
    migrator = PAOMigrator(pao_db, app_root)
    migrator.migrate_down()


@app.command()
def list_migrations(env_file: str = None):
    """ Runs all unapplied migrations """
    app_root = get_app_root()
    load_environment(env_file=env_file)
    pao_db = PAODatabase()
    migrator = PAOMigrator(pao_db, app_root)
    migrations = migrator.list_migrations()
    print(json.dumps(migrations, indent=4))


def load_environment(env_file):
    """ Load given environment file, if it exists. """
    if env_file:
        load_dotenv(env_file)

def get_app_root():
    app_root = os.getcwd()
    if app_root not in sys.path:
        site.addsitedir(app_root)
    return app_root

def run():
    app()


if __name__ == "__main__":
    run()
