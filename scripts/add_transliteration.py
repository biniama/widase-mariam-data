#!/usr/bin/env python3
"""
Add Ge'ez transliteration to widase_mariam.json for all chapters.

Reads transliteration data from data/geez_translitration/widase_mariam_transliteration.json
and merges it into data/widase_mariam.json, matching by chapter name and section number.
The daily chapter already has transliteration; this script adds it to the weekday chapters
(monday through sunday).
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

MAIN_FILE = os.path.join(PROJECT_DIR, "data", "widase_mariam.json")
MAIN_MIN_FILE = os.path.join(PROJECT_DIR, "data", "widase_mariam.min.json")
TRANSLIT_FILE = os.path.join(PROJECT_DIR, "data", "geez_translitration", "widase_mariam_transliteration.json")


def main():
    with open(MAIN_FILE, "r", encoding="utf-8") as f:
        main_data = json.load(f)

    with open(TRANSLIT_FILE, "r", encoding="utf-8") as f:
        translit_data = json.load(f)

    # Build lookup: chapter -> section_number -> transliteration text
    translit_lookup = {}
    for chapter in translit_data["chapters"]:
        chapter_name = chapter["chapter"]
        translit_lookup[chapter_name] = {}
        for section in chapter["sections"]:
            translit_lookup[chapter_name][section["section"]] = section["transliteration"]

    # Update main data
    updated = 0
    skipped = 0
    for chapter in main_data["chapters"]:
        day = chapter["chapter"]
        if day not in translit_lookup:
            continue

        for section in chapter["sections"]:
            sec_num = section["section"]
            if sec_num not in translit_lookup[day]:
                print(f"  Warning: no transliteration for {day} section {sec_num}")
                continue

            if "text" not in section:
                print(f"  Warning: {day} section {sec_num} has no 'text' field")
                continue

            if "transliteration" in section["text"]:
                skipped += 1
            else:
                section["text"]["transliteration"] = translit_lookup[day][sec_num]
                updated += 1

    # Write back
    with open(MAIN_FILE, "w", encoding="utf-8") as f:
        json.dump(main_data, f, ensure_ascii=False, indent=2)

    # Also update the minified version if it exists
    if os.path.exists(MAIN_MIN_FILE):
        with open(MAIN_MIN_FILE, "w", encoding="utf-8") as f:
            json.dump(main_data, f, ensure_ascii=False, separators=(",", ":"))
        print(f"Also updated {MAIN_MIN_FILE}")

    print(f"\nDone! Added transliteration to {updated} sections, skipped {skipped} (already present).")


if __name__ == "__main__":
    main()
