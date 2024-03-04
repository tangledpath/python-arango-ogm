from enum import StrEnum, auto
from typing import Union, Sequence


class IndexTypeEnum(StrEnum):
    """
    Field Type Enum, used to specify field type in certain situations:
    """
    HASH = auto()
    INVERTED = auto()
    GEO = auto()
    TTL = auto()


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
