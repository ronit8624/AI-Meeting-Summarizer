import os
import uuid
import yt_dlp

from pydub import AudioSegment


DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:

    unique_id = str(uuid.uuid4())[:8]

    output_path = os.path.join(
        DOWNLOAD_DIR,
        f"%(title)s_{unique_id}.%(ext)s"
    )

    ydl_opts = {

        "format": "bestaudio/best",

        "outtmpl": output_path,

        "quiet": True,

        "noplaylist": True,

        "nocheckcertificate": True,

        "geo_bypass": True,

        "extract_flat": False,

        "cookiefile": None,

        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        },

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            downloaded_file = ydl.prepare_filename(info)

        wav_path = downloaded_file.rsplit(".", 1)[0] + ".wav"

        if not os.path.exists(wav_path):

            audio = AudioSegment.from_file(downloaded_file)

            audio.export(
                wav_path,
                format="wav"
            )

        return wav_path

    except Exception as e:

        raise Exception(
            f"YouTube download failed: {str(e)}"
        )


def split_audio(
    audio_path: str,
    chunk_minutes: int = 10
):

    try:

        audio = AudioSegment.from_wav(audio_path)

    except Exception as e:

        raise Exception(
            f"Audio loading failed: {str(e)}"
        )

    chunk_length_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i in range(
        0,
        len(audio),
        chunk_length_ms
    ):

        chunk = audio[i:i + chunk_length_ms]

        chunk_path = (
            f"{audio_path}_chunk_{i // chunk_length_ms}.wav"
        )

        chunk.export(
            chunk_path,
            format="wav"
        )

        chunks.append(chunk_path)

    if len(chunks) == 0:

        raise Exception(
            "No audio chunks created."
        )

    return chunks


def process_input(source: str):

    if source.startswith("http"):

        audio_path = download_youtube_audio(source)

    else:

        audio_path = source

    chunks = split_audio(audio_path)

    return chunks