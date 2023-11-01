import openai
import os
import re

openai.api_key = os.environ['OPENAI_API_KEY']

def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

def extract_reference_numbers(text):
    pattern = r"\((.+?)\)" 
    matches = re.findall(pattern, text)

    references = []
    for match in matches:
        numbers = [n for n in match.split(',')]

        references.extend(numbers)

    #Strip whitespace
    references = [r.strip() for r in references]

    return references