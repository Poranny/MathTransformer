from typing import List, Dict, Any
from pydantic import BaseModel

class SolveRequest(BaseModel):
    prompt: str

class SolveAnswer(BaseModel):
    symbols: List[str]
    equations: List[str]
    solution: Dict[str, Any]
