import re


def result_parser(answer):

    answers = answer.split(", ")
    answers_cleared = []

    for elem in answers:
        # removing redundant spaces
        elem_clr = " ".join(elem.strip().split())
        elem_clr = elem_clr.replace("'", "")

        answers_cleared.append(elem_clr)

    return answers_cleared


def explicit_multiply_parser(equation):
    pattern = r"(?<![A-Za-z])(\d+)\s*([A-Za-z]+)"

    def insert_multiply(m):
        return f"{m.group(1)} * {m.group(2)}"

    return re.sub(pattern, insert_multiply, equation)


def is_safe_equation(s: str) -> bool:
    if s.count("=") != 1:
        return False  # only one equation sign
    if re.search(r"[\"'`_<>!^&|:%,$@\\\[\]{}]", s):
        return False  # forbidden chars
    if not re.fullmatch(r"[A-Za-z0-9+\-*/=().\s]+", s):
        return False  # allowed chars
    if re.search(r"[A-Za-z]\s*\.\s*[A-Za-z0-9]", s):
        return False  # a.b not allowed
    if re.search(r"\b(def|class)\b", s):
        return False # words def or class are not allowed
    # if re.search(r"[A-Za-z][A-Za-z0-9]*\s*\(", s): return False # not allowed fun(
    L, R = (p.strip() for p in s.split("="))
    if not L or not R:
        return False  # something on both sides of equation

    bal = 0
    for ch in s:  # both brackets present
        bal += (ch == "(") - (ch == ")")
        if bal < 0:
            return False
    return bal == 0


def get_symbols(equations):
    from sympy import symbols

    pattern = r"[A-Za-z][A-Za-z0-9]*"

    names = set()
    for eq in equations:
        names.update(re.findall(pattern, eq))

    blacklist = {"I", "E", "oo", "pi", "nan", "zoo", "sin", "cos", "tan", "log", "exp"}
    names = sorted(n for n in names if n not in blacklist)

    if not names:
        return []

    return list(symbols(" ".join(names), seq=True))


def parse_response(response):
    answer = response

    if "NOTMATH_WARNING" in answer:
        raise Exception("NOTMATH_WARNING")
    elif "INEQUAL_WARNING" in answer:
        raise Exception("INEQUAL_WARNING")

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
        import sympy as sp
        import re

        def fmt_complex_raw(rf, if_):
            sign = "+" if if_ >= 0 else "-"
            mag = abs(if_)
            if rf == 0:
                return f"{'-' if if_ < 0 else ''}{mag} i"
            return f"{rf} {sign} {mag} i"

        def to_sympy(expr):
            if isinstance(expr, sp.Basic):
                return expr
            if isinstance(expr, (int, float, complex)):
                try:
                    return sp.nsimplify(expr)
                except Exception:
                    if isinstance(expr, complex):
                        return sp.Float(expr.real) + sp.Float(expr.imag) * sp.I
                    return sp.Float(expr)
            if isinstance(expr, str):
                s = expr.strip()

                if "=" in s:
                    s = s.split("=", 1)[1].strip()

                if not re.fullmatch(r"[A-Za-z0-9+\-*/().,^ \t\n]*", s):
                    return None
                locals_map = {
                    "I": sp.I, "pi": sp.pi, "E": sp.E,
                    "sqrt": sp.sqrt, "root": sp.root,
                    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
                    "cot": sp.cot, "sec": sp.sec, "csc": sp.csc,
                    "log": sp.log, "exp": sp.exp,
                }
                try:
                    return sp.sympify(s, locals=locals_map, evaluate=True)
                except Exception:
                    return None
            return None

        def num_re_im(sym):
            n = sp.N(sym)
            r = sp.re(n)
            i = sp.im(n)
            try:
                rf = float(r)
            except Exception:
                rf = float(r.evalf())
            try:
                if_ = float(i)
            except Exception:
                if_ = float(i.evalf())
            return rf, if_

        if hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
            return [_to_jsonable(v) for v in value]

        sym = to_sympy(value)
        if sym is not None:
            rf, if_ = num_re_im(sym)
            if if_ == 0.0:
                return float(rf)
            return fmt_complex_raw(rf, if_)

        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, complex):
            return fmt_complex_raw(value.real, value.imag)
        if isinstance(value, str):
            return value.strip()

    except Exception:
        pass

    return str(value)


def solution_to_json(solution):

    if solution is None or solution == {}:
        return {}

    if isinstance(solution, list):
        if not solution:
            return {"result": []}
        if all(isinstance(x, dict) for x in solution):
            return {
                "solutions": [
                    {str(sym): _to_jsonable(val) for sym, val in x.items()}
                    for x in solution
                ]
            }

        return {"results": [_to_jsonable(x) for x in solution]}


    if isinstance(solution, dict):
        return {str(sym): _to_jsonable(val) for sym, val in solution.items()}

    return {"result": _to_jsonable(solution)}


def equations_to_json(equations):
    return [str(eq) for eq in equations]


def symbols_to_json(symbols):
    return [str(symbol) for symbol in symbols]
