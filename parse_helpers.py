import re

def result_parser (result) :
    answer = result[0]["generated_text"] [-1] ['content']

    answers = answer.split(', ')
    answers_cleared = []

    for elem in answers :
        elem_clr = elem.replace("'", "")

        answers_cleared.append(elem_clr)

    return answers_cleared

def explicit_multiply_parser (equation) :
    import re

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