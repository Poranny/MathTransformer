import re


def result_parser (answer):

    answers = answer.split(', ')
    answers_cleared = []

    for elem in answers:
        # removing redundant spaces
        elem_clr = ' '.join(elem.strip().split())
        elem_clr = elem_clr.replace("'", "")

        answers_cleared.append(elem_clr)

    return answers_cleared

def explicit_multiply_parser (equation) :
    pattern = r'([0-9])\s*([A-Za-z])|([A-Za-z])\s*([0-9])'

    def insert_multiply(match):
        if match.group(1) and match.group(2):
            # digit+letter
            return f"{match.group(1)} * {match.group(2)}"
        else:
            # letter+digit
            return f"{match.group(3)} * {match.group(4)}"

    eq_expl = re.sub(pattern, insert_multiply, equation)
    return eq_expl

def is_safe_equation(s: str) -> bool:
    if s.count('=') != 1: return False # only one equation sign
    if re.search(r"[\"'`_<>!^&|:%,$\\\[\]{}]", s): return False # forbidden chars
    if not re.fullmatch(r"[A-Za-z0-9+\-*/=().\s]+", s): return False # allowed chars
    if re.search(r"[A-Za-z]\s*\.\s*[A-Za-z0-9]", s): return False # a.b not allowed
    if re.search(r"[A-Za-z][A-Za-z0-9]*\s*\(", s): return False # not allowed fun(
    L, R = (p.strip() for p in s.split('='))
    if not L or not R: return False # something on both sides of equation

    bal = 0
    for ch in s: # both brackets present
        bal += (ch == '(') - (ch == ')')
        if bal < 0: return False
    return bal == 0


def get_symbols (equations) :
    from sympy import symbols, Symbol

    symbol_names = set()

    for eq in equations:
        matches = re.findall(r"[A-Za-z]+", eq)
        symbol_names.update(matches)

    symbol_names = sorted(list(symbol_names))

    sympy_symbols = symbols(" ".join(symbol_names))

    try:
        iter(sympy_symbols)
    except TypeError:
        sympy_symbols = [sympy_symbols]
    else:
        if isinstance(sympy_symbols, str) or isinstance(sympy_symbols, Symbol):
            sympy_symbols = [sympy_symbols]

    return sympy_symbols


def parse_response (response) :
    answer = response[0]["generated_text"][-1]['content']

    if 'NOTMATH_WARNING' in answer:
        raise Exception('The prompt was detected not to be a math equation.')
    elif 'INEQUAL_WARNING' in answer:
        raise Exception('The prompt was detected to be an inequality.')

    parsed_answer = result_parser(answer)

    equations = []
    for eq in parsed_answer:
        equations.append(explicit_multiply_parser(eq))

    for eq in equations:
        if not is_safe_equation(eq):
            raise Exception(f"The equation {eq} is not safe.")

    return equations


def solution_to_json(solution):
    from sympy import N

    return {
        str(symbol): float(round(N(value), 5))
        for symbol, value in solution[0].items()
    }

def equations_to_json(equations):
    return list(equations)

def symbols_to_json(symbols):
    return [str(symbol) for symbol in symbols]