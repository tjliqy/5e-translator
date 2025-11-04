from typing import List
from .job import Job

class FileWorkInfo:
    def __init__(self, job_list:List[Job], json_obj: object, json_path:str):
        self.job_list:List[Job] = job_list
        self.json_obj = json_obj
        self.json_path = json_path