import sys
from typing import Dict, Any, Union, Sequence


class PAOEdge:
    def __init__(self, from_model: ["python_arango_ogm.db.pao_model.PAOModel", str], to_model: ["python_arango_ogm.db.pao_model.PAOModel", str]):
        self.from_model = from_model
        self.to_model = to_model
        if self.to_model is None:
            raise ValueError("PAOEdge to_model cannot be None")

    def associated_edges(self, lookup_key_dict: Dict[str, Any] = None) -> Sequence["PAOEdge"]:
        from_model = self.get_model_class(self.to_model, self.from_model)
        to_model = self.get_model_class(self.to_model, self.from_model)
        from_collection_name = from_model.collection_name()
        to_collection_name = to_model.collection_name()
        from_model.db.get_edge_associations(from_collection_name, to_collection_name, lookup_key_dict)
        # TODO: Marshall and return

    def associated_docs(self, lookup_key_dict: Dict[str, Any]) -> Sequence["python_arango_ogm.db.pao_model.PAOModel"]:
        from_model = self.get_model_class(self.to_model, self.from_model)
        to_model = self.get_model_class(self.to_model, self.from_model)
        from_collection_name = from_model.collection_name()
        to_collection_name = to_model.collection_name()
        from_model.db.get_doc_associations(from_collection_name, to_collection_name, lookup_key_dict)
        # TODO: Marshall and return

    @staticmethod
    def get_model_class(cls, model: Union[str, "python_arango_ogm.db.pao_model.PAOModel"]) -> "python_arango_ogm.db.pao_model.PAOModel":
        if isinstance(model, str):
            module = sys.modules[__name__]
            result = getattr(module, model)
        else:
            result = model
        return result
