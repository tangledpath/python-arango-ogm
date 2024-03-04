from abc import ABC, abstractmethod
from enum import StrEnum, auto
from typing import Dict


class FieldTypeEnum(StrEnum):
    """
    Field Type Enum, used to specify field type in certain situations:
    """

    ARRAY = auto()
    FLOAT = auto()
    INT = auto()
    STRING = auto()


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
        props = {'type': 'number'}
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
