from pydantic import BaseModel
from typing import List, Dict

class SolveRequest (BaseModel) :
    prompt : str

class SolveAnswer(BaseModel):
    symbols: List[str]
    equations: List[str]
    solution: Dict[str, float]
