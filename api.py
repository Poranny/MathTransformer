import fastapi
from math_transformer import setup_generator, setup_prompt, solve_equations
from parse_helpers import parse_response, get_symbols, present_solution, present_symbols, present_equations
from misc import load_token


def setup_model () :
    try:
        token = load_token()
    except Exception as e:
        return 'There was an error loading the model. Please try again later.'

    try :
        generator = setup_generator(token)
    except Exception as e:
        return 'There was an error setting the generator. Please try again later.'

    return 'Success setting up the model.'


def get_answer (prompt : str, generator) :

    try :
        ready_prompt = setup_prompt(prompt)
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

    return presented_symbols, presented_equations, presented_solution