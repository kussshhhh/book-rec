import csv
import google.generativeai as genai
import os
import json
import time

genai.configure(api_key=os.environ['api_key'])
model = genai.GenerativeModel("gemini-1.5-flash")

file_path = "books_data/books.csv"
progress_file = "progress.json"
embeddings_file = "embeddings.json"

def parse(input_list):
    # Split the contents of the first element in the list
    arr = [item.strip() for item in input_list]
    # Get the first element of the split list
    arr = arr[0]
    # Split the first element by semicolons
    arr = arr.split(";")
    # Return the second element of the split list
    return arr

def generate_embedding(book, author):
    response = model.generate_content(f"what is the {book} book by the author {author} about? give a brief summary in around 100 words and ill use your summary to generate a vector embedding so crunch up as much context about this book as you can in around 100 words")
    text = ""
    try:
        text = response.text
    except:
        text = ""
    print(text)
    result = ""
    if len(text) > 0:
        result = genai.embed_content(model="models/text-embedding-004", content=text)
    return result

def load_progress():
    default_progress = {"request_count": 0, "last_processed_row": -1}
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default_progress
    return default_progress

def save_progress(request_count, last_processed_row):
    with open(progress_file, 'w') as f:
        json.dump({"request_count": request_count, "last_processed_row": last_processed_row}, f)

def load_embeddings():
    default_embeddings = {}
    if os.path.exists(embeddings_file):
        try:
            with open(embeddings_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default_embeddings
    return default_embeddings

def save_embeddings(book, embedding):
    embeddings = load_embeddings()
    embeddings[book] = embedding
    with open(embeddings_file, 'w') as f:
        json.dump(embeddings, f)

progress = load_progress()
request_count = progress["request_count"]
last_processed_row = progress["last_processed_row"]

with open(file_path, 'r', encoding='latin-1') as file:
    reader = csv.reader(file)
    for i, row in enumerate(reader):
        if i <= last_processed_row:
            continue
        if request_count >= 4000:
            print("daily limit reached, stopping.")
            break
        arr = parse(row)
        book_id = arr[0]
        book = arr[1]
        author = ""
        if len(arr) >= 3:
            author = arr[2]
        embedding = generate_embedding(book, author)
        if embedding != "":
            save_embeddings(book, embedding)
            print(f"Processed book: {book} by {author}")
            if embedding != "":
                print(str(embedding['embedding'])[:50], '... TRIMMED]')
                print(len(embedding['embedding']))
        request_count += 1
        last_processed_row = i
        print(f"Requests made: {request_count}")
        save_progress(request_count, last_processed_row)
        # Add a delay of 5 seconds between requests
        time.sleep(5)

print("processing complete")