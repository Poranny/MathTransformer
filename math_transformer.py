def setup_generator (token : str) :
    from transformers import pipeline

    generator = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.3", token=token, temperature=0.001)
    return generator