

# MathTransformer


An app that turns plain English into solvable math. It parses a sentence, deduces the equation, solves it and returns the result.

👉 **Try it out:** <https://mathtransformer.app/>

<p align="center">
  <img src="web_dev/og-image.png" alt="MathTransformer Logo" width="220">
</p>

## Features

- Natural language → equation (via a HuggingFace transformer, particularly the Mistral-7B-Instruct-v0.3 model with Q6_K quantization)
- Equation → result (via lots of parsing + Sympy)
- Clean JSON output accessible by FastAPI
- Minimal Gradio UI site with a dynamic interface, a custom logo & shareable previews
