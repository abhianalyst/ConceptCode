import json
import re
from pathlib import Path


FILES = [
    Path("data/books/biology/biology_11.json"),
    Path("data/books/biology/biology_12.json"),
]


for file_path in FILES:
    print()
    print("=" * 70)
    print(file_path)
    print("=" * 70)

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    document = data["document"]

    print("Filename:", document["filename"])
    print("Pages:", document["page_count"])
    print()

    chapter_pattern = re.compile(
        r"^(CHAPTER|Chapter)\s+\d+",
        re.IGNORECASE,
    )

    matches = []

    for page in data["pages"]:
        for line in page["text"].splitlines():
            line = line.strip()

            if chapter_pattern.search(line):
                matches.append(
                    (page["page_number"], line)
                )

    print("Possible chapter headings:")
    print()

    if not matches:
        print("No CHAPTER headings found.")
    else:
        for page_number, line in matches:
            print(f"PAGE {page_number}: {line}")

    print()