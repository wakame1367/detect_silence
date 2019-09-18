import itertools
from pathlib import Path

from pydub import AudioSegment
from pydub.utils import db_to_float
from pytube import YouTube

root_path = Path("resources")

if not root_path.exists():
    root_path.mkdir()


# https://github.com/jiaaro/pydub/blob/master/pydub/silence.py
def detect_silence(audio_segment, min_silence_len=1000, silence_thresh=-16,
                   seek_step=1):
    seg_len = len(audio_segment)

    # you can't have a silent portion of a sound that is longer than the sound
    if seg_len < min_silence_len:
        return []

    # convert silence threshold to a float value (so we can compare it to rms)
    silence_thresh = db_to_float(
        silence_thresh) * audio_segment.max_possible_amplitude

    # find silence and add start and end indicies to the to_cut list
    silence_starts = []

    # check successive (1 sec by default) chunk of sound for silence
    # try a chunk at every "seek step" (or every chunk for a seek step == 1)
    last_slice_start = seg_len - min_silence_len
    slice_starts = range(0, last_slice_start + 1, seek_step)

    # guarantee last_slice_start is included in the range
    # to make sure the last portion of the audio is seached
    if last_slice_start % seek_step:
        slice_starts = itertools.chain(slice_starts, [last_slice_start])

    for i in slice_starts:
        audio_slice = audio_segment[i:i + min_silence_len]
        if audio_slice.rms <= silence_thresh:
            silence_starts.append(i)

    # short circuit when there is no silence
    if not silence_starts:
        return []

    # combine the silence we detected into ranges (start ms - end ms)
    silent_ranges = []

    prev_i = silence_starts.pop(0)
    current_range_start = prev_i

    for silence_start_i in silence_starts:
        continuous = (silence_start_i == prev_i + seek_step)

        # sometimes two small blips are enough for one particular slice to be
        # non-silent, despite the silence all running together. Just combine
        # the two overlapping silent ranges.
        silence_has_gap = silence_start_i > (prev_i + min_silence_len)

        if not continuous and silence_has_gap:
            silent_ranges.append([current_range_start,
                                  prev_i + min_silence_len])
            yield current_range_start, prev_i + min_silence_len
            current_range_start = silence_start_i
        prev_i = silence_start_i


def main():
    # url = "https://www.youtube.com/watch?v=2A3gRyT54Wc"
    # download_audio(url)
    path = "resources/audio/02-505_チームメイトのためにdocstringを書こう(ku-mu).mp4"
    audio_seg = AudioSegment.from_file(path, "mp4")

    # silent point at first
    for silent_point in detect_silence(audio_seg):
        print(silent_point)
        break


def download_audio(url, file_ext='mp4'):
    audio_path = root_path / "audio"
    if not audio_path.exists():
        audio_path.mkdir()
    yt = YouTube(url)
    query = yt.streams.filter(only_audio=True, file_extension=file_ext).all()
    if query:
        query[0].download(str(audio_path))


if __name__ == '__main__':
    main()
