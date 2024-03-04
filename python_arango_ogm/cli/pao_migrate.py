import json
import os
import site
import sys

from dotenv import load_dotenv
import typer

from python_arango_ogm.db.pao_migration_builder import PAOMigrationBuilder
from python_arango_ogm.db.pao_database import PAODatabase
from python_arango_ogm.db.pao_migrator import PAOMigrator

print("LOADING DOTENV FROM ", os.getcwd())
app_root = os.getcwd()
load_dotenv(f"{app_root}/.env")
if app_root not in sys.path:
    site.addsitedir(app_root)

app = typer.Typer()

@app.command()
def make_migrations():
    """
    Make migrations from models
    """
    migration_builder = PAOMigrationBuilder(app_root)
    migration_builder.create_model_migrations()

@app.command()
def new_migration(name: str):
    """
    Make a new migration with a new number prefix and suffix of given name

    @params:
        name is the suffix of the migration
    """
    migration_builder = PAOMigrationBuilder(app_root)
    migration_builder.create_blank_migration(name)


@app.command()
def migrate(clean:bool=False):
    """ Runs all unapplied migrations.  If clean is true, database will be deleted first. """
    pao_db = PAODatabase(delete_db=clean)
    migrator = PAOMigrator(pao_db, app_root)
    migrator.apply_migrations()

@app.command()
def migrate_rollback():
    """ Runs all unapplied migrations """
    pao_db = PAODatabase()
    migrator = PAOMigrator(pao_db, app_root)
    migrator.migrate_down()


@app.command()
def list_migrations():
    """ Runs all unapplied migrations """
    pao_db = PAODatabase()
    migrator = PAOMigrator(pao_db, app_root)
    migrations = migrator.list_migrations()
    print(json.dumps(migrations, indent=4))

def run():
    app()

if __name__ == "__main__":
    run()

