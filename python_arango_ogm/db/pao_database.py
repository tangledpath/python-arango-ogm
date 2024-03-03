import os
from arango import ArangoClient


class PAODatabase:
    def __init__(self, delete_db: bool = False):
        # TODO: These probably don't need to be members:
        self.db_name = os.getenv('PAO_DB_NAME')
        self.host = os.getenv('PAO_DB_HOST', 'localhost')
        self.port = os.getenv('PAO_DB_PORT', 8529)
        self.protocol = os.getenv('PAO_DB_PROTOCOL', 'http')
        self.root_user = os.getenv('PAO_DB_ROOT_USER')
        root_password = os.getenv('PAO_DB_ROOT_PASS')
        self.username = os.getenv('PAO_DB_USER', 'root')
        password = os.getenv('PAO_DB_PASS')

        if self.db_name is None:
            raise ValueError("PAO_DB_NAME needs to be defined in environment or in a .env file.")

        if self.root_user is None:
            raise ValueError("PAO_DB_ROOT_USER needs to be defined in environment or in a .env file.")

        if root_password is None:
            raise ValueError('PAO_DB_ROOT_PASS needs to be defined in environment or in a .env file.')

        if password is None:
            raise ValueError('PAO_DB_PASS needs to be defined in environment or in a .env file.')

        self.client = ArangoClient(hosts=f"{self.protocol}://{self.host}:{self.port}")

        # Connect to "_system" database as root user.
        # This returns an API wrapper for "_system" database.
        print(f"Connecting to system DB with {self.root_user}:{root_password}...")
        sys_db = self.client.db('_system', username=self.root_user, password=root_password)

        # Create a new database named "test" if it does not exist.
        create_db = True
        if sys_db.has_database(self.db_name):
            if delete_db:
                sys_db.delete_database(self.db_name, ignore_missing=True)
            else:
                create_db = False
        if create_db:
            was_created = sys_db.create_database(self.db_name, [{
                'username': self.username,
                'password': password,
                'active': True,
            }])
            if not was_created:
                raise ValueError(f"Database {self.db_name} was not created.")

        self.db = self.client.db(self.db_name, username=self.username, password=password)

    def get_db(self):
        return self.db
