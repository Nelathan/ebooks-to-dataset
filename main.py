import os
from tqdm import tqdm

from src.github_api import fetch_repo_list
from src.downloader import download_repo, cleanup_repo
from src.opf_parser import parse_opf_and_extract_text
from src.dataset import update_dataset
from src.progress import load_books_list, save_books_list

BOOKS_LIST_FILE = "books_list.json"
DATASET_FILE = "books_dataset.arrow"
TMP_ROOT = "tmp_books"

def main():
    """
    Orchestrate the dataset initialization process:
    1. Fetch repo list.
    2. Compare to old list.
    3. For each repo to process:
        - Download
        - Parse and extract
        - Update dataset
        - Cleanup
    """
    os.makedirs(TMP_ROOT, exist_ok=True)
    fresh_repos = fetch_repo_list()

    # Load previous successful list
    old_list = load_books_list(BOOKS_LIST_FILE)
    # Only process if not present or updated
    to_process = []
    for repo in fresh_repos:
        old = old_list.get(repo["name"])
        if not old or repo["updated_at"] > old["updated_at"]:
            to_process.append(repo)
    print(f"{len(to_process)} repos to process (new or updated).")

    successful_repos = dict(old_list)
    try:
        for repo in tqdm(to_process, desc="Processing books"):
            tmp_dir = os.path.join(TMP_ROOT, repo["name"])
            try:
                download_repo(repo["clone_url"], tmp_dir, branch=repo.get("default_branch", "master"))
                epub_dir = os.path.join(tmp_dir, "src", "epub")
                if not os.path.exists(epub_dir):
                    print(f"src/epub not found in {repo['name']}, skipping.")
                    continue
                book = parse_opf_and_extract_text(epub_dir)
                if not book or not book.get("text"):
                    print(f"Failed to extract book text for {repo['name']}, skipping.")
                    continue
                book_entry = {
                    "link": repo["link"],
                    "title": book["title"] or "",
                    "author": book["author"] or "",
                    "text": book["text"],
                    "language": book["language"] or ""
                }
                update_dataset(book_entry, DATASET_FILE)
                successful_repos[repo["name"]] = repo
                save_books_list(successful_repos, BOOKS_LIST_FILE)
                cleanup_repo(tmp_dir)


            except Exception as e:
                print(f"Exception for {repo['name']}: {e}")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Cleaning up and exiting.")
    finally:
        pass
    print("Dataset update complete.")

if __name__ == "__main__":
    main()
