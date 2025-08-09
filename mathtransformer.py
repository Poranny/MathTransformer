from transformers import pipeline
from sympy import symbols, Eq, solve
import re
import os
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("HUGGING_TOKEN")

generator = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.3", token=token)

def parse_equation_description(prompt):

    instruction = (
        "Read the following instruction and return Python code using sympy that defines and solves the equations:\n"
        f"{prompt}\n"
        "Only return the Python code, without explanation."
    )

    result = generator(instruction, max_new_tokens=200)[0]["generated_text"]

    code_match = re.search(r"```python\n(.*?)```", result, re.DOTALL)

    if code_match:
        code = code_match.group(1)
    else:
        code = result.split("```")[-1]

    return code

def execute_sympy_code(code):
    local_vars = {}
    exec(code, {"symbols": symbols, "Eq": Eq, "solve": solve}, local_vars)

    return local_vars


prompt = "Nina has one apple. John has one apple more than Nina. How many apples does John have?"
code = parse_equation_description(prompt)
print("Generated code:\n", code)

result_vars = execute_sympy_code(code)
print("Result:\n", result_vars)
