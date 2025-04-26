# gen_chords.py (refactored)
import os
from music21 import stream, harmony, midi
from chord_templates import chord_progressions, get_random_progression

def generate_chord_progression(genre, mood, output_path):
    # Validate inputs
    genre_key = next((g for g in chord_progressions.keys() if g.lower() == genre.lower()), None)
    if not genre_key:
        raise ValueError(f"Invalid genre: {genre}")
    
    moods = chord_progressions[genre_key].keys()
    mood_key = next((m for m in moods if m.lower() == mood.lower()), None)
    if not mood_key:
        raise ValueError(f"Invalid mood '{mood}' for genre '{genre}'")

    # Generate progression
    progression = get_random_progression(genre=genre_key, mood=mood_key)
    
    # Create MIDI stream
    s = stream.Stream()
    for symbol in progression:
        try:
            cs = harmony.ChordSymbol(symbol)
            cs.duration.quarterLength = 4
            s.append(cs)
        except Exception as e:
            raise ValueError(f"Error parsing chord '{symbol}': {e}")

    # Create parent directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Export MIDI
    mf = midi.translate.streamToMidiFile(s)
    mf.open(output_path, 'wb')
    mf.write()
    mf.close()