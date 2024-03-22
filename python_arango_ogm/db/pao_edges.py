from __future__ import annotations

import os
import sys
from typing import Dict, Any, Union, Sequence, Type
import python_arango_ogm.db
from python_arango_ogm.db.pao_db_base import PAODBBase


class PAOEdgeDef:
    def __init__(self, from_model: [Type[python_arango_ogm.db.pao_model.PAOModel], str],
                 to_model: [Type[python_arango_ogm.db.pao_model.PAOModel], str]):
        self.from_model = from_model
        self.to_model = to_model
        if self.to_model is None:
            raise ValueError("PAOEdgeDef to_model cannot be None")

    def db(self) -> PAODBBase:
        return self.model_class_from().db

    def insert_edge(
            self,
            _from: [str, python_arango_ogm.db.pao_model.PAOModel],
            _to: Union[str, python_arango_ogm.db.pao_model.PAOModel]
    ):
        pass

    def associated_edges(self, lookup_key_dict: Dict[str, Any] = None) -> Sequence[PAOEdgeDef]:
        from_model_cls = self.model_class_from()
        to_model_cls = self.model_class_to()
        from_collection_name = from_model_cls.collection_name()
        to_collection_name = to_model_cls.collection_name()
        return from_model_cls.db.get_edge_associations(from_collection_name, to_collection_name, lookup_key_dict)

    def associated_vertices(self, lookup_key_dict: Dict[str, Any], marshall=True) -> Sequence[
        Type[python_arango_ogm.db.pao_model.PAOModel]]:
        from_model_cls = self.model_class_from()
        to_model_cls = self.model_class_to()
        from_collection_name = from_model_cls.collection_name()
        to_collection_name = to_model_cls.collection_name()
        vertices = from_model_cls.db.get_related_vertices(from_collection_name, to_collection_name, lookup_key_dict)
        return to_model_cls.marshall_row(vertices, marshall)

    def model_class_from(self) -> Type[python_arango_ogm.db.pao_model.PAOModel]:
        return self.get_model_class(self.from_model)

    def model_class_to(self) -> Type[python_arango_ogm.db.pao_model.PAOModel]:
        return self.get_model_class(self.to_model)

    @staticmethod
    def get_model_class(
            model: Union[str, Type[python_arango_ogm.db.pao_model.PAOModel]]
    ) -> Type[python_arango_ogm.db.pao_model.PAOModel]:
        # Get model class, whether it is defined as an actual class or a model:
        if isinstance(model, str):
            mod_nm = os.getenv('PAO_MODELS')
            module = sys.modules[mod_nm]
            result = getattr(module, model)
        else:
            result = model
        return result
