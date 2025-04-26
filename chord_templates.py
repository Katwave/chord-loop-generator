# chord_templates.py

import random
import json
import os

# Load chord progressions from JSON file
json_path = os.path.join(os.path.dirname(__file__), "json-data/popular_chords.json")

with open(json_path, "r") as f:
    chord_progressions = json.load(f)

def get_random_progression(genre, mood):
    genre = genre.lower()
    mood = mood.lower()

    # Find matching keys in the JSON data (case-insensitive)
    genre_key = next((g for g in chord_progressions if g.lower() == genre), None)
    if genre_key is None:
        raise ValueError(f"Genre '{genre}' not found in chord progressions")

    mood_key = next((m for m in chord_progressions[genre_key] if m.lower() == mood), None)
    if mood_key is None:
        raise ValueError(f"Mood '{mood}' not found under genre '{genre_key}'")

    return random.choice(chord_progressions[genre_key][mood_key])
