from python_arango_ogm.db.model_discovery import ModelDiscovery
from python_arango_ogm.db.tests.models import FooModel, BarModel
def test_simple_discovery():
    discovery = ModelDiscovery()
    models = discovery.discover()

    assert FooModel in models.values()
    assert BarModel in models.values()
