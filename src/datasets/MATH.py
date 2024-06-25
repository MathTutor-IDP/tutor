from src.datasets.BaseDataset import BaseDataset
from src.datasets.BaseRecord import BaseRecord
import copy
import json

from datasets import load_dataset
import os


class MATHRecord(BaseRecord):
    """ Record for MATH dataset. """
    def __init__(self, record_id, record_data, perturbed=False):

        REQUIRED_KEYS = ['problem', 'level', 'type', 'solution', 'split']
        assert perturbed or all(key in record_data for key in REQUIRED_KEYS), "Record data is missing required keys!"
        record_data['dataset'] = 'MATH'
        if not perturbed:
            record_data['question'] = record_data.pop('problem')
            dataset_solution_text = record_data['solution']
            record_data['final_answer'] = self.get_final_answer(dataset_solution_text)
            record_data['solution'] = self._split_solution(dataset_solution_text, record_data['final_answer'])

        super().__init__(record_id, record_data, perturbed)

        self.split = record_data['split']
        self.type = record_data['type']
        self.level = record_data['level'].split(" ")[-1]

    @staticmethod
    def _split_solution(solution, final_answer):
        steps = [step + '.' if not step.endswith('.') else step for step in solution.split(". ")]
        steps.append("Final answer: " + final_answer)
        return steps

    @staticmethod
    def get_final_answer(solution):
        # Finds final answer from string using //boxed higlight in LaTeX.
        start = solution.rfind("boxed") + 6
        end = start + 1
        bracket_counter = 0

        # Find the end of //boxed{} area
        while end < len(solution) and (solution[end] != '}' or bracket_counter != 0):
            if solution[end] == '{':
                bracket_counter += 1
            if solution[end] == '}':
                bracket_counter -= 1
            end += 1
            # Fail safe for misused boxed at the end
        if end == len(solution):
            return "ERROR"
        return solution[start:end]

    @property
    def formatted_solution(self):
        solution = ' '.join(self.solution[:-1])
        # solution += f"  #### Final answer is \\boxed{{{self.final_answer}}}"
        return solution

    def get_indices_to_perturb(self):
        candidate_steps = []
        for i, step in enumerate(self.solution, start=1):
            if step.count('$') >= 2:
                candidate_steps.append(i)
        return candidate_steps


class MATH(BaseDataset):
    def __init__(self, from_file="", from_huggingface=False, file_format="jsonl", perturbed=False, filter_drawings=True):
        super().__init__("MATH")

        assert os.path.exists(from_file) or from_huggingface, "File does not exist!"
        assert bool(from_file) != from_huggingface, "Only one source can be provided!"

        self.file_path = from_file
        self.file_format = file_format
        self.download_dataset = from_huggingface
        self.perturbed = perturbed
        self.filter_drawings = filter_drawings
        self.fields += ["split"]
        self.categories = ['Counting & Probability', 'Prealgebra', 'Number Theory', 'Algebra', 'Intermediate Algebra',
                           'Geometry', 'Precalculus']

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
                sample = json.loads(line)
                if self.filter_drawings and "[asy]" in sample["problem"]:
                    continue
                record = MATHRecord(sample["id"], sample, perturbed=self.perturbed)
                self.records.append(record)

    def _download(self):
        dataset_name = 'lighteval/MATH'
        qid = 0
        splits = ["train", "test"]

        dataset = load_dataset(dataset_name)

        for split in splits:
            for sample in dataset[split]:
                sample["split"] = split
                if self.filter_drawings and "[asy]" in sample["problem"]:
                    continue
                new_record = MATHRecord(qid, sample)
                self.records.append(new_record)
                qid += 1

    @property
    def questions(self):
        return [record.question for record in self.records]

    @property
    def solutions(self):
        return [record.solution for record in self.records]

    def filter(self, category=None, level=None, split=None):
        assert category in self.categories or category is None, "Invalid category!"
        assert level in range(1, 6) or level is None, "Invalid level!"
        assert split in ["train", "test"] or split is None, "Invalid split!"

        new_ds = copy.deepcopy(self)
        new_ds.records = [record for record in self.records if (category is None or record.type == category) and
                          (level is None or record.level == str(level)) and
                          (split is None or record.split == split)]
        return new_ds
