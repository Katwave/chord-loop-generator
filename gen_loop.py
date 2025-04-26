# gen_loop.py (fixed version)
import json
import os
import random
from pydub import AudioSegment
import glob
import zipfile

# Configuration
DRUM_SAMPLES_DIR = "drum_samples"
JSON_INSTRUMENT_KEYS = {
    'Kick': 'Kick',
    'Snare': 'Snare',
    'HiHat': 'HiHat',
    'OpenHat': 'OpenHat',
    'Clap': 'Clap',
    'Percussion': 'percussion'
}
INSTRUMENT_FOLDERS = {
    'Kick': 'kicks',
    'Snare': 'snares',
    'HiHat': 'hi-hats',
    'OpenHat': 'open-hats',
    'Clap': 'claps',
    'Percussion': 'percussions'
}

with open("json-data/drum_patterns.json", "r") as f:
    drum_patterns = json.load(f)

def get_random_sample(instrument, genre):
    folder = INSTRUMENT_FOLDERS.get(instrument)
    if not folder:
        return None
    samples = glob.glob(os.path.join('assets', DRUM_SAMPLES_DIR, genre, folder, "*.wav"))
    return random.choice(samples) if samples else None

def process_pattern(pattern, required_length=64):
    """Expand pattern to required length safely"""
    if not pattern or len(pattern) == 0:
        return [0] * required_length
    repeats = required_length // len(pattern)
    remainder = required_length % len(pattern)
    return (pattern * repeats + pattern[:remainder])[:required_length]

def select_pattern_and_instruments(style_data, genre, inspired_by=None):
    """Select patterns with validation"""
    if inspired_by:
        filtered = [p for p in style_data if inspired_by.lower() in p['inspired_by'].lower()]
        selected_pattern = random.choice(filtered or style_data)
    else:
        selected_pattern = random.choice(style_data)

    instruments = {}
    for instr in INSTRUMENT_FOLDERS.keys():
        json_key = JSON_INSTRUMENT_KEYS[instr]
        pattern = selected_pattern.get(json_key, [])
        
        # Only add instrument if pattern is valid
        if pattern and len(pattern) > 0:
            sample = get_random_sample(instr, genre)
            if sample:
                instruments[instr] = {
                    'pattern': process_pattern(pattern),
                    'sample': sample
                }
    return instruments

def create_drum_loop(patterns, bpm=120):
    """Create loop with pattern validation"""
    beat_duration = 60 * 1000 / bpm
    step_duration = beat_duration / 4
    total_duration = 16 * 4 * step_duration  # 16 bars
    loop = AudioSegment.silent(duration=total_duration)
    
    for instr, data in patterns.items():
        sample = AudioSegment.from_wav(data['sample'])
        pattern = data['pattern']
        
        # Final safety check
        if len(pattern) == 0:
            continue
            
        for step, val in enumerate(pattern):
            if val:
                position = step * step_duration
                loop = loop.overlay(sample, position=position)
    return loop

def create_stems(patterns, output_dir):
    """Create individual stem tracks"""
    stems_dir = os.path.join(output_dir, 'stems')
    os.makedirs(stems_dir, exist_ok=True)
    stem_files = []
    
    for instr, data in patterns.items():
        if not data['sample'] or not os.path.exists(data['sample']):
            continue
            
        pattern = process_pattern(data['pattern'])
        sample = AudioSegment.from_wav(data['sample'])
        
        # Create silent track for this stem
        stem = AudioSegment.silent(duration=len(create_drum_loop({instr: data})))
        
        # Add hits
        step_duration = len(stem) / len(pattern)
        for step, val in enumerate(pattern):
            if val:
                position = step * step_duration
                stem = stem.overlay(sample, position=position)
        
        # Save stem
        stem_path = os.path.join(stems_dir, f"{instr}.wav")
        stem.export(stem_path, format="wav")
        stem_files.append(stem_path)
    
    return stem_files

def generate_drum_loop(genre, style, inspired_by, output_path):
    # Validate inputs
    genre_key = next((g for g in drum_patterns.keys() if g.lower() == genre.lower()), None)
    if not genre_key:
        raise ValueError(f"Invalid genre: {genre}")
    
    styles = drum_patterns[genre_key].keys()
    style_key = next((s for s in styles if s.lower() == style.lower()), None)
    if not style_key:
        raise ValueError(f"Invalid style '{style}' for genre '{genre}'")

    # Generate loop
    patterns = select_pattern_and_instruments(
        drum_patterns[genre_key][style_key],
        genre_key,
        inspired_by
    )
    
    if not patterns:
        raise ValueError("No instruments could be selected for the loop")

    # Create parent directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Export WAV
    loop = create_drum_loop(patterns)
    loop.export(output_path, format="wav")

    folder_path = os.path.dirname(output_path)
    filename = os.path.basename(output_path)

    # Create and zip stems
    stems = create_stems(patterns, folder_path)

    if stems:
        zip_path = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for stem in stems:
                zipf.write(stem, os.path.basename(stem))
        
        # Cleanup stem files
        for stem in stems:
            os.remove(stem)
        os.rmdir(os.path.join(folder_path, 'stems'))