from enum import StrEnum, auto
from abc import ABC, abstractmethod
from typing import Sequence, Dict


class FieldTypeEnum(StrEnum):
    """
    Field Type Enum, used to specify field type in certain situations:
    """

    ARRAY = auto()
    FLOAT = auto()
    INT = auto()
    STRING = auto()


class IndexEnum(StrEnum):
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
            index: bool = False,
            required: bool = False,
            unique: bool = False,
            minimum: float = None,
            maximum: float = None
    ):
        self.field_type = field_type
        self.index = index
        self.unique = unique
        self.required = required
        self.minimum = minimum
        self.maximum = maximum

    @abstractmethod
    def build_schema_property(self) -> Dict[str, any]:
        pass


class FloatField(Field):
    def __init__(self,
                 index: bool = False,
                 required: bool = False,
                 unique: bool = False,
                 minimum: float = None,
                 maximum: float = None):
        super().__init__(FieldTypeEnum.FLOAT, index=index, unique=unique, required=required, minimum=minimum,
                         maximum=maximum)

    def build_schema_property(self) -> Dict[str, any]:
        return {'type': 'number', 'minimum': self.minimum, 'maximum': self.maximum}


class IntField(Field):
    def __init__(self,
                 index: bool = False,
                 unique: bool = False,
                 required: bool = False,
                 minimum=None,
                 maximum=None):
        super().__init__(FieldTypeEnum.INT, index=index, unique=unique, required=required, minimum=minimum,
                         maximum=maximum)

    def build_schema_property(self) -> Dict[str, any]:
        return {'type': 'number', 'multipleOf': 1, 'minimum': self.minimum, 'maximum': self.maximum}


class StrField(Field):
    def __init__(self,
                 index: bool = False,
                 unique: bool = False,
                 required: bool = False,
                 minimum=None,
                 maximum=None):
        super().__init__(FieldTypeEnum.STRING, index=index, unique=unique, required=required, minimum=minimum,
                         maximum=maximum)

    def build_schema_property(self) -> Dict[str, any]:
        return {'type': 'string', 'minimum': self.minimum, 'maximum': self.maximum}


class ArrayField(Field):
    def __init__(self, array_type: FieldTypeEnum, required: bool = False, minimum=None, maximum=None):
        self.array_type = array_type
        self.minimum = minimum
        self.maximum = maximum
        super().__init__(FieldTypeEnum.ARRAY, required=required)

    def build_schema_property(self) -> Dict[str, any]:
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
    def __init__(self, to_model: ['Model', str]):
        self.to_model = to_model


class Index:
    def __init__(self, fields: [str], index_type: IndexEnum, name=None, expiry_seconds=None):
        self.fields = fields
        self.index_type = index_type
        self.name = name
        self.expiry_seconds = expiry_seconds

        if index_type == IndexEnum.INVERTED and len(fields) < 2:
            raise ValueError('INVERTED indexes must have at least 2 fields')
        elif index_type == IndexEnum.TTL and expiry_seconds is None:
            raise ValueError('TTL indexes must also have expiry seconds')


class Model(ABC):
    LEVEL = LevelEnum.STRICT
    ADDITIONAL_PROPERTIES = False
    SCHEMA_NAME = None

    def __init__(self):
        super().__init__()

    @classmethod
    def is_field(cls, attribute_name: str) -> bool:
        attr = getattr(cls, attribute_name)
        return ((not attribute_name.startswith('_')) and
                (issubclass(type(attr), Field) or issubclass(type(attr), EdgeTo)))

    @classmethod
    def getFields(cls) -> Sequence:
        model_fields = [f for f in dir(cls) if cls.is_field(f)]
        return model_fields
