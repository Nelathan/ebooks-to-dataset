import pyarrow as pa
import pyarrow.ipc as ipc
import os

def test_arrow_dataset():
    """Test creating, writing, and reading Arrow IPC dataset"""

    # Test data
    test_books = [
        {
            "link": "https://example.com/book1",
            "title": "Test Book 1",
            "author": "Test Author 1",
            "text": "This is the content of test book 1.",
            "language": "en"
        },
        {
            "link": "https://example.com/book2",
            "title": "Test Book 2",
            "author": "Test Author 2",
            "text": "This is the content of test book 2.",
            "language": "en"
        }
    ]

    dataset_path = "test_dataset.arrow"

    # Clean up any existing test file
    if os.path.exists(dataset_path):
        os.remove(dataset_path)

    # Test writing books one by one (simulating incremental updates)
    for i, book in enumerate(test_books):
        print(f"Adding book {i+1}: {book['title']}")

        # Create table for this book
        fields = ["link", "title", "author", "text", "language"]
        arr = {k: [book.get(k, "")] for k in fields}
        table = pa.table(arr)

        # Read existing data if file exists
        if os.path.exists(dataset_path):
            print("  Reading existing dataset...")
            with open(dataset_path, 'rb') as f:
                reader = ipc.RecordBatchFileReader(f)
                old = reader.read_all()
            table = pa.concat_tables([old, table])
            print(f"  Combined with {old.num_rows} existing rows")

        # Write updated table
        with open(dataset_path, 'wb') as f:
            writer = ipc.RecordBatchFileWriter(f, table.schema)
            writer.write_table(table)
            writer.close()

        print(f"  Dataset now has {table.num_rows} rows")

    # Test reading the final dataset
    print("\nFinal dataset verification:")
    with open(dataset_path, 'rb') as f:
        reader = ipc.RecordBatchFileReader(f)
        final_table = reader.read_all()

    print(f"Total rows: {final_table.num_rows}")
    print(f"Schema: {final_table.schema}")

    # Print all book titles
    titles = final_table.column('title').to_pylist()
    print(f"Book titles: {titles}")

    # Check file size
    file_size = os.path.getsize(dataset_path)
    print(f"File size: {file_size} bytes")

    # Clean up
    os.remove(dataset_path)
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_arrow_dataset()
