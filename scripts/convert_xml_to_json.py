import xml.etree.ElementTree as ET
import json
import re
import os
import sys
from pathlib import Path

LANGUAGES = {
    'english': 'en',
    'amharic': 'am',
    'geez': 'gez',
    'deutsch': 'de',
}

# Geez numeral mapping
GEEZ_NUMERALS = {
    '፩': 1, '፪': 2, '፫': 3, '፬': 4, '፭': 5,
    '፮': 6, '፯': 7, '፰': 8, '፱': 9, '፲': 10,
    '፲፩': 11, '፲፪': 12, '፲፫': 13, '፲፬': 14, '፲፭': 15,
    '፲፮': 16, '፲፯': 17, '፲፰': 18, '፲፱': 19, '፳': 20,
    '፳፩': 21, '፳፪': 22, '፳፫': 23, '፳፬': 24, '፳፭': 25,
    '፳፮': 26, '፳፯': 27, '፳፰': 28, '፳፱': 29, '፴': 30,
    '፴፩': 31, '፴፪': 32, '፴፫': 33, '፴፬': 34, '፴፭': 35,
    '፴፮': 36, '፴፯': 37, '፴፰': 38, '፴፱': 39, '፵': 40,
    '፵፩': 41, '፵፪': 42, '፵፫': 43, '፵፬': 44, '፵፭': 45,
    '፵፮': 46, '፵፯': 47, '፵፰': 48, '፵፱': 49, '፶': 50,
    '፶፩': 51, '፶፪': 52, '፶፫': 53, '፶፬': 54, '፶፭': 55,
    '፶፮': 56, '፶፯': 57, '፶፰': 58, '፶፱': 59, '፷': 60,
}

# All chapters with their XML key prefix
# Note: XML uses "wedensday" (typo) not "wednesday"
CHAPTERS = [
    {'id': 'daily', 'key': 'daily'},
    {'id': 'monday', 'key': 'monday'},
    {'id': 'tuesday', 'key': 'tuesday'},
    {'id': 'wednesday', 'key': 'wedensday'},
    {'id': 'thursday', 'key': 'thursday'},
    {'id': 'friday', 'key': 'friday'},
    {'id': 'saturday', 'key': 'saturday'},
    {'id': 'sunday', 'key': 'sunday'},
    {'id': 'anqetse_birhan', 'key': 'anqetse_birhan'},
    {'id': 'yiwedswea_melaekt', 'key': 'yiwedswea_melaekt'},
    {'id': 'melka_mariam', 'key': 'melka_mariam'},
    {'id': 'melka_eyesus', 'key': 'melka_eyesus'},
    {'id': 'melka_edom', 'key': 'melka_edom'},
]

# Button keys for localized chapter names
CHAPTER_BUTTON_KEYS = {
    'daily': 'home_day_zeweter_button',
    'monday': 'home_day_monday_button',
    'tuesday': 'home_day_tuesday_button',
    'wednesday': 'home_day_wednesday_button',
    'thursday': 'home_day_thursday_button',
    'friday': 'home_day_friday_button',
    'saturday': 'home_day_saturday_button',
    'sunday': 'home_day_sunday_button',
    'anqetse_birhan': 'home_day_anqetse_birhan_button',
    'yiwedswea_melaekt': 'home_day_yiwedsewa_melaekt_button',
    'melka_mariam': 'home_day_melka_mariam_button',
    'melka_eyesus': 'home_day_melka_eyesus_button',
    'melka_edom': 'home_day_melka_edom_button',
}


def clean_text(text):
    """Remove \\n, \\t literals and collapse excessive whitespace."""
    if not text:
        return ''
    text = text.replace('\\n', ' ')
    text = text.replace('\\t', ' ')
    text = re.sub(r'[ \t]+', ' ', text)
    lines = [line.strip() for line in text.splitlines()]
    text = ' '.join(line for line in lines if line)
    return text.strip()


# Words that should stay uppercase even in sentence case
UPPERCASE_WORDS = {'O', 'I'}

# Small words that should stay lowercase in title case (unless first/last word)
TITLE_CASE_SMALL = {
    'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'yet', 'so',
    'in', 'on', 'at', 'to', 'of', 'by', 'up', 'as', 'is', 'it',
    'with', 'from', 'into', 'upon',
    'ein', 'eine', 'der', 'die', 'das', 'und', 'oder', 'am', 'im',
    'an', 'auf', 'für', 'von', 'zu', 'mit', 'dem', 'den', 'des',
}


