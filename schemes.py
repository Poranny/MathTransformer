from pydantic import BaseModel


class SolveRequest (BaseModel) :
    prompt : str

class SolveAnswer (BaseModel) :
    symbols : str
    solution : str
    equations : str
