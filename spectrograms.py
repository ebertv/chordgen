import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
NOTES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
CHORDS = ['maj', 'maj6', 'dom7', 'maj7', 'aug', 'aug7', 'min', 'min6', 'min7', 'minmaj7', 'dim', 'dim7', 'hdim7']
AXES = {'stft': 'log', 'cqt': 'cqt_note', 'chroma': 'chroma'}
HOP_LENGTH = 2048
N_FFT = 2048

def get_spectrogram_from_file(file, type='stft', mono=True):
    
    y, sr = librosa.load(file, mono=mono, sr=44100)
    
    if type == 'stft':
        stft = librosa.stft(y, hop_length=HOP_LENGTH, n_fft=N_FFT)
        return stft, sr
    elif type == 'cqt':
        cqt = librosa.cqt(y=y, sr=sr, bins_per_octave=12, hop_length=HOP_LENGTH)
        return cqt, sr
    elif type == 'chroma':
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=HOP_LENGTH)
        return chroma, sr


def plot_same_notes(note, spec_type, note_location='Single Piano Notes'):
    spec_ff, sr = get_spectrogram_from_file(f'{note_location}\Piano.ff.{note}.aiff', spec_type)
    spec_mf, sr = get_spectrogram_from_file(f'{note_location}\Piano.mf.{note}.aiff', spec_type)
    spec_pp, sr = get_spectrogram_from_file(f'{note_location}\Piano.pp.{note}.aiff', spec_type)

    if spec_type != 'chroma':
        spec_ff = librosa.amplitude_to_db(np.abs(spec_ff), ref=np.max)
        spec_mf = librosa.amplitude_to_db(np.abs(spec_mf), ref=np.max)
        spec_pp = librosa.amplitude_to_db(np.abs(spec_pp), ref=np.max)
    else:
        spec_ff = np.abs(spec_ff)
        spec_mf = np.abs(spec_mf)
        spec_pp = np.abs(spec_pp)

    fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True)
    img1 = librosa.display.specshow(spec_ff, x_axis='time', y_axis=AXES[spec_type], ax=ax[0], sr=sr)
    ax[0].set(title=note+' - ff')
    img2 = librosa.display.specshow(spec_mf, x_axis='time', y_axis=AXES[spec_type], ax=ax[1], sr=sr)
    ax[1].set(title=note+' - mf')
    img3 = librosa.display.specshow(spec_pp, x_axis='time', y_axis=AXES[spec_type], ax=ax[2], sr=sr)
    ax[2].set(title=note+' - pp')

    for ax_i in ax:
        ax_i.label_outer()

    if spec_type == 'chroma':
        fig.colorbar(img1, ax=[ax[0], ax[1], ax[2]])
    else:
        fig.colorbar(img1, ax=[ax[0], ax[1], ax[2]], format="%+2.f dB")

    fig.suptitle(f'{spec_type} plot for {note} at different dynamics')

    plt.show()

def _get_note_start_(spec, spec_type='stft'):
    if spec_type == 'stft':
        threshold = 10
    elif spec_type == 'cqt':
        threshold = 0.1
    elif spec_type == 'chroma':
        threshold = 0
    temp = np.abs(spec)
    for i in range(temp.shape[-1]):
        if np.sum(temp[:, i]) > threshold:
            return i
    return 0

def get_chord_spectrogram(specs, spec_type='stft', mono=True):
    if mono:
        max_shape = [max(spec.shape[-2] for spec in specs), max(spec.shape[-1] for spec in specs)]
        min_shape = [min(spec.shape[-2] for spec in specs), min(spec.shape[-1] for spec in specs)]
    else:
        max_shape = [2, max(spec.shape[-2] for spec in specs), max(spec.shape[-1] for spec in specs)]
        min_shape = [2, min(spec.shape[-2] for spec in specs), min(spec.shape[-1] for spec in specs)]
    chord_spec = np.zeros(min_shape, dtype=np.complex128)
    start_idxs = [_get_note_start_(spec, spec_type) for spec in specs]
    first_start_idx = min(start_idxs)
    for spec, start_idx in zip(specs, start_idxs):
        start_idx -= first_start_idx
        for i in range(spec.shape[-2]):
            for j in range(spec.shape[-1]):
                if j >= chord_spec.shape[-1]:
                    break
                if mono:
                    if j+start_idx < spec.shape[-1]:
                        chord_spec[i][j] += spec[i][j+start_idx]
                    else:
                        chord_spec[i][j] += spec[i][-1]
                else:
                    if j+start_idx < spec.shape[-1]:
                        chord_spec[0][i][j] += spec[0][i][j+start_idx]
                        chord_spec[1][i][j] += spec[1][i][j+start_idx]
                    else:
                        chord_spec[0][i][j] += spec[0][i][-1]
                        chord_spec[1][i][j] += spec[1][i][-1]
    return chord_spec

