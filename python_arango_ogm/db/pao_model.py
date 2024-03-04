from enum import StrEnum, auto
from abc import ABC, abstractmethod
from typing import Dict, Sequence, Union

from python_arango_ogm.utils import str_util
class FieldTypeEnum(StrEnum):
    """
    Field Type Enum, used to specify field type in certain situations:
    """

    ARRAY = auto()
    FLOAT = auto()
    INT = auto()
    STRING = auto()


class IndexTypeEnum(StrEnum):
    """
    Field Type Enum, used to specify field type in certain situations:
    """
    HASH = auto()
    INVERTED = auto()
    GEO = auto()
    TTL = auto()


class LevelEnum(StrEnum):
    """
    Level Enum, used to specify when schema validation is applied
    """

    NONE = auto()
    NEW = auto()
    MODERATE = auto()
    STRICT = auto()


class Field(ABC):
    def __init__(
            self,
            field_type: FieldTypeEnum,
            index_name: str = None,
            required: bool = False,
            unique: bool = False,
            minimum: float = None,
            maximum: float = None
    ):
        if unique and not index_name:
            raise ValueError(f"unique attribute requires an index_name for field {self.__class__.__name__}")
        self.field_type = field_type
        self.index_name = index_name
        self.unique = unique
        self.required = required
        self.minimum = minimum
        self.maximum = maximum

    @abstractmethod
    def build_schema_properties(self) -> Dict[str, any]:
        pass


class FloatField(Field):
    def __init__(self,
                 index_name: str = None,
                 required: bool = False,
                 unique: bool = False,
                 minimum: float = None,
                 maximum: float = None):
        super().__init__(FieldTypeEnum.FLOAT, index_name=index_name, unique=unique, required=required, minimum=minimum,
                         maximum=maximum)

    def build_schema_properties(self) -> Dict[str, any]:
        props= {'type': 'number'}
        if self.minimum is not None:
            props['minimum'] = self.minimum

        if self.maximum is not None:
            props['maximum'] = self.maximum
        return props

class IntField(Field):
    def __init__(self,
                 index_name: str = None,
                 unique: bool = False,
                 required: bool = False,
                 minimum=None,
                 maximum=None):
        super().__init__(FieldTypeEnum.INT, index_name=index_name, unique=unique, required=required, minimum=minimum,
                         maximum=maximum)

    def build_schema_properties(self) -> Dict[str, any]:
        props = {'type': 'number', 'multipleOf': 1}
        if self.minimum is not None:
            props['minimum'] = self.minimum

        if self.maximum is not None:
            props['maximum'] = self.maximum

        return props


class StrField(Field):
    def __init__(self,
                 index_name: str = None,
                 unique: bool = False,
                 required: bool = False,
                 minimum=None,
                 maximum=None):
        super().__init__(FieldTypeEnum.STRING, index_name=index_name, unique=unique, required=required, minimum=minimum,
                         maximum=maximum)

    def build_schema_properties(self) -> Dict[str, any]:
        props = {'type': 'string'}
        if self.minimum is not None:
            props['minimum'] = self.minimum

        if self.maximum is not None:
            props['maximum'] = self.maximum

        return props


class ArrayField(Field):
    def __init__(self, array_type: FieldTypeEnum, required: bool = False, minimum=None, maximum=None):
        self.array_type = array_type
        self.minimum = minimum
        self.maximum = maximum
        super().__init__(FieldTypeEnum.ARRAY, required=required)

    def build_schema_properties(self) -> Dict[str, any]:
        inner_field_type = 'number' if self.array_type in [FieldTypeEnum.INT, FieldTypeEnum.FLOAT] else 'string'

        schema = {
            'type': 'array',
            'items': {
                'type': inner_field_type
            }
        }

        if self.minimum is not None:
            schema['items']['minimum'] = self.minimum

        if self.maximum is not None:
            schema['items']['maximum'] = self.maximum

        return schema


class EdgeTo:
    def __init__(self, to_model: ['PAOModel', str]):
        self.to_model = to_model


class Index:
    def __init__(self, fields: Union[Sequence[str], dict[str: any]], index_type: IndexTypeEnum, name, unique=False, expiry_seconds=None):
        self.fields = fields
        self.index_type = index_type
        self.name = name
        self.expiry_seconds = expiry_seconds
        self.unique = unique
        if index_type == IndexTypeEnum.INVERTED and (len(fields) < 2 or not isinstance(fields, dict)):
            raise ValueError('INVERTED indexes must have at least 2 fields in a dictinoary.')
        elif index_type == IndexTypeEnum.TTL and expiry_seconds is None:
            raise ValueError('TTL indexes must also have expiry seconds')


class PAOModel(ABC):
    LEVEL = LevelEnum.STRICT
    ADDITIONAL_PROPERTIES = False
    SCHEMA_NAME = None
    db = None # :PAODatabase (or TODO:interface)

    def __init__(self):
        super().__init__()

    @classmethod
    def is_field(cls, attribute_name: str) -> bool:
        attr = getattr(cls, attribute_name)
        return ((not attribute_name.startswith('_')) and
                (issubclass(type(attr), Field) or issubclass(type(attr), EdgeTo)))

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
    def collection_name(cls) -> str:
        if cls.SCHEMA_NAME:
            coll_name = cls.SCHEMA_NAME
        else:
            coll_name = str_util.snake_text(cls.__name__.split('PAOModel')[0])
        return coll_name
