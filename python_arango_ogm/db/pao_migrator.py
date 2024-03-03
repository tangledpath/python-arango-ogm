import importlib
import os
from pathlib import Path

import arango

from python_arango_ogm.db.pao_database import PAODatabase


class PAOMigrator():
    def __init__(self, pao_db:PAODatabase, target_path: str = '.'):
        self.pao_db = pao_db
        p = Path(target_path)
        self.app_package = os.getenv('PAO_APP_PACKAGE')
        if not self.app_package:
            raise ValueError('PAO_APP_PACKAGE needs to be defined in environment or in a .env file.')
        self.migration_package = self.app_package + '.migrations'

        print("TARGETPATH", target_path)
        self.migration_pathname = p.joinpath("migrations")


    def find_migration_record(self, migration_filename):
        return self.pao_db.find_by_attributes("pao_migrations", {
            "migration_filename": migration_filename
        })

    def create_migration_record(self, migration_filename):
        migration_number, migration_name = migration_filename.split('_', 1)
        self.pao_db.insert_doc("pao_migrations", {
            "migration_number": migration_number,
            "migration_name": migration_name,
            "migration_filename": migration_filename,
        })

    def apply_migrations(self):
        migrations = [f.stem for f in self.migration_pathname.iterdir() if not f.is_dir() and f.suffix == '.py']
        print(f"Applying migrations from {self.migration_pathname}", migrations)
        for m in sorted(migrations):
            try:
                if self.find_migration_record(m):
                    print(f"Migration already applied; skipping [m]")
                    continue
            except arango.exceptions.AQLQueryExecuteError:
                # Collection not there at all:
                print(f"Collection not found for [m]...adding.")

            print(f"Applying migration {m}", type(m))
            migration = importlib.import_module(f"{self.migration_package}.{m}")
            # migration = importlib.import_module(m, self.migration_package)
            migration.up(self.pao_db.db)
            self.create_migration_record(m)
