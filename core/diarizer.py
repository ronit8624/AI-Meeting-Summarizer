"""
diarizer.py
-----------
Speaker diarization using pyannote.audio 3.1
Tells us WHO spoke and WHEN — e.g. Speaker A: 0.0s-12.3s
Requires HF_TOKEN env variable (free Hugging Face account).
"""

import os
from pyannote.audio import Pipeline


HF_TOKEN = os.getenv("HF_TOKEN")

_pipeline = None


def load_pipeline():
    global _pipeline
    if _pipeline is None:
        if not HF_TOKEN:
            raise RuntimeError(
                "HF_TOKEN not set in .env — needed to download pyannote models.\n"
                "Get it from: https://huggingface.co/settings/tokens"
            )
        print("Loading pyannote speaker diarization pipeline...")
        _pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=HF_TOKEN,
        )
        print("Pyannote pipeline loaded.")
    return _pipeline


def diarize(audio_path: str) -> list:
    """
    Run speaker diarization on a WAV file.

    Returns a list of dicts:
        [{"speaker": "SPEAKER_00", "start": 0.0, "end": 4.2}, ...]
    """
    pipeline = load_pipeline()
    print(f"Running diarization on: {audio_path}")

    diarization = pipeline(audio_path)

    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "speaker": speaker,
            "start":   round(turn.start, 2),
            "end":     round(turn.end,   2),
        })

    print(f"Diarization done — {len(set(s['speaker'] for s in segments))} speaker(s) found.")
    return segments
