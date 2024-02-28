from glob import iglob
import importlib, inspect

class ModelDiscovery:
    def __init__(self, path: str = '.'):
        self.path = path

    def discover(self):
        models = []
        print("Discovered models:")
        for file in iglob("**/models.py", recursive=True):
            print("Checking file: {}".format(file))
            name = file.split(".")[0].replace("/", ".")

            print("Checking file: {} -> {}".format(file, name))
            module = importlib.import_module(name)
            for name, cls in inspect.getmembers(module, inspect.isclass):
                models.append(cls)
                print("member", name, cls)
        return models


