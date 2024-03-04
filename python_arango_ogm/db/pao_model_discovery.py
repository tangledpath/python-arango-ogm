import importlib, inspect
import json
import os
from typing import Sequence, Type, Dict

from python_arango_ogm.db.pao_model import PAOModel

class PAOModelDiscovery:
    def __init__(self):
        self.models_module_name = os.getenv('PAO_MODELS')
        if not self.models_module_name:
            raise RuntimeError("PAO_MODELS must be defined in the environment (or a .env.test file)")

    def is_valid_model(self, model: Type) -> bool:
        return (not model is PAOModel) and issubclass(model, PAOModel)

    def discover(self) -> Dict[str, type[PAOModel]]:
        print("IMPORTING MODELS MODULE FROM", self.models_module_name)
        module = importlib.import_module(self.models_module_name)
        models = [cls for _, cls in inspect.getmembers(module, inspect.isclass) if self.is_valid_model(cls)]

        # Sort by line number; this is important as we should
        # generate migrations in the defined order:
        sorted_models = sorted(models, key=self.__get_model_line_num);

        model_dict = {m.__name__: m for m in sorted_models}

        print('MODEL_DICT:', model_dict)
        return model_dict

    def __get_model_line_num(self, model):
        _, line_num = inspect.getsourcelines(model)
        return line_num


