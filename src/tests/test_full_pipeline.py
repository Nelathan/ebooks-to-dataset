#!/usr/bin/env python3
"""
Test script to simulate the full pipeline with mock book data.
This helps debug the dataset creation without needing GitHub API or actual repos.
"""

import os
import json
from main import update_dataset, DATASET_FILE, BOOKS_LIST_FILE

def create_mock_book_data():
    """Create mock book entries to test the pipeline"""
    return [
        {
            "name": "test-book-1",
            "link": "https://github.com/standardebooks/test-book-1",
            "updated_at": "2024-01-01T00:00:00Z",
            "clone_url": "https://github.com/standardebooks/test-book-1.git",
            "default_branch": "master",
            "book_data": {
                "title": "The Great Test Novel",
                "author": "Jane Testwriter",
                "language": "en",
                "text": "# Chapter 1: The Beginning\n\nIt was the best of tests, it was the worst of tests. This is a sample book content that would normally be extracted from EPUB files. The content goes on for several paragraphs to simulate a real book.\n\n---\n\n# Chapter 2: The Middle\n\nMore content here. This represents the main body of the book after parsing the EPUB structure and extracting text from multiple XHTML files in the correct reading order.\n\n---\n\n# Chapter 3: The End\n\nAnd finally, the conclusion of our test book. In a real scenario, this would be much longer and contain the full text of a public domain book from Standard Ebooks."
            }
        },
        {
            "name": "another-test-book",
            "link": "https://github.com/standardebooks/another-test-book",
            "updated_at": "2024-01-02T00:00:00Z",
            "clone_url": "https://github.com/standardebooks/another-test-book.git",
            "default_branch": "master",
            "book_data": {
                "title": "Adventures in Testing",
                "author": "Bob Debugger",
                "language": "en",
                "text": "# Prologue\n\nThis is the second test book in our mock dataset. It has different content and structure to ensure our dataset builder can handle multiple books correctly.\n\n---\n\n# Part I: Setup\n\nThe art of testing requires careful preparation and attention to detail. Each test case must be crafted with precision.\n\n---\n\n# Part II: Execution\n\nRunning tests and analyzing results forms the core of the testing process.\n\n---\n\n# Epilogue\n\nWith proper testing, we can ensure our systems work as expected."
            }
        },
        {
            "name": "short-test-book",
            "link": "https://github.com/standardebooks/short-test-book",
            "updated_at": "2024-01-03T00:00:00Z",
            "clone_url": "https://github.com/standardebooks/short-test-book.git",
            "default_branch": "master",
            "book_data": {
                "title": "Brief Tales",
                "author": "C. Concise",
                "language": "en",
                "text": "A very short story for testing purposes. Sometimes books are brief, and our system should handle them just as well as longer works."
            }
        }
    ]

def test_full_pipeline():
    """Test the complete pipeline with mock data"""
    print("=== Testing Full Pipeline with Mock Data ===\n")

    # Clean up any existing test files
    for file in [DATASET_FILE, BOOKS_LIST_FILE]:
        if os.path.exists(file):
            print(f"Removing existing {file}")
            os.remove(file)

    mock_books = create_mock_book_data()
    successful_repos = []

    print(f"Processing {len(mock_books)} mock books...\n")

    # Simulate the main processing loop
    for i, repo in enumerate(mock_books, 1):
        print(f"--- Processing Book {i}: {repo['name']} ---")

        # Simulate book extraction (normally done by parse_opf_and_extract_text)
        book_data = repo["book_data"]

        # Create book entry (same format as main.py)
        book_entry = {
            "link": repo["link"],
            "title": book_data["title"],
            "author": book_data["author"],
            "text": book_data["text"],
            "language": book_data["language"]
        }

        print(f"Title: {book_entry['title']}")
        print(f"Author: {book_entry['author']}")
        print(f"Text length: {len(book_entry['text'])} characters")

        # Update dataset (this is the actual function from main.py)
        try:
            update_dataset(book_entry, DATASET_FILE)
            print("✅ Dataset updated successfully")
        except Exception as e:
            print(f"❌ Failed to update dataset: {e}")
            continue

        # Update successful repos list (simulate main.py behavior)
        successful_repos = [r for r in successful_repos if r["name"] != repo["name"]]
        successful_repos.append(repo)

        # Write books_list.json
        try:
            with open(BOOKS_LIST_FILE, "w") as f:
                json.dump(successful_repos, f, indent=2)
            print("✅ Books list updated successfully")
        except Exception as e:
            print(f"❌ Failed to update books list: {e}")

        print()

    # Verify final results
    print("=== Final Verification ===")

    # Check dataset file
    if os.path.exists(DATASET_FILE):
        file_size = os.path.getsize(DATASET_FILE)
        print(f"✅ Dataset file created: {DATASET_FILE} ({file_size} bytes)")

        # Try to read and verify content
        try:
            import pyarrow.ipc as ipc
            with open(DATASET_FILE, 'rb') as f:
                reader = ipc.RecordBatchFileReader(f)
                table = reader.read_all()

            print(f"✅ Dataset contains {table.num_rows} books")
            print(f"✅ Schema: {[field.name for field in table.schema]}")

            # Print summary of books
            titles = table.column('title').to_pylist()
            authors = table.column('author').to_pylist()
            text_lengths = [len(text) for text in table.column('text').to_pylist()]

            print("\nBooks in dataset:")
            for i, (title, author, text_len) in enumerate(zip(titles, authors, text_lengths), 1):
                print(f"  {i}. '{title}' by {author} ({text_len} chars)")

        except Exception as e:
            print(f"❌ Failed to read dataset: {e}")
    else:
        print(f"❌ Dataset file not found: {DATASET_FILE}")

    # Check books list file
    if os.path.exists(BOOKS_LIST_FILE):
        try:
            with open(BOOKS_LIST_FILE, 'r') as f:
                books_list = json.load(f)
            print(f"✅ Books list file created with {len(books_list)} entries")
        except Exception as e:
            print(f"❌ Failed to read books list: {e}")
    else:
        print(f"❌ Books list file not found: {BOOKS_LIST_FILE}")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_full_pipeline()
