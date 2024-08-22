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
    arr = [item.strip() for item in input_list]
    arr = arr[0]
    arr = arr.split(";")
    return arr

def generate_embeddings(books):
    prompt = "Provide brief summaries (around 100 words each) for the following books. Start each summary with the book title and author in bold also if you dont know or cant give the summary due to any reason still just give the author and book name in bold and then blank:\n\n"
    for book, author in books:
        prompt += f"- '{book}' by {author}\n"
    prompt += "\nInclude as much context as possible about each book in the summaries."

    response = model.generate_content(prompt)
    text = ""
    try:
        text = response.text
    except:
        text = ""
    print(text)

    results = []
    if len(text) > 0:
        summaries = text.split('\n\n')
        for summary, (book, author) in zip(summaries, books):
            if summary.strip():
                # Extract the summary without the title and author
                summary_text = summary.split('\n', 1)[-1].strip()
                result = genai.embed_content(model="models/text-embedding-004", content=summary_text)
                results.append((book, result))
    return results

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
    current_embeddings = load_embeddings()
    current_embeddings[book] = embedding
    with open(embeddings_file, 'w') as f:
        json.dump(current_embeddings, f)

progress = load_progress()
request_count = progress["request_count"]
last_processed_row = progress["last_processed_row"]

batch_size = 3
current_batch = []

with open(file_path, 'r', encoding='latin-1') as file:
    reader = csv.reader(file)
    for i, row in enumerate(reader):
        if i <= last_processed_row:
            continue
        if request_count >= 1900:
            print("Daily limit reached, stopping.")
            break

        arr = parse(row)
        book = arr[1]
        author = arr[2] if len(arr) >= 3 else ""
        
        current_batch.append((book, author))
        
        if len(current_batch) == batch_size:
            embeddings = generate_embeddings(current_batch)
            if embeddings:
                for book, embedding in embeddings:
                    save_embeddings(book, embedding)
                    print(f"Processed book: {book}")
                    print(str(embedding['embedding'])[:50], '... TRIMMED]')
                    print(len(embedding['embedding']))
                
                request_count += 1
                last_processed_row = i
                print(f"Requests made: {request_count}")
                save_progress(request_count, last_processed_row)
                
                current_batch = []
                time.sleep(5)  # Add a delay of 5 seconds between batches

    # Process any remaining books in the last batch
    if current_batch:
        embeddings = generate_embeddings(current_batch)
        if embeddings:
            for book, embedding in embeddings:
                save_embeddings(book, embedding)
                print(f"Processed book: {book}")
                print(str(embedding['embedding'])[:50], '... TRIMMED]')
                print(len(embedding['embedding']))
            
            request_count += 1
            last_processed_row = i
            print(f"Requests made: {request_count}")
            save_progress(request_count, last_processed_row)

print("Processing complete")