from abc import ABC, abstractmethod


class BaseRecord(ABC):
    """ Record interface. """
    def __init__(self, record_id, record_data, perturbed=False):
        self.id = record_id
        self.dataset_name = record_data['dataset']
        self.question_raw = record_data['question']
        self.solution = record_data['solution']
        self.final_answer = record_data['final_answer']
        self.question = self.question_raw

        if perturbed:
            self.perturbed = True
            self.perturbed_solution = record_data['perturbed_solution']
            self.error_type = record_data['error_type']
            self.error_step = record_data['error_step']
        else:
            self.perturbed = False
            self.perturbed_solution = None
            self.error_type = None
            self.error_step = None
        self.assigned_solution = None
        self.assigned_final_answer = None
        self.is_assigned_solution_correct = None

    def __repr__(self):
        return f"""{self.dataset_name} | Record: {self.id} \t Question: {self.question}"""

    def __copy__(self):
        return self.__class__(self.id, self.__dict__.copy())

    def __str__(self):
        rec = {
            'id': self.id,
            'dataset': self.dataset_name,
            'question': self.question,
            'solution': self.solution,
            'final_answer': self.final_answer,
            'perturbed': self.perturbed,
            'perturbed_solution': self.perturbed_solution,
            'error_type': self.error_type,
            'error_step': self.error_step
        }
        return str(rec)

    @property
    @abstractmethod
    def formatted_solution(self):
        pass

    @abstractmethod
    def get_indices_to_perturb(self):
        return

    def set_perturbation(self, perturbed_solution, error_type, error_step):
        self.perturbed = True
        self.perturbed_solution = perturbed_solution
        self.error_type = error_type
        self.error_step = error_step
