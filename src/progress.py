import os
import json

BOOKS_LIST_FILE = "books_list.json"

def load_books_list(path=BOOKS_LIST_FILE):
    """
    Load the books_list.json file.
    Returns a dict mapping repo name to repo info.
    If the file does not exist, returns an empty dict.
    """
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            # Support both list and dict formats
            if isinstance(data, list):
                return {r["name"]: r for r in data if "name" in r}
            elif isinstance(data, dict):
                return data
            else:
                return {}
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return {}

def save_books_list(books_dict, path=BOOKS_LIST_FILE):
    """
    Save the books_list.json file.
    Accepts a dict mapping repo name to repo info.
    Writes as a list of repo info dicts.
    """
    books_list = list(books_dict.values())
    with open(path, "w", encoding="utf-8") as f:
        json.dump(books_list, f, indent=2, ensure_ascii=False)
