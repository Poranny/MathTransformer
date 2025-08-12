import re

def result_parser (result):
    answer = result[0]["generated_text"][-1]['content']

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
    from sympy import symbols

    symbol_names = set()

    for eq in equations:
        matches = re.findall(r"[A-Za-z]+", eq)
        symbol_names.update(matches)

    symbol_names = sorted(list(symbol_names))

    sympy_symbols = symbols(" ".join(symbol_names))

    if len(sympy_symbols) == 1:
        sympy_symbols = [sympy_symbols]

    return sympy_symbols


def parse_response (response) :
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


def present_solution (solution):
    from sympy import N
    sol_result = ''

    for symbol, value in solution[0].items():
        sol_result += str(symbol) + ' = ' + str(round(N(value), 5)).rstrip('0').rstrip('.')
        sol_result += '\n'
    return sol_result

def present_equations (equations) :
    eqs_presented = ''
    for equation in equations :
        eqs_presented += equation + "\n"
    return eqs_presented

def present_symbols(symbols):
    syms_presented = ''
    for symbol in symbols:
        syms_presented += str(symbol) + "\n"
    return syms_presented