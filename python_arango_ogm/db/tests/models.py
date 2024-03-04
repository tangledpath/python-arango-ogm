from python_arango_ogm.db import pao_model


class FooModel(pao_model.PAOModel):
    field_int = pao_model.IntField(index_name='field_int_idx')
    field_str = pao_model.StrField(unique=True, index_name='field_str_idx')
    bar_edge = pao_model.EdgeTo("BarModel")

class BarModel(pao_model.PAOModel):
    field_int = pao_model.IntField(index_name='field_int_idx', required=True)
    field_str = pao_model.StrField(unique=True, index_name='field_str_idx')

class BazModel(pao_model.PAOModel):
    field_int = pao_model.IntField(index_name='field_int_idx', unique=True, required=True)
    field_str = pao_model.StrField(index_name='field_str_idx')
    foo_edge = pao_model.EdgeTo(FooModel)
