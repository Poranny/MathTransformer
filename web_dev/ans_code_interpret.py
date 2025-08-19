from typing import Optional, Dict

_MESSAGES: Dict[str, str] = {
    "MODEL_NOT_READY": (
        "MathTransformer is still stretching its neurons... Please try again in a moment."
    ),
    "GENERATOR_INIT_FAILED": (
        "The math engine stumbled on startup. Let’s try again later."
    ),
    "PROMPT_INVALID": (
        "Hmm, I can’t quite prepare that request. Try simplifying your input. "
    ),
    "GENERATION_FAILED": (
        "The generator lost its train of thought mid-equation. Please try again."
    ),
    "PARSING_ERROR": (
        "I couldn’t interpret the generated output as equations. Try rephrasing the request a bit."
    ),
    "SOLVE_FAILED": (
        "These equations resisted my solving powers. Try adjusting the input or provide more details."
    ),
    "SERIALIZATION_FAILED": (
        "I solved it, but dropped the chalk while writing it down. Please try again."
    ),
    "NETWORK_ERROR": (
        "MathTransformer is waving from afar but the line broke. Please check your connection and try again."
    ),
    "TIMEOUT": (
        "Still calculating... or just daydreaming. Please try again."
    ),
    "UNKNOWN_ERROR": (
        "An unexpected gremlin appeared. Please try again."
    ),
}

def nice_message(code: Optional[str]) -> str:
    if code and code in _MESSAGES:
        return _MESSAGES[code]
    return _MESSAGES["UNKNOWN_ERROR"]
