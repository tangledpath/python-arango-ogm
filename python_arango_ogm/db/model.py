from enum import StrEnum, auto
from abc import ABC
from arango import ArangoClient
from typing import Sequence
class FieldTypeEnum(StrEnum):
    """
    Field Type Enum, used to specify field type in certain situations:
    """

    ARRAY = auto()
    FLOAT = auto()
    INT = auto()
    STRING = auto()


class LevelEnum(StrEnum):
    """
    Level Enum, used to specify when schema validation is applied
    """

    NONE = auto()
    NEW = auto()
    MODERATE = auto()
    STRICT = auto()


class _Field:
    def __init__(
            self,
            field_type: FieldTypeEnum,
            index: bool = False,
            unique: bool = False,
            required: bool = False,
    ):
        self.field_type = field_type
        self.index = index
        self.unique = unique
        self.required = required


class FloatField(_Field):
    def __init__(self,
                 index: bool = False,
                 unique: bool = False,
                 required: bool = False, ):
        super().__init__(FieldTypeEnum.INT, index, unique, required)


class IntField(_Field):
    def __init__(self,
                 index: bool = False,
                 unique: bool = False,
                 required: bool = False, ):
        super().__init__(FieldTypeEnum.INT, index, unique, required)


class StrField(_Field):
    def __init__(self,
                 index: bool = False,
                 unique: bool = False,
                 required: bool = False, ):
        super().__init__(FieldTypeEnum.STRING, index, unique, required)


class ArrayField(_Field):
    def __init__(self, array_type: FieldTypeEnum, required: bool = False, maximum=None):
        self.array_type = array_type
        self.maximum = maximum
        super().__init__(FieldTypeEnum.ARRAY, required=required)


class EdgeTo:
    def __init__(self, to_model: ['Model', str]):
        self.to_model = to_model


class Model(ABC):
    def __init__(
            self, level: LevelEnum = LevelEnum.STRICT, user_defined_fields: bool = False
    ):
        self.level = level
        self.name = self.__class__.__name__
        self.user_defined_fields = user_defined_fields
        super().__init__()

    @classmethod
    def is_field(cls, attribute_name: str) -> bool:
        attr = getattr(cls, attribute_name)
        return ((not attribute_name.startswith('_')) and
            (issubclass(type(attr), _Field) or issubclass(type(attr), EdgeTo)))

    @classmethod
    def getFields(cls) -> Sequence:
        model_fields = [f for f in dir(cls) if cls.is_field(f)]
        return model_fields
