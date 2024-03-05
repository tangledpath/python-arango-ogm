from abc import ABC, abstractmethod
from enum import StrEnum, auto
from typing import Any, Dict, Sequence, Union
import sys

from python_arango_ogm.db.pao_edges import PAOEdge
from python_arango_ogm.db.pao_fields import Field, FloatField
from python_arango_ogm.utils import str_util
from python_arango_ogm.db.pao_db_base import PAODBBase

class LevelEnum(StrEnum):
    """
    Level Enum, used to specify when schema validation is applied
    """

    NONE = auto()
    NEW = auto()
    MODERATE = auto()
    STRICT = auto()

class PAOModel(ABC):
    LEVEL = LevelEnum.STRICT
    ADDITIONAL_PROPERTIES = False
    SCHEMA_NAME = None
    db:PAODBBase = None

    created_at = FloatField(required=True)
    updated_at = FloatField(required=True)


    def __init__(self):
        super().__init__()

    @classmethod
    def is_field(cls, attribute_name: str) -> bool:
        attr = getattr(cls, attribute_name)
        return ((not attribute_name.startswith('_')) and
                (issubclass(type(attr), Field) or issubclass(type(attr), PAOEdge)))

    @classmethod
    def all(cls, sort_fields:Dict[str, str], marshall=True) -> str:
        records = cls.db.get_by_attributes(cls.collection_name(), sort_key_dict=sort_fields)
        return cls.marshall_rows(records) if marshall else records

    @classmethod
    def insert(cls, attributes:Dict[str, Any]):
        cls.db.insert_doc(cls.collection_name(), attributes)
    @classmethod
    def find_by_key(cls, key, marshall:bool=True) -> Union[Dict[str, Any], "PAOModel"]:
        """ Find a single record by given key and return """
        record = cls.db.find_by_attributes(cls.collection_name(), {'_key': key})
        return cls.marshall_row(record) if marshall and record else record

    @classmethod
    def find_by_attributes(cls, attributes:Dict[str, Any], marshall:bool=True):
        """ Find a single record by given attributes and return """
        records = cls.db.find_by_attributes(cls.collection_name(), {'_key': key})
        return cls.marshall_rows(records) if marshall else records
    @classmethod
    def get_by_attributes(cls, attributes:Dict[str, Any], sort_keys: Dict[str, str], marshall:bool=True):
        """ Find records by given attributes, sorting by sort_keys and return """
        cls.db.get_by_attributes(cls.collection_name(), {'_key': key})

    @classmethod
    def remove_by_key(cls, key):
        cls.db.remove_by_key(cls.collection_name(), key)

    @classmethod
    def getFields(cls) -> Sequence:
        model_fields = [f for f in dir(cls) if cls.is_field(f)]
        return model_fields

    @classmethod
    def getEdges(cls):
        return [e for e in dir(cls) if isinstance(getattr(cls, e), PAOEdge)]

    @classmethod
    def collection_name(cls) -> str:
        if cls.SCHEMA_NAME:
            coll_name = cls.SCHEMA_NAME
        else:
            coll_name = str_util.snake_text(cls.__name__.split('PAOModel')[0])
        return coll_name

    @classmethod
    def marshall_row(cls, field_dict:Dict[str, Any]) -> "PAOModel":
        model = PAOModel()
        for key, value in field_dict.items():
            setattr(model, key, value)
        return model

    @classmethod
    def marshall_rows(cls, rows:Sequence[Dict[str, Any]]) -> Sequence["PAOModel"]:
        return [cls.marshall_row(row) for row in rows]


