import os
from typing import Any, Dict, Sequence, Literal
import uuid

from arango import ArangoClient

from python_arango_ogm.db.pao_db_base import PAODBBase
from python_arango_ogm.db.pao_model_discovery import PAOModelDiscovery
from python_arango_ogm.db.pao_queries import PAOQueries
from python_arango_ogm.db.pao_migration_model import PAOMigrationModel
from python_arango_ogm.utils.logger import logging
from python_arango_ogm.utils.singleton import Singleton


class PAODatabase(PAODBBase):
    __metaclass__ = Singleton
    VALID_SORT_VALUES = ["ASC", "DESC", ""]

    def __init__(self, delete_db: bool = False):
        # TODO: These probably don't need to be members:
        print("CONSTRUCTING DB")
        self.app_db_name = os.getenv('PAO_APP_DB_NAME')
        host = os.getenv('PAO_DB_HOST', 'localhost')
        port = os.getenv('PAO_DB_PORT', 8529)
        protocol = os.getenv('PAO_DB_PROTOCOL', 'http')
        root_user = os.getenv('PAO_DB_ROOT_USER')
        root_password = os.getenv('PAO_DB_ROOT_PASS')

        if self.app_db_name is None:
            raise ValueError("PAO_APP_DB_NAME needs to be defined in environment or in a .env file.")

        if root_user is None:
            raise ValueError("PAO_DB_ROOT_USER needs to be defined in environment or in a .env file.")

        if root_password is None:
            raise ValueError('PAO_DB_ROOT_PASS needs to be defined in environment or in a .env file.')

        self.client = ArangoClient(hosts=f"{protocol}://{host}:{port}")

        # Connect to "_system" database as root user.
        # This returns an API wrapper for "_system" database.
        # logging.debug(f"Connecting to system DB with {root_user}:{root_password}...")
        self.sys_db = self.client.db('_system', username=root_user, password=root_password)

        self.db = None

        # Create a new database if it does not exist.
        self.setup_app_database(delete_db)

    def setup_app_database(self, delete_db):
        """
        Setup app databases; deleting if specified by delete_db
        This is called by constructor, but since this based on a
        Singleton metaclass, it might neccesary to call it manually
        after migrations have been appplied and whatnot.
        """
        app_user = os.getenv('PAO_APP_DB_USER', 'root')
        app_pass = os.getenv('PAO_APP_DB_PASS')

        if app_pass is None:
            raise ValueError('PAO_APP_DB_PASS needs to be defined in environment or in a .env file.')

        create_db = True
        if self.sys_db.has_database(self.app_db_name):
            if delete_db:
                self.sys_db.delete_database(self.app_db_name, ignore_missing=True)
            else:
                create_db = False
        if create_db:
            was_created = self.sys_db.create_database(self.app_db_name, [{
                'username': app_user,
                'password': app_pass,
                'active': True,
            }])
            if not was_created:
                raise ValueError(f"Database {self.app_db_name} was not created.")

        self.db = self.client.db(self.app_db_name, username=app_user, password=app_pass)
        self.inject_into_models()

    def inject_into_models(self):
        """ Inject database into models, as PAODatabase is where the functionality is implemented."""
        discoverer = PAOModelDiscovery()
        model_hash: Dict[str, any] = discoverer.discover()
        for m, model in model_hash.items():
            logging.debug(f"Injecting DB into model {m}")
            model.db = self

        # Inject into built-in models:
        PAOMigrationModel.db = self

    def get_db(self):
        """ Return underlying python-arango database"""
        return self.db

    def find_by_key(self, collection_name: str, key: Any):
        """
          Find document on collection by given key value:
        """
        return self.db.collection(collection_name).get(key)

    def get_related_edges(self, collection_name: str, association_collection_name: str, lookup_key_dict: Dict):
        """
        Gets `association_collection_name` edges of `collection_name`;
        looking up by the keys and values in `lookup_key_dict`:
        """
        lookup_filter = self._format_lookup_filter(lookup_key_dict)
        aql = PAOQueries.AQL_QUERY_RELATED_EDGES.format(lookup_filter=lookup_filter)
        edge_collection_name = f"{collection_name}__{association_collection_name}"
        logging.debug(f"Association query on [{collection_name}]->[{edge_collection_name}] [aql]")
        cursor = self.db.aql.execute(aql, count=True, batch_size=10, bind_vars={
            '@collection': collection_name,
            '@edge_collection': edge_collection_name
        })

        return self._cursor_doc_generator(cursor)

    def get_related_vertices(self, collection_name: str, association_collection_name: str, lookup_key_dict: Dict):
        """
        Lookup associated vertices (`association_collection_name`) through edges,
        from given collection_name, using keys and values in lookup_key_dict:
        """
        lookup_filter = self._format_lookup_filter(lookup_key_dict)
        aql = PAOQueries.AQL_QUERY_RELATED_VERTICES.format(lookup_filter=lookup_filter)
        edge_collection_name = f"{collection_name}__{association_collection_name}"
        logging.debug(f"Association query on [{collection_name}]->[{edge_collection_name}] [aql]")
        cursor = self.db.aql.execute(aql, count=True, batch_size=10, bind_vars={
            '@collection': collection_name,
            '@edge_collection': edge_collection_name,
            '@association_collection': association_collection_name
        })

        return self._cursor_doc_generator(cursor)

    def find_by_attributes(self, collection_name: str, lookup_key_dict: Dict = None):
        """
        Find a single document by given collection_name,
        looking up by the keys and values in lookup_key_dict:
        """
        docs = self.get_by_attributes(collection_name, lookup_key_dict)
        try:
            result = docs.__next__()
        except StopIteration:
            result = None

        return result

    def remove_by_key(self, collection_name: str, key: str):
        """ Remove a document identified by `key` from collection """
        lookup_filter = self._format_lookup_filter({"_key": key})
        aql = PAOQueries.AQL_REMOVE_BY_ATTRS.format(lookup_filter=lookup_filter)

        logging.debug(f"REMOVE query: [{aql}]")
        cursor = self.db.aql.execute(aql, count=True, bind_vars={'@collection': collection_name})
        return self._cursor_doc_generator(cursor)

    def get_by_attributes(
            self,
            collection_name: str,
            lookup_key_dict: Dict[str, Any] = None,
            sort_key_dict: Dict[str, Literal['ASC', 'DESC', '']] = None
    ):
        """
        Gets documents from given collection_name, looking up by the keys and values
        in lookup_key_dict, sorting by keys and direction

        :param lookup_key_dict: A dictionary of keys and corresponding values used to query this collection values
        (ASC, DESC): :param sort_key_dict: A dictionary of keys by which to sort documents.  Values specify
        direction: [ASC, DESC, '']
        """
        logging.debug(f"LOOKUP:{lookup_key_dict} and SORT:{sort_key_dict}")
        lookup_filter = self._format_lookup_filter(lookup_key_dict)
        sort_by = self._format_sort(sort_key_dict)
        aql = PAOQueries.AQL_QUERY_BY_ATTRS.format(lookup_filter=lookup_filter, sort_by=sort_by)
        logging.debug(f"LOOKUP query: {aql}")
        cursor = self.db.aql.execute(aql, count=True, bind_vars={'@collection': collection_name})
        return self._cursor_doc_generator(cursor)

    def insert_edge(self, collection_name: str, association_collection_name: str, from_key, to_key):
        """
          Insert edge document using keys (_from and _to are generated using collection name).
          Collection inferred from collection_name and association_collection_name.
          TODO: Add attributes to set on edge
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
        print(f"Inserting into collection {collection_name}: ", doc)
        new_doc = self.__autogen_keys(collection_name, doc)
        insert_attrs = self._format_query_attrs(new_doc)
        aql = PAOQueries.AQL_INSERT_DOC.format(insert_attrs=insert_attrs)
        logging.debug(f"INSERT QUERY: {aql}: {insert_attrs}")
        inserted_docs = self.db.aql.execute(aql, count=True, bind_vars={'@collection': collection_name})
        logging.debug(f"inserted_docs: {inserted_docs.count()}")
        if not inserted_docs.count():
            raise RuntimeError(f"Error: collection_name document {doc} was not inserted.")

        return inserted_docs.next()

    def insert_docs(self, collection_name: str, docs: Sequence[dict[str, Any]]):
        """ Insert given documents into collection with a single query"""
        new_docs = [self.__autogen_keys(collection_name, doc) for doc in docs]
        new_docs = [self.__format_query_values(doc) for doc in new_docs]
        cursor = self.db.aql.execute(PAOQueries.AQL_INSERT_DOCS, bind_vars={
            '@collection': collection_name,
            'docs': new_docs
        })

        return self._cursor_doc_generator(cursor)

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
        update_attrs = self._format_query_attrs(update_doc)  # str(update_attrs)[1:-1]

        logging.debug(f"key_attrs: {key_attrs}")
        logging.debug(f"insert_attrs: {insert_attrs}")
        logging.debug(f"update_attrs: {update_attrs}")

        upsert = PAOQueries.AQL_UPSERT_DOC.format(
            key_attrs=key_attrs,
            insert_attrs=insert_attrs,
            update_attrs=update_attrs)

        logging.debug(f"UPSERT QUERY: {upsert}")
        upserted_docs = self.db.aql.execute(upsert, count=True, bind_vars={'@collection': collection_name})
        logging.debug(f"upserted_docs: {upserted_docs.count()}")
        if not upserted_docs.count():
            raise RuntimeError(f"Error: collection_name document {doc} was not upserted.")

        return upserted_docs.next()

    def _format_sort(self, sort_list: Dict[str, str]) -> str:
        """
          Format a lookup filter from keys and values in lookup_key_dict
          Returns string in format "doc.active == true AND doc.gender == 'f'"
        """
        result = ''
        if sort_list and len(sort_list):
            sorts = []
            for k, v in sort_list.items():
                if v not in self.VALID_SORT_VALUES:
                    raise ValueError(f"Sort value for {k} is should be one of {self.VALID_SORT_VALUES}")
                sorts.append(f"doc.{k} {v}")

            sort_by = " ,".join(sorts)
            result = f"SORT {sort_by}" if sort_by else ""
        return result

    def _format_lookup_filter(self, lookup_key_dict: Dict):
        """
          Format a lookup filter from keys and values in lookup_key_dict
          Returns string in format "doc.active == true AND doc.gender == 'f'"
        """
        result = ''
        if lookup_key_dict and len(lookup_key_dict) > 0:
            attrs = {f"doc.{k} == {self.__format_query_value(v)}" for (k, v) in lookup_key_dict.items()}
            filter_by = " AND ".join(attrs)
            result = f"FILTER {filter_by}" if filter_by else ""
        return result

    def _format_query_attrs(self, doc: Dict) -> str:
        """
          Format keys and values for query, allowing for literals.
          Returns a string with format:
            'key1':'val1', 'key2':'val2", 'key3': literal_expression...
        """
        attrs = {f"'{k}': {self.__format_query_value(v)}" for (k, v) in doc.items()}
        return ", ".join(attrs)

    @staticmethod
    def _cursor_doc_generator(cursor):
        while True:
            # batch_items = cursor.batch()
            # logging.debug(f"batch_items", batch_items)
            for doc in cursor.batch():
                yield doc
            if not cursor.has_more():
                break
            cursor.next()

    def __format_query_values(self, doc: Dict[str, Any]):
        return {k: self.__format_query_value(v) for k, v in doc.items()}

    @staticmethod
    def __format_query_value(value: Any):
        """ Format value, allowing for literals """
        if isinstance(value, str):
            if value.startswith('`') and value.endswith('`'):
                # Literal, no quotes:
                query_expression = value.replace('`', '')
            else:
                # Non-literal; quote it:
                query_expression = f"'{value}'"
        else:
            query_expression = value

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
