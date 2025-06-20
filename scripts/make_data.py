from dataclasses import dataclass
import os
import shutil
import re
import sys

DOCS_DIR = os.environ.get("DOCS_DIR", os.path.join(os.path.dirname(__file__), "..", "siv3d.docs"))
OUT_DIR = os.environ.get("OUT_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))

MARKDOWN_MAPPINGS = {
    "en-us/docs": "en-us",
    #"ja-jp/docs": "ja-jp",
}

HEADING_PATTERN = re.compile(r"^(#+) ")
ASCII_SYMBOLS = r"""`~!@#$%^&*()_-+={[}}|\:;"'<,>.?/"""
SPLIT_HEADING_LEVEL = 2  # Level of heading to split at (e.g., 2 for ## headings)

@dataclass
class Section:
    id: str
    headings: list[str]
    content: str
    is_empty: bool = True

def generate_section_id(heading: str) -> str:
    """
    Generate a unique section ID based on the headings.
    """
    return "-".join(heading.lower().translate(str.maketrans("", "", ASCII_SYMBOLS)).split(" "))

def split_sections(src: str) -> list[Section]:
    src = src.strip()
    if not src.startswith("#"):
        return []

    # Build sections from lines
    lines = src.splitlines()
    headings: list[str] = []
    sections: list[Section] = []
    for line in lines:
        heading_match = HEADING_PATTERN.match(line)
        
        heading_level = len(heading_match.group(1)) if heading_match else 0

        if heading_match and heading_level <= SPLIT_HEADING_LEVEL:
            # Start a new section
            
            heading_text = line[heading_level:].strip()

            # Ensure headings list is the correct length
            while len(headings) >= heading_level:
                headings.pop()
            while len(headings) < heading_level:
                headings.append("")
            headings[-1] = heading_text
            
            # If the last section is not empty, append a new empty section
            if len(sections) == 0 or not sections[-1].is_empty:
                sections.append(Section(
                    id="",
                    headings=[],
                    content="",
                    is_empty=True
                ))
            
            # Initialize the new section
            content = ""
            for i in range(heading_level):
                content += f"{'#' * (i + 1)} {headings[i]}\n"
            last_section = sections[-1]
            last_section.id = generate_section_id(heading_text)
            last_section.headings = headings.copy()
            last_section.content = content
        else:
            # Continue the current section
            last_section = sections[-1]
            last_section.content += f"{line}\n"
            last_section.is_empty &= len(line.strip()) == 0

    # Remove last section if it is empty
    if sections and sections[-1].is_empty:
        sections.pop()
    
    return sections

def clear_data():
    """
    Clear the data directory by removing all files and directories.
    """
    shutil.rmtree(OUT_DIR)

def make_data():
    if os.path.exists(OUT_DIR):
        clear_data()
    
    for src_dir, dest_dir in MARKDOWN_MAPPINGS.items():
        src_dir = os.path.join(DOCS_DIR, src_dir)
        dest_dir = os.path.join(OUT_DIR, dest_dir)
        for root, _, files in os.walk(src_dir):
            for filename in files:
                basename, ext = os.path.splitext(filename)
                if ext != ".md":
                    continue

                src_path = os.path.join(root, filename)
                rel_path = os.path.relpath(src_path, src_dir)
                target_dir = os.path.join(dest_dir, os.path.dirname(rel_path), basename)

                os.makedirs(target_dir, exist_ok=True)

                with open(src_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    sections = split_sections(content)
                    if not sections:
                        continue

                    # Write each section to a separate file
                    for section in sections:
                        section_path = os.path.join(target_dir, f"{section.id}.md")
                        with open(section_path, "w", encoding="utf-8") as section_file:
                            section_file.write(section.content)

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ["clear", "make"]:
        print(f"Usage: python {sys.argv[0]} [clear|make]")
        sys.exit(1)
    
    if sys.argv[1] == "clear":
        clear_data()
    elif sys.argv[1] == "make":
        make_data()
