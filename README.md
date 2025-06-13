# Standard Ebooks Dataset Builder

This project builds a high-quality dataset of public domain books from [Standard Ebooks](https://standardebooks.org) for LLM pretraining and research.

## Features

- Fetches all book repositories from the Standard Ebooks GitHub organization.
- Downloads only the `src/epub` folder of each repo (using sparse checkout).
- Parses the reading order from `content.opf` and extracts the full book text in the correct order.
- Skips common metadata and structural files (e.g., imprint, colophon, uncopyright, dedication, index, etc.) and obvious copyright pages. Includes narrative and structural elements like parts, volumes, and endnotes.
- Stores each book as a single entry in an Apache Arrow dataset (`books_dataset.arrow`), with fields:
  `link`, `title`, `author`, `text`, `language`.
- Maintains a `books_list.json` to track successfully processed books and avoid redundant work.
- Robust to interruptions: progress is saved after each book.
- Designed for incremental updates—only new or updated books are processed.

## Usage

1. **Install dependencies**
   Use [uv](https://github.com/astral-sh/uv) or your preferred tool:
   ```
   uv pip install -r requirements.txt
   ```

2. **Set your GitHub token**
   To avoid API rate limits, set a GitHub personal access token:
   ```
   export GITHUB_TOKEN=ghp_...yourtoken...
   ```

3. **Run the dataset builder**
   ```
   uv run main.py
   ```

   - The script will fetch the latest repo list, process new/updated books, and update the dataset and book list incrementally.
   - If interrupted, rerun to continue where you left off.

## Output

- `books_dataset.arrow` — The dataset file, one row per book.
- `books_list.json` — Tracks processed books and their update dates.

## Customization

- To debug or process only a subset, adjust the fetch logic in `main.py`.
- To adjust the filtering of included/excluded sections, edit the keyword lists and logic in the `parse_opf_and_extract_text` function in `src/opf_parser.py`.

## License

All code in this repo is MIT licensed. Book content is public domain, but check [Standard Ebooks](https://standardebooks.org) for details.
