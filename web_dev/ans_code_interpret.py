from typing import Optional, Dict

_MESSAGES: Dict[str, str] = {
    "MODEL_NOT_READY": (
        "MathTransformer is still stretching its neurons...\nPlease try again in a moment."
    ),
    "GENERATOR_INIT_FAILED": (
        "The math engine stumbled on startup.\nLet’s try again later."
    ),
    "PROMPT_INVALID": (
        "Hmm, I can’t quite prepare that request.\nTry simplifying your input. "
    ),
    "GENERATION_FAILED": (
        "The generator lost its train of thought mid-equation.\nPlease try again."
    ),
    "PARSING_ERROR": (
        "I couldn’t interpret the generated output as equations.\nTry rephrasing the request a bit."
    ),
    "NOTMATH_WARNING": (
        "Oh, that didn’t look like math to me... maybe a poem?\nTry phrasing it more numerically"
    ),
    "INEQUAL_WARNING": (
        "I can only handle proper equations, not inequalities :(\nCould you rewrite it as an equation?"
    ),
    "SOLVE_FAILED": (
        "These equations resisted my solving powers.\nTry adjusting the input or provide more details."
    ),
    "SERIALIZATION_FAILED": (
        "I solved it, but dropped the chalk while writing it down.\nPlease try again."
    ),
    "NETWORK_ERROR": (
        "MathTransformer is waving from afar but the line broke.\nPlease check your connection and try again."
    ),
    "TIMEOUT": ("Still calculating... or just daydreaming.\nPlease try again."),
    "UNKNOWN_ERROR": ("An unexpected gremlin appeared.\nPlease try again."),
    "NO_SOLUTION": (
        "I couldn’t find a consistent solution here...\nMaybe the equations don’t quite fit together?"
    ),
}


def nice_message(code: Optional[str]) -> str:
    if code and code in _MESSAGES:
        return _MESSAGES[code]
    return _MESSAGES["UNKNOWN_ERROR"]
