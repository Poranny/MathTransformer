import os


def load_token():
    from dotenv import load_dotenv

    load_dotenv()

    token = os.environ.get("HUGGING_TOKEN")
    return token
