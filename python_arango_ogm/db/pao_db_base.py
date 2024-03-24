from abc import ABC, abstractmethod
from typing import Any, Dict, Sequence


class PAODBBase(ABC):
    @abstractmethod
    def setup_app_database(self, delete_db):
        """
        Setup app databases; deleting if specified by delete_db
        This is called by constructor, but since this based on a
        Singleton metaclass, it might neccesary to call it manually
        after migrations have been appplied and whatnot.
        """
        pass

    def get_related_edges(self, collection_name: str, association_collection_name: str, lookup_key_dict: Dict):
        """
        Gets `association_collection_name` edges of `collection_name`;
        looking up by the keys and values in `lookup_key_dict`:
        """
        pass

    @abstractmethod
    def get_related_vertices(self, collection_name: str, association_collection_name: str, lookup_key_dict: Dict):
        """
        Lookup associated vertices (`association_collection_name`) through edges,
        from given collection_name, using keys and values in lookup_key_dict:
        """
        pass

    @abstractmethod
    def inject_into_models(self):
        """ Inject database into models, as PAODatabase is where the functionality is implemented."""
        pass

    @abstractmethod
    def get_db(self):
        """ Return underlying python-arango database"""
        pass

    @abstractmethod
    def find_by_key(self, collection_name: str, key: Any):
        """
          Find document on collection by given key value:
        """
        pass

    @abstractmethod
    def find_by_attributes(self, collection_name: str, lookup_key_dict: Dict = None):
        """
          Find a single document by given collection_name,
          looking up by the keys and values in lookup_key_dict:
        """
        pass

    @abstractmethod
    def remove_by_key(self, collection_name: str, key: str):
        """ Remove a document identified by `key` from collection """
        pass

    @abstractmethod
    def get_by_attributes(
            self,
            collection_name: str,
            lookup_key_dict: Dict = None,
            sort_key_dict: Dict[str, str] = None
    ):
        """
          Gets documents from given collection_name, looking up by the keys and values
          in lookup_key_dict, sorting by keys and direction

          :param collection_name: Name of collection in Graph DB.
          :param lookup_key_dict: A dictionary of keys and corresponding values used to query this collection
          values (ASC, DESC):
          :param sort_key_dict: A dictionary of keys by which to sort documents.  Values specify direction (ASC, DESC, '')
        """
        pass

    @abstractmethod
    def insert_edge(self, collection_name: str, association_collection_name: str, from_key, to_key):
        """
          Insert edge document using keys (_from and _to are generated using collection name).
          Collection inferred from collection_name and association_collection_name.
        """
        pass

    @abstractmethod
    def insert_doc(self, collection_name: str, doc: Dict):
        """
          Insert a new doc in collection:
        """
        pass

    @abstractmethod
    def insert_docs(self, collection_name: str, docs: Sequence[dict[str, Any]]):
        """ Insert given documents into collection with a single query"""
        pass

    @abstractmethod
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
        pass
