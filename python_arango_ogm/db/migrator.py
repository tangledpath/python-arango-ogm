from python_arango_ogm.db.model_discovery import ModelDiscovery

from dotenv import load_dotenv
load_dotenv()

class Migrator:
    def __init__(self, target_path: str = '.'):
        self.models_module_name = os.getenv('PAO_MODELS')
        if not self.models_module_name:
            raise RuntimeError("PAO_MODELS must be defined in the environment (or a .env.test file)")

    def create_model_migrations(self, overwrite=False):
        discovery = ModelDiscovery()
        models = discovery.discover()

        for model in models:
            # Determine whether migration already exists
            # and whether we are overwriting.  If not, we
            # will need to use `StandardCollection.configure`
            # to replace the schema in a new migration.
            # Likewise, if there are existing indexes
            # that differ from those specified in the model, they should
            # be removed and re-added

            print(f"Creating migration for model [{model.name}")
