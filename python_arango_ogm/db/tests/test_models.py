from python_arango_ogm.db.tests.models import FooModel, BarModel
def test_model_basic():
    fields = FooModel.getFields()
    assert("field_int" in fields)
    assert("field_str" in fields)

def test_models_with_edge():
    fields = BarModel.getFields()
    assert("field_int" in fields)
    assert("field_str" in fields)
    assert("foo_edge" in fields)
