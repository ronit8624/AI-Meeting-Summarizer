"""
routes/meeting.py
-----------------
API route handlers for all meeting operations.
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from app.schemas.meeting import (
    UploadResponse,
    SummarizeRequest,
    SummaryResponse,
    ChatRequest,
    ChatResponse,
    MeetingDetailResponse,
)
from app.services import file_service, meeting_service, rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/meeting", tags=["Meetings"])


# ─────────────────────────────────────────────────────────────────
# 1. UPLOAD FILE
# ─────────────────────────────────────────────────────────────────

@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Meeting Audio/Video",
)
async def upload_meeting_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing."
        )

    logger.info(f"Received upload request for file: {file.filename}")

    try:
        result = await file_service.save_upload_file(file)
        return UploadResponse(
            meeting_id=result["meeting_id"],
            filename=result["filename"],
            file_path=result["file_path"],
            message="File uploaded successfully. Proceed to /summarize."
        )
    except IOError as e:
        logger.error(f"IOError saving uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file to disk: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in upload endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during upload."
        )


# ─────────────────────────────────────────────────────────────────
# 2. SUMMARIZE
# ─────────────────────────────────────────────────────────────────

@router.post(
    "/summarize",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Summarize Meeting",
)
async def summarize_meeting_endpoint(request: SummarizeRequest):
    meeting_id      = request.meeting_id
    youtube_url     = request.youtube_url
    transcript_text = request.transcript_text

    # At least one input must be provided
    if not meeting_id and not youtube_url and not transcript_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide one of: meeting_id, youtube_url, or transcript_text."
        )

    try:
        result, meeting_id = await meeting_service.summarize_meeting(
            meeting_id=meeting_id,
            youtube_url=youtube_url,
            transcript_text=transcript_text,
        )
        return SummaryResponse(
            meeting_id=meeting_id,
            title=result["title"],
            transcript=result["transcript"],
            summary=result["summary"],
            action_items=result["action_items"],
            key_decisions=result["key_decisions"],
            open_questions=result["open_questions"],
            message="Meeting processed successfully."
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unhandled error in summarize endpoint: {e}")
        raise HTTPException(status_code=500, detail="An error occurred.")


# ─────────────────────────────────────────────────────────────────
# 3. CHAT WITH TRANSCRIPT (RAG)
# ─────────────────────────────────────────────────────────────────

@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with Transcript",
)
async def chat_with_transcript(request: ChatRequest):
    meeting_id = request.meeting_id
    question   = request.question

    try:
        answer = await rag_service.query_meeting(meeting_id, question)
        return ChatResponse(
            meeting_id=meeting_id,
            question=question,
            answer=answer
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error(f"Unhandled error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="An error occurred.")


# ─────────────────────────────────────────────────────────────────
# 4. GET MEETING DETAIL
# ─────────────────────────────────────────────────────────────────

@router.get(
    "/{meeting_id}",
    response_model=MeetingDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Processed Meeting Details",
)
async def get_meeting_by_id(meeting_id: str):
    try:
        detail = meeting_service.get_meeting_detail(meeting_id)
        return MeetingDetailResponse(
            meeting_id=meeting_id,
            filename=detail.get("filename", "unknown"),
            title=detail["title"],
            summary=detail["summary"],
            transcript=detail["transcript"],
            action_items=detail["action_items"],
            key_decisions=detail["key_decisions"],
            open_questions=detail["open_questions"],
            created_at=detail.get("created_at", "")
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching details for meeting {meeting_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve meeting details.")