def plot_chord_breakdown(chord, chord_name, dynamic, spec_type, note_location='Single Piano Notes'):
    spec = [get_spectrogram_from_file(f'{note_location}\Piano.{dynamic}.{note}.aiff', spec_type) for note in chord]
    sr = spec[0][1]
    spec = [s[0] for s in spec]
    spec.append(get_chord_spectrogram(spec, spec_type))

    if spec_type != 'chroma':
        spec = [librosa.amplitude_to_db(np.abs(s), ref=np.max) for s in spec]
    else:
        spec = [np.abs(s) for s in spec]

    fig, ax = plt.subplots(nrows=len(chord)+1, ncols=1, sharex=True)

    imgs = [librosa.display.specshow(s, x_axis='time', y_axis=AXES[spec_type], ax=ax[i], sr=sr) for i, s in enumerate(spec)]
    for i in range(len(chord)):
        ax[i].set(title=chord[i])
    ax[len(chord)].set(title=chord_name)

    for ax_i in ax:
        ax_i.label_outer()

    if spec_type == 'chroma':
        fig.colorbar(imgs[0], ax=ax)
    else:
        fig.colorbar(imgs[0], ax=ax, format="%+2.f dB")

    fig.suptitle(f'{spec_type} plot for {chord_name} ({dynamic})')

    plt.show()

def save_chord_audio(chord, chord_name, dynamic, input_dir='Single Piano Notes', output_dir='.'):
    chord_data = [get_spectrogram_from_file(f'{input_dir}/Piano.{dynamic}.{note}.aiff', mono=False) for note in chord]
    chord = get_chord_spectrogram([chord_data[i][0] for i in range(len(chord_data))], mono=False)
    sr = chord_data[0][1]
    sf.write(f'{output_dir}/Piano.{dynamic}.{chord_name}.aiff', librosa.istft(chord, hop_length=HOP_LENGTH).transpose(), sr)

def save_chord_from_spectrogram(spec, output_path, sr=44100):
    sf.write(output_path, librosa.istft(spec, hop_length=HOP_LENGTH).transpose(), sr)

def get_chord(tonic, chord_type, octave=4, name=None, degrees=None):
    tonic = _convert_to_flats_(tonic)
    if chord_type in CHORDS:
        chord_name = f'{tonic}{octave}.{chord_type}'
    else: 
        chord_name = f'{tonic}{octave}.{name}'

    sd_0 = f'{tonic}{octave}'
    sd_1 = NOTES.index(tonic)+1
    if sd_1 > 11:
        sd_1 %= 12
        sd_1 = f'{NOTES[sd_1]}{str(octave+1)}'
    else:
        sd_1 = f'{NOTES[sd_1]}{octave}'
    sd_2 = NOTES.index(tonic)+2
    if sd_2 > 11:
        sd_2 %= 12
        sd_2 = f'{NOTES[sd_2]}{str(octave+1)}'
    else:
        sd_2 = f'{NOTES[sd_2]}{octave}'
    sd_3 = NOTES.index(tonic)+3
    if sd_3 > 11:
        sd_3 %= 12
        sd_3 = f'{NOTES[sd_3]}{str(octave+1)}'
    else:
        sd_3 = f'{NOTES[sd_3]}{octave}'
    sd_4 = NOTES.index(tonic)+4
    if sd_4 > 11:
        sd_4 %= 12
        sd_4 = f'{NOTES[sd_4]}{str(octave+1)}'
    else:
        sd_4 = f'{NOTES[sd_4]}{octave}'
    sd_5 = NOTES.index(tonic)+5
    if sd_5 > 11:
        sd_5 %= 12
        sd_5 = f'{NOTES[sd_5]}{str(octave+1)}'
    else:
        sd_5 = f'{NOTES[sd_5]}{octave}'
    sd_6 = NOTES.index(tonic)+6
    if sd_6 > 11:
        sd_6 %= 12
        sd_6 = f'{NOTES[sd_6]}{str(octave+1)}'
    else:
        sd_6 = f'{NOTES[sd_6]}{octave}'
    sd_7 = NOTES.index(tonic)+7
    if sd_7 > 11:
        sd_7 %= 12
        sd_7 = f'{NOTES[sd_7]}{str(octave+1)}'
    else:
        sd_7 = f'{NOTES[sd_7]}{octave}'
    sd_8 = NOTES.index(tonic)+8
    if sd_8 > 11:
        sd_8 %= 12
        sd_8 = f'{NOTES[sd_8]}{str(octave+1)}'
    else:
        sd_8 = f'{NOTES[sd_8]}{octave}'
    sd_9 = NOTES.index(tonic)+9
    if sd_9 > 11:
        sd_9 %= 12
        sd_9 = f'{NOTES[sd_9]}{str(octave+1)}'
    else:
        sd_9 = f'{NOTES[sd_9]}{octave}'
    sd_10 = NOTES.index(tonic)+10
    if sd_10 > 11:
        sd_10 %= 12
        sd_10 = f'{NOTES[sd_10]}{str(octave+1)}'
    else:
        sd_10 = f'{NOTES[sd_10]}{octave}'
    sd_11 = NOTES.index(tonic)+11
    if sd_11 > 11:
        sd_11 %= 12
        sd_11 = f'{NOTES[sd_11]}{str(octave+1)}'
    else:
        sd_11 = f'{NOTES[sd_11]}{octave}'
    sd_12 = NOTES.index(tonic)+12
    if sd_12 > 11:
        sd_12 %= 12
        sd_12 = f'{NOTES[sd_12]}{str(octave+1)}'
    else:
        sd_12 = f'{NOTES[sd_12]}{octave}'

    scale_degrees = [sd_0, sd_1, sd_2, sd_3, sd_4, sd_5, sd_6, sd_7, sd_8, sd_9, sd_10, sd_11, sd_12]
    
    if chord_type in CHORDS:
        if chord_type == 'maj':
            chord = [sd_0, sd_4, sd_7]
        elif chord_type == 'maj6':
            chord = [sd_0, sd_4, sd_7, sd_9]
        elif chord_type == 'dom7':
            chord = [sd_0, sd_4, sd_7, sd_10]
        elif chord_type == 'maj7':
            chord = [sd_0, sd_4, sd_7, sd_11]
        elif chord_type == 'aug':
            chord = [sd_0, sd_4, sd_8]
        elif chord_type == 'aug7':
            chord = [sd_0, sd_4, sd_8, sd_10]
        elif chord_type == 'min':
            chord = [sd_0, sd_3, sd_7]
        elif chord_type == 'min6':
            chord = [sd_0, sd_3, sd_7, sd_9]
        elif chord_type == 'min7':
            chord = [sd_0, sd_3, sd_7, sd_10]
        elif chord_type == 'minmaj7':
            chord = [sd_0, sd_3, sd_7, sd_11]
        elif chord_type == 'dim':
            chord = [sd_0, sd_3, sd_6]
        elif chord_type == 'dim7':
            chord = [sd_0, sd_3, sd_6, sd_9]
        elif chord_type == 'hdim7':
            chord = [sd_0, sd_3, sd_6, sd_10]
    else:
        chord = [scale_degrees[i] for i in degrees]

    return chord, chord_name

