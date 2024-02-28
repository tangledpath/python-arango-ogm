import typer
from datetime import datetime

app = typer.Typer()

MIGRATION_FILE_TEMPLATE = """
def up(db):
    pass
def down(db):
    pass
"""

@app.command()
def make_migration(name:str):
    """
    Make a new migration named using `name` as a suffix,
    with a prefix of the current time.

    @params:
        name is the suffix of the migration
    """
    date_str = datetime.now().strftime('%Y%m%d%H%M%s')
    mig_name = f"{date_str}_{name}"
    with open(f"./migrations/{mig_name}.py", 'w') as mig_file:
        mig_file.write(MIGRATION_FILE_TEMPLATE)

@app.command()
def migrate():
    """ Runs all unapplied migrations """
    print(f"Hello")

def run():
    app()

if __name__ == "__main__":
    run()
