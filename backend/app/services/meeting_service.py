"""
services/meeting_service.py
----------------------------
Orchestrates the full AI pipeline for a given meeting_id.
"""

import os
import uuid
import logging
import asyncio
from functools import partial

from app.services import file_service

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# INTERNAL: SYNCHRONOUS PIPELINE (Audio)
# ─────────────────────────────────────────────────────────────────

def _run_pipeline(meeting_id: str, audio_file_path: str) -> dict:
    logger.info(f"[{meeting_id}] Step 1/6 — Processing audio: {audio_file_path}")
    chunks = process_input(audio_file_path)
    logger.info(f"[{meeting_id}] Audio split into {len(chunks)} chunk(s).")

    logger.info(f"[{meeting_id}] Step 2/6 — Transcribing audio...")
    transcript = transcribe_all(chunks, language=None)
    logger.info(f"[{meeting_id}] Transcription complete. Length: {len(transcript)} characters.")

    if not transcript.strip():
        raise ValueError(
            "Transcription returned empty text. "
            "The audio may be silent or in an unsupported format."
        )

    return _run_nlp_pipeline(meeting_id, transcript)


# ─────────────────────────────────────────────────────────────────
# INTERNAL: NLP PIPELINE (Text → Summary)
# Used for both audio transcripts and pasted text
# ─────────────────────────────────────────────────────────────────

def _run_nlp_pipeline(meeting_id: str, transcript: str) -> dict:
    logger.info(f"[{meeting_id}] Step 3/6 — Generating title...")
    title = generate_title(transcript)
    logger.info(f"[{meeting_id}] Title: '{title}'")

    logger.info(f"[{meeting_id}] Step 4/6 — Generating summary...")
    summary_text = summarize(transcript)
    logger.info(f"[{meeting_id}] Summary generated.")

    logger.info(f"[{meeting_id}] Step 5/6 — Extracting insights...")
    action_items  = extract_action_items(transcript)
    key_decisions = extract_key_decisions(transcript)
    open_questions = extract_questions(transcript)
    logger.info(f"[{meeting_id}] All insights extracted.")

    logger.info(f"[{meeting_id}] Step 6/6 — Pipeline complete.")

    return {
        "title":          title,
        "transcript":     transcript,
        "summary":        summary_text,
        "action_items":   action_items,
        "key_decisions":  key_decisions,
        "open_questions": open_questions,
    }


# ─────────────────────────────────────────────────────────────────
# PUBLIC: ASYNC SUMMARIZE
# ─────────────────────────────────────────────────────────────────

async def summarize_meeting(
    meeting_id: str = None,
    youtube_url: str = None,
    transcript_text: str = None,
) -> tuple:

    meeting_id = meeting_id or str(uuid.uuid4())

    loop = asyncio.get_event_loop()

    # ── Flow 1: Paste Text — skip audio, go straight to NLP ──────
    if transcript_text:
        logger.info(f"[{meeting_id}] Paste text flow — skipping transcription.")
        try:
            result = await loop.run_in_executor(
                None,
                partial(_run_nlp_pipeline, meeting_id, transcript_text)
            )
        except Exception as e:
            logger.error(f"NLP pipeline failed: {e}")
            raise RuntimeError(f"AI pipeline error: {str(e)}")

        metadata = {**result, "filename": "pasted_text"}
        file_service.save_meeting_metadata(meeting_id, metadata)
        return result, meeting_id

    # ── Flow 2: YouTube URL ───────────────────────────────────────
    if youtube_url:
        logger.info(f"[{meeting_id}] YouTube URL flow.")
        audio_file_path = youtube_url
    # ── Flow 3: Uploaded File ─────────────────────────────────────
    else:
        audio_file_path = file_service.get_upload_file_path(meeting_id)
        if audio_file_path is None:
            raise FileNotFoundError(
                f"No uploaded file found for meeting_id '{meeting_id}'. "
                "Please call /upload first."
            )

    logger.info(f"Starting pipeline for meeting_id={meeting_id}")

    try:
        result = await loop.run_in_executor(
            None,
            partial(_run_pipeline, meeting_id, audio_file_path)
        )
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise RuntimeError(f"AI pipeline error: {str(e)}")

    metadata = {**result, "filename": youtube_url or "uploaded_file"}
    file_service.save_meeting_metadata(meeting_id, metadata)

    return result, meeting_id


# ─────────────────────────────────────────────────────────────────
# PUBLIC: GET MEETING DETAIL
# ─────────────────────────────────────────────────────────────────

def get_meeting_detail(meeting_id: str) -> dict:
    metadata = file_service.load_meeting_metadata(meeting_id)

    if metadata is None:
        raise FileNotFoundError(
            f"Meeting '{meeting_id}' not found. "
            "Either it doesn't exist or hasn't been summarized yet."
        )

    return metadata