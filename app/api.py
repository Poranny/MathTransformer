from app.math_transformer import setup_generator, setup_prompt, solve_equations
from app.parse_helpers import (
    parse_response,
    get_symbols,
    solution_to_json,
    symbols_to_json,
    equations_to_json,
)
from app.schemes import SolveRequest, SolveAnswer

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.generator = setup_generator()
    except Exception:
        api_error(500, "GENERATOR_INIT_FAILED")
    yield


app = FastAPI(lifespan=lifespan)


def get_generator(req: Request):
    gen = getattr(req.app.state, "generator", None)
    if gen is None:
        api_error(503, "MODEL_NOT_READY")
    return gen


def api_error(status: int, code: str):
    raise HTTPException(status_code=status, detail={"code": code})


@app.post("/answer", response_model=SolveAnswer)
def answer(data: SolveRequest, generator=Depends(get_generator)):
    try:
        ready_prompt = setup_prompt(data.prompt)
    except Exception:
        api_error(400, "PROMPT_INVALID")

    try:
        response = generator(ready_prompt)
        if not isinstance(response, str):
            response = str(response)
    except Exception:
        api_error(500, "GENERATION_FAILED")

    try:
        equations = parse_response(response)
        symbols = get_symbols(equations)
    except Exception as error:
        raw = getattr(error, "code", None) or (error.args[0] if error.args else None)
        code = raw if isinstance(raw, str) else "PARSING_ERROR"
        api_error(422, code)

    try:
        solution = solve_equations(equations, symbols)
    except Exception:
        api_error(500, "SOLVE_FAILED")

    try:
        json_symbols = symbols_to_json(symbols)
        json_equations = equations_to_json(equations)
        json_solution = solution_to_json(solution)
    except Exception:
        api_error(500, "SERIALIZATION_FAILED")

    return SolveAnswer(
        symbols=json_symbols, equations=json_equations, solution=json_solution
    )


@app.get("/healthz")
def healthz():
    return {"ok": True}
