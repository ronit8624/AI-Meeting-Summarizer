"""
services/file_service.py
------------------------
Handles all filesystem operations for the meeting pipeline.

Responsibilities:
  - Saving uploaded audio/video files to backend/uploads/{meeting_id}/
  - Building consistent, predictable directory/file paths
  - Writing AI output (metadata.json, transcript.txt) to backend/outputs/{meeting_id}/
  - Reading saved metadata back for the GET /meeting/{meeting_id} endpoint

Directory layout managed by this service:
  backend/
  ├── uploads/
  │   └── {meeting_id}/
  │       └── {original_filename}        ← raw uploaded file
  └── outputs/
      └── {meeting_id}/
          ├── metadata.json              ← full AI pipeline output
          └── transcript.txt             ← plain-text transcript

No other module should touch the filesystem directly.
"""

import os
import uuid
import json
import logging
import shutil
from datetime import datetime, timezone
from typing import Optional

from fastapi import UploadFile

from app.core.config import settings

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# PATH HELPERS
# Centralised path-building so every module uses identical paths.
# ─────────────────────────────────────────────────────────────────

def get_upload_dir(meeting_id: str) -> str:
    """Return the upload directory path for a given meeting_id."""
    return os.path.join(settings.UPLOADS_DIR, meeting_id)


def get_output_dir(meeting_id: str) -> str:
    """Return the output directory path for a given meeting_id."""
    return os.path.join(settings.OUTPUTS_DIR, meeting_id)


def get_metadata_path(meeting_id: str) -> str:
    """Return the full path to the metadata.json file for a meeting."""
    return os.path.join(get_output_dir(meeting_id), "metadata.json")


def get_transcript_path(meeting_id: str) -> str:
    """Return the full path to the transcript.txt file for a meeting."""
    return os.path.join(get_output_dir(meeting_id), "transcript.txt")


# ─────────────────────────────────────────────────────────────────
# SAVE UPLOADED FILE
# ─────────────────────────────────────────────────────────────────

async def save_upload_file(file: UploadFile) -> dict:
    """
    Save an uploaded audio/video file to disk under a unique meeting_id.

    Steps:
      1. Generate a UUID as the meeting_id
      2. Create backend/uploads/{meeting_id}/ directory
      3. Stream the file content to disk (memory-efficient for large files)
      4. Return meeting metadata dict

    Args:
        file: The UploadFile object from FastAPI's multipart form parser.

    Returns:
        dict with keys: meeting_id, filename, file_path

    Raises:
        IOError: If the file cannot be written to disk.
    """
    # 1. Generate unique meeting ID
    meeting_id = str(uuid.uuid4())

    # 2. Sanitise filename and build destination path
    original_filename = file.filename or "upload"
    # Replace spaces with underscores for filesystem safety
    safe_filename = original_filename.replace(" ", "_")

    upload_dir = get_upload_dir(meeting_id)
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, safe_filename)

    # 3. Stream file to disk in 1 MB chunks (avoids loading entire file into RAM)
    logger.info(f"Saving uploaded file '{safe_filename}' → {file_path}")

    try:
        with open(file_path, "wb") as dest:
            while chunk := await file.read(1024 * 1024):  # 1 MB chunks
                dest.write(chunk)
    except Exception as e:
        logger.error(f"Failed to save file for meeting {meeting_id}: {e}")
        raise IOError(f"Could not save uploaded file: {e}")

    logger.info(f"File saved successfully. meeting_id={meeting_id}")

    return {
        "meeting_id": meeting_id,
        "filename": safe_filename,
        "file_path": file_path,
    }


# ─────────────────────────────────────────────────────────────────
# GET UPLOAD FILE PATH
# ─────────────────────────────────────────────────────────────────

