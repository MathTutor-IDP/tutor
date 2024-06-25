from abc import ABC


class BaseModel(ABC):
    def __init__(self, **kwargs):
        pass

    def query(self, dataset):
        pass
