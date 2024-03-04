from python_arango_ogm.db.pao_model_discovery import PAOModelDiscovery
from python_arango_ogm.db.tests.models import FooModel, BarModel
def test_simple_discovery():
    discovery = PAOModelDiscovery()
    models = discovery.discover()

    assert FooModel in models.values()
    assert BarModel in models.values()
