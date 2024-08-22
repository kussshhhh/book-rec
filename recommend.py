import numpy as np 
import google.generativeai as  genai
import json
import os 
import re

genai.configure(api_key=os.environ['api_key']) 
model = genai.GenerativeModel("gemini-1.5-flash")

def cosine(vec1, vec2):
    return np.dot(vec1, vec2)/ (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def recommend(context, book_embeddings, titles, top_n=5):
    similarities = []
    for title, embedding in book_embeddings.items():
        similarirty = 1 - cosine(context, embedding)
        similarities.append((title, similarirty))

    similarities.sort(key=lambda x:x[1], reverse=True)

    return similarities[:top_n]


def inspect_json(data, level=0):
    indent = "  " * level
    if isinstance(data, dict):
        print(f"{indent}Object:")
        for key, value in data.items():
            print(f"{indent}  {key}:")
            inspect_json(value, level + 2)
    elif isinstance(data, list):
        print(f"{indent}Array of {len(data)} items:")
        for item in data[:3]:  # Print first 3 items as example
            inspect_json(item, level + 1)
        if len(data) > 3:
            print(f"{indent}  ...")
    else:
        print(f"{indent}{type(data).__name__}: {data}")

def process_book_data(title, book_data):
    try:
        # Check if book_data is a dictionary and has 'embedding' key
        if not isinstance(book_data, dict) or 'embedding' not in book_data:
            raise ValueError("Book data is not in the expected format")
            return []
        embedding = book_data['embedding']
        
        # Check if embedding is a list and has at least 5 elements
        if not isinstance(embedding, list) or len(embedding) < 5:
            raise ValueError("Embedding is not in the expected format")
            return []
        # print(f"Title: {title}")
        # print(f"First 5 embedding values: {embedding[:5]}")
        # print()
        return embedding
    except Exception as e:
        # print(f"Error processing book '{title}': {str(e)}")
        print("Skipping this entry.")
        # print()


with open('embeddings.json', 'r') as f:
    f = json.load(f)

context = input("context: ")
context = genai.embed_content(model="models/text-embedding-004", content=context)
context = context['embedding']

book_embeddings = {}


for title, book_data in f.items():
    embedding = process_book_data(title, book_data)
    if embedding is not None:
        book_embeddings[title] = embedding
    
recommendations = recommend(context, book_embeddings, list(f.keys()))

for title, embedding in recommendations:
    print(f'{title}')