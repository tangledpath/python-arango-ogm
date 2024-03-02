import importlib, inspect
import os
from typing import Sequence, Type, Dict
from dotenv import load_dotenv
load_dotenv()

class ModelDiscovery:
    def __init__(self, path: str = '.'):
        self.models_module_name = os.getenv('PAO_MODELS')
        if not self.models_module_name:
            raise RuntimeError("PAO_MODELS must be defined in the environment (or a .env.test file)")

    def discover(self) -> Dict[str, Type]:
        module = importlib.import_module(self.models_module_name)
        models = [cls for _, cls in inspect.getmembers(module, inspect.isclass)]

        # Sort by line number; this is important as we should
        # generate migrations in the defined order:
        sorted_models = sorted(models, key=self.__get_model_line_num);

        model_dict = {m.__name__: m for m in sorted_models}

        print('model_dict', model_dict)
        return model_dict

    def __get_model_line_num(self, model):
        _, line_num = inspect.getsourcelines(model)
        return line_num