def get_upload_file_path(meeting_id: str) -> Optional[str]:
    """
    Locate the uploaded audio file for a given meeting_id.

    Since we don't store the filename in a database, we scan the
    upload directory for the first file we find. There should only
    ever be one file per meeting_id directory.

    Returns:
        Absolute path to the audio file, or None if not found.
    """
    upload_dir = get_upload_dir(meeting_id)

    if not os.path.isdir(upload_dir):
        logger.warning(f"Upload directory not found for meeting_id={meeting_id}")
        return None

    # Find the first file in the directory
    for filename in os.listdir(upload_dir):
        full_path = os.path.join(upload_dir, filename)
        if os.path.isfile(full_path):
            logger.info(f"Found upload file: {full_path}")
            return full_path

    logger.warning(f"No files found in upload dir for meeting_id={meeting_id}")
    return None


# ─────────────────────────────────────────────────────────────────
# SAVE MEETING METADATA
# ─────────────────────────────────────────────────────────────────

def save_meeting_metadata(meeting_id: str, data: dict) -> None:
    """
    Persist the full AI pipeline output to disk as metadata.json.

    Also writes a plain-text transcript.txt as a convenience file
    that can be read directly without parsing JSON.

    Args:
        meeting_id: The UUID of the meeting.
        data: Dict containing title, transcript, summary, action_items,
              key_decisions, open_questions, filename.

    Raises:
        IOError: If files cannot be written.
    """
    output_dir = get_output_dir(meeting_id)
    os.makedirs(output_dir, exist_ok=True)

    # Add timestamp to the stored metadata
    data["meeting_id"] = meeting_id
    data["created_at"] = datetime.now(timezone.utc).isoformat()

    # ── Write metadata.json ───────────────────────────────────────
    metadata_path = get_metadata_path(meeting_id)
    try:
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Metadata saved → {metadata_path}")
    except Exception as e:
        logger.error(f"Failed to save metadata for meeting {meeting_id}: {e}")
        raise IOError(f"Could not write metadata: {e}")

    # ── Write transcript.txt (convenience file) ───────────────────
    transcript_path = get_transcript_path(meeting_id)
    try:
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(data.get("transcript", ""))
        logger.info(f"Transcript saved → {transcript_path}")
    except Exception as e:
        # Non-fatal — log and continue, metadata.json is what matters
        logger.warning(f"Could not write transcript.txt: {e}")


# ─────────────────────────────────────────────────────────────────
# LOAD MEETING METADATA
# ─────────────────────────────────────────────────────────────────

def load_meeting_metadata(meeting_id: str) -> Optional[dict]:
    """
    Load previously saved meeting metadata from disk.

    Used by GET /api/v1/meeting/{meeting_id} to retrieve a processed
    meeting without re-running the AI pipeline.

    Returns:
        Parsed metadata dict, or None if the meeting doesn't exist.
    """
    metadata_path = get_metadata_path(meeting_id)

    if not os.path.isfile(metadata_path):
        logger.warning(f"Metadata not found for meeting_id={meeting_id}")
        return None

    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Metadata loaded for meeting_id={meeting_id}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Corrupt metadata.json for meeting {meeting_id}: {e}")
        return None


# ─────────────────────────────────────────────────────────────────
# EXISTENCE CHECK
# ─────────────────────────────────────────────────────────────────

def meeting_exists(meeting_id: str) -> bool:
    """
    Check whether a meeting has been fully processed.

    A meeting is considered processed when its metadata.json exists.
    The upload directory existing alone does NOT count — it just means
    the file was uploaded but /summarize hasn't been called yet.

    Returns:
        True if the meeting has been summarized, False otherwise.
    """
    return os.path.isfile(get_metadata_path(meeting_id))


def upload_exists(meeting_id: str) -> bool:
    """
    Check whether an uploaded file exists for a given meeting_id.

    Used by /summarize to validate the meeting_id before processing.

    Returns:
        True if the upload directory exists and contains at least one file.
    """
    file_path = get_upload_file_path(meeting_id)
    return file_path is not None
