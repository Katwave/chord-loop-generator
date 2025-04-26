import os
import json
import mido
import time
from collections import defaultdict
import merge_json_data

# Mapping from folder names to JSON instrument keys
INSTRUMENT_MAPPING = {
    'kicks': 'Kick',
    'snares': 'Snare',
    'claps': 'Clap',
    'hi-hats': 'HiHat',
    'open-hats': 'OpenHat',
    'percussions': 'Percussion'
}

def main():
    genre = 'house'
    style = 'makompo'

    # Genre at index 0, style at index 1
    genre_style_list = [
        ['house', 'makompo'], 
        ['hiphop', 'trap'],
        ['hiphop', 'drill'],
    ]

    for genre, style in genre_style_list:
        root_dir = f'assets/midi/{genre}/{style}'
        patterns = defaultdict(dict)

        # Process all MIDI files in subdirectories
        for instrument_folder, json_key in INSTRUMENT_MAPPING.items():
            instrument_dir = os.path.join(root_dir, instrument_folder)
            
            if not os.path.exists(instrument_dir):
                print(f'instrument_dir "{instrument_dir}" does not exist')
                continue

            for filename in os.listdir(instrument_dir):
                if filename.endswith('.mid'):
                    midi_path = os.path.join(instrument_dir, filename)
                    inspired_by = os.path.splitext(filename)[0]
                    # print('inspired_by:', inspired_by)
                    
                    # Process MIDI file to get pattern
                    pattern = process_midi(midi_path)
                    
                    # Add to patterns dictionary
                    patterns[inspired_by][json_key] = pattern

        # Create output JSON structure
        output = {
            f"{genre}": {
                f"{style}": []
            }
        }

        # Generate pattern entries with sequential IDs
        pattern_number = 1
        for inspired_by, instruments in patterns.items():
            pattern_entry = {
                "pattern_id": f"f{genre}_{style}_{pattern_number}",
                "inspired_by": inspired_by,
                **instruments
            }
            output[f"{genre}"][f"{style}"].append(pattern_entry)
            pattern_number += 1

        # Save to JSON file
        with open(os.path.join('json-data', 'drum_patterns', f'{genre}-{style}.json'), 'w') as f:
            json.dump(output, f, indent=2)
    
    print('Drum Pattern json files created...')

    # Merge the json files created
    time.sleep(1)
    merge_json_data.main()

def process_midi(midi_path):
    try:
        mid = mido.MidiFile(midi_path)
    except:
        return [0] * 64  # Return empty pattern for invalid files

    ticks_per_beat = mid.ticks_per_beat
    note_ticks = []
    current_tick = 0

    # Collect all note-on events
    for track in mid.tracks:
        for msg in track:
            current_tick += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                note_ticks.append(current_tick)

    # Calculate steps (64 steps = 2 bars of 16th notes)
    ticks_per_step = ticks_per_beat / 4  # 16th notes
    pattern = [0] * 64

    for tick in note_ticks:
        step = int(tick / ticks_per_step) % 64
        if 0 <= step < 64:
            pattern[step] = 1

    return pattern

if __name__ == '__main__':
    main()
    