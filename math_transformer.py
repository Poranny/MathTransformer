def setup_generator (token : str) :
    from transformers import pipeline

    generator = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.3", token=token, temperature=0.001)
    return generator

def setup_prompt (prompt : str) :
    instruction = [
        {
            "role": "system", "content":
            "You are a natural language equation parser. You will receive an equation described in a natural language.\n"
            "1. Output ONLY a comma-separated list of equations. Each equation must:\n"
            "   - Be in single quotes: 'example'\n"
            "   - Consist of two expressions separated by =\n"
            "   - Both of the expressions must consist of named variables, numbers, and operators between them\n"
            "   - The named variables consist of latin characters only, e.g. x, y, var, john, apple etc.\n"
            "   - The numbers should use '.' for decimal points when necessary\n"
            "   - The only operators allowed are: +, -, *, /, ** and there should be spaces on both sides of each operator \n"
            "2. If the input describes an inequality (>, <, >=, <=, !=, or their verbal forms), respond ONLY with: INEQUAL_WARNING.\n"
            "3. If the input does not describe a valid math equation, respond ONLY with: NOTMATH_WARNING.\n"
            "Do not solve the equations. Do not explain anything. Do not output code. Output nothing except what the rules above require."
        },
    ]

    messages = [
        {"role": "user",
         "content": "This is the equation described in a natural language:\n<<<\n3 times a plus 4b equals 7\n>>>"},
        {"role": "assistant", "content": "'3 * a + 4 * b = 7'"},
        {"role": "user",
         "content": "This is the equation described in a natural language:\n<<<\ntwo a minus twentyone equals b. and c squared equals b as well. c=2a\n>>>"},
        {"role": "assistant", "content": "'2 * a - 21 = b', 'c ** 2 = b', c = 2 * a"},
        {"role": "user",
         "content": "This is the equation described in a natural language:\n<<<\n2x minus five equals zero\n>>>"},
        {"role": "assistant", "content": "'2 * x - 5 = 0'"},
        {"role": "user", "content":
            f"This is the equation described in a natural language:\n<<<\n{prompt}\n>>>"
         },
    ]

    query = instruction + messages

    return query

def solve_equations (equations, symbols) :
    from sympy import sympify, Eq

    equation_set = []

    for eq in equations:
        left, right = eq.split('=')

        equation_set.append(
            Eq(sympify(left), sympify(right))
        )

    from sympy import solve

    solution = solve(equation_set, symbols, dict=True)

    return solution

def parse_response (response) :
    from parse_helpers import result_parser, explicit_multiply_parser, is_safe_equation

    parsed_answer = result_parser(response)

    if parsed_answer == 'NOTMATH_WARNING':
        raise Exception('The prompt was detected not to be a math equation.')
    elif parsed_answer == 'INEQUAL_WARNING':
        raise Exception('The prompt was detected to be an inequality.')

    equations = []
    for eq in parsed_answer:
        equations.append(explicit_multiply_parser(eq))

    for eq in equations:
        if not is_safe_equation(eq):
            raise Exception(f"The equation {eq} is not safe.")

    return equations

def get_symbols (equations) :
    import re
    from sympy import symbols

    symbol_names = set()

    for eq in equations:
        matches = re.findall(r"[A-Za-z]+", eq)
        symbol_names.update(matches)


    sympy_symbols = symbols(" ".join(symbol_names))

    return sympy_symbols