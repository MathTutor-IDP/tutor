from src.datasets.BaseDataset import BaseDataset
from src.datasets.BaseRecord import BaseRecord

from datasets import load_dataset
import os


class GSM8KRecord(BaseRecord):
    """ Record for GSM8K dataset. """
    def __init__(self, record_id, record_data):

        self.REQUIRED_KEYS = ['question', 'answer', 'split']
        assert all(key in record_data for key in self.REQUIRED_KEYS), "Record data is missing required keys!"

        record_data['dataset'] = 'GSM8K'
        record_data['solution'] = self._split_solution(record_data.pop('answer'))
        record_data['final_answer'] = record_data['solution'][-1].replace("Final answer: ", "")

        super().__init__(record_id, record_data)
        self.socratic_questions = [_.split("**")[0] for _ in record_data["solution"][:-1]]
        self.split = record_data['split']

    @staticmethod
    def _split_solution(solution):
        steps = [step.split("**")[1] for step in solution.split("\n")[:-1]]
        steps[-1] = steps[-1].replace("#### ", "Final answer: ")
        return steps

    @property
    def question(self):
        return self.question_raw

    @property
    def formatted_solution(self):
        solution = ""
        for i, step in enumerate(self.solution[:-1], start=1):
            solution += f"Step {i}:\n"
            solution += f"{step}\n\n"
        solution += self.solution[-1]
        return solution

    def get_indices_to_perturb(self):
        candidate_steps = []
        for i, step in enumerate(self.solution):
            if "<<" in step and ">>" in step:
                candidate_steps.append(i)
        return candidate_steps


class GSM8K(BaseDataset):
    def __init__(self, from_file="", from_huggingface=False, file_format="jsonl"):
        super().__init__("GSM8K")

        assert os.path.exists(from_file) or from_huggingface, "File does not exist!"
        assert bool(from_file) != from_huggingface, "Only one source can be provided!"

        self.file_path = from_file
        self.file_format = file_format
        self.download_dataset = from_huggingface
        self.fields += ["split"]

        if self.download_dataset:
            self._download()
        else:
            self._read()

    def _read(self):
        if self.file_format == "jsonl":
            self._read_jsonl()
        else:
            raise NotImplementedError("File format not supported!")

    def _read_jsonl(self):
        with open(self.file_path, "r") as f:
            for line in f:
                sample = eval(line)
                record = GSM8KRecord(sample["id"], sample)
                self.records.append(record)
        
    def _download(self):
        dataset_name = self.name
        qid = 0
        subset = "socratic"
        splits = ["train", "test"]

        dataset = load_dataset(dataset_name, subset)
        
        for split in splits:
            for sample in dataset[split]:
                sample["split"] = split
                new_record = GSM8KRecord(qid, sample)
                self.records.append(new_record)
                qid += 1

    @property
    def questions(self):
        return [record.question for record in self.records]

    @property
    def solutions(self):
        return [record.solution for record in self.records]

    @property
    def answers(self):
        return [record.final_answer for record in self.records]

    def write(self, file_path):
        with open(file_path, "w") as f:
            for record in self.records:
                f.write(str(record) + "\n")
