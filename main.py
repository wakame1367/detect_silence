from pathlib import Path

from pydub import AudioSegment
from pydub.silence import detect_silence
from pytube import YouTube

root_path = Path("resources")

if not root_path.exists():
    root_path.mkdir()


def main():
    # url = "https://www.youtube.com/watch?v=2A3gRyT54Wc"
    # download_audio(url)
    path = "resources/audio/02-505_チームメイトのためにdocstringを書こう(ku-mu).mp4"
    audio_seg = AudioSegment.from_file(path, "mp4")
    print(detect_silence(audio_seg))


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
