"""
schemas/meeting.py
------------------
Pydantic models defining the request and response contracts
for all meeting-related API endpoints.

These models serve three purposes:
  1. Input validation  — FastAPI auto-validates incoming JSON
  2. Output shaping    — FastAPI serializes responses via these models
  3. API documentation — Swagger UI at /docs is auto-generated from them

Flutter ↔ FastAPI communication is fully typed through these contracts.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ─────────────────────────────────────────────────────────────────
# REQUEST MODELS
# ─────────────────────────────────────────────────────────────────

class SummarizeRequest(BaseModel):
    meeting_id: Optional[str] = Field(
        default=None,
        description="UUID returned by /upload endpoint (for file uploads)",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"],
    )
    youtube_url: Optional[str] = Field(
        default=None,
        description="YouTube URL to directly summarize",
        examples=["https://youtu.be/abc123"],
    )
    transcript_text: Optional[str] = Field(
        default=None,
        description="Raw transcript text to summarize directly",
        examples=["Speaker 1: Hello everyone...\nSpeaker 2: Thanks for organizing..."],
    )


class ChatRequest(BaseModel):
    meeting_id: str = Field(
        ...,
        description="UUID of the meeting to query",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"],
    )
    question: str = Field(
        ...,
        min_length=3,
        description="Natural-language question about the meeting",
        examples=["What action items were assigned to John?"],
    )


# ─────────────────────────────────────────────────────────────────
# RESPONSE MODELS
# ─────────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    meeting_id: str = Field(description="Unique identifier for this meeting session")
    filename: str   = Field(description="Original uploaded filename")
    file_path: str  = Field(description="Server-side path where the file is stored")
    message: str    = Field(description="Human-readable status message")


class SummaryResponse(BaseModel):
    meeting_id: str     = Field(description="Unique identifier for this meeting")
    title: str          = Field(description="AI-generated meeting title")
    transcript: str     = Field(description="Full transcribed text from the audio")
    summary: str        = Field(description="AI-generated summary of the meeting")
    action_items: str   = Field(description="Extracted action items with owners and deadlines")
    key_decisions: str  = Field(description="Key decisions made during the meeting")
    open_questions: str = Field(description="Unresolved questions or follow-up topics")
    message: str        = Field(description="Human-readable status message")


class ChatResponse(BaseModel):
    meeting_id: str = Field(description="Meeting that was queried")
    question: str   = Field(description="The question that was asked")
    answer: str     = Field(description="AI-generated answer from the RAG engine")


class MeetingDetailResponse(BaseModel):
    meeting_id: str     = Field(description="Unique identifier for this meeting")
    filename: str       = Field(description="Original uploaded filename")
    title: str          = Field(description="AI-generated title")
    summary: str        = Field(description="Full AI-generated summary")
    transcript: str     = Field(description="Full transcript text")
    action_items: str   = Field(description="Extracted action items")
    key_decisions: str  = Field(description="Key decisions")
    open_questions: str = Field(description="Open questions")
    created_at: str     = Field(description="ISO 8601 timestamp of when the meeting was processed")


class ErrorResponse(BaseModel):
    detail: str               = Field(description="Human-readable error message")
    error_code: Optional[str] = Field(
        default=None,
        description="Machine-readable error code for client-side handling",
    )