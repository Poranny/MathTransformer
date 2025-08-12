from pip._internal import req

from math_transformer import setup_generator, setup_prompt, solve_equations
from parse_helpers import parse_response, get_symbols, present_solution, present_symbols, present_equations
from misc import load_token
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request

from schemes import SolveRequest, SolveAnswer


@asynccontextmanager
async def lifespan (app: FastAPI) :
    try:
        token = load_token()
    except Exception:
        raise RuntimeError("There was an error loading the model. Please try again later.")
    try:
        app.state.generator = setup_generator(token)
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

    try :
        ready_prompt = setup_prompt(data.prompt)
    except Exception as e:
        return 'There was an error setting the prompt. Please try again later.'

    try :
        response = generator(ready_prompt)
    except Exception as e:
        return 'There was an error generating the answer. Please try again later.'

    try :
        equations = parse_response(response)
        symbols = get_symbols(equations)
    except Exception as e:
        return 'There was an error parsing the response. Please try again later.'

    try :
        solution = solve_equations(equations, symbols)
    except Exception as e:
        return 'There was an error solving the equations. Please try again later.'

    try :
        presented_symbols = present_symbols(symbols)
        presented_equations = present_equations(equations)
        presented_solution = present_solution(solution)
    except Exception as e:
        return 'There was an error parsing the responses. Please try again later.'

    return SolveAnswer (
        symbols = presented_symbols,
        equations = presented_equations,
        solution = presented_solution
    )