def to_title_case(text):
    """Convert text to Title Case for chapter/section titles (en/de).

    Capitalizes first letter of significant words. Small words like articles,
    conjunctions, and short prepositions stay lowercase unless first or last.
    """
    if not text:
        return text
    words = text.split()
    result = []
    for i, word in enumerate(words):
        # Preserve words inside parentheses as-is after capitalizing first letter
        if word.startswith('(') and len(word) > 1:
            inner = word[1:].rstrip(')')
            closing = ')' if word.endswith(')') else ''
            result.append('(' + inner.capitalize() + closing)
            continue
        lower = word.lower()
        # First and last word always capitalized
        if i == 0 or i == len(words) - 1:
            result.append(word.capitalize())
        elif lower in TITLE_CASE_SMALL:
            result.append(lower)
        else:
            result.append(word.capitalize())
    return ' '.join(result)


def to_sentence_case(text):
    """Convert text to Sentence case for body content (en/de).

    - ALL-CAPS words (2+ letters) become Title Case (proper nouns like ADAM -> Adam)
    - Single uppercase letter words 'O' and 'I' stay uppercase
    - First letter of each sentence is uppercase
    """
    if not text:
        return text

    def convert_word(word):
        # Strip leading/trailing punctuation for checking
        leading = ''
        trailing = ''
        core = word
        while core and not core[0].isalpha():
            leading += core[0]
            core = core[1:]
        while core and not core[-1].isalpha():
            trailing = core[-1] + trailing
            core = core[:-1]
        if not core:
            return word
        # Keep 'O' and 'I' uppercase
        if core in UPPERCASE_WORDS:
            return word
        # ALL-CAPS word (2+ letters) -> Title Case (proper noun)
        if len(core) >= 2 and core.isupper():
            return leading + core.capitalize() + trailing
        return word

    # Split into sentences (on . ! ? followed by space)
    # Process each sentence
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result_sentences = []
    for sentence in sentences:
        words = sentence.split()
        if not words:
            result_sentences.append(sentence)
            continue
        converted = [convert_word(w) for w in words]
        # Ensure first word starts with uppercase
        if converted[0] and converted[0][0].islower():
            converted[0] = converted[0][0].upper() + converted[0][1:]
        result_sentences.append(' '.join(converted))
    return ' '.join(result_sentences)


def geez_num_to_int(geez_str):
    """Convert a Geez numeral string to an integer."""
    if geez_str in GEEZ_NUMERALS:
        return GEEZ_NUMERALS[geez_str]
    # Try to parse compound Geez numerals (tens + units)
    geez_tens = '፲፳፴፵፶፷፸፹፺'
    geez_ones = '፩፪፫፬፭፮፯፰፱'
    if len(geez_str) == 2 and geez_str[0] in geez_tens and geez_str[1] in geez_ones:
        combined = geez_str
        if combined in GEEZ_NUMERALS:
            return GEEZ_NUMERALS[combined]
    return None


def split_into_sections(text):
    """Split prayer content into numbered sections using Geez numerals as primary delimiter,
    falling back to Arabic numerals."""
    if not text:
        return []

    cleaned = clean_text(text)
    if not cleaned:
        return []

    # Geez numeral characters for pattern
    geez_num_chars = '፩፪፫፬፭፮፯፰፱፲፳፴፵፶፷፸፹፺'

    # Try Geez numerals first: match patterns like ፩. or ፲፪.
    geez_pattern = r'([' + geez_num_chars + r']+)\.\s*'
    geez_matches = list(re.finditer(geez_pattern, cleaned))

    if geez_matches:
        return _extract_sections_from_matches(cleaned, geez_matches, is_geez=True)

    # Fall back to Arabic numerals: match patterns like 1. or 12.
    arabic_pattern = r'(?:^|\s)(\d+)\.\s+'
    arabic_matches = list(re.finditer(arabic_pattern, cleaned))

    if arabic_matches:
        return _extract_sections_from_matches(cleaned, arabic_matches, is_geez=False)

    # No numbered sections found, return the whole text as section 1
    return [{'section': 1, 'text': cleaned}]


def _extract_sections_from_matches(text, matches, is_geez):
    """Extract sections from regex matches."""
    sections = []
    for i, match in enumerate(matches):
        num_str = match.group(1)
        if is_geez:
            num = geez_num_to_int(num_str)
            if num is None:
                num = i + 1
        else:
            num = int(num_str)

        # Text starts after the match, ends at next match or end of string
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()

        if section_text:
            sections.append({'section': num, 'text': section_text})

    return sections


def parse_xml(xml_file):
    """Parse a strings.xml file and return a dict of name -> raw text."""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    content = {}
    for string_elem in root.findall('.//string'):
        name = string_elem.get('name')
        text = string_elem.text if string_elem.text else ''
        if text.strip():
            content[name] = text
    return content