def _convert_to_flats_(note):
    if note == 'Cb':
        note = 'B'

    if note == 'B#':
        note = 'C'

    if note == 'E#':
        note = 'F'

    if note == 'Fb':
        note = 'E'

    if '#' in note:
        note = ALPHABET[(ALPHABET.index(note[0])+1)%7]
        note += 'b'
    
    return note

def plot_spectrogram(spec, spec_name, dynamic, spec_type, sr, title=None):
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 5)
    
    if spec_type != 'chroma':
        spec = librosa.amplitude_to_db(np.abs(spec), ref=np.max)
    else:
        spec = np.abs(spec)
    
    img1 = librosa.display.specshow(spec, sr=sr, hop_length=HOP_LENGTH, y_axis=AXES[spec_type], ax=ax, x_axis='s')
    if title == None:
        title = f'{spec_name} {dynamic} {spec_type}'
        ax.set_title(f'{spec_name} {dynamic} {spec_type}')
    else:
        ax.set_title(title)
    
    if spec_type == 'chroma':
        fig.colorbar(img1, ax=ax)
    else:
        fig.colorbar(img1, ax=ax, format="%+2.f dB")
    plt.savefig(spec_name)
    plt.close()

def plot_single_note(note, dynamic, spec_type, note_location='Single Piano Notes'):
    note = _convert_to_flats_(note)
    spec, sr = get_spectrogram_from_file(f'{note_location}\Piano.{dynamic}.{note}.aiff', spec_type)
    plot_spectrogram(spec, note, dynamic, spec_type, sr)

def plot_chord(chord, chord_name, dynamic, spec_type, note_location='Single Piano Notes'):
    spec = [get_spectrogram_from_file(f'{note_location}\Piano.{dynamic}.{note}.aiff', spec_type) for note in chord]
    sr = spec[0][1]
    spec = [s[0] for s in spec]
    chord_spec = get_chord_spectrogram(spec, spec_type)
    
    plot_spectrogram(chord_spec, chord_name, dynamic, spec_type, sr)

def save_spectrogram(spec, spec_name, dynamic, spec_type):
    np.abs(spec).astype(np.float32).tofile(f'{spec_name}_{dynamic}_{spec_type}.csv')

def load_spectrogram(spec_name, dynamic, spec_type):
    spec = np.fromfile(f'{spec_name}_{dynamic}_{spec_type}.csv', dtype=np.float32)
    if spec_type == 'stft':
        spec = spec.reshape(1025,-1)
    elif spec_type == 'cqt':
        spec = spec.reshape(84,-1)
    elif spec_type == 'chroma':
        spec = spec.reshape(12,-1)
    return spec

def plot_spectrogram_from_file(file, name, dynamic, spec_type='stft'):
    spec, sr = get_spectrogram_from_file(file, spec_type)
    plot_spectrogram(spec, name, dynamic, spec_type, sr)
