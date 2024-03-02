import typer
from datetime import datetime
from python_arango_ogm.db.migration_builder import MigrationBuilder

app = typer.Typer()

MIGRATION_FILE_TEMPLATE = """
def up(db):
    pass
def down(db):
    pass
"""

@app.command()
def make_migrations():
    """
    Make migrations from models
    """
    migration_builder = MigrationBuilder()
    migration_builder.create_model_migrations()


@app.command()
def new_migration(name: str):
    """
    Make a new migration with a new number prefix and suffix of given name

    @params:
        name is the suffix of the migration
    """
    migration_builder = MigrationBuilder()
    migration_builder.create_blank_migration(name)

@app.command(env=None)
def migrate():
    """ Runs all unapplied migrations """
    # env_filename = f".env.{env}" if env else ".env"
    # load_dotenv(env_filename)


def run():
    app()


run()
if __name__ == "__main__":
    pass
