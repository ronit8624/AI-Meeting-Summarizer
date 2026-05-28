import os
import logging
from typing import Optional

log = logging.getLogger(__name__)

DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
COMPUTE_TYPE = "int8"
WHISPER_SIZE = os.getenv("WHISPER_MODEL", "small")
HF_TOKEN = os.getenv("HF_TOKEN")


def diarize_audio(
    audio_path: str,
    language: str = "en"
) -> Optional[str]:

    try:

        import whisperx
        import pandas as pd

        from pyannote.audio import Pipeline

        log.info("Loading WhisperX model...")

        model = whisperx.load_model(
            WHISPER_SIZE,
            DEVICE,
            compute_type=COMPUTE_TYPE
        )

        audio = whisperx.load_audio(audio_path)

        result = model.transcribe(
            audio,
            batch_size=8
        )

        log.info("Loading alignment model...")

        align_model, metadata = whisperx.load_align_model(
            language_code=result["language"],
            device=DEVICE
        )

        result = whisperx.align(
            result["segments"],
            align_model,
            metadata,
            audio,
            DEVICE,
            return_char_alignments=False
        )

        if not HF_TOKEN:

            raise RuntimeError(
                "HF_TOKEN not found."
            )

        log.info("Running speaker diarization...")

        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=HF_TOKEN
        )

        diarize_segments = pipeline(audio_path)

        segments_list = []

        for turn, _, speaker in diarize_segments.itertracks(
            yield_label=True
        ):

            segments_list.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })

        diarize_df = pd.DataFrame(
            segments_list
        )

        result = whisperx.assign_word_speakers(
            diarize_df,
            result
        )

        diarized_lines = []

        current_speaker = None

        current_text = []

        for segment in result["segments"]:

            speaker = segment.get(
                "speaker",
                "UNKNOWN"
            )

            text = segment["text"].strip()

            if speaker != current_speaker:

                if current_speaker is not None:

                    diarized_lines.append(
                        f"[{current_speaker}]: {' '.join(current_text)}"
                    )

                current_speaker = speaker

                current_text = [text]

            else:

                current_text.append(text)

        if current_speaker and current_text:

            diarized_lines.append(
                f"[{current_speaker}]: {' '.join(current_text)}"
            )

        return "\n".join(diarized_lines)

    except Exception as e:

        log.exception(
            "Diarization failed."
        )

        return None