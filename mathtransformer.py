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
        "Read the following instruction regarding a math equation and return a structurized json describing the equation:\n"
        f"{prompt}\n"
        "Only return the equation's json. No explanation."
    )

    result = generator(instruction, max_new_tokens=300)[0]["generated_text"]


    return result



prompt = "Nina has one apple. John has one apple more than Nina. How many apples does John have?"
result = parse_equation_description(prompt)
print("Generated json:\n", result)

