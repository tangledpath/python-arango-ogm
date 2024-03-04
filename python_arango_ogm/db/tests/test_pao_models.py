from python_arango_ogm.db.tests.models import FooModel, BarModel, BazModel
def test_model_basic():
    fields = BarModel.getFields()
    assert("field_str" in fields)
    assert("field_int" in fields)

def test_models_with_named_edge():
    fields = FooModel.getFields()
    assert("field_int" in fields)
    assert("field_str" in fields)
    assert("bar_edge" in fields)

def test_models_with_edge_obj():
    fields = BazModel.getFields()
    assert("field_str" in fields)
    assert("field_int" in fields)
    assert("foo_edge" in fields)
