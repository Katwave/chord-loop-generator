import json
import random
import os

# Mood-specific chord pools (compatible with music21 harmony.ChordSymbol)
mood_chord_choices = {
    'Sad': ['Am', 'Em', 'Dm', 'Bm7b5', 'Cm', 'F#m7', 'Cmaj7', 'Gm', 'Fmaj7', 'E7'],
    'Happy': ['C', 'G', 'F', 'D', 'A', 'E', 'Cmaj7', 'A7', 'D7', 'G7'],
    'Uplifting': ['Cmaj7', 'Fmaj7', 'D', 'G', 'Amaj7', 'Emaj7', 'Dadd9', 'G6'],
    'Chilled': ['Am7', 'D7', 'Gmaj7', 'Cmaj7', 'Bm7', 'Em7', 'F#m7'],
    'Atmospheric': ['Dadd9', 'Cmaj7', 'Em9', 'G6', 'Am9', 'Fmaj7', 'Bm7b5']
}

genres = ['Gospel', 'HipHop', 'EDM', 'Pop', 'Rock', 'Jazz', 'Classical', 'Reggae', 'LoFi', 'R&B']
moods = ['Sad', 'Happy', 'Uplifting', 'Chilled', 'Atmospheric']

def generate_progression(mood):
    chord_pool = mood_chord_choices[mood]
    length = random.choice([4, 8])
    return random.sample(chord_pool, min(length, len(chord_pool)))

# Generate progressions
all_progressions = {}
for genre in genres:
    all_progressions[genre] = {}
    for mood in moods:
        all_progressions[genre][mood] = [generate_progression(mood) for _ in range(100)]

# Save to JSON
output_path = "chords_by_genre_mood_large.json"
with open(output_path, "w") as f:
    json.dump(all_progressions, f, indent=2)

print(f"✅ Saved 100 progressions per genre-mood to: {os.path.abspath(output_path)}")
