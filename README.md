# Book Recommendation System

This project implements a book recommendation system using embeddings and cosine similarity.

## Features

- Generate embeddings for books using Google's Generative AI
- Recommend books based on user input context
- Process and store book data from CSV file
- Manage API request limits and progress tracking

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your Google API key as an environment variable
4. Prepare your book data CSV file

## Usage

1. Run the embedding generation script to process book data
2. Use the recommendation system to get book suggestions based on input context

## File Structure

- `main.py`: Main script for book recommendations
- `embedding_generator.py`: Script to generate and store book embeddings
- `books.csv`: Input data file containing book information
- `embeddings.json`: Stored book embeddings
- `progress.json`: Tracks progress of embedding generation

## Dependencies

See `requirements.txt` for a full list of dependencies.

## Note

This project uses Google's Generative AI. Make sure you have the necessary API access and credentials.