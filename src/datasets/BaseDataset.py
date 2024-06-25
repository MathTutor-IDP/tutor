from abc import ABC, abstractmethod
import json


class BaseDataset(ABC):

    @abstractmethod
    def __init__(self, name):
        self.name = name
        self.records = list()
        self.fields = ['id', 'question', 'solution', 'final_answer']

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        return self.records[idx]

    def __iter__(self):
        return iter(self.records)

    @abstractmethod
    def _read(self):
        pass

    @abstractmethod
    def _download(self):
        pass

    def save_as(self, write_path, only_perturbed=False):
        with open(write_path, "w") as f:
            for record in self.records:
                if only_perturbed and not record.perturbed:
                    continue
                f.write(json.dumps(vars(record)))
                f.write("\n")
