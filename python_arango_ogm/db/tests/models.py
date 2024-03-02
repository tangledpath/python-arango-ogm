from python_arango_ogm.db import model


class FooModel(model.Model):
    field_int = model.IntField(index_name='field_int_idx')
    field_str = model.StrField(unique=True, index_name='field_str_idx')
    bar_edge = model.EdgeTo("BarModel")

class BarModel(model.Model):
    field_int = model.IntField(index_name='field_int_idx', required=True)
    field_str = model.StrField(unique=True, index_name='field_str_idx')

class BazModel(model.Model):
    field_int = model.IntField(index_name='field_int_idx', unique=True, required=True)
    field_str = model.StrField(index_name='field_str_idx')
    foo_edge = model.EdgeTo(FooModel)
