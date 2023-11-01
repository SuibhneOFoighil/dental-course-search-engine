import openai
import os
import re

openai.api_key = os.environ['OPENAI_API_KEY']

def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

def extract_reference_numbers(text: str) -> list[str]:
    pattern = r"\((\d+(?:,\d+)*)\)"
    matches = re.findall(pattern, text)
    references = [ref for match in matches for ref in match.split(',')]
    return references