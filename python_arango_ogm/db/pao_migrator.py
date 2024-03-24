import importlib
import os
from pathlib import Path

import arango
from arango import AQLQueryExecuteError

from python_arango_ogm.db.pao_migration_model import PAOMigrationModel
from python_arango_ogm.db.pao_database import PAODatabase


class PAOMigrator():
    def __init__(self, pao_db:PAODatabase, target_path: str = '.'):
        self.pao_db = pao_db
        self.app_package = os.getenv('PAO_APP_PACKAGE')
        if not self.app_package:
            raise ValueError('PAO_APP_PACKAGE needs to be defined in environment or in a .env file.')
        self.migration_package = self.app_package + '.migrations'

        app_root = self.app_package.replace('.', '/')
        p = Path(target_path).joinpath(app_root)
        self.migration_pathname = p.joinpath("migrations")
        if not self.migration_pathname.exists():
            raise RuntimeError(f"Migration path does not exist: {self.migration_pathname}; please run make-migrations.")


    def list_migrations(self):
        try:
            result = list(PAOMigrationModel.all({"migration_filename": "ASC"}, marshall=False))
        except AQLQueryExecuteError as e:
            result = None
        return result

    def migrate_down(self):
        migrations = self.list_migrations()
        if len(migrations):
            m = migrations[-1]
            migration = importlib.import_module(f"{self.migration_package}.{m['migration_filename']}")
            migration.down(self.pao_db.db)
            PAOMigrationModel.remove_by_key(m['_key'])

    def apply_migrations(self):
        migrations = [f.stem for f in self.migration_pathname.iterdir() if not f.is_dir() and f.suffix == '.py']
        print(f"Applying migrations from {self.migration_pathname}", migrations)
        for m in sorted(migrations):
            try:
                if self.__find_migration_record(m):
                    print(f"Migration already applied; skipping [{m}]")
                    continue
            except arango.exceptions.AQLQueryExecuteError:
                # Collection not there at all:
                print(f"Collection not found for [{m}]...running migration")

            print(f"Applying migration {m}", type(m))
            migration = importlib.import_module(f"{self.migration_package}.{m}")
            # migration = importlib.import_module(m, self.migration_package)
            migration.up(self.pao_db.db)
            self.__create_migration_record(m)

    def __find_migration_record(self, migration_filename):
        return self.pao_db.find_by_attributes("pao_migrations", {
            "migration_filename": migration_filename
        })

    def __create_migration_record(self, migration_filename):
        migration_number, migration_name = migration_filename.split('_', 1)
        PAOMigrationModel.insert({
            "migration_number": f"`{int(migration_number)}`",
            "migration_name": migration_name,
            "migration_filename": migration_filename,
        })
