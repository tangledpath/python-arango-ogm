from python_arango_ogm.db.tests.database import use_database
from python_arango_ogm.db.tests.models import FooModel, BarModel, BazModel


def test_model_basic():
    fields = BarModel.get_fields()
    assert ("field_str" in fields)
    assert ("field_int" in fields)


def test_models_with_named_edge():
    fields = FooModel.get_fields()
    assert ("field_int" in fields)
    assert ("field_str" in fields)
    assert ("bar_edge" in fields)


def test_models_with_edge_obj():
    fields = BazModel.get_fields()
    assert ("field_str" in fields)
    assert ("field_int" in fields)
    assert ("foo_edge" in fields)


def test_model_marshalling():
    with use_database() as db:
        for i in range(10):
            FooModel.insert({"field_str": f"foo_{i}", "field_int": i})
            BarModel.insert({"field_str": f"bar_{i}", "field_int": i})

        foos = FooModel.all(sort_fields={"field_str": "ASC"})
        print("FOOS:", foos)
        assert len(foos) == 10


if __name__ == '__main__':
    test_model_marshalling()
    # test_migrator_idempotency()
