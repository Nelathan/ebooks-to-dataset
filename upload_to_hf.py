import os
import pyarrow as pa
import pyarrow.ipc as ipc
from datasets import Dataset
from huggingface_hub import login

# --- Configuration ---
DATASET_FILE = "books_dataset.arrow"
HF_REPO_ID = "Nelathan/standardebooks"

def upload_dataset_to_huggingface():
    """
    Loads the Arrow dataset from disk and uploads it to the Hugging Face Hub.
    """
    print("Logging in to Hugging Face Hub...")
    try:
        login(new_session=False)
        print("Successfully logged in.")
    except Exception as e:
        print(f"Error logging in to Hugging Face Hub. Please run 'huggingface-cli login' or set HF_TOKEN. Details: {e}")
        return

    if not os.path.exists(DATASET_FILE):
        print(f"Error: Dataset file not found at {DATASET_FILE}. Please run main.py first to generate it.")
        return

    try:
        print(f"Loading data from {DATASET_FILE}...")
        # Use pyarrow.ipc.RecordBatchFileReader to read the .arrow file
        with pa.memory_map(DATASET_FILE, 'r') as source:
             reader = ipc.RecordBatchFileReader(source)
             pa_table = reader.read_all()

        dataset = Dataset(pa_table)
        print(f"Successfully loaded dataset with {len(dataset)} rows.")
        print(f"Dataset size in memory: {pa_table.get_total_buffer_size() / (1024*1024):.2f} MB")

        print(f"Uploading dataset to {HF_REPO_ID}...")
        dataset.push_to_hub(HF_REPO_ID)
        print("Dataset uploaded successfully!")

    except FileNotFoundError:
        print(f"Error: Dataset file not found at {DATASET_FILE}.")
    except Exception as e:
        print(f"An error occurred during upload: {e}")
        print("Please ensure you have created the dataset repository on Hugging Face Hub.")


if __name__ == "__main__":
    upload_dataset_to_huggingface()
