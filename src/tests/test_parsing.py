#!/usr/bin/env python3
"""
Test script to simulate real XHTML parsing and test formatting improvements.
This creates mock XHTML content similar to what Standard Ebooks uses.
"""

import tempfile
from pathlib import Path
from bs4 import BeautifulSoup
import re

def create_mock_xhtml_files():
    """Create mock XHTML files that simulate Standard Ebooks structure"""

    # Mock titlepage.xhtml (this should be filtered out)
    titlepage_content = '''<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/, se: https://standardebooks.org/vocab/1.0" xml:lang="en-US">
<head>
    <title>Titlepage</title>
</head>
<body epub:type="frontmatter z3998:fiction">
    <section id="titlepage" epub:type="titlepage">
        <h1 epub:type="fulltitle">Dubliners</h1>
        <p>By</p>
        <h2 epub:type="z3998:author">James Joyce</h2>
        <p>.</p>
    </section>
</body>
</html>'''

    # Mock chapter content
    chapter1_content = '''<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/, se: https://standardebooks.org/vocab/1.0" xml:lang="en-US">
<head>
    <title>The Sisters</title>
</head>
<body epub:type="bodymatter z3998:fiction">
    <section id="the-sisters" epub:type="chapter">
        <h2 epub:type="title">The Sisters</h2>
        <p>There was no hope for him this time: it was the third stroke. Night after night I had passed the house (it was vacation time) and studied the lighted square of window: and night after night I had found it lighted in the same way, faintly and evenly.</p>
        <p>If he was dead, I thought, I would see the reflection of candles on the darkened blind for I knew that two candles must be set at the head of a corpse. He had often said to me: "I am not long for this world," and I had thought his words idle. Now I knew they were true.</p>
        <p>Every night as I gazed up at the window I said softly to myself the word <em>paralysis</em>. It had always sounded strangely in my ears, like the word <em>gnomon</em> in the Euclid and the word <em>simony</em> in the Catechism.</p>
    </section>
</body>
</html>'''

    # Mock second chapter
    chapter2_content = '''<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" epub:prefix="z3998: http://www.daisy.org/z3998/2012/vocab/structure/, se: https://standardebooks.org/vocab/1.0" xml:lang="en-US">
<head>
    <title>An Encounter</title>
</head>
<body epub:type="bodymatter z3998:fiction">
    <section id="an-encounter" epub:type="chapter">
        <h2 epub:type="title">An Encounter</h2>
        <p>It was Joe Dillon who introduced the Wild West to us. He had a little library made up of old numbers of <i>The Union Jack</i>, <i>Pluck</i> and <i>The Halfpenny Marvel</i>. Every evening after school we met in his back garden and arranged Indian battles.</p>
        <p>He and his fat young brother Leo, the idler, held the loft of the stable while we tried to carry it by storm; or we fought a pitched battle on the grass.</p>
    </section>
</body>
</html>'''

    return {
        'titlepage.xhtml': titlepage_content,
        'the-sisters.xhtml': chapter1_content,
        'an-encounter.xhtml': chapter2_content
    }

def test_current_parsing():
    """Test the current parsing logic"""
    print("=== Testing Current XHTML Parsing ===\n")

    mock_files = create_mock_xhtml_files()

    # Create temporary directory and files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Write mock files
        for filename, content in mock_files.items():
            file_path = temp_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        # Test parsing each file
        for filename in mock_files.keys():
            print(f"--- Parsing {filename} ---")
            file_path = temp_path / filename

            # Current parsing logic (from main.py)
            with open(file_path, "r", encoding="utf-8") as xf:
                soup = BeautifulSoup(xf, "lxml-xml")

                # Remove unwanted tags
                for tag in soup(["style", "script", "footer", "nav", "header"]):
                    tag.decompose()

                # Get text content with current method
                text = soup.get_text(separator=" ", strip=True)

                # Apply current cleanup
                if text:
                    text = re.sub(r'\s+', ' ', text)
                    text = re.sub(r'\s*\.\s*$', '.', text)
                    text = text.strip()

                print(f"Length: {len(text)} characters")
                print(f"Content: {text[:200]}{'...' if len(text) > 200 else ''}")
                print()

def test_improved_parsing():
    """Test improved parsing logic"""
    print("=== Testing Improved XHTML Parsing ===\n")

    mock_files = create_mock_xhtml_files()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Write mock files
        for filename, content in mock_files.items():
            file_path = temp_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        # Simulate filtering titlepage
        keep_files = []
        drop_keywords = ["imprint", "colophon", "uncopyright", "titlepage"]

        for filename in mock_files.keys():
            name = filename.lower()
            if any(k in name for k in drop_keywords):
                print(f"Skipping {filename} (contains {[k for k in drop_keywords if k in name]})")
                continue
            keep_files.append(temp_path / filename)

        # Parse remaining files
        text_parts = []
        for file_path in keep_files:
            print(f"--- Parsing {file_path.name} ---")

            with open(file_path, "r", encoding="utf-8") as xf:
                soup = BeautifulSoup(xf, "lxml-xml")

                # Remove unwanted tags and elements
                for tag in soup(["style", "script", "footer", "nav", "header"]):
                    tag.decompose()

                # Better text extraction - preserve paragraph structure
                paragraphs = []

                # Extract title if present
                title_elem = soup.find(attrs={"epub:type": "title"}) or soup.find("h1") or soup.find("h2")
                if title_elem:
                    title_text = title_elem.get_text(strip=True)
                    if title_text and len(title_text) < 100:  # Reasonable title length
                        paragraphs.append(f"# {title_text}")

                # Extract paragraphs
                for p in soup.find_all('p'):
                    p_text = p.get_text(strip=True)
                    if p_text and len(p_text) > 10:  # Skip very short paragraphs
                        paragraphs.append(p_text)

                if paragraphs:
                    chapter_text = '\n\n'.join(paragraphs)
                    text_parts.append(chapter_text)
                    print(f"Extracted {len(paragraphs)} paragraphs")
                    print(f"Preview: {chapter_text[:200]}{'...' if len(chapter_text) > 200 else ''}")
                else:
                    print("No content extracted")
                print()

        # Combine all parts
        full_text = '\n\n---\n\n'.join(text_parts)  # Use separator between chapters

        print("=== Final Combined Text ===")
        print(f"Total length: {len(full_text)} characters")
        print(f"Number of chapters: {len(text_parts)}")
        print("\nFull text:")
        print("-" * 50)
        print(full_text)
        print("-" * 50)

if __name__ == "__main__":
    test_current_parsing()
    print("\n" + "="*60 + "\n")
    test_improved_parsing()
