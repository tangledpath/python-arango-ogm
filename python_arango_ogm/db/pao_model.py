from abc import ABC, abstractmethod
from enum import StrEnum, auto
from typing import Any, Dict, Sequence, Union
import sys

from python_arango_ogm.db.pao_edges import PAOEdge
from python_arango_ogm.db.pao_fields import Field
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
    db:PAODBBase = None # (or TODO:interface)

    def __init__(self):
        super().__init__()

    @classmethod
    def is_field(cls, attribute_name: str) -> bool:
        attr = getattr(cls, attribute_name)
        return ((not attribute_name.startswith('_')) and
                (issubclass(type(attr), Field) or issubclass(type(attr), PAOEdge)))

    @classmethod
    def all(cls, sort_fields:Dict[str, str]) -> str:
        return cls.db.get_by_attributes(cls.collection_name(), sort_key_dict=sort_fields)

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
    def marshall(cls, field_dict:Dict[str, Any]) -> "PAOModel":
        model = PAOModel()
        for key, value in field_dict.items():
            setattr(model, key, value)
        return model

