import re
from pathlib import Path
from lxml.etree import parse as etree_parse
from markdownify import markdownify as md

def parse_opf_and_extract_text(epub_path, max_files=None):
    """
    Parse src/epub/content.opf to get reading order.
    Extract title, author, language, and book text (using referenced xhtml files in order).
    Output book text as Markdown using markdownify.
    Only the first `max_files` valid content files are included.
    """
    book_dir = Path(epub_path).parent.parent.name
    opf_file = Path(epub_path) / "content.opf"
    if not opf_file.exists():
        print(f"DEBUG: OPF file not found at {opf_file}")
        return None

    tree = etree_parse(str(opf_file))
    ns = {"opf": "http://www.idpf.org/2007/opf", "dc": "http://purl.org/dc/elements/1.1/"}
    title = tree.findtext(".//dc:title", namespaces=ns)
    author = tree.findtext(".//dc:creator", namespaces=ns)
    language = tree.findtext(".//dc:language", namespaces=ns)
    manifest = {item.get("id"): item.get("href") for item in tree.findall(".//opf:item", namespaces=ns)}
    spine = [item.get("idref") for item in tree.findall(".//opf:itemref", namespaces=ns)]

    # Map idrefs to file paths
    files = []
    for idref in spine:
        href = manifest.get(idref)
        if href:
            file_path = Path(epub_path) / href
            files.append(file_path)

    # Only filter out the most obvious metadata files
    drop_keywords = ["imprint", "colophon", "uncopyright", "titlepage", "dedication", "acknowledgments", "foreword", "preface", "epigraph", "afterword", "appendix", "glossary", "index", "bibliography", "toc", "cover", "license"]
    keep_files = []
    for f in files:
        name = f.name.lower()
        if any(k in name for k in drop_keywords):
            continue
        keep_files.append(f)

    # Only process the first `max_files` valid files (or all if max_files is None)
    if max_files is not None:
        keep_files = keep_files[:max_files]
    if len(keep_files) == 0:
        print("WARNING: No files to process after filtering")

    text_parts = []
    for f in keep_files:
        if not f.exists():
            continue
        with open(f, "r", encoding="utf-8", errors='replace') as xf:
            file_content = xf.read()
            file_content = re.sub(r'<\?xml[^>]*\?>', '', file_content)

            # Only skip obvious copyright pages
            if "copyright" in file_content.lower() and "all rights reserved" in file_content.lower():
                preview = file_content[:120].replace('\n', '\\n')
                print(f"SKIP [{book_dir}]: {f.name} (copyright page) - {preview}...")
                continue

            # Strip HTML head section that might contain duplicate title
            body_match = re.search(r'<body[^>]*>(.*?)</body>', file_content, re.DOTALL)
            if body_match:
                file_content = body_match.group(1)

            # Markdownify conversion
            def custom_md_tag(tag, name, value):
                if name == "p":
                    return "\n\n" + value + "\n\n"
                if name == "hr":
                    return "\n\n---\n\n"
                return None

            markdown = md(
                file_content,
                convert=['p', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'em', 'i', 'b', 'strong', 'abbr', 'blockquote', 'code', 'pre'],
                heading_style="ATX",
                bullets="-",
                custom_tags=custom_md_tag
            )

            # Clean up excessive blank lines
            markdown = re.sub(r'\n{3,}', '\n\n', markdown)
            markdown = markdown.strip()

            if markdown:
                text_parts.append(markdown)

    # Join all parts with double line breaks
    full_text = '\n\n'.join(text_parts)
    full_text = re.sub(r'\n{3,}', '\n\n', full_text)
    full_text = full_text.strip()

    return {
        "title": title,
        "author": author,
        "language": language,
        "text": full_text
    }
