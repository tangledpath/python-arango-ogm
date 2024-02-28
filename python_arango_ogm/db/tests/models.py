from python_arango_ogm.db import model


class FooModel(model.Model):
    field_int = model.IntField(index=True)
    field_str = model.IntField(unique=True)


class BarModel(model.Model):
    field_int = model.IntField(index=True)
    field_str = model.IntField(unique=True)
    foo_edge = model.EdgeTo(FooModel)
