import json
import sys
from pathlib import Path


def minify(input_path, output_path=None):
    """Minify a JSON file by removing all whitespace."""
    if output_path is None:
        p = Path(input_path)
        output_path = p.with_suffix('.min.json')

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

    original_size = Path(input_path).stat().st_size
    minified_size = Path(output_path).stat().st_size
    reduction = (1 - minified_size / original_size) * 100

    print(f"Original:  {original_size:,} bytes")
    print(f"Minified:  {minified_size:,} bytes")
    print(f"Reduction: {reduction:.1f}%")
    print(f"Output:    {output_path}")


if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'data/widase_mariam.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    minify(input_file, output_file)