def build_widase_mariam_json(base_dir):
    """Build the consolidated JSON from all language XML files."""
    all_content = {}
    for lang_dir, lang_code in LANGUAGES.items():
        xml_path = Path(base_dir) / lang_dir / 'strings.xml'
        if xml_path.exists():
            all_content[lang_code] = parse_xml(str(xml_path))
            print(f"  Parsed {xml_path}")
        else:
            print(f"  Warning: {xml_path} not found, skipping {lang_dir}")
            all_content[lang_code] = {}

    chapters = []
    for ch in CHAPTERS:
        header_key = f"reader_prayer_{ch['key']}_header_label"
        content_key = f"reader_prayer_{ch['key']}_label"
        button_key = CHAPTER_BUTTON_KEYS.get(ch['id'], '')

        # Build chapter_name from header labels
        chapter_name = {}
        for lang_code in LANGUAGES.values():
            lang_data = all_content.get(lang_code, {})
            name_text = lang_data.get(header_key, '') or lang_data.get(button_key, '')
            cleaned = clean_text(name_text) if name_text else None
            if cleaned and lang_code in ('en', 'de'):
                cleaned = to_title_case(cleaned)
            chapter_name[lang_code] = cleaned

        # Parse sections per language
        lang_sections = {}
        max_section = 0
        for lang_code in LANGUAGES.values():
            lang_data = all_content.get(lang_code, {})
            raw_content = lang_data.get(content_key, '')
            secs = split_into_sections(raw_content)
            lang_sections[lang_code] = {s['section']: s['text'] for s in secs}
            if secs:
                max_num = max(s['section'] for s in secs)
                max_section = max(max_section, max_num)

        # Merge sections across languages
        merged_sections = []
        for num in range(1, max_section + 1):
            text_obj = {}
            has_any = False
            for lang_code in LANGUAGES.values():
                t = lang_sections.get(lang_code, {}).get(num)
                if t and lang_code in ('en', 'de'):
                    t = to_sentence_case(t)
                    # If first section text matches chapter name, set to null
                    if num == 1 and t and chapter_name.get(lang_code):
                        if t.lower().strip().rstrip('.') == chapter_name[lang_code].lower().strip().rstrip('.'):
                            t = None
                text_obj[lang_code] = t
                if t:
                    has_any = True
            if has_any:
                merged_sections.append({
                    'section': num,
                    'text': text_obj,
                })

        chapters.append({
            'chapter': ch['id'],
            'chapter_name': chapter_name,
            'sections': merged_sections,
        })

    output = {
        'book_name': {
            'en': 'Widase Mariam',
            'am': 'ውዳሴ ማርያም',
            'gez': 'ውዳሴሃ ለእግዝእትነ ማርያም ወላዲተ አምላክ',
            'de': 'Lobpreis der Heiligen Maria',
        },
        'full_title': 'Wéddase égzéýténä Maryam déngél wäladitä amlak (Praise of our Lady Mary, the virgin genitrix of God)',
        'about': {
            'description': 'Wéddase Maryam (Praise of Mary) is a significant liturgical office within the Ethiopian Orthodox Täwahédo Church (EOTC). It constitutes one of three major offices dedicated to Saint Mary, alongside the Anqäsä bérhan and Argänonä Maryam. It comprises blessings and praise of the Mother of God and intercessions to her, organized into seven sections corresponding to each weekday.',
            'origins': 'Ethiopian tradition attributes the work to either Ephrem the Syrian (d. 373) or Simeon the Potter, a Syrian poet from the 5th-6th century. However, scholars find these ascriptions questionable. The actual lineage traces through Coptic sources. A Bohairic Theotokion (hymn to Mary) containing influences from Ephrem\'s compositions and Greek-Byzantine models served as the original template. An Arabic intermediary translation preceded the Ethiopic version, likely produced during the second half of the 14th century by abba Sälama the Translator.',
            'manuscript_tradition': 'The work achieved considerable popularity, with abundant manuscripts existing across libraries. It frequently appears in Psalter appendices alongside Biblical canticles and other liturgical texts. The Mééraf included the composition in its second section. Educational significance remained substantial, as andémta (interpretive commentary) developed around it as required teaching material in mäshaf bet (church schools).',
            'theological_significance': 'The Wéddase Maryam\'s theological importance profoundly shaped subsequent liturgies, including the Anaphora of Pseudo-Cyriacus of Behnesa and related Marian liturgical texts.',
        },
        'chapters': chapters,
    }

    return output


if __name__ == '__main__':
    base_dir = Path('data/xml')
    if not base_dir.exists():
        print(f"Error: {base_dir} directory not found!")
        print("Run this script from the project root directory.")
        sys.exit(1)

    print("Converting XML to JSON...")
    result = build_widase_mariam_json(base_dir)

    output_file = Path('data/widase_mariam.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    total_sections = sum(len(c['sections']) for c in result['chapters'])
    print(f"\nGenerated {output_file}")
    print(f"  Chapters: {len(result['chapters'])}")
    print(f"  Total sections: {total_sections}")
    for ch in result['chapters']:
        print(f"    {ch['chapter']}: {len(ch['sections'])} sections")
