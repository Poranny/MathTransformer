def setup_generator(token: str | None = None):
    from transformers import pipeline
    return pipeline(
        "text-generation",
        model="/models/mistral",
        temperature=0.001
    )

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
         "content": "This is the equation described in a natural language:\n<<<\nx is 1. var b is 20-x.\n>>>"},
        {"role": "assistant", "content": "'x = 1', 'b = 20 - x'"},
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
