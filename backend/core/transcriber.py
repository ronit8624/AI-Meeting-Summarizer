"""
transcriber.py
--------------
Fast transcription using faster-whisper (CTranslate2 INT8).
Optimized for CPU + Apple Silicon.
Supports automatic language detection.
"""

import os

from faster_whisper import WhisperModel


# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
WHISPER_MODEL_SIZE = os.getenv(
    "WHISPER_MODEL",
    "small"
)

DEVICE = os.getenv(
    "WHISPER_DEVICE",
    "cpu"
)

COMPUTE_TYPE = "int8"

_model = None


# ─────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────
def load_model() -> WhisperModel:

    global _model

    if _model is None:

        print(
            f"\nLoading faster-whisper model: "
            f"{WHISPER_MODEL_SIZE} "
            f"on {DEVICE} ({COMPUTE_TYPE})..."
        )

        _model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=DEVICE,
            compute_type=COMPUTE_TYPE,
        )

        print("Model loaded successfully.\n")

    return _model


# ─────────────────────────────────────────────
# TRANSCRIBE SINGLE CHUNK
# ─────────────────────────────────────────────
def transcribe_chunk(
    chunk_path: str,
    language: str = None
) -> str:

    """
    Transcribe a single audio chunk.

    language=None enables automatic language detection.
    """

    model = load_model()

    segments, info = model.transcribe(

        chunk_path,

        language=language,

        beam_size=5,

        vad_filter=True,

        vad_parameters=dict(
            min_silence_duration_ms=500
        ),
    )

    detected_language = info.language

    print(
        f"Detected language: {detected_language}"
    )

    transcript_parts = []

    for segment in segments:

        text = segment.text.strip()

        if text:

            transcript_parts.append(text)

    return " ".join(transcript_parts)


# ─────────────────────────────────────────────
# TRANSCRIBE ALL CHUNKS
# ─────────────────────────────────────────────
def transcribe_all(
    chunks: list,
    language: str = None
) -> str:

    """
    Transcribe all chunks and combine them.
    """

    print(
        "\nUsing faster-whisper for transcription.\n"
    )

    full_transcript = []

    total_chunks = len(chunks)

    for i, chunk in enumerate(chunks):

        print(
            f"Transcribing chunk "
            f"{i + 1}/{total_chunks}..."
        )

        chunk_text = transcribe_chunk(
            chunk,
            language
        )

        if chunk_text.strip():

            full_transcript.append(
                chunk_text
            )

    print("\nTranscription complete.\n")

    return "\n\n".join(full_transcript).strip()