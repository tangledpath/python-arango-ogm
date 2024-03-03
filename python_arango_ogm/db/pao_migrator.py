import importlib
import os
from pathlib import Path

from python_arango_ogm.db.pao_database import PAODatabase


class PAOMigrator():
    def __init__(self, pao_db:PAODatabase, target_path: str = '.'):
        self.pao_db = pao_db
        p = Path(target_path)
        self.app_package = os.getenv('PAO_APP_PACKAGE')
        if not self.app_package:
            raise ValueError('PAO_APP_PACKAGE needs to be defined in environment or in a .env file.')
        self.migration_package = self.app_package + '.migrations'

        print("TARGERPATH", target_path)
        self.migration_pathname = p.joinpath("migrations")


    def apply_migrations(self):
        migrations = [f.stem for f in self.migration_pathname.iterdir() if not f.is_dir() and f.suffix == '.py']
        print(f"Applying migrations from {self.migration_pathname}", migrations)
        for m in sorted(migrations):
            print(f"Applying migration {m}")
            migration = importlib.import_module(f"{self.migration_package}.{m}")
            # migration = importlib.import_module(m, self.migration_package)
            migration.up(self.pao_db.db)
