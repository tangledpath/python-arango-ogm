import os
from typing import Any, Dict, Sequence
import uuid

from arango import ArangoClient

from python_arango_ogm.db.pao_queries import PAOQueries


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

    def find_by_id(self, collection_name: str, key: Any):
        """
          Find document on collection by given key value:
        """
        return self.db.collection(collection_name).get(key)

    def get_doc_associations(self, collection_name: str, association_collection_name: str, lookup_key_dict: Dict):
        """
          Gets document associations (association_collection_name) from given collection_name,
          looking up by the keys and values in lookup_key_dict:
        """
        lookup_filter = self._format_lookup_filter(lookup_key_dict)
        aql = PAOQueries.AQL_QUERY_RELATED.format(lookup_filter=lookup_filter)
        edge_collection_name = f"{collection_name}__{association_collection_name}"
        print("Association query", aql, collection_name, association_collection_name, edge_collection_name)
        return self.db.aql.execute(aql, count=True, batch_size=10, bind_vars={
            '@collection': collection_name,
            '@edge_collection': edge_collection_name,
            '@association_collection': association_collection_name
        })

    def _format_lookup_filter(self, lookup_key_dict: Dict):
        """
          Format a lookup filter from keys and values in lookup_key_dict
          Returns string in format "doc.active == true AND doc.gender == 'f'"
        """
        attrs = {f"doc.{k} == {self._format_query_value(str(v))}" for (k, v) in lookup_key_dict.items()}
        return " AND ".join(attrs)

    def find_by_attributes(self, collection_name: str, lookup_key_dict: Dict):
        """
          Find a single document by given collection_name,
          looking up by the keys and values in lookup_key_dict:
        """
        docs = self.get_by_attributes(collection_name, lookup_key_dict)
        result = None
        if docs.count():
            result = docs.next()

        return result

    def get_by_attributes(self, collection_name: str, lookup_key_dict: Dict):
        """
          Gets document associations (association_collection_name) from given collection_name,
          looking up by the keys and values in lookup_key_dict:
        """
        print("lookuip key dict", lookup_key_dict)
        lookup_filter = self._format_lookup_filter(lookup_key_dict)
        aql = PAOQueries.AQL_QUERY_BY_ATTRS.format(lookup_filter=lookup_filter)
        print("LOOKUP query", aql)
        return self.db.aql.execute(aql, count=True, bind_vars={'@collection': collection_name})

    def insert_edge(self, collection_name: str, association_collection_name: str, from_key, to_key):
        """
          Insert edge document using keys (_from and _to are generated using collection name).
          Collection inferred from collection_name and association_collection_name.
        """
        edge_collection_name = f"{collection_name}__{association_collection_name}"
        doc = {
            "_from": f"{collection_name}/{from_key}",
            "_to": f"{association_collection_name}/{to_key}"
        }
        return self.insert_doc(edge_collection_name, doc)

    def insert_doc(self, collection_name: str, doc: Dict):
        """
          Insert a new doc in collection:
        """
        new_doc = self.__autogen_keys(collection_name, doc)
        insert_attrs = self._format_query_attrs(new_doc)
        aql = PAOQueries.AQL_INSERT_DOC.format(insert_attrs=insert_attrs)
        print("INSERT QUERY", aql)
        inserted_docs = self.db.aql.execute(aql, count=True, bind_vars={'@collection': collection_name})
        print("inserted_docs", inserted_docs)
        if not inserted_docs.count():
            raise RuntimeError(f"Error: collection_name document {doc} was not inserted.")

        return inserted_docs.next()

    def upsert_doc(
            self,
            collection_name: str,
            doc: Dict,
            lookup_keys: Sequence[str] = None,
            insert_dict=None,
            update_dict=None
    ):
        """
          Upsert a doc in collection using given lookup_keys
          collection_name: Name of DB collection
          doc:Dict: Document containing keys and values to insert and update
          lookup_keys: Sequence of keys to lookup document to update
          insert_dict: Dictionary of values to insert only
          update_dict: Dictionary of values to update only
        """
        if update_dict is None:
            update_dict = {}
        if insert_dict is None:
            insert_dict = {}
        lookup_key_dict = {k: v for (k, v) in doc.items() if k in lookup_keys}

        new_doc = self.__autogen_keys(collection_name, doc)
        new_doc.update(insert_dict)
        update_doc = {k: v for (k, v) in doc.items() if k not in lookup_keys}
        update_doc.update(update_dict)

        # Create key:val pairs (dictionary without braces):
        key_attrs = self._format_query_attrs(lookup_key_dict)  # str(lookup_key_dict)[1:-1]
        insert_attrs = self._format_query_attrs(new_doc)  # str(new_doc)[1:-1]
        update_attrs = self._format_query_attrs(update_doc)  # str(update_doc)[1:-1]

        print(f"key_attrs: {key_attrs}")
        print(f"insert_attrs: {insert_attrs}")
        print(f"update_attrs: {update_attrs}")

        upsert = PAOQueries.AQL_UPSERT_DOC.format(
            key_attrs=key_attrs,
            insert_attrs=insert_attrs,
            update_attrs=update_attrs)

        print("UPSERT QUERY", upsert)
        upserted_docs = self.db.aql.execute(upsert, count=True, bind_vars={'@collection': collection_name})
        print("upserted_docs", upserted_docs)
        if not upserted_docs.count():
            raise RuntimeError(f"Error: collection_name document {doc} was not upserted.")

        return upserted_docs.next()

    def _format_query_attrs(self, doc: Dict) -> str:
        """
          Format keys and values for query, allowing for literals.
          Returns a string with format:
            'key1':'val1', 'key2':'val2", 'key3': literal_expression...
        """
        attrs = {f"'{k}': {self._format_query_value(str(v))}" for (k, v) in doc.items()}
        return ", ".join(attrs)

    @staticmethod
    def _format_query_value(value: str):
        """ Format value, allowing for literals """
        if value.startswith('`') and value.endswith('`'):
            # Literal, no quotes:
            query_expression = value.replace('`', '')
        else:
            # Non-literal; quote it:
            query_expression = f"'{value}'"

        return query_expression

    def __autogen_keys(self, collection_name: str, doc: dict):
        """ Autogenerate key & id using UUID.  Can probably be changed to a DB function.  """
        new_doc = dict(doc)
        new_doc["_key"] = self.__new_uuid()
        new_doc["_id"] = f"{collection_name}/{new_doc['_key']}"
        return new_doc

    @staticmethod
    def __new_uuid():
        """ Return a new UUID  """
        return str(uuid.uuid1())
