import spectrograms as sp
import os

def get_common_chords(note_location='Single Piano Notes (Trimmed)'):
    octaves = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    common_chords = []
    for octave in octaves:
        for note in sp.NOTES:
            for chord in sp.CHORDS:
                common_chords.append(sp.get_chord(note, chord, octave))

    for chord in common_chords.copy():
        for note in chord[0]:
            if not os.path.isfile(f'{note_location}/Piano.mf.{note}.aiff') or not os.path.isfile(f'{note_location}/Piano.ff.{note}.aiff'):
                common_chords.remove(chord)
                break

    return common_chords

def get_all_intervals(note_location='Single Piano Notes (Trimmed)'):
    octaves = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    intervals = ["minor_second", "major_second", "minor_third", "major_third", "perfect_fourth", "tritone", "perfect_fifth", "minor_sixth", "major_sixth", "minor_seventh", "major_seventh", "octave"]

    all_intervals = []
    for octave in octaves:
        for note in sp.NOTES:
            for i, interval in enumerate(intervals):
                all_intervals.append(sp.get_chord(note, None, octave, interval, degrees=[0, i+1]))

    for interval in all_intervals.copy():
        for note in interval[0]:
            if not os.path.isfile(f'{note_location}/Piano.mf.{note}.aiff') or not os.path.isfile(f'{note_location}/Piano.ff.{note}.aiff'):
                all_intervals.remove(interval)
                break

    return all_intervals

def generate_chords(note_location='Single Piano Notes (Trimmed)', output_location='Simple Piano Chords (Trimmed)'):
    chords = get_common_chords(note_location=note_location)
    for i, chord in enumerate(chords):
        for j, dynamic in enumerate(['mf', 'ff']):
            if not os.path.isfile(f'{output_location}/Piano.{dynamic}.{chord[1]}.aiff'):
                print(f'{((((i+1)*3)-(3-j))/(len(chords)*3))*100:.2f}% complete (currently generating {chord[1]} at {dynamic})              ', end='\r')
                sp.save_chord_audio(chord[0], chord[1], dynamic, input_dir=note_location, output_dir=output_location)

def generate_intervals(note_location='Single Piano Notes (Trimmed)', output_location='Simple Piano Intervals (Trimmed)'):
    intervals = get_all_intervals(note_location=note_location)
    for i, interval in enumerate(intervals):
        for j, dynamic in enumerate(['mf', 'ff']):
            if not os.path.isfile(f'{output_location}\Piano.{dynamic}.{interval[1]}.aiff'):
                print(f'{((((i+1)*3)-(3-j))/(len(intervals)*3))*100:.2f}% complete (currently generating {interval[1]} at {dynamic})              ', end='\r')
                sp.save_chord_audio(interval[0], interval[1], dynamic, input_dir=note_location, output_dir=output_location)
