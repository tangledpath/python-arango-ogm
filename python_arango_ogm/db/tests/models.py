from python_arango_ogm.db import pao_fields
from python_arango_ogm.db.pao_edges import PAOEdgeDef
from python_arango_ogm.db.pao_model import PAOModel


class FooModel(PAOModel):
    field_int = pao_fields.IntField(index_name='field_int_idx')
    field_str = pao_fields.StrField(unique=True, index_name='field_str_idx')
    bar_edge = PAOEdgeDef("FooModel", "BarModel")


class BarModel(PAOModel):
    field_int = pao_fields.IntField(index_name='field_int_idx', required=True)
    field_str = pao_fields.StrField(unique=True, index_name='field_str_idx')


class BazModel(PAOModel):
    field_int = pao_fields.IntField(index_name='field_int_idx', unique=True, required=True)
    field_str = pao_fields.StrField(index_name='field_str_idx')
    foo_edge = PAOEdgeDef("BazModel", FooModel)