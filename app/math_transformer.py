import os, glob
from ctransformers import AutoModelForCausalLM

def setup_generator():
    model_dir = os.getenv("MODEL_DIR")
    model_file = os.getenv("MODEL_FILE")
    quant = os.getenv("MODEL_QUANT")

    if not model_file:
        pattern = f"*{quant}*.gguf" if quant else "*.gguf"
        candidates = sorted(
            p for p in glob.glob(os.path.join(model_dir, pattern))
            if quant is None or p.lower().endswith(f"{quant.lower()}.gguf")
        )
        if not candidates:
            files = ", ".join(sorted(os.listdir(model_dir))) if os.path.isdir(model_dir) else "(no directory)"
            raise FileNotFoundError(f"No GGUF for quant='{quant}' in {model_dir}. Available: {files}")
        model_file = os.path.basename(candidates[0])

    llm = AutoModelForCausalLM.from_pretrained(
        model_dir,
        model_file=model_file,
        model_type="mistral",
        gpu_layers=0,
        threads=int(os.getenv("LLM_THREADS", "4")),
        context_length=int(os.getenv("LLM_CTX", "32768")),
    )

    def infer(prompt: str, max_new_tokens: int = 128, temperature: float = 0.01):
        return llm(prompt, max_new_tokens=max_new_tokens, temperature=temperature, stop=["</s>"])

    return infer

def build_mistral_prompt(system_text: str, examples: list[tuple[str, str]], user_text: str) -> str:
    parts = []
    sys = system_text.strip()

    for u, a in examples:
        if sys:
            parts.append(f"<s>[INST] {sys}\n{u} [/INST] {a} </s>")
            sys = ""
        else:
            parts.append(f"<s>[INST] {u} [/INST] {a} </s>")

    if sys:
        parts.append(f"<s>[INST] {sys}\n{user_text} [/INST]")
    else:
        parts.append(f"<s>[INST] {user_text} [/INST]")

    return " ".join(parts)

def setup_prompt(nl_prompt: str) -> str:
    system_txt = (
        "You are a natural language equation parser. You will receive an equation described in a natural language.\n"
        "1. Output ONLY a comma-separated list of equations. Each equation must:\n"
        "   - Be in single quotes: 'example'\n"
        "   - Consist of two expressions separated by =\n"
        "   - Both of the expressions must consist of named variables, numbers, and operators between them\n"
        "   - The named variables start with latin characters only, and might contain digits, e.g. x, y, john, var1, apple, const1b etc.\n"
        "   - The numbers should use '.' for decimal points when necessary\n"
        "   - The only operators allowed are: +, -, *, /, ** and there should be spaces on both sides of each operator\n"
        "2. If the input describes an inequality (>, <, >=, <=, !=, or their verbal forms), respond ONLY with: INEQUAL_WARNING.\n"
        "3. If the input does not describe a valid math equation, respond ONLY with: NOTMATH_WARNING.\n"
        "Do not solve the equations. Do not explain anything. Do not output code. Output nothing except what the rules above require."
    )

    examples = [
        ("This is the equation described in a natural language:\n<<<\n3 times a plus 4b equals 7\n>>>",
         "'3 * a + 4 * b = 7'"),
        ("This is the equation described in a natural language:\n<<<\ntwo a minus twentyone equals b. and c squared equals b as well. c=2a\n>>>",
         "'2 * a - 21 = b', 'c ** 2 = b', 'c = 2 * a'"),
        ("This is the equation described in a natural language:\n<<<\nx is 1. variable b is 20-x.\n>>>",
         "'x = 1', 'b = 20 - x'"),
        ("This is the equation described in a natural language:\n<<<\nconstant1a is two times more than var1Z\n>>>",
         "'constant1a = 2 * var1Z'"),
    ]

    user_txt = f"This is the equation described in a natural language:\n<<<\n{nl_prompt}\n>>>"
    return build_mistral_prompt(system_txt, examples, user_txt)

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
