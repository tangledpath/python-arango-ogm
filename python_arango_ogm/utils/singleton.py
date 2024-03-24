class Singleton(type):
    """
    A Singleton metaclass to implement Singleton pattern on classes

    Usage:
    class MyClass(BaseClass, metaclass=Singleton):
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]