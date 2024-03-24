from __future__ import annotations

import copy
import sys
from abc import ABC, abstractmethod
from enum import StrEnum, auto
from functools import partialmethod
from typing import Any, Dict, Sequence, Type, Union

from python_arango_ogm.db.pao_edges import PAOEdgeDef
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

    def __init__(self):
        super().__init__()

    @classmethod
    def is_field(cls, attribute_name: str) -> bool:
        attr = getattr(cls, attribute_name)
        return ((not attribute_name.startswith('_')) and
                (issubclass(type(attr), Field) or issubclass(type(attr), PAOEdgeDef)))

    @classmethod
    def all(cls, sort_fields:Dict[str, str], marshall=True) -> str:
        records = cls.db.get_by_attributes(cls.collection_name(), sort_key_dict=sort_fields)
        return cls.marshall_rows(records) if marshall else records

    @classmethod
    def insert(cls, attributes:Dict[str, Any]):
        # TODO: See if we have timestamp fields (created_at, updated_at) and add accordingly
        doc = cls.add_timestamps(attributes, created=True, updated=True)
        return cls.db.insert_doc(cls.collection_name(), doc)
    @classmethod
    def upsert(cls, attributes:Dict[str, Any], insert_attrs:Dict[str, Any], update_attrs:Dict[str, Any]):
        insert_doc = cls.add_timestamps(insert_attrs, created=True, updated=True)
        update_doc = cls.add_timestamps(update_attrs, updated=True)
        return cls.db.upsert_doc(cls.collection_name(), attributes, insert_doc, update_doc)

    @classmethod
    def find_by_key(cls, key, marshall:bool=True) -> Union[Dict[str, Any], Type[PAOModel]]:
        """ Find a single record by given key and return """
        record = cls.db.find_by_key(cls.collection_name(), key)
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
    def get_fields(cls) -> Dict[str, Union[Field, PAOEdgeDef]]:
        model_fields = {f:getattr(cls, f) for f in dir(cls) if cls.is_field(f)}
        return model_fields

    @classmethod
    def get_edge_defs(cls) -> Dict[str, PAOEdgeDef]:
        return {e:getattr(cls, e) for e in dir(cls) if isinstance(getattr(cls, e), PAOEdgeDef)}

    def get_edges(self, edge_def:PAOEdgeDef) -> Sequence[PAOEdgeDef]:
        if not self._key:
            raise AttributeError("_key field is not present (this model instance hasn't been obtained from a marshalling method).")

        return edge_def.associated_edges({"key": self._key})

    def insert_edge(self, edge_def:PAOEdgeDef, to: Union[str, PAOModel]) -> Sequence[PAOEdgeDef]:
        if not self._key:
            raise AttributeError("_key field is not present (this model instance hasn't been obtained from a marshalling method).")

        return edge_def.insert_edge({"from": self._key, "to": to})

    @classmethod
    def collection_name(cls) -> str:
        if cls.SCHEMA_NAME:
            coll_name = cls.SCHEMA_NAME
        else:
            coll_name = str_util.snake_text(cls.__name__.split('Model')[0])
        return coll_name

    @classmethod
    def add_timestamps(cls, field_dict:Dict[str, Any], created:bool=False, updated:bool=False) -> Dict[str, Any]:
        fields = cls.get_fields()
        doc = copy.copy(field_dict)
        if created and 'created_at' in fields:
            doc['created_at'] = '`DATE_NOW()`'
        if updated and 'updated_at' in fields:
            doc['updated_at'] = '`DATE_NOW()`'
        return doc

    @classmethod
    def marshall_row(cls, field_dict:Dict[str, Any]) -> Type[PAOModel]:
        model = PAOModel()
        for k, v in field_dict.items():
            setattr(model, k, v)

        # edge_defs = cls.get_edge_defs()
        # for edge_def in edge_defs.values():
        #     to_model = edge_def.model_class_to()
        #     def edge_accessor(self):
        #         self.get_edges(self.key, edge)
        #
        #     # edge_accessor = partialmethod(get_edges, edge_def=edge_def)
        #
        #     setattr(model, f"{to_model.collection_name()}_edges", edge_accessor)
        return model

    @classmethod
    def marshall_rows(cls, rows:Sequence[Dict[str, Any]]) -> Sequence[Type[PAOModel]]:
        return [cls.marshall_row(row) for row in rows]


