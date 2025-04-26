import os
import json
from pathlib import Path

def merge_drum_patterns(input_dir: Path, output_file: Path) -> None:
    """
    Merge all JSON drum pattern files in input_dir into a single JSON file at output_file.

    Each file in input_dir should be named <genre>-<style>.json and contain a JSON structure
    with a single top-level genre key mapping to styles and patterns.
    The merged output will organize patterns under their respective genres and styles.
    """
    merged: dict = {}

    # Ensure input directory exists
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input directory '{input_dir}' does not exist or is not a directory.")

    # Iterate over all JSON files in the input directory
    for file in input_dir.glob("*.json"):
        # Expect filename like "genre-style.json"
        name_parts = file.stem.split("-", 1)
        if len(name_parts) != 2:
            print(f"Skipping file with unexpected name format: {file.name}")
            continue
        genre, style = name_parts

        # Load JSON content
        try:
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in file {file.name}: {e}")
            continue

        # Ensure structure matches expectation
        if genre not in data or style not in data[genre]:
            # if file data nested differently, try to adapt
            # e.g., data: { genre: { style: [...] } }
            print(f"Unexpected data structure in {file.name}, expected key '{genre}' with subkey '{style}'. Skipping.")
            continue

        patterns = data[genre][style]

        # Initialize genre and style in merged dict
        if genre not in merged:
            merged[genre] = {}
        if style not in merged[genre]:
            merged[genre][style] = []

        # Append patterns, avoiding duplicate pattern_ids
        existing_ids = {p.get("pattern_id") for p in merged[genre][style]}
        for patt in patterns:
            pid = patt.get("pattern_id")
            if pid in existing_ids:
                print(f"Duplicate pattern_id '{pid}' in {file.name}, skipping.")
            else:
                merged[genre][style].append(patt)

    # Write merged output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"Merged drum patterns written to {output_file}")

def main():
    print('Merging json files...')
    
    # Define input and output paths relative to script location
    base_dir = Path(__file__).resolve().parent
    input_directory = base_dir / "drum_patterns"
    output_path = base_dir / "drum_patterns.json"

    merge_drum_patterns(input_directory, output_path)


if __name__ == "__main__":
    main()
