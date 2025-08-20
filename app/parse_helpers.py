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

def explicit_multiply_parser(equation):
    pattern = r'(?<![A-Za-z])(\d+)\s*([A-Za-z]+)'

    def insert_multiply(m):
        return f"{m.group(1)} * {m.group(2)}"

    return re.sub(pattern, insert_multiply, equation)

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

    pattern = r'[A-Za-z][A-Za-z0-9]*'

    names = set()
    for eq in equations:
        names.update(re.findall(pattern, eq))

    blacklist = {'I', 'E', 'oo', 'pi', 'nan', 'zoo', 'sin', 'cos', 'tan', 'log', 'exp'}
    names = sorted(n for n in names if n not in blacklist)

    if not names:
        return []

    return list(symbols(' '.join(names), seq=True))


def parse_response (response) :
    answer = response

    if 'NOTMATH_WARNING' in answer:
        raise Exception('NOTMATH_WARNING')
    elif 'INEQUAL_WARNING' in answer:
        raise Exception('INEQUAL_WARNING')

    parsed_answer = result_parser(answer)

    equations = []
    for eq in parsed_answer:
        equations.append(explicit_multiply_parser(eq))

    for eq in equations:
        if not is_safe_equation(eq):
            raise Exception(f"The equation {eq} is not safe.")

    return equations

def _to_jsonable(value):

    try:
        if isinstance(value, (int, float)):
            return float(round(value, 5))

        from sympy import N
        if hasattr(value, "is_number") and bool(value.is_number):
            n = N(value)
            try:
                return float(round(n, 5))
            except Exception:
                return str(value)

        if hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
            return [_to_jsonable(v) for v in value]
    except Exception:
        pass

    return str(value)


def solution_to_json(solution):
    if solution is None:
        return {}

    if isinstance(solution, list) and solution:
        candidate = solution[0]
    else:
        candidate = solution

    if isinstance(candidate, dict):
        return {str(sym): _to_jsonable(val) for sym, val in candidate.items()}

    return {"result": _to_jsonable(candidate)}


def equations_to_json(equations):
    return [str(eq) for eq in equations]


def symbols_to_json(symbols):
    return [str(symbol) for symbol in symbols]