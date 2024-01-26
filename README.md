# chordgen
Generate synthetic note combinations from real audio

## Folders
- **Single Piano Notes**: all of the Piano files from the [University of Iowa Electronic Music Labs Dataset](https://theremin.music.uiowa.edu/MISpiano.html).
- **Single Piano Notes (Trimmed)**: the same files as above, but with silence at the beginning and end removed. Does not include the pianissimo files, as they were too quiet to remove silence from.
- **Simple Piano Chords (Trimmed)**: Each of the following chords using the named note as the root note. All notes in the chord are the same dynamic
    - Major
    - Minor
    - Diminished
    - Augmented
    - Major 7th
    - Minor 7th
    - Diminished 7th
    - Augmented 7th
    - Dominant 7th
    - Half-diminished 7th
    - Minor Major 7th
    - Major 6th
    - Minor 6th
- **Simple Piano Intervals (Trimmed)**: Each of the following intervals using the names note as the root note. Both notes in the interval are the same dynamic
    - Minor 2nd
    - Major 2nd
    - Minor 3rd
    - Major 3rd
    - Perfect 4th
    - Tritone
    - Perfect 5th
    - Minor 6th
    - Major 6th
    - Minor 7th
    - Major 7th
    - Octave

## Usage
### Regenerating common chords and intervals
To regenerate common chords and intervals (from other recordings, redoing it yourself, etc.) call `generate_chords` or `generate_intervals` from `get_chords.py`. Chords/intervals will be generated automatically with the file naming convention of `{instrument}.{dynamic}.{root note}.{chord/interval name}.aiff`. (Note: this will take some time)

### Creating new note combinations
To create other note combinations, call `get_chord` followed by `save_chord_audio` both from `spectrograms.py`. 

`get_chord` requires 5 parameters: **tonic**, **chord_type**, **octave**, **name**, **degrees**, and returns two elements: `chord` and `chord_name` 
- **tonic**: This is the letter name of the lowest note of your note combinations (A, Bb, B, C, Db, etc.. If you give a sharp, it will be converted to a flat)
- **chord_type**: If not one of the chords listed above, put `None`
- **octave**: The octave in which the root note (tonic) occurs (a number between 0-8. Make sure that the root note name occurs within this octave. There are only 3 notes with octave 0 and 1 with octave 8)
- **name** How your file will be distinguished. The file will be created with the naming convention {instrument}.{dynamic}.{root note}.{name}.aiff
- **degrees**: Not needed if one of the chords listed above. Otherwise the most important part. Must include 0 followed by the scale degree (1-12) of the other notes you wish to generate a combination with. 

`save_chord_audio` requires 5 parameters: **chord**, **chord_name**, **dynamic**, **input_dir**, **output_dir**, and creates the file.
- **chord**: The first return value from `get_chord`
- **chord_name**: The second return value from `get_chord`
- **dynamic**: The dynamic (ff, mf, pp) in which to generate the files
- **input_dir**: The directory where the individual notes are stored
- **output_dir**: The directory in which to save the new file (Needs to exist already)

#### Example:
```py
chord, name = get_chord('A', None, 4, 'demo', [0, 7, 11])
save_chord_audio(chord, name, 'ff', 'Single Piano Notes (Trimmed)', 'Test Combos')
```
Will generate a file in the folder `Test Combos` named `Piano.ff.A4.demo.aiff` that contains a combination of A4, E5, and Ab5.

### Other
There are many other functions in `spectrogram.py`, mostly for creating and displaying spectrograms. Adding comments is a TODO. Hopefully relatively self-explanatory if needed, otherwise send me a message and I am happy to help
