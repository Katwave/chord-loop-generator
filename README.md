# Python Powered GUI App For generating chords and drum loops in my production style

## Data Training/Feeding Process for Drum Patterns

- First make sure to have midi files setup
- You can create midi files using fl studio by running script "python midi_exporter_automation.py"
- Then in fl studio you can click on the channels you want to export midi files of
- Make sure the channels are named accordingly (should have key words snare, kick, hi-hat, open-hat, percussion, clap)
- Then make sure you have fl studio open to make sure channels are clicked once the program runs

- Then you can run the midi file saver to save the files in the right folders "python midi_file_saver.py"

- Then you can generate the patterns from the midi files by running "python json-data/midi_to_json.py"
- Make sure to update genre and style inside this file midi_to_json.py to create the right json data

- Then to merge all the json files into a single json file called "drum_patterns.json", run the script "python json-data/merge_json_data.py"
