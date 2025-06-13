# instructions
fetch all repos available in https://github.com/standardebooks
save a list with link, type, updated_date
filter by type HTML
compare to old list, drop if updated_date is the same as the old list, keep if updated_date is newer or not present
goal is to create a dataset of all standardebooks books for llm continued pretraining.
for book in books:
    - download repo without history
    - only folder src/epub if possible
    - reference ./consolidator.py for parsing, but dont split the data. the whole book should be one text entry in the dataset
    - theres a src/epub/content.opf
    - it references the xhtml files in the text subfolder, use this order
    - use titlepage and chapters, but drop imprint, colophon and uncopyright
    - read books pyarrow file or create a new one if not present
    - add a entry for the book to it
    - use those fields: link, title, author, text, language
    - save the arrow file
    - delete the repo
