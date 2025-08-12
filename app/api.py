from app.math_transformer import setup_generator, setup_prompt, solve_equations
from app.parse_helpers import parse_response, get_symbols, solution_to_json, symbols_to_json, equations_to_json
from app.misc import load_token
from app.schemes import SolveRequest, SolveAnswer

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request


@asynccontextmanager
async def lifespan (app: FastAPI) :
    try:
        app.state.generator = setup_generator()
    except Exception:
        raise RuntimeError("There was an error setting the generator. Please try again later.")

    yield

app = FastAPI(lifespan=lifespan)

def get_generator (req : Request) :
    gen = getattr(req.app.state, "generator", None)
    if gen is None:
        raise HTTPException(status_code=503, detail="Model not ready.")
    return gen

@app.post("/answer", response_model=SolveAnswer)
def answer(data : SolveRequest, generator=Depends(get_generator)) :
    try:
        ready_prompt = setup_prompt(data.prompt)
    except Exception:
        raise HTTPException(status_code=400, detail="There was an error setting the prompt. Please try again later.")

    try:
        response = generator(ready_prompt)
    except Exception:
        raise HTTPException(status_code=500, detail="There was an error generating the answer. Please try again later.")

    try:
        equations = parse_response(response)
        symbols = get_symbols(equations)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"There was an error parsing the response: {e}")

    try:
        solution = solve_equations(equations, symbols)
    except Exception:
        raise HTTPException(status_code=500, detail="There was an error solving the equations. Please try again later.")

    try :
        json_symbols = symbols_to_json(symbols)
        json_equations = equations_to_json(equations)
        json_solution = solution_to_json(solution)
    except Exception:
        raise HTTPException(status_code=500, detail="There was an error parsing the responses. Please try again later.")

    return SolveAnswer (
            symbols = json_symbols,
            equations = json_equations,
            solution = json_solution
        )